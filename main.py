from fastapi import FastAPI, File, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import torch
import cv2
import numpy as np
from pathlib import Path
import base64
from typing import Optional

app = FastAPI(title="Posture Detection App")

# Load YOLOv5 model
MODEL_PATH = 'small640.pt'
model = None

def load_model():
    global model
    try:
        model = torch.hub.load('ultralytics/yolov5', 'custom', path=MODEL_PATH)
        model.conf = 0.5  # confidence threshold
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Using dummy model for demo purposes")

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        return HTMLResponse(
            content=f"<h1>Error loading page: {str(e)}</h1>",
            status_code=500
        )

@app.post("/detect")
async def detect_posture(file: UploadFile = File(...)):
    """Detect posture from uploaded image"""
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if model is None:
            return JSONResponse({
                "error": "Model not loaded",
                "posture": "sitting_bad",  # Demo fallback
                "confidence": 0.0,
                "trigger_animation": True
            })
        
        # Run inference
        results = model(img)
        
        # Parse results
        detections = results.pandas().xyxy[0]
        
        if len(detections) > 0:
            # Get the detection with highest confidence
            best_detection = detections.iloc[0]
            posture = best_detection['name']
            confidence = float(best_detection['confidence'])
            
            trigger_animation = posture == 'sitting_bad'
            
            return JSONResponse({
                "posture": posture,
                "confidence": confidence,
                "trigger_animation": trigger_animation
            })
        else:
            return JSONResponse({
                "posture": "no_detection",
                "confidence": 0.0,
                "trigger_animation": False
            })
            
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "posture": "error",
            "confidence": 0.0,
            "trigger_animation": False
        }, status_code=500)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time webcam detection"""
    await websocket.accept()
    try:
        while True:
            # Receive image data from client
            data = await websocket.receive_text()
            
            # Decode base64 image
            img_data = base64.b64decode(data.split(',')[1])
            nparr = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if model is None:
                await websocket.send_json({
                    "posture": "sitting_bad",
                    "confidence": 0.0,
                    "trigger_animation": True
                })
                continue
            
            # Run inference
            results = model(img)
            detections = results.pandas().xyxy[0]
            
            if len(detections) > 0:
                best_detection = detections.iloc[0]
                posture = best_detection['name']
                confidence = float(best_detection['confidence'])
                trigger_animation = posture == 'sitting_bad'
                
                await websocket.send_json({
                    "posture": posture,
                    "confidence": confidence,
                    "trigger_animation": trigger_animation
                })
            else:
                await websocket.send_json({
                    "posture": "no_detection",
                    "confidence": 0.0,
                    "trigger_animation": False
                })
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")

# Mount static files AFTER all route definitions
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)