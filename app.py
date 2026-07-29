import os
import subprocess
import json
import uuid
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/v1/scrape")
def scrape_fast(payload: dict):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing 'query' parameter.")

    unique_id = str(uuid.uuid4())
    output_file = f"/tmp/res_{unique_id}.json"

    try:
        # Launching the binary using Go's concurrent fast-mode parser
        # It hits raw HTTP search nodes directly without spinning up Chrome
        subprocess.run([
            "/app/google-maps-scraper",
            "-query", query,
            "-results", output_file,
            "-fast-mode", "true",    # Crucial flag: Skips browser UI rendering
            "-max-results", "20"     # Limit to initial load for instant 3-second return
        ], check=True, timeout=10)   

        # Immediate return from memory
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        return {"status": "success", "results": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper Error: {str(e)}")
        
    finally:
        # AUTOMATIC DELETION: Immediate memory cleanup 
        if os.path.exists(output_file):
            os.remove(output_file)
