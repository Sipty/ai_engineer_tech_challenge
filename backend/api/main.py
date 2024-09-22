"""
A FastAPI application for handling chat requests and responses using RabbitMQ.

This module sets up a FastAPI server that communicates with a RabbitMQ message
queue to handle chat requests and responses asynchronously. It provides endpoints
for submitting chat messages and retrieving responses.

In a real life project, it would also use Redis to cache pending requests.
"""

from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import aio_pika
import uuid
from pydantic import BaseModel
import asyncio
from asyncio import Task
import os

app = FastAPI()

origins = [
    "http://frontend:3000",
    "*"
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for pending requests.
# In reality, this would be replaced by Redis.
pending_requests = {}

# RabbitMQ connection
rabbitmq_connection = None
rabbitmq_channel = None

def __rabbitmq_url() -> str:
    """
    Constructs the RabbitMQ URL from environment variables.

    Returns:
        str: The constructed RabbitMQ URL.

    Raises:
        ValueError: If any of the required environment variables are not set.
    """
    host = os.getenv('RABBITMQ_HOST')
    port = os.getenv('RABBITMQ_PORT')
    user = os.getenv('RABBITMQ_USER')
    password = os.getenv('RABBITMQ_PASSWORD')
    
    if not all([host, port, user, password]):
        raise ValueError("RabbitMQ connection details are not properly set in environment variables.")
    
    return f"amqp://{user}:{password}@{host}:{port}/"

async def __get_rabbitmq_channel():
    """
    Returns the RabbitMQ channels, ensuring they are created.

    Returns:
        aio_pika.Channel: The RabbitMQ channel.
    """
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        rabbitmq_url = __rabbitmq_url()
        rabbitmq_connection = await aio_pika.connect_robust(rabbitmq_url)
        rabbitmq_channel = await rabbitmq_connection.channel()
        await rabbitmq_channel.declare_queue('chat_requests')
        await rabbitmq_channel.declare_queue('chat_responses')
    return rabbitmq_channel

async def publish_message(message: str, token: str):
    """
    Publishes a message to the RabbitMQ queue.

    Fails quietly, in case of failure, since RabiitMQ would attempt to bring itself back up.

    In a real deployment, better error handling would be needed. Especially for cases when
    the queue falls over and never comes back up. Cloud Watch alarms come to mind for this.

    Args:
        message (str): The message to publish.
        token (str): The correlation ID for the message.
    """
    try:
        channel = await __get_rabbitmq_channel()
        await channel.default_exchange.publish(
            aio_pika.Message(
                body=message.encode(),
                correlation_id=token
            ),
            routing_key='chat_requests'
        )
        print(f"Published message with token: {token}")
    except Exception as e:
        print(f"Error publishing message: {e}")

async def consume_responses():
    """
    Consumes responses from the RabbitMQ queue and updates pending requests.

    Shabby error handling is present here, but the motivation was explained above already:
    In a real deployment, the api would incorporate much nicer error handling mechanisms.
    """
    while True:
        try:
            channel = await __get_rabbitmq_channel()
            queue = await channel.declare_queue('chat_responses')
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        try:
                            token = message.correlation_id
                            response = message.body.decode()
                            if token in pending_requests:
                                pending_requests[token] = response
                                print(f"Received response for token: {token}")
                        except Exception as e:
                            print(f"Error processing message: {e}")
        except Exception as e:
            print(f"Error in consume_responses: {e}")
            await asyncio.sleep(5)  # Wait before retrying

async def monitor_consume_task():
    """
    Monitors and restarts the consume_responses task if it fails.

    A very minimal error handling present. Its backed up by rebuilding mechanisms from the
    deployment, but more can definitely be done.
    """
    while True:
        if app.state.consume_task.done():
            app.state.consume_task = asyncio.create_task(consume_responses())
            print("Restarted consume_responses task")
        await asyncio.sleep(60)  # Check every minute

class ChatMessage(BaseModel):
    """
    Pydantic base model for chat messages.

    Attributes:
        message (str): The content of the chat message.
    """
    message: str

@app.post("/api/chat")
async def chat(message: ChatMessage, background_tasks: BackgroundTasks):
    """
    Handles incoming chat messages.

    Args:
        message (ChatMessage): The incoming chat message.
        background_tasks (BackgroundTasks): FastAPI background tasks handler.

    Returns:
        dict: A dictionary containing the token for the chat request.
    """
    token = str(uuid.uuid4())
    
    # Send message to RabbitMQ in the background
    background_tasks.add_task(publish_message, message.message, token)
    
    # Store retrieval token for later
    pending_requests[token] = None
    
    return {"token": token}

@app.get("/api/chat/{token}")
async def get_chat_response(token: str):
    """
    Retrieves the chat response for a given token.

    Args:
        token (str): The token associated with the chat request.

    Returns:
        dict: A dictionary containing the response or status of the request.
    """
    if token in pending_requests:
        response = pending_requests.get(token)
        if response is not None:
            del pending_requests[token]
            return {"response": response}
        else:
            return {"status": "processing"}
    else:
        return {"status": "not_found"}

@app.on_event("startup")
async def startup_event():
    """
    Initializes background tasks on application startup.
    """
    app.state.consume_task = asyncio.create_task(consume_responses())
    app.state.monitor_task = asyncio.create_task(monitor_consume_task())

@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleans up resources on application shutdown.
    """
    for task in [app.state.consume_task, app.state.monitor_task]:
        if isinstance(task, Task):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

    global rabbitmq_connection
    if rabbitmq_connection and not rabbitmq_connection.is_closed:
        await rabbitmq_connection.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)