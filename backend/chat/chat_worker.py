import os
import asyncio
from aio_pika import connect_robust, Message

# Global variables for RabbitMQ connection and channel
rabbitmq_connection = None
rabbitmq_channel = None

def __rabbitmq_url():
    host = os.getenv('RABBITMQ_HOST')
    port = os.getenv('RABBITMQ_PORT')
    user = os.getenv('RABBITMQ_USER')
    password = os.getenv('RABBITMQ_PASSWORD')
    
    if not all([host, port, user, password]):
        raise ValueError("RabbitMQ connection details are not properly set in environment variables.")
    
    return f"amqp://{user}:{password}@{host}:{port}/"

async def __get_rabbitmq_channel():
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        rabbitmq_connection = await connect_robust(__rabbitmq_url())
        rabbitmq_channel = await rabbitmq_connection.channel()
        await rabbitmq_channel.declare_queue('chat_requests')
        await rabbitmq_channel.declare_queue('chat_responses')
    return rabbitmq_channel

async def process_message(message):
    async with message.process():
        body = message.body.decode()
        print(f"Received message: {body[:50]}...")
        print(f"The message has correlation_id: {message.correlation_id}")

        response = get_chat_response(body)

        channel = await __get_rabbitmq_channel()
        await channel.default_exchange.publish(
            Message(
                body=response.encode(),
                correlation_id=message.correlation_id
            ),
            routing_key='chat_responses'
        )
        print(f"Published response: {response[:50]}...")

async def consume_messages():
    while True:
        try:
            channel = await __get_rabbitmq_channel()
            queue = await channel.declare_queue('chat_requests')
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    await process_message(message)
        except Exception as e:
            print(f"Error in consume_messages: {e}")
            await asyncio.sleep(5)  # Wait before retrying

async def main():
    consume_task = asyncio.create_task(consume_messages())
    
    try:
        await consume_task
    except asyncio.CancelledError:
        print("Consumer task was cancelled")
    finally:
        if rabbitmq_connection and not rabbitmq_connection.is_closed:
            await rabbitmq_connection.close()

if __name__ == "__main__":
    print("Initializing chat worker...")
    try:
        from chat import get_chat_response
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Worker stopped by user.")