from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = FastAPI(title="Posture Detection App")

# Check if static folder exists
static_path = Path("static")
print(f"Static folder exists: {static_path.exists()}")
print(f"Index.html exists: {(static_path / 'index.html').exists()}")

# Mount static files directory
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    print("Static files mounted successfully!")
except Exception as e:
    print(f"Error mounting static files: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_home():
    """Serve the main HTML page"""
    try:
        html_path = Path("static/index.html")
        print(f"Attempting to read: {html_path.absolute()}")
        
        if not html_path.exists():
            return HTMLResponse(
                content=f"<h1>Error: File not found at {html_path.absolute()}</h1>",
                status_code=500
            )
        
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Successfully read HTML file ({len(content)} characters)")
            return HTMLResponse(content=content)
    except Exception as e:
        print(f"Error reading HTML: {e}")
        return HTMLResponse(
            content=f"<h1>Error: {str(e)}</h1>",
            status_code=500
        )

@app.get("/test")
async def test():
    """Simple test endpoint"""
    return {"message": "Server is working!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)