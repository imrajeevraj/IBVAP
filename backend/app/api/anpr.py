from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.app.core.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.event import PlateEvent

router = APIRouter(prefix="/anpr", tags=["anpr"])

@router.get("/plates")
def get_recent_plates(
    limit: int = Query(default=50, ge=1, le=500),
    data_origin: Literal["LIVE", "DEMO", "TEST", "IMPORTED"] = "LIVE",
    db: Session = Depends(get_db),
    _user=Depends(get_current_user),
):
    plates = (
        db.query(PlateEvent)
        .filter(PlateEvent.data_origin == data_origin)
        .order_by(PlateEvent.timestamp.desc())
        .limit(limit)
        .all()
    )
    
    formatted_plates = []
    for p in plates:
        formatted_plates.append({
            "id": p.id,
            "camera_id": p.camera_id,
            "track_id": p.track_id,
            "plate_number": p.plate_number,
            "confidence": p.confidence,
            "watchlist_status": p.watchlist_status,
            "timestamp": p.timestamp.isoformat() + "Z",
            "data_origin": p.data_origin,
        })
        
    return formatted_plates
