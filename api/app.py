from fastapi import FastAPI
from pydantic import BaseModel
from core.retrieval_engine import find_similar_firs

app = FastAPI(title="FIR Similarity Engine")


# Request model
class FIRRequest(BaseModel):
    narrative: str
    top_k: int = 5


@app.get("/")
def home():
    return {"message": "FIR Similarity API Running"}


@app.post("/find-similar")
def find_similar(request: FIRRequest):
    results = find_similar_firs(request.narrative, request.top_k)
    return {"similar_firs": results}