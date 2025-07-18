import ee
import os
import json
import asyncio
from typing import AsyncGenerator
from dotenv import load_dotenv

load_dotenv()

# Authenticate to Earth Engine
try:
    # Use service account credentials in a production environment
    if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
        ee.Initialize(project='your-gcp-project-id')
    else:
        ee.Initialize()
except Exception as e:
    print("Google Earth Engine authentication failed. Please run 'earthengine authenticate' or set up service account credentials.")

async def get_sentinel_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries Sentinel-2 images and yields them as a stream of JSON objects.
    """
    point = ee.Geometry.Point(lon, lat)
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR')
        .filterBounds(point)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    )

    # Apply date filters if provided
    if start_date:
        collection = collection.filterDate(start_date, ee.Date(start_date).advance(1, 'day') if not end_date else end_date)

    collection = collection.sort('system:time_start', False) # Newest first
    collection = collection.limit(50)

    image_list = collection.toList(collection.size())
    
    # The GEE toList call is blocking, so we run it in a thread to not block the event loop
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])
        
        timestamp = image_data['properties']['system:time_start'] / 1000
        
        # This is also a blocking call
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                'bands': ['B4', 'B3', 'B2'], # RGB
                'min': 0,
                'max': 3000,
                'dimensions': 512, 
                'region': point.buffer(500).bounds().getInfo()['coordinates']
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'Sentinel-2'
        }
        
        # Yield the result as a JSON string followed by a newline
        yield f"{json.dumps(result)}\n"