from fastapi import FastAPI
from pydantic import BaseModel
from nlu.pipeline import NLPPipeline

app = FastAPI()

pipeline = NLPPipeline()


class ChatRequest(BaseModel):
	message: str


@app.get("/")
async def root():
	return {"message": "OK"}


@app.post("/chat")
async def chat(req: ChatRequest):
	analysis = pipeline.analyze(req.message)
	return analysis
