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

  const handleLocationSelect = useCallback(async ({ lat, lng }) => {
    // Reset state for new selection
    setImages([]);
    setSelectedImage(null);
    setIsLoading(true);
    setIsStreaming(true);
    setStatusText('Fetching image list...');

    try {
      let apiUrl = `/api/v1/images?lat=${lat}&lon=${lng}`;
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
  }, [startDate, endDate]);

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
        </div>
        <div className="map-container">
          <Map onLocationSelect={handleLocationSelect} />
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