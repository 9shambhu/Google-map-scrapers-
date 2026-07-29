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
    input_file = f"/tmp/in_{unique_id}.txt"
    output_file = f"/tmp/res_{unique_id}.json"

    try:
        with open(input_file, "w") as f:
            f.write(f"{query}\n")

        # Give the headless browser 30 seconds to fetch data and write to disk
        subprocess.run([
            "/app/google-maps-scraper",
            "-input", input_file,
            "-results", output_file,
            "-depth", "1",
            "-exit-on-inactivity", "5s" 
        ], check=True, timeout=35)

        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        return {"status": "success", "results_count": len(data), "results": data}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=544, detail="Google parsing timed out.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
        
    finally:
        # DATA REMOVAL: Wipes transient information immediately from disk storage
        for temp_file in [input_file, output_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
