from flask import Blueprint, jsonify, request
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..extensions import db
from ..models import LearningActivity, Module, Platform

catalog_bp = Blueprint("catalog", __name__)


@catalog_bp.get("/platforms")
def platforms():
    query = (select(Platform).where(Platform.is_active.is_(True)).order_by(Platform.sort_order)
             .options(selectinload(Platform.modules).selectinload(Module.activities)))
    rows = db.session.execute(query).scalars()
    return jsonify(data=[{"id": row.id, "name": row.name, "description": row.description,
                          "modules_count": len(row.modules),
                          "activities_count": sum(len(module.activities) for module in row.modules)} for row in rows])


@catalog_bp.get("/platforms/<platform_id>/modules")
def platform_modules(platform_id):
    query = select(Module).where(
        Module.platform_id == platform_id, Module.is_active.is_(True)
    ).order_by(Module.sort_order).options(selectinload(Module.activities))
    rows = db.session.execute(query).scalars()
    return jsonify(data=[{"id": row.id, "title": row.title, "description": row.description,
                          "activity_count": sum(activity.is_required for activity in row.activities)} for row in rows])


@catalog_bp.get("/modules/<path:module_id>")
def module_detail(module_id):
    module = db.session.get(Module, module_id)
    if not module or not module.is_active:
        return jsonify(error={"code": "not_found", "message": "Module not found"}), 404
    return jsonify(data={"id": module.id, "platform": module.platform_id, "title": module.title,
                         "description": module.description,
                         "activities": [{"id": item.id, "title": item.title, "type": item.activity_type,
                                         "required": item.is_required, "order": item.sort_order}
                                        for item in module.activities if item.is_active]})


@catalog_bp.get("/health")
def health():
    from sqlalchemy import text
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        db.session.rollback()
        return jsonify(data={"status": "degraded", "database": "unavailable"}), 503
    return jsonify(data={"status": "ok", "database": "ok"})

