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

def mask_s2_clouds(image):
    """Masks clouds and shadows in Sentinel-2 images using the QA60 band."""
    qa = image.select('QA60')
    
    # Bits 10 and 11 are clouds and cirrus, respectively
    cloud_bit_mask = 1 << 10
    cirrus_bit_mask = 1 << 11
    
    # Both flags should be set to zero, indicating clear conditions
    mask = qa.bitwiseAnd(cloud_bit_mask).eq(0).And(
           qa.bitwiseAnd(cirrus_bit_mask).eq(0))
    
    # Apply the scaling factor to the optical bands
    optical_bands = image.select('B.*')
    
    # Replace the original bands with the masked and scaled ones
    return image.updateMask(mask).addBands(optical_bands, None, True)

async def get_sentinel2_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries Sentinel-2 SR HARMONIZED images and yields them as a stream of JSON objects.
    Uses cloud masking and 10m resolution where available.
    """
    point = ee.Geometry.Point(lon, lat)
    
    # Use the HARMONIZED collection for consistency across time
    collection = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(point)
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
    )

    # Apply date filters if provided
    if start_date:
        end_date = end_date or ee.Date(start_date).advance(1, 'day')
        collection = collection.filterDate(start_date, end_date)

    # Sort by date (newest first) and limit results
    collection = collection.sort('system:time_start', False).limit(50)
    
    # Apply cloud masking
    collection = collection.map(mask_s2_clouds)

    # Get the list of images
    image_list = collection.toList(collection.size())
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])
        
        timestamp = image_data['properties']['system:time_start'] / 1000
        
        # Get thumbnail URL with 10m resolution settings
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                'bands': ['B4', 'B3', 'B2'],  # RGB
                'min': 0,
                'max': 3000,
                'dimensions': 512,  
                'region': point.buffer(500).bounds().getInfo()['coordinates'],
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'Sentinel-2'
        }
        
        yield f"{json.dumps(result)}\n"

async def get_high_res_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries high-resolution NAIP imagery and yields them as a stream of JSON objects.
    ⚠️ IMPORTANT: This dataset primarily covers the conterminous United States.
    """
    point = ee.Geometry.Point(lon, lat)

    # MODIFICATION 1: Use the NAIP high-resolution image collection
    collection = (
        ee.ImageCollection('USDA/NAIP/DOQQ')
        .filterBounds(point)
    )

    # Apply date filters if provided
    if start_date:
        end_date = end_date or ee.Date(start_date).advance(1, 'year') # NAIP is less frequent
        collection = collection.filterDate(start_date, end_date)

    # Sort by date (newest first) and limit results
    collection = collection.sort('system:time_start', False).limit(50)

    # MODIFICATION 2: Remove Sentinel-2 specific cloud masking
    # The .map(mask_s2_clouds) step is removed as NAIP does not have a QA60 band
    # and is generally processed to be cloud-free.

    # Get the list of images
    image_list = collection.toList(collection.size())
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])

        timestamp = image_data['properties']['system:time_start'] / 1000

        # Get thumbnail URL with parameters appropriate for NAIP
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                # MODIFICATION 3: Update band names for NAIP (R, G, B)
                'bands': ['R', 'G', 'B'],
                # MODIFICATION 4: Adjust visualization range for 8-bit data (0-255)
                'min': 0,
                'max': 255,
                'dimensions': 512,
                # Consider a smaller buffer to appreciate the 1m resolution
                'region': point.buffer(250).bounds().getInfo()['coordinates'],
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'NAIP' # Updated source
        }

        yield f"{json.dumps(result)}\n"

# --- NEW SENTINEL-1 FUNCTION ADDED BELOW ---

