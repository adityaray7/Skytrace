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

async def sentinel2_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the Sentinel-2 GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_sentinel2_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        print(f"Error during Sentinel-2 stream generation: {e}")
        yield json.dumps({"error": str(e)}) + "\n"

async def sentinel1_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the Sentinel-1 GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_sentinel1_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        print(f"Error during Sentinel-1 stream generation: {e}")
        yield json.dumps({"error": str(e)}) + "\n"

async def naip_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the NAIP GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_high_res_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        print(f"Error during NAIP stream generation: {e}")
        yield json.dumps({"error": str(e)}) + "\n"

async def sentinel3_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the Sentinel-3 GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_sentinel3_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        print(f"Error during Sentinel-3 stream generation: {e}")
        yield json.dumps({"error": str(e)}) + "\n"

async def landsat8_stream_generator(lat: float, lon: float, start_date: Optional[str] = None, end_date: Optional[str] = None) -> AsyncGenerator[str, None]:
    """Wraps the Landsat-8 GEE service to handle potential errors."""
    try:
        async for image_data in gee_service.get_landsat8_images_stream(lat, lon, start_date, end_date):
            yield image_data
    except Exception as e:
        print(f"Error during Landsat-8 stream generation: {e}")
        yield json.dumps({"error": str(e)}) + "\n"




@app.get("/api/v1/sentinel2")
def get_sentinel2_images(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of Sentinel-2 satellite images for a specific location via a stream.
    Provides global coverage at 10m resolution. Uses optical imagery (affected by clouds).
    """
    return StreamingResponse(
        sentinel2_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson"
    )

@app.get("/api/v1/sentinel1")
def get_sentinel1_images(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of Sentinel-1 SAR images for a specific location via a stream.
    Uses radar that can see through clouds and at night. 10m resolution.
    """
    return StreamingResponse(
        sentinel1_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson"
    )

@app.get("/api/v1/high-res-images")
def get_naip_images(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of high-resolution NAIP images for a specific location in the US.
    Provides 1m resolution but only covers the continental United States.
    """
    return StreamingResponse(
        naip_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson"
    )

@app.get("/api/v1/sentinel3")
def get_sentinel3_images(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of Sentinel-3 OLCI images for a specific location via a stream.
    Provides global coverage at 300m resolution. Ideal for ocean and large-scale land monitoring.
    """
    return StreamingResponse(
        sentinel3_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson"
    )

@app.get("/api/v1/landsat8")
def get_landsat8_images(
    lat: float = Query(..., description="Latitude of the location."),
    lon: float = Query(..., description="Longitude of the location."),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)")
):
    """
    Get a timeline of Landsat 8 images for a specific location via a stream.
    Provides global coverage at 30m resolution with a long historical archive.
    Uses true color bands (Red, Green, Blue) from the Landsat 8 Collection 2 Tier 1 Real-Time data.
    """
    return StreamingResponse(
        landsat8_stream_generator(lat, lon, start_date, end_date),
        media_type="application/x-ndjson"
    )
