from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserInput(BaseModel):
    message: str

GEMINI_API_KEY =  os.getenv("GEMINI_API_KEY")
POLLINATIONS_BASE_URL = os.getenv("POLLINATIONS_BASE_URL") #image 
# ✅ Your system prompt
SYSTEM_PROMPT = os.getenv("SYSTEM_PROMPT")

async def get_gemini_response(user_message: str) -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    
    data = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_message}
                ]
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, params=params, json=data)
        response.raise_for_status()
        response_json = response.json()
        gemini_text = response_json["candidates"][0]["content"]["parts"][0]["text"]
        return gemini_text

# Pollinations: Generate image
async def generate_image(prompt: str) -> str:
    encoded_prompt = prompt.replace(' ', '%20')
    image_url = f"{POLLINATIONS_BASE_URL}{encoded_prompt}"
    return image_url

@app.post("/ask")
async def ask_converse(input: UserInput):
    try:
        user_msg = input.message
        gemini_reply = await get_gemini_response(user_msg)
        image_url = await generate_image(gemini_reply)
        return {"reply": gemini_reply, "image": image_url}
    except Exception as e:
        return {"error": str(e)}
