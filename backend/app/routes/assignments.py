from datetime import timezone

from flask import Blueprint, jsonify
from flask_login import current_user
from sqlalchemy import or_, select

from ..extensions import db
from ..models import LearningTask, MemberGroup, TaskAssignment, TaskSubmission, User, now_utc
from ..security import authenticated_required, error, json_object
from ..services.progress import task_status

assignments_bp = Blueprint("assignments", __name__)


def assigned_to(user_id):
    group_ids = select(MemberGroup.id).where(MemberGroup.members.any(User.id == user_id))
    task_ids = select(TaskAssignment.task_id).where(
        or_(TaskAssignment.user_id == user_id, TaskAssignment.group_id.in_(group_ids))
    )
    return db.session.execute(select(LearningTask).where(
        LearningTask.id.in_(task_ids), LearningTask.is_active.is_(True)
    ).order_by(LearningTask.deadline_at.asc().nullslast(), LearningTask.created_at.desc())).scalars().all()


def task_json(task, user_id):
    status = task_status(user_id, task)
    now = now_utc()
    deadline = task.deadline_at
    if deadline and deadline.tzinfo is None:
        deadline = deadline.replace(tzinfo=timezone.utc)
    submission = db.session.execute(select(TaskSubmission).where(
        TaskSubmission.task_id == task.id, TaskSubmission.user_id == user_id
    ).order_by(TaskSubmission.submitted_at.desc())).scalars().first()
    if status["completed"]:
        state = "completed"
    elif deadline and deadline < now:
        state = "overdue"
    elif submission and submission.status == "under_review":
        state = "under_review"
    elif submission and submission.status == "submitted":
        state = "submitted"
    elif status["completed_count"]:
        state = "in_progress"
    else:
        state = "pending"
    return {"id": task.id, "title": task.title, "description": task.description,
            "instructions": task.instructions, "platform": task.platform_id,
            "module_id": task.module_id, "difficulty": task.difficulty,
            "starts_at": task.starts_at.isoformat() if task.starts_at else None,
            "deadline_at": deadline.isoformat() if deadline else None,
            "status": state, "completion": status,
            "requirements": [{"activity_id": req.activity_id, "title": req.activity.title,
                              "requires_review": req.requires_review} for req in task.requirements],
            "submission": {"id": submission.id, "status": submission.status,
                           "content": submission.content, "feedback": submission.feedback,
                           "submitted_at": submission.submitted_at.isoformat()} if submission else None}


@assignments_bp.get("/assignments")
@authenticated_required
def list_assignments():
    return jsonify(data=[task_json(task, current_user.id) for task in assigned_to(current_user.id)])


@assignments_bp.get("/assignments/<task_id>")
@authenticated_required
def assignment_detail(task_id):
    task = next((task for task in assigned_to(current_user.id) if task.id == task_id), None)
    if not task:
        return error("task_not_found", "Task not found", 404)
    return jsonify(data=task_json(task, current_user.id))


@assignments_bp.post("/assignments/<task_id>/submissions")
@authenticated_required
def submit_task(task_id):
    task = next((task for task in assigned_to(current_user.id) if task.id == task_id), None)
    if not task:
        return error("task_not_found", "Task not found", 404)
    data = json_object()
    content = data.get("content") if data else None
    if not isinstance(content, str) or not content.strip() or len(content) > 50000:
        return error("invalid_submission", "Submission content must be between 1 and 50000 characters", 422)
    submission = TaskSubmission(task_id=task.id, user_id=current_user.id, content=content.strip())
    db.session.add(submission)
    db.session.commit()
    return jsonify(data={"id": submission.id, "status": submission.status,
                         "submitted_at": submission.submitted_at.isoformat()}), 201

