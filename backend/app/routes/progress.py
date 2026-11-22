from flask import Blueprint, jsonify
from flask_login import current_user
from sqlalchemy import select

from ..extensions import db
from ..models import ActivityVisit, LearningActivity, Module, Platform, UserActivityProgress, now_utc
from ..security import authenticated_required, error, json_object
from ..services.progress import module_status, task_status

progress_bp = Blueprint("progress", __name__)


@progress_bp.post("/progress/visits")
@authenticated_required
def record_visit():
    data = json_object()
    activity_id = data.get("activity_id") if data else None
    activity = db.session.get(LearningActivity, activity_id) if isinstance(activity_id, str) else None
    if not activity or not activity.is_active:
        return error("activity_not_found", "Learning activity not found", 404)
    now = now_utc()
    db.session.add(ActivityVisit(user_id=current_user.id, activity_id=activity.id, visited_at=now))
    progress = db.session.execute(select(UserActivityProgress).where(
        UserActivityProgress.user_id == current_user.id,
        UserActivityProgress.activity_id == activity.id,
    )).scalar_one_or_none()
    if not progress:
        progress = UserActivityProgress(user_id=current_user.id, activity_id=activity.id,
                                        attempt_count=0, time_spent_seconds=0)
        db.session.add(progress)
    progress.last_heartbeat_at = now
    db.session.commit()
    return jsonify(data={"visited": True}), 201


@progress_bp.post("/progress/activities/<path:activity_id>/heartbeat")
@authenticated_required
def activity_heartbeat(activity_id):
    activity = db.session.get(LearningActivity, activity_id)
    if not activity or not activity.is_active:
        return error("activity_not_found", "Learning activity not found", 404)
    progress = db.session.execute(select(UserActivityProgress).where(
        UserActivityProgress.user_id == current_user.id,
        UserActivityProgress.activity_id == activity.id,
    )).scalar_one_or_none()
    if not progress or not progress.last_heartbeat_at:
        return error("activity_not_opened", "Open this activity before reporting reading time", 409)
    now = now_utc()
    elapsed = int((now - progress.last_heartbeat_at).total_seconds())
    if elapsed >= 5:
        progress.time_spent_seconds = min(86400, progress.time_spent_seconds + min(elapsed, 60))
        progress.last_heartbeat_at = now
        db.session.commit()
    return jsonify(data={"time_spent_seconds": progress.time_spent_seconds})


@progress_bp.post("/progress/activities/<path:activity_id>/complete")
@authenticated_required
def complete_activity(activity_id):
    activity = db.session.get(LearningActivity, activity_id)
    if not activity or not activity.is_active:
        return error("activity_not_found", "Learning activity not found", 404)
    if activity.activity_type in {"quiz", "challenge", "exercise"}:
        return error("verified_attempt_required", "Use the activity attempt endpoint to validate this activity", 409)
    visited = db.session.execute(select(ActivityVisit.id).where(
        ActivityVisit.user_id == current_user.id, ActivityVisit.activity_id == activity.id
    ).limit(1)).first()
    if not visited:
        return error("activity_not_opened", "Open this activity before completing it", 409)
    progress = db.session.execute(select(UserActivityProgress).where(
        UserActivityProgress.user_id == current_user.id,
        UserActivityProgress.activity_id == activity.id,
    )).scalar_one_or_none()
    if not progress:
        return error("activity_not_opened", "Open this activity before completing it", 409)
    progress.last_attempt_at = now_utc()
    if progress.time_spent_seconds < activity.min_read_seconds:
        return error("minimum_time_not_met", "Spend more time with this lesson before completing it", 409)
    progress.attempt_count += 1
    progress.completed_at = progress.completed_at or now_utc()
    db.session.commit()
    status = module_status(current_user.id, activity.module)
    return jsonify(data={"completed": True, "module": status}), 200


@progress_bp.post("/progress/activities/<path:activity_id>/attempts")
@authenticated_required
def submit_attempt(activity_id):
    activity = db.session.get(LearningActivity, activity_id)
    if not activity or not activity.is_active:
        return error("activity_not_found", "Learning activity not found", 404)
    if activity.activity_type not in {"quiz", "challenge", "exercise"}:
        return error("invalid_activity_type", "This activity does not accept answer attempts", 409)
    data = json_object()
    if not data:
        return error("invalid_request", "Send a JSON object", 400)
    score = None
    passed = False
    if activity.answer_digest:
        import hashlib
        import hmac
        answer = data.get("answer")
        if not isinstance(answer, str):
            return error("invalid_answer", "Submit an answer", 422)
        candidate = hashlib.sha256(answer.strip().encode("utf-8")).hexdigest()
        passed = hmac.compare_digest(candidate, activity.answer_digest)
        score = 100 if passed else 0
    progress = db.session.execute(select(UserActivityProgress).where(
        UserActivityProgress.user_id == current_user.id,
        UserActivityProgress.activity_id == activity.id,
    )).scalar_one_or_none()
    if not progress:
        progress = UserActivityProgress(user_id=current_user.id, activity_id=activity.id,
                                        attempt_count=0, time_spent_seconds=0)
        db.session.add(progress)
    progress.attempt_count += 1
    progress.last_attempt_at = now_utc()
    if score is not None:
        progress.score = max(progress.score or 0, score)
    if passed and (activity.pass_score is None or score >= activity.pass_score):
        progress.completed_at = progress.completed_at or now_utc()
    db.session.commit()
    return jsonify(data={"passed": passed, "score": score, "attempts": progress.attempt_count,
                         "completed": bool(progress.completed_at)}), 200


@progress_bp.get("/progress")
@authenticated_required
def dashboard_progress():
    platforms = db.session.execute(select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.sort_order)).scalars()
    result = []
    total_required = total_complete = 0
    for platform in platforms:
        modules = []
        for module in platform.modules:
            if not module.is_active:
                continue
            status = module_status(current_user.id, module)
            total_required += status["required_count"]
            total_complete += status["completed_count"]
            modules.append({"id": module.id, "title": module.title, **status})
        count = sum(module["required_count"] for module in modules)
        done = sum(module["completed_count"] for module in modules)
        result.append({"id": platform.id, "name": platform.name, "modules": modules,
                       "required_activities": count, "completed_activities": done,
                       "completion_percent": round(done * 100 / count) if count else 0})
    latest = db.session.execute(select(ActivityVisit).where(
        ActivityVisit.user_id == current_user.id
    ).order_by(ActivityVisit.visited_at.desc()).limit(1)).scalar_one_or_none()
    last_activity = None
    if latest:
        activity = latest.activity
        last_activity = {"id": activity.id, "title": activity.title,
                         "type": activity.activity_type,
                         "platform_id": activity.module.platform_id,
                         "module_id": activity.module_id,
                         "visited_at": latest.visited_at.isoformat()}
    return jsonify(data={"overall": {"required_activities": total_required,
                                     "completed_activities": total_complete,
                                     "completion_percent": round(total_complete * 100 / total_required) if total_required else 0},
                         "platforms": result, "last_activity": last_activity})

