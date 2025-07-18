import React from 'react';

const LogoImage = ({ className = '', size = 'medium' }) => {
  const sizeMap = {
    small: { width: 120, height: 40 },
    medium: { width: 180, height: 60 },
    large: { width: 280, height: 95 },
    xlarge: { width: 340, height: 115 }
  };

  const { width, height } = sizeMap[size];

  return (
    <div className={`logo ${className}`} style={{ width, height }}>
      <img 
        src="/logo.png" 
        alt="SkyTrace - Satellite Imagery Timeline Explorer"
        style={{ 
          width: '100%', 
          height: '100%', 
          objectFit: 'contain' 
        }}
      />
    </div>
  );
};

export default LogoImage;
