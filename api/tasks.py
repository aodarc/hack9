import logging

from api.celery import app

logger = logging.getLogger(__name__)


@app.task
def generate_invoices(invoice_id):
    logger.info(
        f"finished report generation for invoice ID {invoice_id}'"
    )
