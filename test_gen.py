def generate_bulk_update_query(table_name, columns):
    """
    columns: list of column names, e.g. ["id", "batch_id", "current_balance"]
    Assumes "id" is the primary key and is the FIRST column.
    """
    col_names = ", ".join(columns)
    
    set_clauses = ", ".join([f"{col} = v.{col}" for col in columns if col != "id"])
    
    query = f"""
        UPDATE {table_name} AS t
        SET {set_clauses}
        FROM (VALUES %s) AS v({col_names})
        WHERE t.id = CAST(v.id AS INTEGER)
    """
    return query

cols = ["id", "batch_id", "borrower_id", "current_balance"]
print(generate_bulk_update_query("normalized_loans", cols))
