"""
Database Models for Enriched Reviews and Complaints
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, Index
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

Base = declarative_base()

class EnrichedReviewORM(Base):
    __tablename__ = "enriched_reviews"

    review_id = Column(String, primary_key=True, index=True)
    business_id = Column(String, index=True)
    restaurant_name = Column(String, index=True)
    city = Column(String, index=True)
    state = Column(String, index=True)
    categories = Column(String)
    stars = Column(Float, index=True)
    business_stars = Column(Float)
    business_review_count = Column(Integer)
    date = Column(String, index=True)
    useful = Column(Integer, default=0)
    text = Column(Text)
    
    # Enriched Fields
    is_complaint = Column(Boolean, default=False, index=True)
    sentiment = Column(String, index=True) # Negative, Neutral, Positive
    complaint_category = Column(String, index=True) # One of 8 operational categories
    aspect = Column(String, index=True) # Specific aspect e.g., 'slow service', 'cold food'
    severity_score = Column(Integer, default=1) # 1 to 5 scale
    priority_score = Column(Float, default=1.0) # 1.0 to 100.0 scale

    __table_args__ = (
        Index("idx_biz_complaint", "business_id", "is_complaint"),
        Index("idx_category_severity", "complaint_category", "severity_score"),
    )

class EnrichedReviewSchema(BaseModel):
    review_id: str
    business_id: str
    restaurant_name: str
    city: Optional[str] = None
    state: Optional[str] = None
    categories: Optional[str] = None
    stars: float
    business_stars: Optional[float] = None
    business_review_count: Optional[int] = None
    date: str
    useful: int = 0
    text: str
    is_complaint: bool
    sentiment: str
    complaint_category: str
    aspect: str
    severity_score: int
    priority_score: float

    model_config = ConfigDict(from_attributes=True)


class FeedbackORM(Base):
    __tablename__ = "user_feedbacks"

    feedback_id = Column(String, primary_key=True, index=True)
    interaction_id = Column(String, nullable=True)
    user_name = Column(String, default="Operations User")
    user_role = Column(String, default="user")
    rating = Column(Integer, default=5)
    feedback_type = Column(String, default="general", index=True)
    comment = Column(Text, nullable=True)
    status = Column(String, default="Pending", index=True)  # Pending, Resolved, Actioned
    timestamp = Column(String, index=True)


class FeedbackSchema(BaseModel):
    feedback_id: str
    interaction_id: Optional[str] = None
    user_name: str = "Operations User"
    user_role: str = "user"
    rating: int = 5
    feedback_type: str = "general"
    comment: Optional[str] = None
    status: str = "Pending"
    timestamp: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserORM(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user", index=True)  # admin, operations_analyst, store_manager, user
    display_name = Column(String, nullable=False)
    title = Column(String, default="Operations Specialist")
    email = Column(String, nullable=False)
    department = Column(String, default="Fleet Operations")
    status = Column(String, default="Active", index=True)  # Active, Inactive, Suspended
    created_at = Column(String, index=True)
    last_login = Column(String, nullable=True)


class UserSchema(BaseModel):
    user_id: str
    username: str
    password: Optional[str] = None
    role: str = "user"
    display_name: str
    title: str = "Operations Specialist"
    email: str
    department: str = "Fleet Operations"
    status: str = "Active"
    created_at: Optional[str] = None
    last_login: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ChatHistoryORM(Base):
    __tablename__ = "chat_history"

    interaction_id = Column(String, primary_key=True, index=True)
    username = Column(String, index=True, default="user")
    user_name = Column(String, default="Operations Analyst")
    user_role = Column(String, default="user")
    timestamp = Column(String, index=True)
    created_at = Column(String, index=True)
    query = Column(Text, nullable=False)
    category = Column(String, default="General Operations")
    page_source = Column(String, default="Central Operations Analyst")
    response_summary = Column(Text, nullable=True)
    response_json = Column(Text, nullable=True)


class ChatHistorySchema(BaseModel):
    interaction_id: str
    username: str = "user"
    user_name: str = "Operations Analyst"
    user_role: str = "user"
    timestamp: str
    created_at: str
    query: str
    category: str = "General Operations"
    page_source: str = "Central Operations Analyst"
    response_summary: Optional[str] = None
    response_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
