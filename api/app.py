from fastapi import UploadFile, File
import tempfile
from src.extract_text import extract_text_from_pdf
from src.structure_fir import extract_narrative_from_text


@app.post("/upload-fir")
async def upload_fir(file: UploadFile = File(...)):
    # Save temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        content = await file.read()
        temp.write(content)
        temp_path = temp.name

    # Extract raw text
    text = extract_text_from_pdf(temp_path)

    # Extract narrative only
    narrative = extract_narrative_from_text(text)

    # Find similar FIRs
    results = find_similar_firs(narrative)

    return {
        "narrative": narrative,
        "similar_firs": results
    }