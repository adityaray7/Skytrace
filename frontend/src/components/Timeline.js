import React from 'react';

const Timeline = ({ images, onImageSelect, statusText }) => {
  // Display status text if provided, otherwise show the default empty message
  if (!images || images.length === 0) {
    return <div className="timeline-container empty">{statusText || 'Select a location on the map to see the timeline.'}</div>;
  }

  return (
    <div className="timeline-container">
      {statusText && <div className="timeline-status">{statusText}</div>}
      <div className="timeline">
        {images.map((image) => (
          <div key={image.id} className="timeline-item" onClick={() => onImageSelect(image)}>
            <img src={image.thumbnail_url} alt={`Sentinel-2 from ${new Date(image.timestamp * 1000).toLocaleDateString()}`} />
            <div className="timeline-date">{new Date(image.timestamp * 1000).toLocaleDateString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Timeline;
