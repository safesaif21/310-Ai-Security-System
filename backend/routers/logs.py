
from fastapi import APIRouter, HTTPException
from pathlib import Path
from backend.config import settings

router = APIRouter(prefix="/logs", tags=["logs"])

LOGS_DIR = Path(settings.logs_folder)

@router.get("/dates")
async def list_log_dates():
    """List available log dates"""
    if not LOGS_DIR.exists():
        return {"dates": []}
    
    dates = []
    for item in LOGS_DIR.glob("*.txt"):
        # Expect format YYYY-MM-DD.txt
        dates.append(item.stem)
    
    dates.sort(reverse=True)
    return {"dates": dates}

@router.get("/{date}")
async def get_log_content(date: str):
    """Get log content for a specific date"""
    file_path = LOGS_DIR / f"{date}.txt"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return {"date": date, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
