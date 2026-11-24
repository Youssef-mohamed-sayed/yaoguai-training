import hashlib
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import event

from app import create_app
from app.extensions import db
from app.models import LearningActivity, LearningTask, MemberGroup, MemberLevel, Module, Platform, TaskSubmission, User


def register(client, username="Learner"):
    response = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username.lower()}@example.com",
        "password": "a-strong-test-password",
    })
    assert response.status_code == 201
    return response.json["data"]["user"]


def make_lesson(app):
    with app.app_context():
        platform = Platform(id="programming", name="Programming", sort_order=1)
        module = Module(id="programming/basics", platform=platform, title="Basics", sort_order=1)
        activity = LearningActivity(id="programming/basics/first-program", module=module,
                                    stable_key="first-program", title="First program",
                                    activity_type="lesson", sort_order=1, is_required=True)
        db.session.add_all([platform, module, activity])
        db.session.commit()
        return activity.id


def test_lesson_requires_authenticated_open_and_module_progress_is_derived(app, client):
    activity_id = make_lesson(app)
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 401
    register(client)
    complete_url = f"/api/progress/activities/{activity_id}/complete"
    assert client.post(complete_url, json={}).status_code == 409
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    snapshot = client.get("/api/progress").json["data"]
    item = snapshot["platforms"][0]["modules"][0]["activities"][0]
    assert item["started"] is True
    assert item["completed"] is False
    response = client.post(complete_url, json={})
    assert response.status_code == 200
    assert response.json["data"]["module"]["completed"] is True
    progress = client.get("/api/progress").json["data"]
    assert progress["overall"]["completion_percent"] == 100


