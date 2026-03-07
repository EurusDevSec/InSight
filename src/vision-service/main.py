from fastapi import FastAPI, File, UploadFile
import uvicorn

app = FastAPI(title="InSight Vision Service", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "UP", "service": "insight-vision-service"}

@app.post("/api/vision/estimate-volume")
async def estimate_volume(image: UploadFile = File(...)):
    return {"volume_ml": 0.0, "message": "Not implemented — Task 2.1"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
