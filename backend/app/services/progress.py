from sqlalchemy import select

from ..extensions import db
from ..models import LearningActivity, Module, TaskRequirement, TaskSubmission, UserActivityProgress


def module_status(user_id, module):
    return module_statuses(user_id, [module])[module.id]


def module_statuses(user_id, modules):
    """Build progress for a module set with one progress query, not one per module."""
    required_by_module = {
        module.id: [activity for activity in module.activities if activity.is_required and activity.is_active]
        for module in modules
    }
    activity_ids = [activity.id for activities in required_by_module.values() for activity in activities]
    if not activity_ids:
        return {module_id: {"completed": False, "completed_count": 0,
                            "required_count": 0, "activities": []}
                for module_id in required_by_module}
    progress = {
        row.activity_id: row
        for row in db.session.execute(
            select(UserActivityProgress).where(
                UserActivityProgress.user_id == user_id,
                UserActivityProgress.activity_id.in_(activity_ids),
            )
        ).scalars()
    }
    result = {}
    for module_id, activities in required_by_module.items():
        items = []
        for activity in activities:
            record = progress.get(activity.id)
            is_done = bool(record and record.completed_at)
            items.append({"id": activity.id, "title": activity.title, "type": activity.activity_type,
                          "completed": is_done, "started": bool(record and (record.time_spent_seconds or record.attempt_count or record.last_heartbeat_at)),
                          "time_spent_seconds": record.time_spent_seconds if record else 0,
                          "score": record.score if record else None,
                          "attempts": record.attempt_count if record else 0})
        completed_count = sum(item["completed"] for item in items)
        result[module_id] = {"completed": completed_count > 0 and completed_count == len(activities),
                             "completed_count": completed_count,
                             "required_count": len(activities), "activities": items}
    return result


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

