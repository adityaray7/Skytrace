import React from 'react';

const Logo = ({ className = '', size = 'medium' }) => {
  const sizeMap = {
    small: { width: 120, height: 40 },
    medium: { width: 180, height: 60 },
    large: { width: 240, height: 80 }
  };

  const { width, height } = sizeMap[size];

  return (
    <div className={`logo ${className}`} style={{ width, height }}>
      <svg
        viewBox="0 0 400 150"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: '100%', height: '100%' }}
      >
        {/* Satellite */}
        <g transform="translate(50, 20)">
          {/* Main body */}
          <rect x="20" y="30" width="40" height="25" rx="3" fill="#1a365d" />
          {/* Solar panels */}
          <rect x="5" y="25" width="15" height="35" rx="2" fill="#1a365d" />
          <rect x="60" y="25" width="15" height="35" rx="2" fill="#1a365d" />
          {/* Antenna */}
          <circle cx="65" cy="20" r="8" fill="#1a365d" />
          <rect x="63" y="20" width="4" height="15" fill="#1a365d" />
          {/* Communication dish */}
          <path d="M 10 50 Q 25 35 40 50" stroke="#1a365d" strokeWidth="3" fill="none" />
        </g>
        
        {/* Wave */}
        <path 
          d="M 120 80 Q 160 60 200 80 Q 240 100 280 80 Q 320 60 360 80" 
          stroke="#2563eb" 
          strokeWidth="4" 
          fill="none"
        />
        
        {/* Text */}
        <text x="80" y="130" fontFamily="Inter, -apple-system, sans-serif" fontSize="36" fontWeight="600" fill="#1a365d">
          SkyTrace
        </text>
      </svg>
    </div>
  );
};

export default Logo;