async def get_sentinel1_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries Sentinel-1 GRD imagery (10m res) and yields them as a stream.
    🌊 IMPORTANT: Uses Synthetic Aperture Radar (SAR), which sees through clouds/night.
    """
    point = ee.Geometry.Point(lon, lat)

    # Function to apply a simple speckle filter (Lee filter)
    def apply_speckle_filter(image):
        # Using a fixed 5x5 kernel for simplicity.
        # More advanced filtering might use different kernel sizes or algorithms.
        return image.focal_median(5, 'square', 'pixels') # Using focal_median for a simple, quick filter.

    # Use the Sentinel-1 GRD collection
    collection = (
        ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(point)
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) # Filter for VV polarization
        .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VH')) # Filter for VH polarization
        .filter(ee.Filter.eq('instrumentMode', 'IW')) # Select Interferometric Wide Swath mode
        .select(['VV', 'VH']) # Select VV and VH bands
        # Apply speckle filter - uncomment if you want to apply it
        # .map(apply_speckle_filter)
    )

    # Apply date filters if provided
    if start_date:
        # Sentinel-1 has frequent revisits, so a shorter default end_date is fine.
        end_date = end_date or ee.Date(start_date).advance(1, 'month')
        collection = collection.filterDate(start_date, end_date)

    # Sort by date (newest first) and limit results
    collection = collection.sort('system:time_start', False).limit(50)

    # Get the list of images
    image_list = collection.toList(collection.size())
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])

        timestamp = image_data['properties']['system:time_start'] / 1000

        # Get thumbnail URL with parameters appropriate for Sentinel-1
        # Map VV to Red and VH to Green/Blue for a common visualization
        # Min/Max values are for dB scale (log scale of backscatter)
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                'bands': ['VV', 'VH', 'VV'], # Common visualization: VV for Red, VH for Green, VV for Blue
                'min': -25,  # Typical minimum dB value
                'max': 0,    # Typical maximum dB value
                'dimensions': 512,
                'region': point.buffer(500).bounds().getInfo()['coordinates'], # Similar buffer to Sentinel-2
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'Sentinel-1' # Updated source
        }

        yield f"{json.dumps(result)}\n"


# --- NEW SENTINEL-3 FUNCTION ADDED BELOW ---

async def get_sentinel3_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries Sentinel-3 OLCI imagery (300m res) and yields them as a stream.
    🌍 IMPORTANT: Designed for ocean/large-scale land monitoring, much coarser resolution.
    """
    point = ee.Geometry.Point(lon, lat)

    # Use the Sentinel-3 OLCI Level-1 product collection (radiance values)
    collection = (
        ee.ImageCollection('COPERNICUS/S3/OLCI')
        .filterBounds(point)
    )

    # Apply date filters if provided
    if start_date:
        # Sentinel-3 has frequent revisits, so a shorter default end_date is fine.
        end_date = end_date or ee.Date(start_date).advance(1, 'month')
        collection = collection.filterDate(start_date, end_date)

    # Sort by date (newest first) and limit results
    collection = collection.sort('system:time_start', False).limit(50)

    # Get the list of images
    image_list = collection.toList(collection.size())
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])

        timestamp = image_data['properties']['system:time_start'] / 1000

        # Get thumbnail URL with parameters appropriate for Sentinel-3 OLCI
        # Using Oa08 (Red), Oa06 (Green), Oa04 (Blue) for a natural color view.
        # Min/Max values are typical for radiance in these bands.
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                'bands': ['Oa08_radiance', 'Oa06_radiance', 'Oa04_radiance'], # Red, Green, Blue bands
                'min': 0,    # Typical minimum radiance
                'max': 300,  # Typical maximum radiance (adjust if images appear too dark/bright)
                'dimensions': 512,
                # Use a larger buffer due to 300m resolution to show context
                'region': point.buffer(5000).bounds().getInfo()['coordinates'], # 5km buffer
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'Sentinel-3 OLCI' # Specific source to denote OLCI instrument
        }

        yield f"{json.dumps(result)}\n"

# --- LANDSAT 8 FUNCTION ---


async def get_landsat8_images_stream(lat: float, lon: float, start_date: str = None, end_date: str = None) -> AsyncGenerator[str, None]:
    """
    Queries Landsat 8 (LC08/C02/T1_RT) imagery (30m res) and yields them as a stream.
    🌎 Provides global coverage with a long historical archive.
    """
    point = ee.Geometry.Point(lon, lat)

    # Use the Landsat 8 Collection 2 Tier 1 Real-Time collection
    collection = (
        ee.ImageCollection('LANDSAT/LC08/C02/T1') # <--- This is where Landsat 8 is specified
        .filterBounds(point)
    )

    # Apply date filters if provided
    if start_date:
        end_date = end_date or ee.Date(start_date).advance(1, 'year')
        collection = collection.filterDate(start_date, end_date)

    # Select true color bands (B4=Red, B3=Green, B2=Blue)
    collection = collection.select(['B4', 'B3', 'B2'])

    # Sort by date (newest first) and limit results
    collection = collection.sort('system:time_start', False).limit(50)

    # Get the list of images
    image_list = collection.toList(collection.size())
    image_info_list = await asyncio.to_thread(image_list.getInfo)

    for image_data in image_info_list:
        image = ee.Image(image_data['id'])

        timestamp = image_data['properties']['system:time_start'] / 1000

        # Get thumbnail URL with parameters for Landsat 8 true color
        thumb_url = await asyncio.to_thread(
            image.getThumbUrl, {
                'bands': ['B4', 'B3', 'B2'],
                'min': 0.0,
                'max': 30000.0,
                'dimensions': 512,
                'region': point.buffer(1000).bounds().getInfo()['coordinates'],
            }
        )

        result = {
            'id': image_data['id'],
            'timestamp': timestamp,
            'thumbnail_url': thumb_url,
            'source': 'Landsat 8'
        }

        yield f"{json.dumps(result)}\n"