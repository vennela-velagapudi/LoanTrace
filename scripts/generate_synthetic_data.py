import csv
import random
import json
import datetime
import os

def generate_date(start_year, end_year):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    return start + datetime.timedelta(days=random.randint(0, (end - start).days))

def main():
    random.seed(42)
    os.makedirs('data', exist_ok=True)

    num_loans = 2000
    
    loan_tape = []
    servicer_update = []
    document_manifest = []
    
    loan_types = ['Auto', 'Mortgage', 'Personal', 'Student']
    loan_purposes = ['Debt Consolidation', 'Home Improvement', 'Credit Card Refinancing', 'Major Purchase', 'Medical Expenses', 'Other']
    credit_grades = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    income_bands = ['<50k', '50k-100k', '100k-150k', '>150k']
    payment_statuses = ['Current', 'Late (16-30 days)', 'Late (31-120 days)', 'Default', 'Charged Off', 'Fully Paid', 'Closed']
    servicer_names = ['Alpha Servicing', 'Beta Loan Servicers', 'Gamma Collections', 'Delta Financial']
    states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
    doc_statuses = ['Available', 'Missing', 'Pending', 'Expired']
    source_systems = ['Legacy', 'OriginatePro', 'LendingWeb', 'Manual']

    for i in range(num_loans):
        loan_id = f"L-{100000 + i}"
        borrower_id = f"B-{random.randint(10000, 99999)}"
        loan_type = random.choice(loan_types)
        origination_date = generate_date(2018, 2023)
        term_months = random.choice([36, 60, 120, 360])
        maturity_date = origination_date + datetime.timedelta(days=term_months * 30)
        original_principal = round(random.uniform(5000, 500000), 2)
        current_balance = round(original_principal * random.uniform(0.1, 0.9), 2)
        interest_rate = round(random.uniform(0.03, 0.15), 4)
        borrower_state = random.choice(states)
        loan_purpose = random.choice(loan_purposes)
        credit_grade = random.choice(credit_grades)
        employment_length = f"{random.randint(0, 20)} years"
        income_band = random.choice(income_bands)
        
        status = random.choice(payment_statuses)
        if status in ('Current', 'Fully Paid', 'Closed'):
            dpd = 0
        elif status == 'Late (16-30 days)':
            dpd = random.randint(16, 30)
        else:
            dpd = random.randint(31, 200)
            
        servicer_name = random.choice(servicer_names)
        last_payment_date = origination_date + datetime.timedelta(days=random.randint(30, 1000))
        last_updated_at = datetime.date(2024, random.randint(1, 8), random.randint(1, 28))
        document_status = random.choice(doc_statuses)
        source_system = random.choice(source_systems)
        
        record = {
            'loan_id': loan_id,
            'borrower_id': borrower_id,
            'loan_type': loan_type,
            'origination_date': origination_date.strftime("%Y-%m-%d"),
            'maturity_date': maturity_date.strftime("%Y-%m-%d"),
            'original_principal': original_principal,
            'current_balance': current_balance,
            'interest_rate': interest_rate,
            'term_months': term_months,
            'borrower_state': borrower_state,
            'loan_purpose': loan_purpose,
            'credit_grade': credit_grade,
            'employment_length': employment_length,
            'income_band': income_band,
            'payment_status': status,
            'days_past_due': dpd,
            'servicer_name': servicer_name,
            'last_payment_date': last_payment_date.strftime("%Y-%m-%d"),
            'last_updated_at': last_updated_at.strftime("%Y-%m-%d"),
            'document_status': document_status,
            'source_system': source_system
        }
        loan_tape.append(record)

    expected_exceptions = []
    def record_exception(l_id, ext_type):
        expected_exceptions.append({'loan_id': l_id, 'exception_type': ext_type})

    # Injections
    # 1. Missing loan IDs
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['loan_id'] = ''
        record_exception('', 'missing_required_field')
        
    # 2. Duplicate loan IDs
    for _ in range(20): 
        idx1 = random.randint(0, num_loans-1)
        idx2 = random.randint(0, num_loans-1)
        loan_tape[idx1]['loan_id'] = loan_tape[idx2]['loan_id']
        record_exception(loan_tape[idx1]['loan_id'], 'duplicate_loan_id')

    # 3. Duplicate borrower + loan amount + origination date
    for _ in range(20):
        idx = random.randint(0, num_loans-1)
        new_rec = loan_tape[idx].copy()
        new_rec['loan_id'] = f"L-999{random.randint(100, 999)}"
        loan_tape.append(new_rec)
        record_exception(new_rec['loan_id'], 'duplicate_borrower_loan')

    # 4. Invalid date formats
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['origination_date'] = "Not A Date"
        record_exception(loan_tape[idx]['loan_id'], 'invalid_date_format')

    # 5. Maturity date before origination date
    for _ in range(20):
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['origination_date'] = "2023-01-01"
        loan_tape[idx]['maturity_date'] = "2022-01-01"
        record_exception(loan_tape[idx]['loan_id'], 'maturity_before_origination')

    # 6. Negative principal balance
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['original_principal'] = -1000.0
        record_exception(loan_tape[idx]['loan_id'], 'negative_principal')

    # 7. Negative current balance
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['current_balance'] = -500.0
        record_exception(loan_tape[idx]['loan_id'], 'negative_balance')

    # 8. Current balance greater than original principal
    for _ in range(20):
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['current_balance'] = loan_tape[idx]['original_principal'] + 1000.0
        record_exception(loan_tape[idx]['loan_id'], 'balance_exceeds_principal')

    # 9. Interest rate outside expected range (e.g., > 30% or < 0%)
    for _ in range(15): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['interest_rate'] = random.uniform(0.31, 0.50)
        record_exception(loan_tape[idx]['loan_id'], 'invalid_interest_rate')
    for _ in range(15): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['interest_rate'] = random.uniform(-0.05, -0.01)
        record_exception(loan_tape[idx]['loan_id'], 'invalid_interest_rate')

    # 10. Payment status inconsistent with days past due
    for _ in range(20):
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['payment_status'] = 'Current'
        loan_tape[idx]['days_past_due'] = random.randint(90, 120)
        record_exception(loan_tape[idx]['loan_id'], 'payment_status_inconsistent_dpd')

    # 11. Missing document status
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['document_status'] = ''
        record_exception(loan_tape[idx]['loan_id'], 'invalid_document_status')

    # 13. Stale records based on last_updated_at (e.g., older than 6 months)
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['last_updated_at'] = '2023-01-01'
        record_exception(loan_tape[idx]['loan_id'], 'stale_record')

    # 14. Invalid state codes (e.g., "XX")
    for _ in range(20): 
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['borrower_state'] = 'XX'
        record_exception(loan_tape[idx]['loan_id'], 'invalid_state_code')

    # 15. Suspiciously repeated borrower records
    b_id = 'B-99999'
    o_date = '2024-01-01'
    for _ in range(5): # Create 5 identical borrower/date loans to cross threshold
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['borrower_id'] = b_id
        loan_tape[idx]['origination_date'] = o_date
        record_exception(loan_tape[idx]['loan_id'], 'suspicious_borrower_repetition')

    # 16. Loans marked closed while still having positive balance
    for _ in range(20):
        idx = random.randint(0, num_loans-1)
        loan_tape[idx]['payment_status'] = 'Closed'
        loan_tape[idx]['current_balance'] = 5000.0
        record_exception(loan_tape[idx]['loan_id'], 'closed_loan_with_balance')

    # Write loan tape
    fields = ['loan_id', 'borrower_id', 'loan_type', 'origination_date', 'maturity_date', 'original_principal', 'current_balance', 'interest_rate', 'term_months', 'borrower_state', 'loan_purpose', 'credit_grade', 'employment_length', 'income_band', 'payment_status', 'days_past_due', 'servicer_name', 'last_payment_date', 'last_updated_at', 'document_status', 'source_system']
    with open('data/loan_tape.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(loan_tape)

    # Servicer update
    su_loans = random.sample(loan_tape, 500)
    for i, r in enumerate(su_loans):
        su_rec = {
            'loan_id': r['loan_id'],
            'current_balance': r['current_balance'],
            'interest_rate': r['interest_rate'],
            'payment_status': r['payment_status'],
            'days_past_due': r['days_past_due'],
            'servicer_name': r['servicer_name'],
            'last_payment_date': r['last_payment_date'],
            'last_updated_at': '2024-09-01',
            'document_status': r['document_status']
        }
        # 12. Conflicting values between loan_tape.csv and servicer_update.csv
        if i < 20: 
            su_rec['current_balance'] = r['original_principal']
            record_exception(r['loan_id'], 'cross_source_conflict')
        elif i < 40:
            su_rec['payment_status'] = 'Default'
            record_exception(r['loan_id'], 'cross_source_conflict')
        servicer_update.append(su_rec)

    with open('data/servicer_update.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['loan_id', 'current_balance', 'interest_rate', 'payment_status', 'days_past_due', 'servicer_name', 'last_payment_date', 'last_updated_at', 'document_status'])
        writer.writeheader()
        writer.writerows(servicer_update)

    # Document manifest
    for r in loan_tape:
        if r['loan_id']:
            document_manifest.append({
                'loan_id': r['loan_id'],
                'document_status': random.choice(doc_statuses)
            })

    with open('data/document_manifest.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['loan_id', 'document_status'])
        writer.writeheader()
        writer.writerows(document_manifest)

    # Validation rules
    val_rules = {
        "rules": [
            {"field": "loan_id", "rule": "not_null"},
            {"field": "loan_id", "rule": "unique"}
        ]
    }
    with open('data/validation_rules.json', 'w') as f:
        json.dump(val_rules, f)

    # Users
    users = {
        "users": [
            {"id": 1, "name": "Admin", "role": "admin"}
        ]
    }
    with open('data/users.json', 'w') as f:
        json.dump(users, f)

    # Expected exception sample
    with open('data/expected_exception_sample.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['loan_id', 'exception_type'])
        writer.writeheader()
        writer.writerows(expected_exceptions)

    print(f"Generated {len(loan_tape)} loan records in loan_tape.csv.")
    print(f"Generated {len(servicer_update)} servicer records in servicer_update.csv.")
    print(f"Generated {len(document_manifest)} document manifest records in document_manifest.csv.")

if __name__ == '__main__':
    main()
