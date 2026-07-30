from fastapi import UploadFile, File
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import pandas as pd

app = FastAPI()
app.mount("/static", StaticFiles(directory="api/static"), name="static")

templates = Jinja2Templates(directory="api/templates")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):

    os.makedirs("uploads", exist_ok=True)

    file_path = os.path.join("uploads", file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(file_path)

    preview = df.head(5).to_dict(orient="records")

    return {
        "message": "CSV uploaded successfully",
        "filename": file.filename,
        "rows": len(df),
        "columns": list(df.columns),
        "preview": preview
    }
from pydantic import BaseModel

class Question(BaseModel):
    question: str


@app.post("/chat")
async def chat(data: Question):

    return {
        "answer": f"You asked: {data.question}"
    }