def test_progress_dashboard_reads_member_activity_progress_in_one_batch(app, client):
    make_lesson(app)
    with app.app_context():
        for index in range(20):
            module_id = f"programming/module-{index}"
            module = Module(id=module_id, platform_id="programming", title=f"Module {index}", sort_order=index + 2)
            activity = LearningActivity(id=f"{module_id}/lesson", module=module,
                                        stable_key="lesson", title="Lesson", activity_type="lesson",
                                        sort_order=1, is_required=True)
            db.session.add_all([module, activity])
        db.session.commit()
    register(client)
    statements = []
    def capture(_conn, _cursor, statement, *_args):
        statements.append(statement)
    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", capture)
    try:
        response = client.get("/api/progress")
    finally:
        with app.app_context():
            event.remove(db.engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    progress_reads = [sql for sql in statements if "user_activity_progress" in sql.lower()]
    assert len(progress_reads) == 1


def test_catalog_endpoints_batch_module_activity_queries(app, client):
    with app.app_context():
        platform = Platform(id="programming", name="Programming", sort_order=1)
        db.session.add(platform)
        for index in range(20):
            module_id = f"programming/catalog-{index}"
            module = Module(id=module_id, platform=platform, title=f"Module {index}", sort_order=index)
            activity = LearningActivity(id=f"{module_id}/lesson", module=module,
                                        stable_key="lesson", title="Lesson", activity_type="lesson",
                                        sort_order=1, is_required=True)
            db.session.add_all([module, activity])
        db.session.commit()

    statements = []
    def capture(_conn, _cursor, statement, *_args):
        statements.append(statement)
    with app.app_context():
        event.listen(db.engine, "before_cursor_execute", capture)
    try:
        catalog = client.get("/api/platforms")
        catalog_reads = list(statements)
        statements.clear()
        modules = client.get("/api/platforms/programming/modules")
    finally:
        with app.app_context():
            event.remove(db.engine, "before_cursor_execute", capture)
    assert catalog.status_code == modules.status_code == 200
    assert len([sql for sql in catalog_reads if "from learning_activities" in sql.lower()]) == 1
    assert len([sql for sql in statements if "from learning_activities" in sql.lower()]) == 1


def test_guest_can_read_catalog_but_cannot_read_personal_progress(app, client):
    make_lesson(app)
    assert client.get("/api/platforms").status_code == 200
    assert client.get("/api/progress").status_code == 401


def test_production_refuses_sqlite_database_configuration():
    with pytest.raises(RuntimeError, match="DATABASE_URL must point to Neon PostgreSQL"):
        create_app({
            "TESTING": True,
            "ENVIRONMENT": "production",
            "SECRET_KEY": "production-test-secret-with-sufficient-entropy",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///should-not-start.db",
        })


def test_regular_member_cannot_use_admin_api(app, client):
    register(client)
    assert client.get("/api/admin/overview").status_code == 403


def test_other_member_progress_is_not_exposed_by_client_identity(app, client):
    activity_id = make_lesson(app)
    first = register(client, "first-user")
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 200
    client.post("/api/auth/logout", json={})
    second = register(client, "second-user")
    assert second["id"] != first["id"]
    result = client.get("/api/progress").json["data"]["overall"]
    assert result["completed_activities"] == 0


def test_bootstrap_admin_must_change_password_before_using_protected_apis(app, client):
    register(client)
    with app.app_context():
        user = db.session.query(User).filter_by(username="Learner").one()
        user.is_admin = True
        user.must_change_password = True
        db.session.commit()
    client.post("/api/auth/logout", json={})
    assert client.post("/api/auth/admin-login", json={
        "username": "Learner", "password": "a-strong-test-password",
    }).status_code == 200
    assert client.get("/api/admin/overview").status_code == 403
    response = client.post("/api/auth/password", json={
        "current_password": "a-strong-test-password",
        "new_password": "another-strong-test-password",
    })
    assert response.status_code == 200
    assert client.get("/api/admin/overview").status_code == 200


def test_challenge_completion_requires_a_server_verified_answer(app, client):
    with app.app_context():
        platform = Platform(id="crypto", name="Crypto", sort_order=1)
        module = Module(id="crypto/test", platform=platform, title="Test", sort_order=1)
        challenge = LearningActivity(
            id="crypto/test/challenge", module=module, stable_key="test-challenge",
            title="Challenge", activity_type="challenge", is_required=True,
            answer_digest=hashlib.sha256(b"correct-answer").hexdigest(),
        )
        db.session.add_all([platform, module, challenge])
        db.session.commit()
    register(client)
    forged = client.post("/api/progress/activities/crypto/test/challenge/complete", json={})
    assert forged.status_code == 409
    result = client.post("/api/progress/activities/crypto/test/challenge/attempts",
                         json={"answer": "correct-answer"})
    assert result.status_code == 200
    assert result.json["data"]["completed"] is True


def make_admin(app, client, username):
    admin = register(client, username)
    with app.app_context():
        db.session.get(User, admin["id"]).is_admin = True
        db.session.commit()
    client.post("/api/auth/logout", json={})
    return admin


def admin_login(client, admin):
    client.post("/api/auth/logout", json={})
    response = client.post("/api/auth/admin-login", json={"username": admin["username"], "password": "a-strong-test-password"})
    assert response.status_code == 200


def test_admin_can_manage_levels_groups_assignments_and_submission_review(app, client):
    activity_id = make_lesson(app)
    admin = make_admin(app, client, "training-admin")
    learner = register(client, "training-learner")
    # The learner does the work; the administrator manages and reviews it.
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 200
    admin_login(client, admin)

    level_response = client.post("/api/admin/levels", json={"name": "Advanced", "rank": 2})
    assert level_response.status_code == 201
    level_id = level_response.json["data"]["id"]
    assert client.patch(f"/api/admin/members/{learner['id']}", json={"level_id": level_id}).status_code == 200

    group_response = client.post("/api/admin/groups", json={"name": "Blue Team", "level_id": level_id})
    assert group_response.status_code == 201
    group_id = group_response.json["data"]["id"]
    assert client.put(f"/api/admin/groups/{group_id}/members/{learner['id']}", json={}).status_code == 200

    task_response = client.post("/api/admin/tasks", json={
        "title": "Review the lesson", "module_id": "programming/basics",
        "platform_id": "programming", "group_ids": [group_id],
        "requirements": [{"activity_id": activity_id, "requires_review": True}],
    })
    assert task_response.status_code == 201
    task_id = task_response.json["data"]["id"]
    with app.app_context():
        submission = TaskSubmission(task_id=task_id, user_id=learner["id"], content="Completed")
        db.session.add(submission)
        db.session.commit()
        submission_id = submission.id
    review = client.patch(f"/api/admin/submissions/{submission_id}",
                          json={"status": "approved", "feedback": "Reviewed"})
    assert review.status_code == 200
    detail = client.get(f"/api/admin/members/{learner['id']}").json["data"]
    assert next(task for task in detail["tasks"] if task["id"] == task_id)["status"] == "completed"
    assert client.get("/api/assignments").json["data"] == []  # nothing is ever assigned to an administrator

    with app.app_context():
        assert db.session.get(MemberLevel, level_id).name == "Advanced"
        assert db.session.get(MemberGroup, group_id).members[0].id == learner["id"]
        assert db.session.get(LearningTask, task_id).title == "Review the lesson"
        assert db.session.get(TaskSubmission, submission_id).status == "approved"


def test_admin_dashboard_shows_member_progress_and_private_assigned_deadlines(app, client):
    activity_id = make_lesson(app)
    admin = register(client, "dashboard-admin")
    with app.app_context():
        db.session.get(User, admin["id"]).is_admin = True
        db.session.commit()
    client.post("/api/auth/logout", json={})
    learner = register(client, "dashboard-learner")
    client.post("/api/auth/logout", json={})
    other = register(client, "unassigned-learner")

    # Task definitions and deadlines are private to the administrator.
    client.post("/api/auth/logout", json={})
    client.post("/api/auth/admin-login", json={"username": admin["username"], "password": "a-strong-test-password"})
    assert client.get("/api/admin/members").status_code == 200
    assert all(row["id"] != admin["id"] for row in client.get("/api/admin/members").json["data"])
    group = client.post("/api/admin/groups", json={"name": "Dashboard cohort"}).json["data"]
    assert client.put(f"/api/admin/groups/{group['id']}/members/{learner['id']}", json={}).status_code == 200
    deadline = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    task = client.post("/api/admin/tasks", json={
        "title": "Complete the first program", "instructions": "Work through the activity",
        "platform_id": "programming", "module_id": "programming/basics",
        "group_ids": [group["id"]], "deadline_at": deadline,
        "requirements": [{"activity_id": activity_id}],
    }).json["data"]

    client.post("/api/auth/logout", json={})
    client.post("/api/auth/login", json={"username": learner["username"], "password": "a-strong-test-password"})
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 200
    assert client.get("/api/assignments").status_code == 403
    assert client.get(f"/api/assignments/{task['id']}").status_code == 403

    client.post("/api/auth/logout", json={})
    client.post("/api/auth/login", json={"username": other["username"], "password": "a-strong-test-password"})
    assert client.get("/api/assignments").status_code == 403
    assert client.get(f"/api/assignments/{task['id']}").status_code == 403
    assert client.get(f"/api/admin/members/{learner['id']}").status_code == 403

    client.post("/api/auth/logout", json={})
    client.post("/api/auth/admin-login", json={"username": admin["username"], "password": "a-strong-test-password"})
    detail = client.get(f"/api/admin/members/{learner['id']}")
    assert detail.status_code == 200
    record = detail.json["data"]
    module = next(row for row in record["progress"] if row["module"] == "programming/basics")
    assert module["completed_count"] == module["required_count"] == 1
    assert record["progress"]
    assert client.get("/api/admin/overview").json["data"]["completed_modules"] == 1
    assigned = next(row for row in record["tasks"] if row["id"] == task["id"])
    assert assigned["deadline_at"] is not None
    assert assigned["completed_count"] == 1
    admin_tasks = client.get("/api/admin/tasks").json["data"]
    assert any(target["name"] == "Dashboard cohort" for target in next(row for row in admin_tasks if row["id"] == task["id"])["targets"])


def test_admin_has_separate_login_and_admin_route_redirects(app, client):
    assert client.get("/admin", follow_redirects=False).headers["Location"] == "/admin/login"
    assert client.get("/admin/login").status_code == 200
    admin = register(client, "separate-admin")
    with app.app_context():
        db.session.get(User, admin["id"]).is_admin = True
        db.session.commit()
    client.post("/api/auth/logout", json={})

    ordinary_login = client.post("/api/auth/login", json={
        "username": admin["username"], "password": "a-strong-test-password",
    })
    assert ordinary_login.status_code == 401
    admin_login = client.post("/api/auth/admin-login", json={
        "username": admin["username"], "password": "a-strong-test-password",
    })
    assert admin_login.status_code == 200
    assert admin_login.json["data"]["user"]["is_admin"] is True
    assert client.get("/admin", follow_redirects=False).status_code == 200

    client.post("/api/auth/logout", json={})
    learner = register(client, "separate-learner")
    wrong_portal = client.post("/api/auth/admin-login", json={
        "username": learner["username"], "password": "a-strong-test-password",
    })
    assert wrong_portal.status_code == 401
    assert client.get("/admin", follow_redirects=False).headers["Location"] == "/admin/login"


def test_admin_dashboard_returns_every_panel_in_one_request_without_per_row_queries(app, client):
    make_lesson(app)
    admin = register(client, "bundle-admin")
    with app.app_context():
        db.session.get(User, admin["id"]).is_admin = True
        db.session.commit()
    client.post("/api/auth/logout", json={})
    learners = [register(client, f"bundle-learner{i}") for i in range(3)]
    client.post("/api/auth/logout", json={})
    client.post("/api/auth/admin-login", json={"username": admin["username"], "password": "a-strong-test-password"})
    for index in range(3):
        group = client.post("/api/admin/groups", json={"name": f"Cohort {index}"}).json["data"]
        for learner in learners:
            client.put(f"/api/admin/groups/{group['id']}/members/{learner['id']}", json={})

    statements = []
    with app.app_context():
        @event.listens_for(db.engine, "before_cursor_execute")
        def count(_connection, _cursor, statement, *_args):
            statements.append(statement)
        response = client.get("/api/admin/dashboard")
        event.remove(db.engine, "before_cursor_execute", count)
    assert response.status_code == 200
    data = response.json["data"]
    assert set(data) == {"overview", "members", "levels", "groups", "tasks", "submissions", "platforms"}
    assert len(data["members"]) == 3
    assert [group["member_count"] for group in data["groups"]] == [3, 3, 3]
    assert data["platforms"][0]["id"] == "programming"
    # Same shape as the separate endpoints, so the admin screen can use either.
    assert data["overview"] == client.get("/api/admin/overview").json["data"]
    assert data["groups"] == client.get("/api/admin/groups").json["data"]
    # Query count does not grow with the number of groups or members.
    assert len(statements) <= 24, [s.split("FROM")[-1][:40] for s in statements]


def test_dashboard_requires_an_administrator(app, client):
    assert client.get("/api/admin/dashboard").status_code == 401
    register(client, "plain-member")
    assert client.get("/api/admin/dashboard").status_code == 403


def test_session_endpoint_returns_csrf_token_and_user_in_one_call(app, client):
    guest = client.get("/api/auth/session").json["data"]
    assert guest["user"] is None and guest["csrf_token"]
    register(client, "session-member")
    signed_in = client.get("/api/auth/session").json["data"]
    assert signed_in["user"]["username"] == "session-member" and signed_in["csrf_token"]


def test_administrator_is_not_a_learner(app, client):
    activity_id = make_lesson(app)
    admin = make_admin(app, client, "role-admin")
    learner = register(client, "role-learner")
    client.post("/api/auth/logout", json={})
    admin_login(client, admin)
    # No learner progress is read or written for administrators.
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 403
    assert client.post(f"/api/progress/activities/{activity_id}/heartbeat", json={}).status_code == 403
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 403
    assert client.post(f"/api/progress/activities/{activity_id}/attempts", json={"answer": "x"}).status_code == 403
    response = client.get("/api/progress")
    assert response.status_code == 403 and response.json["error"]["code"] == "admin_not_learner"
    with app.app_context():
        from app.models import UserActivityProgress
        assert db.session.query(UserActivityProgress).filter_by(user_id=admin["id"]).count() == 0
    # An administrator cannot be treated as a member by other administrator actions either.
    level = client.post("/api/admin/levels", json={"name": "Core"}).json["data"]
    assert client.patch(f"/api/admin/members/{admin['id']}", json={"level_id": level["id"]}).status_code == 404
    assert client.get(f"/api/admin/members/{admin['id']}").status_code == 404
    group = client.post("/api/admin/groups", json={"name": "Cohort"}).json["data"]
    assert client.put(f"/api/admin/groups/{group['id']}/members/{admin['id']}", json={}).status_code == 422
    assert client.put(f"/api/admin/groups/{group['id']}/members/{learner['id']}", json={}).status_code == 200
    task = client.post("/api/admin/tasks", json={"title": "Self task", "user_ids": [admin["id"]],
                                                  "requirements": [{"activity_id": activity_id}]})
    assert task.status_code == 422 and task.json["error"]["code"] == "admin_not_learner"
    assert all(row["id"] != admin["id"] for row in client.get("/api/admin/members").json["data"])
    assert client.get("/api/admin/overview").json["data"]["members"] == 1


def test_role_matrix_for_anonymous_member_and_administrator(app, client):
    activity_id = make_lesson(app)
    admin = make_admin(app, client, "matrix-admin")
    client.post("/api/auth/logout", json={})
    admin_paths = ["/api/admin/overview", "/api/admin/members", "/api/admin/levels", "/api/admin/groups",
                   "/api/admin/tasks", "/api/admin/submissions", "/api/admin/dashboard", "/api/assignments"]
    learner_paths = ["/api/progress"]

    # Anonymous: every protected API says sign in (401); the catalog stays public.
    for path in admin_paths + learner_paths:
        assert client.get(path).status_code == 401, path
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 401
    assert client.get("/api/platforms").status_code == 200
    assert client.get("/api/auth/session").json["data"]["user"] is None
    assert client.get("/admin", follow_redirects=False).headers["Location"] == "/admin/login"

    # Learner: own progress works, the administration API is closed (403), /admin goes to the admin sign in.
    register(client, "matrix-learner")
    for path in admin_paths:
        assert client.get(path).status_code == 403, path
    assert client.post("/api/admin/levels", json={"name": "Nope"}).status_code == 403
    assert client.post("/api/admin/groups", json={"name": "Nope"}).status_code == 403
    assert client.get("/api/progress").status_code == 200
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    assert client.get("/admin", follow_redirects=False).headers["Location"] == "/admin/login"

    # Learner sign in is closed to administrators and administrator sign in to learners.
    client.post("/api/auth/logout", json={})
    assert client.post("/api/auth/login", json={"username": admin["username"], "password": "a-strong-test-password"}).status_code == 401
    assert client.post("/api/auth/admin-login", json={"username": "matrix-learner", "password": "a-strong-test-password"}).status_code == 401

    # Administrator: administration works, learner progress is closed (403).
    admin_login(client, admin)
    for path in admin_paths:
        assert client.get(path).status_code == 200, path
    assert client.get("/api/progress").status_code == 403
    assert client.get("/api/auth/session").json["data"]["user"]["is_admin"] is True

    # A disabled account loses access at once, even with a valid session cookie.
    client.post("/api/auth/logout", json={})
    learner = client.post("/api/auth/login", json={"username": "matrix-learner", "password": "a-strong-test-password"}).json["data"]["user"]
    with app.app_context():
        db.session.get(User, learner["id"]).is_active = False
        db.session.commit()
    from flask import g
    g.pop("_login_user", None)  # tests share one app context, so drop the cached user a real request would not have
    assert client.get("/api/progress").status_code == 401  # a disabled account is treated as signed out
