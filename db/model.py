from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Table, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from db import Base
import uuid

# Association table for User-to-Role many-to-many relationship
user_role = Table(
    'user_role',
    Base.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) # This ID will now directly correspond to Supabase Auth user ID
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False) # Keeping password for now as per previous decision
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    budgets = relationship('Budget', back_populates='user', cascade='all, delete-orphan')
    goals = relationship('Goal', back_populates='user', cascade='all, delete-orphan')
    user_rewards = relationship('UserReward', back_populates='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    roles = relationship('Role', secondary=user_role, back_populates='users')
    ai_chat_messages = relationship('AIChatMessage', back_populates='user', cascade='all, delete-orphan')
    user_financial_metrics = relationship('UserFinancialMetric', back_populates='user', cascade='all, delete-orphan')
    goal_progress = relationship('GoalProgress', back_populates='user', cascade='all, delete-orphan')
    service_votes = relationship('ServiceVote', back_populates='user', cascade='all, delete-orphan')
    appliances = relationship('Appliance', back_populates='user', cascade='all, delete-orphan')
    energy_consumption = relationship('EnergyConsumption', back_populates='user', cascade='all, delete-orphan')


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    users = relationship('User', secondary=user_role, back_populates='roles')

class Goal(Base):
    __tablename__ = 'goals'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String, nullable=False)
    target = Column(Float, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)
    timeline = Column(DateTime(timezone=True), nullable=False)
    risk_level = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    completed = Column(Boolean, default=False) # New
    completed_at = Column(DateTime(timezone=True), nullable=True) # New

    # Relationships
    user = relationship('User', back_populates='goals')
    goal_progress_entries = relationship('GoalProgress', back_populates='goal', cascade='all, delete-orphan') # New relationship

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='transactions')

# Removed existing Incentive model as per plan

class Budget(Base):
    __tablename__ = 'budgets'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    amount = Column(Float, nullable=False)
    period = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship('User', back_populates='budgets')

# New Models from multi-user.md

class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role = Column(String, nullable=False) # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='ai_chat_messages')

class UserFinancialMetric(Base):
    __tablename__ = "user_financial_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    metric_name = Column(String, nullable=False) # e.g., "total_income", "total_expenses", "net_flow", "savings_rate"
    value = Column(Float, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now()) # Date for which the metric applies

    user = relationship('User', back_populates='user_financial_metrics')

class GoalProgress(Base):
    __tablename__ = "goal_progress"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    date = Column(DateTime(timezone=True), server_default=func.now())
    progress_amount = Column(Float, nullable=False) # Amount contributed or current value

    goal = relationship("Goal", back_populates='goal_progress_entries')
    user = relationship('User', back_populates='goal_progress')

class Incentive(Base): # This is the new global Incentive model
    __tablename__ = "incentives"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    reward_value = Column(Float, nullable=False) # e.g., points, monetary value
    criteria = Column(Text, nullable=True) # Description of how to earn the incentive
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user_rewards = relationship('UserReward', back_populates='incentive', cascade='all, delete-orphan')

class UserReward(Base): # This is the new user-specific reward tracking model
    __tablename__ = "user_rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    incentive_id = Column(Integer, ForeignKey("incentives.id", ondelete='CASCADE'), nullable=False)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
    reward_amount = Column(Float, nullable=False) # Actual amount earned for this instance

    user = relationship('User', back_populates='user_rewards')
    incentive = relationship("Incentive", back_populates='user_rewards')

class FinancialService(Base):
    __tablename__ = "financial_services"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    service_votes = relationship('ServiceVote', back_populates='financial_service', cascade='all, delete-orphan')

class ServiceVote(Base):
    __tablename__ = "service_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    service_id = Column(Integer, ForeignKey("financial_services.id", ondelete='CASCADE'), nullable=False)
    vote_type = Column(String, nullable=False) # e.g., "upvote", "downvote", "recommend"
    voted_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='service_votes')
    financial_service = relationship("FinancialService", back_populates='service_votes')

class Appliance(Base):
    __tablename__ = "appliances"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String, nullable=False) # e.g., "Refrigerator", "Washing Machine"
    appliance_type = Column(String, nullable=True) # e.g., "Kitchen", "Laundry"
    power_rating_watts = Column(Float, nullable=True) # Power consumption in Watts
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    energy_consumption_entries = relationship('EnergyConsumption', back_populates='appliance', cascade='all, delete-orphan')
    user = relationship('User', back_populates='appliances')

class EnergyConsumption(Base):
    __tablename__ = "energy_consumption"

    id = Column(Integer, primary_key=True, index=True)
    appliance_id = Column(Integer, ForeignKey("appliances.id", ondelete='CASCADE'), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    consumption_kwh = Column(Float, nullable=False) # Energy consumed in kWh for a period
    consumption_date = Column(DateTime(timezone=True), nullable=False) # Date of consumption reading
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    appliance = relationship("Appliance", back_populates='energy_consumption_entries')
    user = relationship('User', back_populates='energy_consumption')
