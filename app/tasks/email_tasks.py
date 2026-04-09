from __future__ import annotations

from app.core.logging import get_logger
from app.tasks.celery_app import celery_app


logger = get_logger()


@celery_app.task(name="app.tasks.email_tasks.send_order_confirmation")
def send_order_confirmation(email: str, order_id: int) -> None:
    logger.info("send_order_confirmation", email=email, order_id=order_id)
