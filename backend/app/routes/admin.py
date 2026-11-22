from datetime import datetime, timezone

from flask import Blueprint, jsonify
from flask_login import current_user
from sqlalchemy import func, select

from ..extensions import db
from ..models import (LearningActivity, LearningTask, MemberGroup, MemberLevel, Module,
                      Platform, TaskAssignment, TaskRequirement, TaskSubmission, User,
                      UserActivityProgress, now_utc)
from ..security import admin_required, error, json_object
from ..services.progress import module_status, task_status

admin_bp = Blueprint("admin", __name__)


def parse_datetime(value, field):
    if value in (None, ""):
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO-8601 datetime")
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO-8601 datetime") from exc
    if result.tzinfo is None:
        raise ValueError(f"{field} must include a timezone")
    return result.astimezone(timezone.utc)


def member_json(user):
    return {"id": user.id, "username": user.username, "email": user.email,
            "is_admin": user.is_admin, "is_active": user.is_active,
            "created_at": user.created_at.isoformat(), "last_seen_at": user.last_seen_at.isoformat() if user.last_seen_at else None,
            "level": {"id": user.level.id, "name": user.level.name} if user.level else None,
            "groups": [{"id": group.id, "name": group.name} for group in user.groups]}


@admin_bp.get("/overview")
@admin_required
def overview():
    total_members = db.session.scalar(select(func.count()).select_from(User).where(User.is_admin.is_(False))) or 0
    cutoff = now_utc().replace(hour=0, minute=0, second=0, microsecond=0)
    active = db.session.scalar(select(func.count()).select_from(User).where(User.last_seen_at >= cutoff)) or 0
    groups = db.session.scalar(select(func.count()).select_from(MemberGroup).where(MemberGroup.is_active.is_(True))) or 0
    completed_modules = 0
    platform_stats = []
    for platform in db.session.execute(select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.sort_order)).scalars():
        module_count = 0
        completion_count = 0
        for module in platform.modules:
            if not module.is_active:
                continue
            module_count += 1
            # Aggregate calculated from actual required activities, not a client flag.
            users = db.session.execute(select(User.id).where(User.is_admin.is_(False), User.is_active.is_(True))).scalars()
            completion_count += sum(module_status(uid, module)["completed"] for uid in users)
        completed_modules += completion_count
        platform_stats.append({"id": platform.id, "name": platform.name,
                               "modules": module_count, "member_module_completions": completion_count})
    tasks = db.session.execute(select(LearningTask).where(LearningTask.is_active.is_(True))).scalars().all()
    overdue = sum(bool(task.deadline_at and task.deadline_at < now_utc()) for task in tasks)
    submissions = db.session.scalar(select(func.count()).select_from(TaskSubmission).where(TaskSubmission.status == "submitted")) or 0
    return jsonify(data={"members": total_members, "active_today": active, "groups": groups,
                         "completed_modules": completed_modules, "outstanding_tasks": submissions,
                         "overdue_tasks": overdue, "platforms": platform_stats})


@admin_bp.get("/members")
@admin_required
def members():
    query = select(User).where(User.is_admin.is_(False)).order_by(User.created_at.desc()).limit(200)
    search = (request_arg("q") or "").strip()
    level_id = request_arg("level_id")
    if search:
        needle = f"%{search.lower()}%"
        query = query.where((func.lower(User.username).like(needle)) | (func.lower(User.email).like(needle)))
    if level_id:
        query = query.where(User.level_id == level_id)
    rows = db.session.execute(query).scalars()
    return jsonify(data=[member_json(user) for user in rows])


def request_arg(name):
    from flask import request
    return request.args.get(name)


