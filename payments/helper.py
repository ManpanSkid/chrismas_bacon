import logging

from fastapi import HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor

import in_memory
import smtp
from db import order_service

logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=3)

async def complete_payment(order_id):
    try:
        order = in_memory.get_order(order_id)
        order_service.create_order(order)
        in_memory.delete_order(order.id)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(executor, smtp.send_new_order_received_admin, order)
        await loop.run_in_executor(executor, smtp.send_order_success_customer, order.customer.email, order)  # type: ignore

        logging.info("Successfully saved order in database")
    except Exception as e:
        logging.error(f"saving order: {e}")
        raise HTTPException(status_code=400)