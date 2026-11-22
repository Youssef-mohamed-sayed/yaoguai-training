from sqlalchemy import select

from ..extensions import db
from ..models import LearningActivity, Module, TaskRequirement, TaskSubmission, UserActivityProgress


def module_status(user_id, module):
    required = [activity for activity in module.activities if activity.is_required and activity.is_active]
    if not required:
        return {"completed": False, "completed_count": 0, "required_count": 0, "activities": []}
    progress = {
        row.activity_id: row
        for row in db.session.execute(
            select(UserActivityProgress).where(
                UserActivityProgress.user_id == user_id,
                UserActivityProgress.activity_id.in_([activity.id for activity in required]),
            )
        ).scalars()
    }
    items = []
    for activity in required:
        record = progress.get(activity.id)
        is_done = bool(record and record.completed_at)
        items.append({"id": activity.id, "title": activity.title, "type": activity.activity_type,
                      "completed": is_done, "score": record.score if record else None,
                      "attempts": record.attempt_count if record else 0})
    completed_count = sum(item["completed"] for item in items)
    return {"completed": completed_count == len(required), "completed_count": completed_count,
            "required_count": len(required), "activities": items}


def task_status(user_id, task):
    requirements = task.requirements
    records = {
        row.activity_id: row
        for row in db.session.execute(
            select(UserActivityProgress).where(
                UserActivityProgress.user_id == user_id,
                UserActivityProgress.activity_id.in_([req.activity_id for req in requirements] or [""]),
            )
        ).scalars()
    }
    approved_submissions = set(db.session.execute(
        select(TaskSubmission.task_id).where(
            TaskSubmission.user_id == user_id,
            TaskSubmission.status == "approved",
        )
    ).scalars())
    done = 0
    missing = []
    for requirement in requirements:
        record = records.get(requirement.activity_id)
        complete = bool(record and record.completed_at)
        if requirement.requires_review:
            complete = complete and task.id in approved_submissions
        if complete:
            done += 1
        else:
            missing.append(requirement.activity_id)
    return {"completed": bool(requirements) and done == len(requirements),
            "completed_count": done, "required_count": len(requirements), "outstanding": missing}

