import React, { useState, useCallback, useRef } from 'react';
import Map from './components/Map';
import Timeline from './components/Timeline';
import Viewer from './components/Viewer';
import LogoImage from './components/LogoImage';
import './App.css';

function App() {
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // For the main overlay
  const [isStreaming, setIsStreaming] = useState(false);
  const [statusText, setStatusText] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [satelliteSource, setSatelliteSource] = useState('sentinel2'); // 'sentinel2', 'sentinel1', 'sentinel3', 'landsat8', or 'naip'
  const [timelineHeight, setTimelineHeight] = useState(250); // Default height in pixels
  const timelineRef = useRef(null);

  const handleResize = useCallback((e) => {
    if (timelineRef.current) {
      const newHeight = window.innerHeight - e.clientY;
      if (newHeight > 100 && newHeight < window.innerHeight * 0.8) { // Set min/max resize bounds
        setTimelineHeight(newHeight);
      }
    }
  }, []);

  const stopResize = useCallback(() => {
    window.removeEventListener('mousemove', handleResize);
    window.removeEventListener('mouseup', stopResize);
  }, [handleResize]);

  const startResize = useCallback(() => {
    window.addEventListener('mousemove', handleResize);
    window.addEventListener('mouseup', stopResize);
  }, [handleResize, stopResize]);

  // Handle search completion - just update the map position
  const handleSearchComplete = useCallback(({ lat, lng }) => {
    // Just update the map position without fetching images
    setStatusText('Location updated. Click on the map to view images.');
  }, []);

  // Handle location selection - fetch images for the selected location
  const handleLocationSelect = useCallback(async ({ lat, lng }) => {
    if (isLoading) return; // Prevent multiple clicks while loading
    
    setImages([]);
    setSelectedImage(null);
    setIsLoading(true);
    setIsStreaming(true);
    setStatusText('Fetching images...');
    
    try {
      // Choose the appropriate endpoint based on the selected satellite source
      let endpoint = 'images';
      if (satelliteSource === 'naip') {
        endpoint = 'high-res-images';
      } else if (satelliteSource === 'sentinel1') {
        endpoint = 'sentinel1';
      } else if (satelliteSource === 'sentinel2') {
        endpoint = 'sentinel2';
      } else if (satelliteSource === 'sentinel3') {
        endpoint = 'sentinel3';
      } else if (satelliteSource === 'landsat8') {
        endpoint = 'landsat8';
      }
      let apiUrl = `/api/v1/${endpoint}?lat=${lat}&lon=${lng}`;
      if (startDate) {
        apiUrl += `&start_date=${startDate}`;
      }
      if (endDate) {
        apiUrl += `&end_date=${endDate}`;
      }

      const response = await fetch(apiUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      // As soon as we get a response, we can remove the main loading overlay
      setIsLoading(false);
      setStatusText('Streaming images...');
      
      // Read the stream
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          setIsStreaming(false);
          setStatusText(`All ${images.length > 0 ? images.length : ''} images loaded.`);
          break;
        }
        
        // Decode and process the chunk
        const chunk = decoder.decode(value, { stream: true });
        const jsonObjects = chunk.split('\n').filter(s => s); // Split by newline and remove empty strings
        
        jsonObjects.forEach(objStr => {
          try {
            const image = JSON.parse(objStr);
            if (image.error) {
              console.error("Stream error:", image.error);
              setStatusText(`Error: ${image.error}`);
              return;
            }
            setImages(prevImages => [...prevImages, image]);
          } catch (e) {
            console.error("Failed to parse JSON object from stream:", objStr, e);
          }
        });
      }

    } catch (error) {
      console.error('Error fetching images stream:', error);
      setStatusText('Failed to fetch images. See console for details.');
    } finally {
      // This ensures loading indicators are turned off even if an error occurs mid-stream
      setIsLoading(false);
      setIsStreaming(false);
    }
  }, [startDate, endDate, satelliteSource]);

  const handleImageSelect = (image) => {
    setSelectedImage(image);
  };
  
  const closeViewer = () => {
    setSelectedImage(null);
  }

  return (
    <div className="App">
      <header className="App-header">
        <LogoImage size="xlarge" />
        <div className="header-subtitle">Satellite Imagery Timeline Explorer</div>
      </header>
      <main className="App-main">
        <div className="controls-container">
          <div className="date-filter">
            <label htmlFor="start-date">Start Date:</label>
            <input 
              type="date" 
              id="start-date" 
              value={startDate} 
              onChange={e => setStartDate(e.target.value)} 
            />
          </div>
          <div className="date-filter">
            <label htmlFor="end-date">End Date:</label>
            <input 
              type="date" 
              id="end-date" 
              value={endDate} 
              onChange={e => setEndDate(e.target.value)} 
            />
          </div>
          <div className="satellite-selector">
            <label htmlFor="satellite-source">Satellite:</label>
            <select
              id="satellite-source"
              value={satelliteSource}
              onChange={e => setSatelliteSource(e.target.value)}
            >
              <option value="sentinel2">Sentinel-2 (Optical, 10m)</option>
              <option value="sentinel1">Sentinel-1 (Radar, 10m, All-Weather)</option>
              <option value="landsat8">Landsat 8 (Optical, 30m, Historical)</option>
              <option value="sentinel3">Sentinel-3 (Ocean/Land, 300m)</option>
              <option value="naip">NAIP (US Only, 1m)</option>
            </select>
          </div>
        </div>
        <div className="map-container">
          <Map 
            onLocationSelect={handleLocationSelect}
            onSearchComplete={handleSearchComplete}
          />
          {isLoading && <div className='loading-overlay'>{statusText}</div>}
        </div>
        <div className="timeline-wrapper" ref={timelineRef} style={{ height: `${timelineHeight}px` }}>
          <div className="resize-handle" onMouseDown={startResize}></div>
          <Timeline images={images} onImageSelect={handleImageSelect} statusText={isStreaming ? statusText : ''} />
        </div>
      </main>
      {selectedImage && <Viewer selectedImage={selectedImage} onClose={closeViewer} />}
    </div>
  );
}

export default App;