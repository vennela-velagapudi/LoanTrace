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
    source_type = Column(String) # loan_tape, servicer_update, document_manifest
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default="UPLOADED")

class RawRecord(Base):
    __tablename__ = "raw_records"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("upload_batches.id"))
    row_index = Column(Integer)
    row_data = Column(JSON)
    loan_id = Column(String, index=True, nullable=True) # Soft link

class NormalizedLoan(Base):
    """
    Acts as the canonical view of a loan, aggregating fields from loan_tape, servicer_update, and document_manifest.
    """
    __tablename__ = "normalized_loans"
    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(String, index=True, nullable=True)
    
    # Track the primary raw record
    raw_record_id = Column(Integer, ForeignKey("raw_records.id"), nullable=True)
    batch_id = Column(Integer, ForeignKey("upload_batches.id"), nullable=True)
    
    raw_record = relationship("RawRecord")
    
    # ------------------------------------------------
    # LOAN TAPE FIELDS
    # ------------------------------------------------
    borrower_id = Column(String, index=True, nullable=True)
    loan_type = Column(String, nullable=True)
    origination_date = Column(Date, nullable=True)
    maturity_date = Column(Date, nullable=True)
    original_principal = Column(Float, nullable=True)
    current_balance = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    term_months = Column(Integer, nullable=True)
    borrower_state = Column(String, nullable=True)
    loan_purpose = Column(String, nullable=True)
    credit_grade = Column(String, nullable=True)
    employment_length = Column(String, nullable=True)
    income_band = Column(String, nullable=True)
    payment_status = Column(String, nullable=True)
    days_past_due = Column(Integer, nullable=True)
    servicer_name = Column(String, nullable=True)
    last_payment_date = Column(Date, nullable=True)
    last_updated_at = Column(Date, nullable=True)
    document_status = Column(String, nullable=True)
    source_system = Column(String, nullable=True)

    # ------------------------------------------------
    # SERVICER UPDATE OVERLAPPING FIELDS
    # ------------------------------------------------
    servicer_update_current_balance = Column(Float, nullable=True)
    servicer_update_interest_rate = Column(Float, nullable=True)
    servicer_update_payment_status = Column(String, nullable=True)
    servicer_update_days_past_due = Column(Integer, nullable=True)
    servicer_update_servicer_name = Column(String, nullable=True)
    servicer_update_last_payment_date = Column(Date, nullable=True)
    servicer_update_last_updated_at = Column(Date, nullable=True)
    servicer_update_document_status = Column(String, nullable=True)

    # ------------------------------------------------
    # DOCUMENT MANIFEST FIELDS
    # ------------------------------------------------
    manifest_document_status = Column(String, nullable=True)

class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(Integer, ForeignKey("upload_batches.id"), nullable=True)
    run_time = Column(DateTime(timezone=True), server_default=func.now())

class ValidationResult(Base):
    __tablename__ = "validation_results"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("validation_runs.id"))
    normalized_loan_id = Column(Integer, ForeignKey("normalized_loans.id"))
    is_valid = Column(Boolean)

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
    validation_result_id = Column(Integer, ForeignKey("validation_results.id"), nullable=True)
    normalized_loan_id = Column(Integer, ForeignKey("normalized_loans.id"))
    rule_name = Column(String, nullable=True)
    severity = Column(String)
    field = Column(String, nullable=True)
    actual_value = Column(String, nullable=True)
    expected_condition = Column(String, nullable=True)
    description = Column(String)
    status = Column(String, default="OPEN")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_reason = Column(String, nullable=True)
    version = Column(Integer, default=1)
    
    normalized_loan = relationship("NormalizedLoan", backref="exceptions")

class ExceptionComment(Base):
    __tablename__ = "exception_comments"
    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(Integer, ForeignKey("exceptions.id"))
    reviewer_id = Column(Integer, ForeignKey("users.id"))
    comment_text = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
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
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String)
    entity_type = Column(String)
    entity_id = Column(Integer)
    loan_id = Column(String, index=True, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class AIRecommendation(Base):
    __tablename__ = "ai_recommendations"
    id = Column(Integer, primary_key=True, index=True)
    exception_id = Column(Integer, ForeignKey("exceptions.id"), nullable=True)
    loan_id = Column(String, index=True, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action_type = Column(String)  # EXPLAIN, SUGGEST, COMPARE, NOTE, SEVERITY, SUMMARY, RULE
    model_name = Column(String)
    prompt_template = Column(String)
    raw_response = Column(JSON, nullable=True)
    structured_data = Column(JSON, nullable=True)
    confidence = Column(String, nullable=True)
    status = Column(String, default="GENERATED")  # GENERATED, ACCEPTED, REJECTED, EDITED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
