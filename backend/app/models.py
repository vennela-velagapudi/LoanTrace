from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Float, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)

class UploadBatch(Base):
    __tablename__ = "upload_batches"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="UPLOADED")

class NormalizedLoan(Base):
    __tablename__ = "normalized_loans"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("upload_batches.id"))
    
    # Required Challenge Fields
    loan_id = Column(String, index=True)
    borrower_id = Column(String, index=True)
    loan_type = Column(String)
    origination_date = Column(Date)
    maturity_date = Column(Date)
    original_principal = Column(Float)
    current_balance = Column(Float)
    interest_rate = Column(Float)
    term_months = Column(Integer)
    borrower_state = Column(String)
    loan_purpose = Column(String)
    credit_grade = Column(String)
    employment_length = Column(String)
    income_band = Column(String)
    payment_status = Column(String)
    days_past_due = Column(Integer)
    servicer_name = Column(String)
    last_payment_date = Column(Date)
    last_updated_at = Column(Date)
    document_status = Column(String)
    source_system = Column(String)

    # Conflicting Source Fields (for validation)
    servicer_update_current_balance = Column(Float, nullable=True)
    servicer_update_payment_status = Column(String, nullable=True)

class ValidationRule(Base):
    __tablename__ = "validation_rules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    rule_definition = Column(JSON)
    is_active = Column(Boolean, default=True)

class ExceptionModel(Base):
    __tablename__ = "exceptions"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("normalized_loans.id"))
    rule_id = Column(Integer, ForeignKey("validation_rules.id"))
    severity = Column(String)
    description = Column(String)
    status = Column(String, default="OPEN")
    ai_recommendation = Column(JSON, nullable=True)

class VerifiedLoan(Base):
    __tablename__ = "verified_loans"
    id = Column(Integer, primary_key=True, index=True)
    original_loan_id = Column(Integer, ForeignKey("normalized_loans.id"))
    verified_data = Column(JSON)
    verified_by_user_id = Column(Integer, ForeignKey("users.id"))
    verification_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    record_hash = Column(String)
    version = Column(Integer, default=1)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
