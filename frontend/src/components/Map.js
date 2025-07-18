import React, { useEffect, useRef, useState } from 'react';
import { Wrapper } from '@googlemaps/react-wrapper';

const Map = ({ onLocationSelect }) => {
  const ref = useRef(null);
  const [map, setMap] = useState();

  useEffect(() => {
    if (ref.current && !map) {
      setMap(new window.google.maps.Map(ref.current, {
        center: { lat: 34.0522, lng: -118.2437 }, // Default to Los Angeles
        zoom: 8,
        mapId: 'SKYTRACE_MAP_ID' // For advanced map styling
      }));
    }
  }, [ref, map]);

  useEffect(() => {
    if (map) {
      map.addListener('click', (e) => {
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        onLocationSelect({ lat, lng });
        new window.google.maps.Marker({
            position: e.latLng,
            map: map,
        });
      });
    }
  }, [map, onLocationSelect]);

  return <div ref={ref} id="map" style={{ height: '100%', width: '100%' }} />;
};

const MapWrapper = (props) => {
    return (
        <Wrapper apiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}>
            <Map {...props} />
        </Wrapper>
    )
}

export default MapWrapper;
