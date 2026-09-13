"""Runnable check for the RabbitMQ publish/consume path — needs a live broker.

    docker compose up -d rabbitmq
    python check_events.py

Exercises common/events.py against the real broker: declare + bind the queue,
publish an event, then consume it back and compare the payload.

The queue is declared and bound *before* publishing, and the consumer starts
after, so the message waits in the queue and the check has no timing race.
"""
import asyncio
import sys

import aio_pika
from aio_pika import ExchangeType

from common.events import (
    RABBITMQ_URL,
    USER_CREATED,
    USER_EVENTS_EXCHANGE,
    consume,
    publish,
)

QUEUE = "check_events.user_created"
PAYLOAD = {"id": 4242, "email": "check-events@example.com"}


async def main() -> int:
    received = []

    async def handler(payload):
        received.append(payload)

    # 1. Bind the queue up front so the published event has somewhere to land
    connection = await aio_pika.connect(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            USER_EVENTS_EXCHANGE, ExchangeType.TOPIC, durable=True
        )
        queue = await channel.declare_queue(QUEUE, durable=True)
        await queue.bind(exchange, routing_key=USER_CREATED)
        await queue.purge()  # drop anything left by a previous run

    # 2. Publish, exactly as user_service does
    await publish(USER_EVENTS_EXCHANGE, USER_CREATED, PAYLOAD)

    # 3. Consume, exactly as order_service does
    consumer = asyncio.create_task(
        consume(QUEUE, handler, exchange=USER_EVENTS_EXCHANGE, routing_key=USER_CREATED)
    )
    try:
        for _ in range(50):
            if received:
                break
            await asyncio.sleep(0.1)
    finally:
        consumer.cancel()

    assert received, "published event was never consumed"
    assert received[0] == PAYLOAD, f"payload changed in flight: {received[0]!r}"
    assert isinstance(received[0], dict), f"expected a decoded dict, got {type(received[0])}"

    # 4. Clean up the check's own queue, leaving the exchange for the services
    connection = await aio_pika.connect(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await (await channel.declare_queue(QUEUE, durable=True)).delete()

    print(f"event check: {USER_CREATED} round-tripped {PAYLOAD}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(asyncio.run(main()))
    except (OSError, aio_pika.exceptions.AMQPConnectionError) as exc:
        print(f"no broker at {RABBITMQ_URL} ({exc.__class__.__name__}: {exc})")
        print("start one with: docker compose up -d rabbitmq")
        sys.exit(1)
