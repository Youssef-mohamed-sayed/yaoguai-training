"""Course, public assets, search and answer checking."""
from flask import (Blueprint, abort, current_app, jsonify, redirect,
                   render_template, request, send_from_directory)

site = Blueprint("site", __name__)


def get_course():
    return current_app.extensions["course"]


@site.get("/")
@site.get("/network")
def dashboard():
    course = get_course()
    return render_template("dashboard.html", title="Network Essentials",
                           first=next(iter(course.sequence), None))


@site.get("/network/course")
@site.get("/network/<module>")
@site.get("/network/<module>/<lesson>")
def reader(module=None, lesson=None):
    course = get_course()
    url = "/network/course" if module is None else f"/network/{module}"
    if lesson is not None:
        url += f"/{lesson}"
    page = course.pages.get(url)
    if not page or not (course.root / page.source).is_file():
        abort(404)
    previous, following = course.navigate(page)
    return render_template("reader.html", title=page.title, page=page,
                           module=course.modules.get(page.module),
                           previous=previous, following=following)


@site.get("/network/challenges")
def challenges():
    module = get_course().modules.get("final-challenges")
    if not module:
        abort(404)
    return redirect(module.index.url)


@site.get("/network/search")
def search():
    query = request.args.get("q", "").strip()[:120]
    return render_template("search.html", title="Course search", query=query,
                           results=get_course().search(query))


@site.post("/network/check")
def check():
    if request.content_length is not None and request.content_length > 4096:
        return jsonify(error="Submission is too large."), 413
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Send a valid JSON submission."), 400
    url, activity_id = data.get("page"), data.get("activity")
    if not isinstance(url, str) or not isinstance(activity_id, str):
        return jsonify(error="Select a valid activity."), 400
    page = get_course().pages.get(url)
    if not page or activity_id not in page.questions:
        return jsonify(error="This activity has no automatic answer check."), 404
    try:
        fields = page.questions[activity_id].check(data.get("answers"))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    correct = all(fields)
    if correct:
        from flask_login import current_user
        if current_user.is_authenticated and page.kind != "overview":
            from app.extensions import db
            from app.models import LearningActivity, UserActivityProgress, now_utc
            suffix = page.url.removeprefix("/network/")
            stable_id = f"network/{suffix}/exercise/{activity_id}"
            activity = db.session.get(LearningActivity, stable_id)
            if activity and activity.is_active:
                progress = db.session.execute(db.select(UserActivityProgress).where(
                    UserActivityProgress.user_id == current_user.id,
                    UserActivityProgress.activity_id == activity.id,
                )).scalar_one_or_none()
                if not progress:
                    progress = UserActivityProgress(user_id=current_user.id, activity_id=activity.id,
                                                    attempt_count=0, time_spent_seconds=0)
                    db.session.add(progress)
                progress.attempt_count += 1
                progress.last_attempt_at = now_utc()
                progress.completed_at = progress.completed_at or now_utc()
                db.session.commit()
    return jsonify(correct=correct, fields=fields)


@site.get("/assets/<path:name>")
def asset(name):
    return send_from_directory(current_app.config["PUBLIC_ROOT"] / "assets", name)


@site.get("/favicon.ico")
def favicon():
    return redirect("/assets/images/favicon.ico", code=307)
