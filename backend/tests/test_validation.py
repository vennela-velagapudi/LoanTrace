import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import NormalizedLoan, RawRecord, UploadBatch
from app.services.validation import run_validation

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_missing_loan_id(db):
    norm = NormalizedLoan(loan_id=None)
    db.add(norm)
    db.commit()
    res = run_validation(db)
    exceptions = [e.rule_name for e in db.query(NormalizedLoan).first().exceptions] if hasattr(NormalizedLoan, 'exceptions') else []
    # Actually, we should query exceptions directly
    from app.models import ExceptionModel
    exceptions = [e.rule_name for e in db.query(ExceptionModel).all()]
    assert "missing_required_field" in exceptions

def test_duplicate_loan_id(db):
    db.add(NormalizedLoan(loan_id="L-123"))
    db.add(NormalizedLoan(loan_id="L-123"))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "duplicate_loan_id" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_duplicate_borrower_amount_date(db):
    db.add(NormalizedLoan(loan_id="L-1", borrower_id="B-1", original_principal=100.0, origination_date=date(2023,1,1)))
    db.add(NormalizedLoan(loan_id="L-2", borrower_id="B-1", original_principal=100.0, origination_date=date(2023,1,1)))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "duplicate_borrower_loan" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_invalid_date_format(db):
    batch = UploadBatch()
    db.add(batch)
    db.commit()
    raw = RawRecord(batch_id=batch.id, row_data={"origination_date": "Not A Date"})
    db.add(raw)
    db.commit()
    db.add(NormalizedLoan(loan_id="L-1", raw_record_id=raw.id, origination_date=None))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "invalid_date_format" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_maturity_before_origination(db):
    db.add(NormalizedLoan(loan_id="L-1", origination_date=date(2023,2,1), maturity_date=date(2023,1,1)))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "maturity_before_origination" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_negative_principal(db):
    db.add(NormalizedLoan(loan_id="L-1", original_principal=-500))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "negative_principal" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_negative_current_balance(db):
    db.add(NormalizedLoan(loan_id="L-1", current_balance=-50))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "negative_balance" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_balance_gt_principal(db):
    db.add(NormalizedLoan(loan_id="L-1", original_principal=1000, current_balance=1500))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "balance_exceeds_principal" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_invalid_interest_rate(db):
    db.add(NormalizedLoan(loan_id="L-1", interest_rate=0.50))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "invalid_interest_rate" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_payment_status_dpd_inconsistency(db):
    db.add(NormalizedLoan(loan_id="L-1", payment_status="Current", days_past_due=90))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "payment_status_inconsistent_dpd" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_missing_document_status(db):
    db.add(NormalizedLoan(loan_id="L-1", document_status=None, manifest_document_status=None))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "invalid_document_status" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_cross_source_conflict(db):
    db.add(NormalizedLoan(loan_id="L-1", current_balance=100.0, servicer_update_current_balance=200.0))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "cross_source_conflict" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_stale_record(db):
    db.add(NormalizedLoan(loan_id="L-1", last_updated_at=date(2020,1,1)))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "stale_record" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_invalid_state(db):
    db.add(NormalizedLoan(loan_id="L-1", borrower_state="XX"))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "invalid_state_code" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_suspicious_borrower_repetition(db):
    # Threshold is 3
    for i in range(4):
        db.add(NormalizedLoan(loan_id=f"L-{i}", borrower_id="B-SUS", origination_date=date(2023,1,1)))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "suspicious_borrower_repetition" in [e.rule_name for e in db.query(ExceptionModel).all()]

def test_closed_loan_positive_balance(db):
    db.add(NormalizedLoan(loan_id="L-1", payment_status="Closed", current_balance=50.0))
    db.commit()
    run_validation(db)
    from app.models import ExceptionModel
    assert "closed_loan_with_balance" in [e.rule_name for e in db.query(ExceptionModel).all()]
