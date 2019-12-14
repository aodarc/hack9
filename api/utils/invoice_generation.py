async def submit_new_invoice_request(start_date, end_date, callback, db_conn=None):
    """Create invoices for all numbers in selected date range."""
    sql = """
        SELECT id FROM calls WHERE start>=$1 AND start<=$2 ORDER BY id;
    """
    start_date = start_date.date()
    end_date = end_date.date()
    rows = await db_conn.fetch(sql, start_date, end_date)
    for r in rows:
        print(r)
        generate_invoices.delay()
    await db_conn.close()
