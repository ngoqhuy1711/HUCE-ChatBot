from typing import Optional

from fastapi import FastAPI, Query
from pydantic import BaseModel

from nlu.pipeline import NLPPipeline
from services import csv_service as csvs

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


# -------- Domain Endpoints --------

@app.get("/nganh")
async def get_majors(q: Optional[str] = Query(None, description="Tên ngành hoặc mã ngành")):
    return {"items": csvs.list_majors(q)}


@app.get("/diem")
async def get_scores(
        type: str = Query("chuan", description="chuan | san"),
        major: Optional[str] = Query(None, description="Tên/mã ngành"),
        year: Optional[str] = Query(None, description="Năm, ví dụ 2025")
):
    if type == "san":
        return {"items": csvs.find_floor_score(major, year)}
    return {"items": csvs.find_standard_score(major, year)}


@app.get("/hocphi")
async def get_tuition(year: Optional[str] = Query(None), program: Optional[str] = Query(None)):
    return {"items": csvs.list_tuition(year, program)}


@app.get("/hocbong")
async def get_scholarships(q: Optional[str] = Query(None)):
    return {"items": csvs.list_scholarships(q)}
