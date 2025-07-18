from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import AsyncGenerator, Optional
from .services import gee_service
import json

app = FastAPI(
    title="Skytrace API",
    description="API for fetching satellite image timelines.",
    version="0.1.0"
)

async def image_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_sentinel_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        # This part is tricky in streaming; logging is the best immediate action.
        print(f"Error during stream generation: {e}")
        # You could yield an error object if the client is set up to handle it.
        yield json.dumps({"error": str(e)}) + "\n"


@app.get("/api/v1/images")
def get_images_stream(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of satellite images for a specific location via a stream.
    """
    return StreamingResponse(
        image_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson" # ndjson is a standard for streaming JSON
    )