@admin_bp.get("/members/<user_id>")
@admin_required
def member_detail(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return error("member_not_found", "Member not found", 404)
    progress = []
    platforms = db.session.execute(select(Platform).order_by(Platform.sort_order)).scalars()
    for platform in platforms:
        for module in platform.modules:
            progress.append({"platform": platform.id, "module": module.id, "title": module.title,
                             **module_status(user.id, module)})
    group_ids = {group.id for group in user.groups}
    tasks = [task for task in db.session.execute(select(LearningTask)).scalars()
             if any(assignment.user_id == user.id or assignment.group_id in group_ids
                    for assignment in task.assignments)]
    now = now_utc()
    task_rows = []
    for task in tasks:
        completion = task_status(user.id, task)
        if completion["completed"]:
            status = "completed"
        elif task.deadline_at and task.deadline_at < now:
            status = "overdue"
        elif completion["completed_count"]:
            status = "in_progress"
        else:
            status = "pending"
        task_rows.append({"id": task.id, "title": task.title, "description": task.description,
                          "instructions": task.instructions,
                          "deadline_at": task.deadline_at.isoformat() if task.deadline_at else None,
                          "status": status, **completion})
    submissions = db.session.execute(select(TaskSubmission).where(TaskSubmission.user_id == user.id)
                                     .order_by(TaskSubmission.submitted_at.desc())).scalars()
    return jsonify(data={"member": member_json(user), "progress": progress,
                         "tasks": task_rows,
                         "submissions": [{"id": item.id, "task_id": item.task_id, "status": item.status,
                                          "content": item.content, "feedback": item.feedback,
                                          "submitted_at": item.submitted_at.isoformat()} for item in submissions]})


@admin_bp.patch("/members/<user_id>")
@admin_required
def update_member(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return error("member_not_found", "Member not found", 404)
    data = json_object()
    if not data:
        return error("invalid_request", "Send a JSON object", 400)
    if "level_id" in data:
        level = db.session.get(MemberLevel, data["level_id"]) if data["level_id"] else None
        if data["level_id"] and not level:
            return error("level_not_found", "Member level not found", 404)
        user.level = level
    if "is_active" in data:
        if not isinstance(data["is_active"], bool) or user.id == current_user.id and not data["is_active"]:
            return error("invalid_status", "This account status change is not allowed", 422)
        user.is_active = data["is_active"]
    db.session.commit()
    return jsonify(data=member_json(user))


@admin_bp.get("/levels")
@admin_required
def levels():
    rows = db.session.execute(select(MemberLevel).order_by(MemberLevel.rank, MemberLevel.name)).scalars()
    return jsonify(data=[{"id": row.id, "name": row.name, "rank": row.rank,
                          "description": row.description, "is_active": row.is_active} for row in rows])


@admin_bp.post("/levels")
@admin_required
def create_level():
    data = json_object()
    if not data or not isinstance(data.get("name"), str) or not data["name"].strip():
        return error("invalid_level", "A level name is required", 422)
    row = MemberLevel(name=data["name"].strip(), rank=data.get("rank", 0), description=data.get("description", ""))
    db.session.add(row)
    db.session.commit()
    return jsonify(data={"id": row.id, "name": row.name, "rank": row.rank}), 201


@admin_bp.get("/groups")
@admin_required
def groups():
    rows = db.session.execute(select(MemberGroup).order_by(MemberGroup.created_at.desc())).scalars()
    return jsonify(data=[{"id": row.id, "name": row.name, "description": row.description,
                          "platform_id": row.platform_id, "level_id": row.level_id,
                          "member_count": len(row.members), "is_active": row.is_active,
                          "members": [{"id": user.id, "username": user.username, "email": user.email}
                                      for user in row.members],
                          "created_at": row.created_at.isoformat()} for row in rows])


@admin_bp.post("/groups")
@admin_required
def create_group():
    data = json_object()
    if not data or not isinstance(data.get("name"), str) or not data["name"].strip():
        return error("invalid_group", "A group name is required", 422)
    if data.get("platform_id") and not db.session.get(Platform, data["platform_id"]):
        return error("platform_not_found", "Platform not found", 404)
    if data.get("level_id") and not db.session.get(MemberLevel, data["level_id"]):
        return error("level_not_found", "Member level not found", 404)
    row = MemberGroup(name=data["name"].strip(), description=str(data.get("description", ""))[:500],
                      platform_id=data.get("platform_id"), level_id=data.get("level_id"), created_by=current_user.id)
    db.session.add(row)
    db.session.commit()
    return jsonify(data={"id": row.id, "name": row.name}), 201


@admin_bp.put("/groups/<group_id>/members/<user_id>")
@admin_required
def add_group_member(group_id, user_id):
    group, user = db.session.get(MemberGroup, group_id), db.session.get(User, user_id)
    if not group or not user:
        return error("not_found", "Group or member not found", 404)
    if user not in group.members:
        group.members.append(user)
        db.session.commit()
    return jsonify(data={"group_id": group.id, "member_id": user.id, "added": True})


@admin_bp.delete("/groups/<group_id>/members/<user_id>")
@admin_required
def remove_group_member(group_id, user_id):
    group, user = db.session.get(MemberGroup, group_id), db.session.get(User, user_id)
    if not group or not user:
        return error("not_found", "Group or member not found", 404)
    if user in group.members:
        group.members.remove(user)
        db.session.commit()
    return jsonify(data={"group_id": group.id, "member_id": user.id, "removed": True})


@admin_bp.post("/tasks")
@admin_required
def create_task():
    data = json_object()
    if not data or not isinstance(data.get("title"), str) or not data["title"].strip():
        return error("invalid_task", "A task title is required", 422)
    users = data.get("user_ids", [])
    group_ids = data.get("group_ids", [])
    requirements = data.get("requirements", [])
    if not isinstance(users, list) or not isinstance(group_ids, list) or not isinstance(requirements, list):
        return error("invalid_task", "Recipients and requirements must be lists", 422)
    if not users and not group_ids:
        return error("missing_recipients", "Assign the task to at least one member or group", 422)
    if len(users) + len(group_ids) > 500:
        return error("too_many_recipients", "A task can have at most 500 assignment targets", 422)
    try:
        starts_at = parse_datetime(data.get("starts_at"), "starts_at")
        deadline_at = parse_datetime(data.get("deadline_at"), "deadline_at")
    except ValueError as exc:
        return error("invalid_datetime", str(exc), 422)
    if starts_at and deadline_at and deadline_at <= starts_at:
        return error("invalid_deadline", "Deadline must be after the start date", 422)
    if data.get("platform_id") and not db.session.get(Platform, data["platform_id"]):
        return error("platform_not_found", "Platform not found", 404)
    if data.get("module_id") and not db.session.get(Module, data["module_id"]):
        return error("module_not_found", "Module not found", 404)
    task_module = db.session.get(Module, data["module_id"]) if data.get("module_id") else None
    if task_module and data.get("platform_id") and task_module.platform_id != data["platform_id"]:
        return error("module_platform_mismatch", "The module does not belong to the selected platform", 422)
    users_found = db.session.execute(select(User).where(User.id.in_(users))).scalars().all() if users else []
    groups_found = db.session.execute(select(MemberGroup).where(MemberGroup.id.in_(group_ids))).scalars().all() if group_ids else []
    if len(users_found) != len(set(users)) or len(groups_found) != len(set(group_ids)):
        return error("recipient_not_found", "An assigned member or group does not exist", 404)
    activity_ids = [row.get("activity_id") for row in requirements if isinstance(row, dict)]
    if len(activity_ids) != len(requirements) or len(set(activity_ids)) != len(activity_ids):
        return error("invalid_requirements", "Each requirement needs a unique activity_id", 422)
    activities = db.session.execute(select(LearningActivity).where(LearningActivity.id.in_(activity_ids))).scalars().all() if activity_ids else []
    if len(activities) != len(activity_ids):
        return error("activity_not_found", "A required learning activity does not exist", 404)
    if task_module and any(activity.module_id != task_module.id for activity in activities):
        return error("activity_module_mismatch", "Every required activity must belong to the selected module", 422)
    if any(not group.is_active for group in groups_found):
        return error("inactive_group", "Tasks cannot be assigned to inactive groups", 422)
    if any(not user.is_active for user in users_found):
        return error("inactive_member", "Tasks cannot be assigned to inactive accounts", 422)
    task = LearningTask(title=data["title"].strip(), description=str(data.get("description", "")),
                        instructions=str(data.get("instructions", "")), platform_id=data.get("platform_id"),
                        module_id=data.get("module_id"), difficulty=str(data.get("difficulty", "intermediate"))[:24],
                        starts_at=starts_at, deadline_at=deadline_at, created_by=current_user.id)
    db.session.add(task)
    for user in users_found:
        task.assignments.append(TaskAssignment(user=user))
    for group in groups_found:
        task.assignments.append(TaskAssignment(group=group))
    for req in requirements:
        task.requirements.append(TaskRequirement(activity_id=req["activity_id"], requires_review=bool(req.get("requires_review", False))))
    db.session.commit()
    return jsonify(data={"id": task.id, "title": task.title,
                         "assignment_count": len(task.assignments),
                         "requirement_count": len(task.requirements)}), 201


@admin_bp.get("/tasks")
@admin_required
def admin_tasks():
    rows = db.session.execute(select(LearningTask).order_by(LearningTask.created_at.desc()).limit(200)).scalars()
    return jsonify(data=[{"id": task.id, "title": task.title,
                          "deadline_at": task.deadline_at.isoformat() if task.deadline_at else None,
                          "assignments": len(task.assignments), "requirements": len(task.requirements),
                          "targets": [{"type": "member", "id": assignment.user.id,
                                       "name": assignment.user.username}
                                      if assignment.user else
                                      {"type": "group", "id": assignment.group.id,
                                       "name": assignment.group.name}
                                      for assignment in task.assignments],
                          "active": task.is_active} for task in rows])


@admin_bp.patch("/tasks/<task_id>")
@admin_required
def update_task(task_id):
    task = db.session.get(LearningTask, task_id)
    if not task:
        return error("task_not_found", "Task not found", 404)
    data = json_object()
    if not data or "is_active" not in data or not isinstance(data["is_active"], bool):
        return error("invalid_task", "Provide an is_active boolean", 422)
    task.is_active = data["is_active"]
    db.session.commit()
    return jsonify(data={"id": task.id, "is_active": task.is_active})


@admin_bp.get("/submissions")
@admin_required
def submissions():
    rows = db.session.execute(select(TaskSubmission).order_by(TaskSubmission.submitted_at.desc()).limit(300)).scalars()
    return jsonify(data=[{"id": item.id, "task_id": item.task_id, "task_title": item.task.title,
                          "user_id": item.user_id, "username": item.user.username,
                          "status": item.status, "content": item.content, "feedback": item.feedback,
                          "submitted_at": item.submitted_at.isoformat()} for item in rows])


@admin_bp.patch("/submissions/<submission_id>")
@admin_required
def review_submission(submission_id):
    submission = db.session.get(TaskSubmission, submission_id)
    if not submission:
        return error("submission_not_found", "Submission not found", 404)
    data = json_object()
    status = data.get("status") if data else None
    feedback = data.get("feedback", "") if data else ""
    if status not in {"under_review", "approved", "rejected"} or not isinstance(feedback, str) or len(feedback) > 10000:
        return error("invalid_review", "Provide a review status and feedback of at most 10000 characters", 422)
    submission.status = status
    submission.feedback = feedback
    submission.reviewer_id = current_user.id
    submission.reviewed_at = now_utc()
    db.session.commit()
    return jsonify(data={"id": submission.id, "status": submission.status,
                         "reviewer_id": submission.reviewer_id, "reviewed_at": submission.reviewed_at.isoformat()})

