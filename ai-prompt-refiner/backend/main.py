import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Prompt Refiner API")

# Allow CORS so the frontend can call the API from any local origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Original rough prompt to refine")

class Variant(BaseModel):
    version: str
    explanation: str

class PromptResponse(BaseModel):
    variants: list[Variant]

SYSTEM_PROMPT = """You are an expert prompt engineer.
Given a user's rough prompt, generate exactly 3 refined, high-quality variations tailored for LLMs.
For each version, provide:
1. The improved prompt text.
2. A brief explanation of why this version is effective and what technique was used (e.g., adding role/persona, step-by-step reasoning/few-shot, constraints & output formatting).

Return the response strictly as valid JSON matching this schema:
{
  "variants": [
    {
      "version": "Refined prompt 1...",
      "explanation": "Why this version works..."
    },
    {
      "version": "Refined prompt 2...",
      "explanation": "Why this version works..."
    },
    {
      "version": "Refined prompt 3...",
      "explanation": "Why this version works..."
    }
  ]
}
"""

def generate_with_gemini(prompt: str) -> dict:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        # Fallback simulation if no API key is provided
        return {
            "variants": [
                {
                    "version": f"Act as an industry expert. {prompt.strip()}. Provide a well-structured breakdown with key insights and actionable takeaways.",
                    "explanation": "Adds an expert persona and specifies structure and output format for clearer, more authoritative output."
                },
                {
                    "version": f"Write a comprehensive guide on: '{prompt.strip()}'. Break down the response step-by-step: 1) Context & background, 2) Core concepts, 3) Real-world examples, and 4) Summary checklist.",
                    "explanation": "Uses step-by-step decomposition to ensure thorough coverage across all key dimensions."
                },
                {
                    "version": f"You are a concise technical writer. Summarize and explain '{prompt.strip()}' in under 300 words. Use bullet points for readability and avoid generic fluff.",
                    "explanation": "Enforces strict length and formatting constraints for high-signal, concise output."
                }
            ]
        }

    from google import genai
    client = genai.Client(api_key=api_key)
    
    response = client.models.generate_content(
        model="gemini-3.7-flash",
        contents=f"{SYSTEM_PROMPT}\n\nUser Prompt: {prompt}",
        config={
            "response_mime_type": "application/json",
            "temperature": 0.7,
        }
    )
    return json.loads(response.text)

@app.post("/refine", response_model=PromptResponse)
async def refine_prompt(request: PromptRequest):
    try:
        data = generate_with_gemini(request.prompt)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refine prompt: {str(e)}")

# Mount static frontend files
from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if os.path.exists(os.path.join(frontend_dir, "index.html")):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

