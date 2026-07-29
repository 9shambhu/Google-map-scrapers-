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
        # Write the query line to a temp text file for processing
        with open(input_file, "w") as f:
            f.write(f"{query}\n")

        # Execute using native light configuration (no slow browser rendering)
        subprocess.run([
            "/app/google-maps-scraper",
            "-input", input_file,
            "-results", output_file,
            "-depth", "1",
            "-exit-on-inactivity", "1s" # Stops immediately after processing the query
        ], check=True, timeout=8)

        # Read the raw resulting data array into memory
        if os.path.exists(output_file):
            with open(output_file, "r") as f:
                data = json.load(f)
        else:
            data = []

        return {"status": "success", "results_count": len(data), "results": data}

    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Execution timeout occurred.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper Error: {str(e)}")
        
    finally:
        # AUTOMATIC DELETION: Clears file allocation records immediately
        for temp_file in [input_file, output_file]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
