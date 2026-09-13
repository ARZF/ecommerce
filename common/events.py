import asyncio
import json
import os
from typing import Awaitable, Callable, Optional

import aio_pika
from aio_pika import ExchangeType, Message
from aio_pika.abc import AbstractIncomingMessage

# Compose sets RABBITMQ_URL to the broker's service name; localhost covers a dev run.
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@localhost/")

# Shared by publisher and consumer — a mismatch here silently drops every event.
USER_EVENTS_EXCHANGE = "user_events"
USER_CREATED = "user.created"


async def publish(exchange: str, routing_key: str, payload: dict) -> None:
    """Publish `payload` as JSON to exchange/routing_key.

    Uses a plain connection so an unreachable broker raises instead of hanging;
    callers decide whether that's fatal.
    """
    connection = await aio_pika.connect(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        declared = await channel.declare_exchange(exchange, ExchangeType.TOPIC, durable=True)
        await declared.publish(
            Message(body=json.dumps(payload).encode(), content_type="application/json"),
            routing_key=routing_key,
        )


async def consume(
    queue: str,
    callback: Callable[[dict], Awaitable[None]],
    exchange: Optional[str] = None,
    routing_key: str = "",
) -> None:
    """Declare `queue`, bind it to exchange/routing_key when given, and hand every
    JSON message to `callback`.

    connect_robust retries until the broker is up, which covers the startup race
    against compose's rabbitmq container. Runs until the task is cancelled.
    """
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)
        declared = await channel.declare_queue(queue, durable=True)

        if exchange:
            source = await channel.declare_exchange(exchange, ExchangeType.TOPIC, durable=True)
            await declared.bind(source, routing_key=routing_key)

        async def on_message(message: AbstractIncomingMessage) -> None:
            async with message.process():  # ack on success, reject on exception
                await callback(json.loads(message.body))

        await declared.consume(on_message)
        await asyncio.Future()  # hold the task open until it's cancelled
