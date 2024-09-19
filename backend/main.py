from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from chat import Chat

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

@app.get("/api/chat/{message}")
async def chat(message):
    chat = Chat()
    response = await chat.message(message)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

