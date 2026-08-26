import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for User and Role
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Role and Permission
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)

# Association table for Tier and Feature
tier_features = Table(
    "tier_features",
    Base.metadata,
    Column("tier_id", Integer, ForeignKey("tiers.id", ondelete="CASCADE"), primary_key=True),
    Column("feature_id", Integer, ForeignKey("features.id", ondelete="CASCADE"), primary_key=True),
)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    permissions = relationship("Permission", secondary=role_permissions, backref="roles")

class Feature(Base):
    __tablename__ = "features"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    code = Column(String, unique=True, index=True, nullable=False)  # e.g., "watchlist_access"
    description = Column(String, nullable=True)

class Tier(Base):
    __tablename__ = "tiers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    price = Column(Float, default=0.0, nullable=False)
    description = Column(String, nullable=True)
    features = relationship("Feature", secondary=tier_features, backref="tiers")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    account_number = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # Legacy string role
    tier = Column(String, default="starter", nullable=True)  # Legacy string tier
    tier_id = Column(Integer, ForeignKey("tiers.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    roles = relationship("Role", secondary=user_roles, backref="users")
    current_tier = relationship("Tier")

class ApprovalRequest(Base):
    __tablename__ = "approval_requests"
    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(String, nullable=False)  # e.g., "change_user_tier", "update_tier_features"
    payload = Column(String, nullable=False)  # JSON encoded string of data details
    status = Column(String, default="pending", nullable=False)  # 'pending', 'approved', 'rejected'
    maker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    actioned_at = Column(DateTime, nullable=True)
    rejection_reason = Column(String, nullable=True)

    maker = relationship("User", foreign_keys=[maker_id])
    checker = relationship("User", foreign_keys=[checker_id])
