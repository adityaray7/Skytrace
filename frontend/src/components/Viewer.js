import React from 'react';

const Viewer = ({ selectedImage, onClose }) => {
    if (!selectedImage) {
    return null;
  }

  // Stop propagation to prevent clicks inside the content from closing the viewer
  const handleContentClick = (e) => {
    e.stopPropagation();
  };

  return (
        <div className="viewer-backdrop" onClick={onClose}>
                <div className="viewer-content" onClick={handleContentClick}>
            <img src={selectedImage.thumbnail_url.replace('dimensions=256', 'dimensions=1024')} alt={`Full view from ${new Date(selectedImage.timestamp * 1000).toLocaleDateString()}`} />
            <div className="viewer-metadata">
                <p><strong>Date:</strong> {new Date(selectedImage.timestamp * 1000).toLocaleString()}</p>
                {selectedImage.cloud_cover !== undefined && (
                  <p><strong>Cloud Cover:</strong> {selectedImage.cloud_cover.toFixed(2)}%</p>
                )}
                <p><strong>Source:</strong> {selectedImage.source}</p>
            </div>
        </div>
    </div>
  );
};

export default Viewer;
