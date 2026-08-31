with open("backend/app/services/validation.py") as f:
    lines = f.readlines()
    for i, line in enumerate(lines[:100]):
        if "loans = db.query(NormalizedLoan).all()" in line:
            print(f"Line {i}: {line.strip()}")
