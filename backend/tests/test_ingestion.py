import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import UploadBatch, RawRecord, NormalizedLoan
from app.services.ingestion import ingest_csv

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

def test_ingest_loan_tape(db):
    csv_data = """loan_id,borrower_id,loan_type,origination_date,maturity_date,original_principal,current_balance,interest_rate,term_months,borrower_state,payment_status
L1,B1,Personal,2023-01-01,2025-01-01,10000,5000,5.5,24,CA,CURRENT
L2,B2,Auto,invalid_date,2026-01-01,20000,18000,4.0,36,NY,LATE
"""
    result = ingest_csv(db, csv_data, "loan_tape_2023.csv")

    assert result["total_rows"] == 2
    assert result["normalized_count"] == 2
    assert result["failed_count"] == 0
    assert result["filename"] == "loan_tape_2023.csv"
    assert result["source_type"] == "loan_tape"

    loans = db.query(NormalizedLoan).all()
    assert len(loans) == 2
    assert loans[0].loan_id == "L1"
    assert loans[0].original_principal == 10000.0
    
    # Check bad date parsed as null but raw is preserved
    assert loans[1].origination_date is None
    raw2 = db.query(RawRecord).filter(RawRecord.id == loans[1].raw_record_id).first()
    assert raw2.row_data["origination_date"] == "invalid_date"

def test_ingest_cross_source(db):
    csv_tape = "loan_id,current_balance\nL1,10000"
    ingest_csv(db, csv_tape, "loan_tape.csv")
    
    csv_serv = "loan_id,current_balance,payment_status\nL1,9000,Closed"
    ingest_csv(db, csv_serv, "servicer_update.csv")
    
    csv_man = "loan_id,document_status\nL1,Missing"
    ingest_csv(db, csv_man, "document_manifest.csv")
    
    loans = db.query(NormalizedLoan).all()
    assert len(loans) == 1
    loan = loans[0]
    
    assert loan.current_balance == 10000.0
    assert loan.servicer_update_current_balance == 9000.0
    assert loan.servicer_update_payment_status == "Closed"
    assert loan.manifest_document_status == "Missing"
