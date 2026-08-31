from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import ExceptionModel, NormalizedLoan, AuditLog
from app.services.review import assign_reviewer, make_decision

db = SessionLocal()

# Find a loan with at least two exceptions
# Let's find one
loans_with_multiple_excs = db.query(NormalizedLoan.id).join(ExceptionModel).group_by(NormalizedLoan.id).having(db.func.count(ExceptionModel.id) >= 2).all()
loan_id = loans_with_multiple_excs[0][0]

excs = db.query(ExceptionModel).filter(ExceptionModel.normalized_loan_id == loan_id).all()
ex1 = excs[0]
ex2 = excs[1]

print(f"Found EX1: ID={ex1.id}, LoanID={loan_id}")
print(f"Found EX2: ID={ex2.id}, LoanID={loan_id}")

# 1. Assign EX2
assign_reviewer(db, ex2.id, 2) # Assign to user 2
print(f"Assigned EX2, status is now {ex2.status}")

# 2. Make decision on EX2 (Resolve)
make_decision(db, ex2.id, 2, "APPROVE", "looks good")
print(f"Resolved EX2, status is now {ex2.status}")

# 3. Check Audit Logs for EX1
from app.api.audit import get_audit_trail_for_exception
logs1 = get_audit_trail_for_exception(ex1.id, db)
print(f"Audit logs for EX1 (count={len(logs1)}):")
for log in logs1:
    print(f"  - {log.action}")

# 4. Check Audit Logs for EX2
logs2 = get_audit_trail_for_exception(ex2.id, db)
print(f"Audit logs for EX2 (count={len(logs2)}):")
for log in logs2:
    print(f"  - {log.action}")

