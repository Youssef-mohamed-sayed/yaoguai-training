import hashlib
from datetime import datetime, timedelta, timezone
import pytest

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
    assert client.post("/api/auth/login", json={
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


def test_admin_can_manage_levels_groups_assignments_and_submission_review(app, client):
    activity_id = make_lesson(app)
    admin = register(client, "training-admin")
    with app.app_context():
        user = db.session.get(User, admin["id"])
        user.is_admin = True
        db.session.commit()

    level_response = client.post("/api/admin/levels", json={"name": "Advanced", "rank": 2})
    assert level_response.status_code == 201
    level_id = level_response.json["data"]["id"]
    assert client.patch(f"/api/admin/members/{admin['id']}", json={"level_id": level_id}).status_code == 200

    group_response = client.post("/api/admin/groups", json={"name": "Blue Team", "level_id": level_id})
    assert group_response.status_code == 201
    group_id = group_response.json["data"]["id"]
    assert client.put(f"/api/admin/groups/{group_id}/members/{admin['id']}", json={}).status_code == 200

    task_response = client.post("/api/admin/tasks", json={
        "title": "Review the lesson", "module_id": "programming/basics",
        "platform_id": "programming", "group_ids": [group_id],
        "requirements": [{"activity_id": activity_id, "requires_review": True}],
    })
    assert task_response.status_code == 201
    task_id = task_response.json["data"]["id"]
    assert client.post("/api/progress/visits", json={"activity_id": activity_id}).status_code == 201
    assert client.post(f"/api/progress/activities/{activity_id}/complete", json={}).status_code == 200

    submission_response = client.post(f"/api/assignments/{task_id}/submissions", json={"content": "Completed"})
    assert submission_response.status_code == 201
    submission_id = submission_response.json["data"]["id"]
    review = client.patch(f"/api/admin/submissions/{submission_id}",
                          json={"status": "approved", "feedback": "Reviewed"})
    assert review.status_code == 200
    assignments = client.get("/api/assignments").json["data"]
    assert next(task for task in assignments if task["id"] == task_id)["status"] == "completed"

    with app.app_context():
        assert db.session.get(MemberLevel, level_id).name == "Advanced"
        assert db.session.get(MemberGroup, group_id).members[0].id == admin["id"]
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
    client.post("/api/auth/login", json={"username": admin["username"], "password": "a-strong-test-password"})
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
    client.post("/api/auth/login", json={"username": admin["username"], "password": "a-strong-test-password"})
    detail = client.get(f"/api/admin/members/{learner['id']}")
    assert detail.status_code == 200
    record = detail.json["data"]
    module = next(row for row in record["progress"] if row["module"] == "programming/basics")
    assert module["completed_count"] == module["required_count"] == 1
    assert record["progress"]
    assigned = next(row for row in record["tasks"] if row["id"] == task["id"])
    assert assigned["deadline_at"] is not None
    assert assigned["completed_count"] == 1
    admin_tasks = client.get("/api/admin/tasks").json["data"]
    assert any(target["name"] == "Dashboard cohort" for target in next(row for row in admin_tasks if row["id"] == task["id"])["targets"])
