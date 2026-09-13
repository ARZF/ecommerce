from loguru import logger

from common.events import USER_CREATED, USER_EVENTS_EXCHANGE, consume

# The queue order_service owns; the publisher only declares the exchange.
QUEUE = "order_service.user_created"


async def handle_user_created(payload: dict) -> None:
    logger.info(f"received {USER_CREATED}: {payload}")


async def consume_user_created() -> None:
    """Run for the life of the app — main.py starts this as a background task."""
    try:
        await consume(
            QUEUE,
            handle_user_created,
            exchange=USER_EVENTS_EXCHANGE,
            routing_key=USER_CREATED,
        )
    except Exception as exc:
        logger.error(f"{USER_CREATED} consumer stopped: {exc}")
