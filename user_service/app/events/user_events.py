import asyncio

from loguru import logger

from app.models.user_model import User
from common.events import USER_CREATED, USER_EVENTS_EXCHANGE, publish


def publish_user_created(user: User) -> None:
    """Announce a new user.

    Best-effort on purpose — a broker outage must not fail the request that
    created the user. create_user is a sync endpoint, so this runs in a worker
    thread with no event loop of its own, which is what makes asyncio.run safe.

    ponytail: opens a connection per event. Fine at this size; move to a
    long-lived connection if user creation ever gets hot.
    """
    payload = {"id": user.id, "email": user.email}
    try:
        asyncio.run(publish(USER_EVENTS_EXCHANGE, USER_CREATED, payload))
        logger.info(f"published {USER_CREATED}: {payload}")
    except Exception as exc:
        logger.warning(f"could not publish {USER_CREATED}: {exc}")
