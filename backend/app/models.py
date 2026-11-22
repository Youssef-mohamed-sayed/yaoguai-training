from datetime import datetime, timezone
from uuid import uuid4

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Index, UniqueConstraint, func

from .extensions import db


def now_utc():
    return datetime.now(timezone.utc)


group_members = db.Table(
    "group_members",
    db.Column("group_id", db.String(36), db.ForeignKey("member_groups.id", ondelete="CASCADE"), primary_key=True),
    db.Column("user_id", db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("joined_at", db.DateTime(timezone=True), nullable=False, server_default=func.now()),
)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(32), nullable=False, unique=True, index=True)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False, server_default="false")
    must_change_password = db.Column(db.Boolean, nullable=False, default=False, server_default="false")
    level_id = db.Column(db.String(36), db.ForeignKey("member_levels.id", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    last_seen_at = db.Column(db.DateTime(timezone=True))
    level = db.relationship("MemberLevel", back_populates="users")
    groups = db.relationship("MemberGroup", secondary="group_members", lazy="selectin", back_populates="members")

    def get_id(self):
        return self.id


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_digest = db.Column(db.String(64), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    used_at = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    user = db.relationship("User")


class MemberLevel(db.Model):
    __tablename__ = "member_levels"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(80), nullable=False, unique=True)
    rank = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.String(500), nullable=False, default="")
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    users = db.relationship("User", back_populates="level")


class Platform(db.Model):
    __tablename__ = "platforms"
    id = db.Column(db.String(40), primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    modules = db.relationship("Module", back_populates="platform", cascade="all, delete-orphan", order_by="Module.sort_order")


class Module(db.Model):
    __tablename__ = "modules"
    id = db.Column(db.String(160), primary_key=True)
    platform_id = db.Column(db.String(40), db.ForeignKey("platforms.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    platform = db.relationship("Platform", back_populates="modules")
    activities = db.relationship("LearningActivity", back_populates="module", cascade="all, delete-orphan", order_by="LearningActivity.sort_order")


class LearningActivity(db.Model):
    __tablename__ = "learning_activities"
    __table_args__ = (
        UniqueConstraint("module_id", "stable_key", name="uq_activity_module_stable_key"),
        CheckConstraint("activity_type IN ('lesson','challenge','exercise','quiz','task')", name="activity_type"),
        CheckConstraint("pass_score IS NULL OR (pass_score >= 0 AND pass_score <= 100)", name="pass_score_range"),
        Index("ix_activities_module_required", "module_id", "is_required"),
    )
    id = db.Column(db.String(240), primary_key=True)
    module_id = db.Column(db.String(160), db.ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    stable_key = db.Column(db.String(160), nullable=False)
    title = db.Column(db.String(240), nullable=False)
    activity_type = db.Column(db.String(24), nullable=False)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_required = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    min_read_seconds = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    pass_score = db.Column(db.Integer)
    answer_digest = db.Column(db.String(64))
    module = db.relationship("Module", back_populates="activities")


class UserActivityProgress(db.Model):
    __tablename__ = "user_activity_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "activity_id", name="uq_progress_user_activity"),
        CheckConstraint("attempt_count >= 0", name="attempt_count_nonnegative"),
        CheckConstraint("score IS NULL OR (score >= 0 AND score <= 100)", name="score_range"),
    )
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = db.Column(db.String(240), db.ForeignKey("learning_activities.id", ondelete="CASCADE"), nullable=False, index=True)
    attempt_count = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    completed_at = db.Column(db.DateTime(timezone=True))
    score = db.Column(db.Integer)
    time_spent_seconds = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    last_attempt_at = db.Column(db.DateTime(timezone=True))
    last_heartbeat_at = db.Column(db.DateTime(timezone=True))
    activity = db.relationship("LearningActivity")


class ActivityVisit(db.Model):
    __tablename__ = "activity_visits"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = db.Column(db.String(240), db.ForeignKey("learning_activities.id", ondelete="CASCADE"), nullable=False, index=True)
    visited_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    activity = db.relationship("LearningActivity")


class MemberGroup(db.Model):
    __tablename__ = "member_groups"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    name = db.Column(db.String(120), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=False, default="")
    platform_id = db.Column(db.String(40), db.ForeignKey("platforms.id", ondelete="SET NULL"))
    level_id = db.Column(db.String(36), db.ForeignKey("member_levels.id", ondelete="SET NULL"))
    created_by = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    members = db.relationship("User", secondary=group_members, lazy="selectin", back_populates="groups")


class LearningTask(db.Model):
    __tablename__ = "learning_tasks"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False, default="")
    instructions = db.Column(db.Text, nullable=False, default="")
    platform_id = db.Column(db.String(40), db.ForeignKey("platforms.id", ondelete="SET NULL"))
    module_id = db.Column(db.String(160), db.ForeignKey("modules.id", ondelete="SET NULL"))
    difficulty = db.Column(db.String(24), nullable=False, default="intermediate")
    starts_at = db.Column(db.DateTime(timezone=True))
    deadline_at = db.Column(db.DateTime(timezone=True))
    created_by = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    is_active = db.Column(db.Boolean, nullable=False, default=True, server_default="true")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    requirements = db.relationship("TaskRequirement", cascade="all, delete-orphan", back_populates="task")
    assignments = db.relationship("TaskAssignment", cascade="all, delete-orphan", back_populates="task")


class TaskRequirement(db.Model):
    __tablename__ = "task_requirements"
    __table_args__ = (UniqueConstraint("task_id", "activity_id", name="uq_task_requirement"),)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("learning_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = db.Column(db.String(240), db.ForeignKey("learning_activities.id", ondelete="CASCADE"), nullable=False)
    requires_review = db.Column(db.Boolean, nullable=False, default=False, server_default="false")
    task = db.relationship("LearningTask", back_populates="requirements")
    activity = db.relationship("LearningActivity")


class TaskAssignment(db.Model):
    __tablename__ = "task_assignments"
    __table_args__ = (
        CheckConstraint("(user_id IS NOT NULL AND group_id IS NULL) OR (user_id IS NULL AND group_id IS NOT NULL)", name="one_assignment_target"),
        Index("ix_task_assignments_user", "user_id", "task_id"),
        Index("ix_task_assignments_group", "group_id", "task_id"),
    )
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("learning_tasks.id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"))
    group_id = db.Column(db.String(36), db.ForeignKey("member_groups.id", ondelete="CASCADE"))
    assigned_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    task = db.relationship("LearningTask", back_populates="assignments")
    user = db.relationship("User")
    group = db.relationship("MemberGroup")


class TaskSubmission(db.Model):
    __tablename__ = "task_submissions"
    __table_args__ = (CheckConstraint("status IN ('submitted','under_review','approved','rejected')", name="submission_status"),)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    task_id = db.Column(db.String(36), db.ForeignKey("learning_tasks.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(24), nullable=False, default="submitted")
    feedback = db.Column(db.Text, nullable=False, default="")
    reviewer_id = db.Column(db.String(36), db.ForeignKey("users.id", ondelete="SET NULL"))
    submitted_at = db.Column(db.DateTime(timezone=True), nullable=False, default=now_utc)
    reviewed_at = db.Column(db.DateTime(timezone=True))
    task = db.relationship("LearningTask")
    user = db.relationship("User", foreign_keys=[user_id])
    reviewer = db.relationship("User", foreign_keys=[reviewer_id])


class LoginThrottle(db.Model):
    __tablename__ = "login_throttles"
    key_hash = db.Column(db.String(64), primary_key=True)
    window_started_at = db.Column(db.DateTime(timezone=True), nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)

