import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Date,
    JSON,
    ForeignKey,
    Text,
    Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def utc_now():
    return datetime.now(timezone.utc)


class Site(Base):
    __tablename__ = "sites"

    site_id = Column(String(50), primary_key=True)
    pseudonym = Column(String(100), nullable=False)
    sector = Column(String(100), nullable=False, default="Outdoor Construction")
    region = Column(String(100), nullable=False, default="Abu Dhabi")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timezone = Column(String(50), nullable=False, default="Asia/Dubai")
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    environment_records = relationship("EnvironmentRecord", back_populates="site", cascade="all, delete-orphan")
    workplace_records = relationship("WorkplaceDaily", back_populates="site", cascade="all, delete-orphan")
    risk_evaluations = relationship("RiskEvaluation", back_populates="site", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="site", cascade="all, delete-orphan")


class EnvironmentRecord(Base):
    __tablename__ = "environment_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String(50), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False, index=True)
    valid_at = Column(DateTime(timezone=True), nullable=False, index=True)
    issued_at = Column(DateTime(timezone=True), nullable=False)
    received_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    temperature_c = Column(Float, nullable=True)
    humidity_pct = Column(Float, nullable=True)
    pm25 = Column(Float, nullable=True)
    heat_index_c = Column(Float, nullable=True)
    source = Column(String(50), nullable=False, default="Open-Meteo")
    is_forecast = Column(Boolean, default=False, nullable=False)

    site = relationship("Site", back_populates="environment_records")

    __table_args__ = (
        Index("ix_env_site_valid", "site_id", "valid_at"),
    )


class WorkplaceDaily(Base):
    __tablename__ = "workplace_daily"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String(50), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False, index=True)
    shift_date = Column(Date, nullable=False, index=True)
    workers_on_shift = Column(Integer, nullable=False)
    worker_hours = Column(Float, nullable=False)
    heat_incidents = Column(Integer, nullable=False, default=0)
    near_misses = Column(Integer, nullable=False, default=0)
    sickness_absence_count = Column(Integer, nullable=False, default=0)
    received_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    synthetic_flag = Column(Boolean, default=True, nullable=False)

    site = relationship("Site", back_populates="workplace_records")

    __table_args__ = (
        Index("ix_workplace_site_shift", "site_id", "shift_date", unique=True),
    )


class RiskEvaluation(Base):
    __tablename__ = "risk_evaluations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    site_id = Column(String(50), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False, index=True)
    evaluated_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    heat_signal = Column(Float, nullable=False)
    pm25_signal = Column(Float, nullable=False)
    workplace_signal = Column(Float, nullable=False)
    score = Column(Float, nullable=False)
    ml_score = Column(Float, nullable=True)
    model_version = Column(String(50), nullable=True)
    tier = Column(String(20), nullable=False)  # Normal, Watch, Advisory, Action, Degraded
    quality_flags = Column(JSON, default=dict)  # missing feeds, freshness status, tier cap reasons
    config_version = Column(String(20), default="1.0.0")

    site = relationship("Site", back_populates="risk_evaluations")


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String(50), primary_key=True, default=lambda: f"ALT-{uuid.uuid4().hex[:8].upper()}")
    site_id = Column(String(50), ForeignKey("sites.site_id", ondelete="CASCADE"), nullable=False, index=True)
    tier = Column(String(20), nullable=False)  # Watch, Advisory, Action
    issued_at = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    evidence_json = Column(JSON, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(50), nullable=True)
    action_code = Column(String(50), nullable=True)
    action_time = Column(DateTime(timezone=True), nullable=True)
    feedback = Column(Text, nullable=True)

    site = relationship("Site", back_populates="alerts")


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(50), primary_key=True, default=lambda: f"USR-{uuid.uuid4().hex[:6].upper()}")
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # hse_officer, public_health_viewer, data_steward
    permitted_site_id = Column(String(50), nullable=True)  # Nullable: null means all sites (for public health / admin)
    created_at = Column(DateTime(timezone=True), default=utc_now)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(50), nullable=False)
    role = Column(String(50), nullable=False)
    action = Column(String(100), nullable=False)  # acknowledge_alert, execute_action, upload_csv, etc.
    object_id = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)


class MLRun(Base):
    __tablename__ = "ml_runs"

    run_id = Column(String(50), primary_key=True, default=lambda: f"RUN-{uuid.uuid4().hex[:8].upper()}")
    model_version = Column(String(50), nullable=False)
    feature_cutoff_at = Column(DateTime(timezone=True), nullable=False)
    label_window = Column(String(50), default="next_24h")
    simulated_label = Column(Integer, nullable=True)
    predicted_score = Column(Float, nullable=True)
    split = Column(String(50), nullable=False)  # train, test, held_out, chronological_held_out
    evaluation_json = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)
