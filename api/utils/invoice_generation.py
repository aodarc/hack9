import uuid

import httpx


async def submit_new_invoice_request(start_date, end_date, callback, db_conn=None):
    """Create invoices for all numbers in selected date range."""
    sql = """
        SELECT id, calling, called, start, duration, rounded, price, cost, in_invoice FROM calls WHERE start>=$1 AND start<=$2 ORDER BY id;
    """
    update_calls = """
    UPDATE calls
    SET in_invoice=TRUE
    WHERE start>=$1 AND start<=$2
    """
    insert_invoice_sql = """
        INSERT INTO invoice(calling, start, "end", sum, count) VALUES ($1, $2, $3, $4, $5);
    """
    invoice_sql = """
        SELECT * FROM invoice;
    """
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)
    rows = await db_conn.fetch(sql, start_date, end_date)
    invoices = {}
    for row in rows:
        if row['calling'] in invoices:
            invoices[row['calling']].append([row['calling'], row['start'], row['price'], row['cost']])
        else:
            invoices[row['calling']] = [[row['calling'], row['start'], row['price'], row['cost']]]
    for calling, data in invoices.items():
        count = len(data)
        summ = 0
        for d in data:
            summ += d[3]
        await db_conn.execute(insert_invoice_sql, calling, start_date, end_date,
                              summ, count)

    await db_conn.fetch(update_calls, start_date, end_date)
    result = []
    db_invoices = await db_conn.fetch(invoice_sql)
    for invoice in db_invoices:
        result.append({'id': invoice['id'], 'calling': str(invoice['calling']), 'start': str(invoice['start']),
                       'end': str(invoice['end']), 'sum': invoice['sum'], 'count': invoice['count']})
    await db_conn.close()
    master_uuid = uuid.uuid4().hex
    data = {'master_id': master_uuid, 'invoices': result}

    print(callback, 'AAAAAAAAAAAAAAAAAAAAAAAAAAA')
    await httpx.post(callback, json=data, timeout=5, headers={'Content-type': 'application/json'})
