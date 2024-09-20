from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import aio_pika
import uuid
from pydantic import BaseModel
import asyncio
from asyncio import Task

app = FastAPI()

origins = [
    "http://localhost:3000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for pending requests
pending_requests = {}

# RabbitMQ connection
rabbitmq_connection = None
rabbitmq_channel = None

async def get_rabbitmq_channel():
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_connection is None or rabbitmq_connection.is_closed:
        rabbitmq_connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
        rabbitmq_channel = await rabbitmq_connection.channel()
        await rabbitmq_channel.declare_queue('chat_requests')
        await rabbitmq_channel.declare_queue('chat_responses')
    return rabbitmq_channel

async def publish_message(message: str, token: str):
    """
    Publish message to the RabbitMQ queue.
    """
    try:
        channel = await get_rabbitmq_channel()
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
        # Handle the error appropriately

async def consume_responses():
    while True:
        try:
            channel = await get_rabbitmq_channel()
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
    while True:
        if app.state.consume_task.done():
            app.state.consume_task = asyncio.create_task(consume_responses())
            print("Restarted consume_responses task")
        await asyncio.sleep(60)  # Check every minute

class ChatMessage(BaseModel):
    message: str

@app.post("/api/chat")
async def chat(message: ChatMessage, background_tasks: BackgroundTasks):
    token = str(uuid.uuid4())
    
    # Send message to RabbitMQ in the background
    background_tasks.add_task(publish_message, message.message, token)
    
    # Store retrieval token for later
    pending_requests[token] = None
    
    return {"token": token}

@app.get("/api/chat/{token}")
async def get_chat_response(token: str):
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
    app.state.consume_task = asyncio.create_task(consume_responses())
    app.state.monitor_task = asyncio.create_task(monitor_consume_task())

@app.on_event("shutdown")
async def shutdown_event():
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