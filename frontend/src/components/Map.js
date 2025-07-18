import React, { useEffect, useRef, useState } from 'react';
import { Wrapper } from '@googlemaps/react-wrapper';

const Map = ({ onLocationSelect, onSearchComplete }) => {
  const ref = useRef(null);
  const [map, setMap] = useState();
  const [autocomplete, setAutocomplete] = useState(null);
  const searchInput = useRef(null);

  useEffect(() => {
    if (ref.current && !map) {
      const newMap = new window.google.maps.Map(ref.current, {
        center: { lat: 34.0522, lng: -118.2437 }, // Default to Los Angeles
        zoom: 8,
        mapId: 'SKYTRACE_MAP_ID', // For advanced map styling
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: true,
      });
      
      setMap(newMap);
      
      // Initialize Autocomplete
      const searchBox = new window.google.maps.places.SearchBox(searchInput.current);
      setAutocomplete(searchBox);
      
      // Listen for the event fired when the user selects a prediction
      searchBox.addListener('places_changed', () => {
        const places = searchBox.getPlaces();
        
        if (places.length === 0) {
          return;
        }
        
        // Get the first place
        const place = places[0];
        
        if (!place.geometry || !place.geometry.location) {
          console.error("Returned place contains no geometry");
          return;
        }
        
        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
          newMap.fitBounds(place.geometry.viewport);
        } else {
          newMap.setCenter(place.geometry.location);
          newMap.setZoom(12);  // Zoom in a bit
        }
        
        // Clear existing markers
        // markers.forEach(marker => marker.setMap(null));
        // markers = [];
        
        // Add a marker for the selected place
        new window.google.maps.Marker({
          map: newMap,
          position: place.geometry.location,
          title: place.name,
        });
        
        // Call the appropriate callback based on whether this is a search or a click
        const locationData = {
          lat: place.geometry.location.lat(),
          lng: place.geometry.location.lng()
        };
        
        if (onSearchComplete) {
          // For search, just update the map position
          onSearchComplete(locationData);
        } else if (onLocationSelect) {
          // For direct map clicks, process the location
          onLocationSelect(locationData);
        }
      });
    }
  }, [ref, map, onLocationSelect]);

  useEffect(() => {
    if (map) {
      // Add click listener to the map
      const clickListener = map.addListener('click', (e) => {
        const lat = e.latLng.lat();
        const lng = e.latLng.lng();
        onLocationSelect({ lat, lng });
        
        // Clear previous marker
        // if (marker) marker.setMap(null);
        
        // Add new marker
        new window.google.maps.Marker({
          position: e.latLng,
          map: map,
        });
      });
      
      // Clean up the event listener when component unmounts
      return () => {
        window.google.maps.event.removeListener(clickListener);
      };
    }
  }, [map, onLocationSelect]);

  return (
    <div style={{ position: 'relative', height: '100%', width: '100%' }}>
      <div style={{
        position: 'absolute',
        top: '20px',
        left: '50%',
        transform: 'translateX(-50%)',
        zIndex: 1,
        width: '90%',
        maxWidth: '500px'
      }}>
        <input
          ref={searchInput}
          type="text"
          placeholder="Search for a location..."
          style={{
            width: '100%',
            padding: '12px 16px',
            fontSize: '16px',
            border: 'none',
            borderRadius: '24px',
            boxShadow: '0 2px 10px rgba(0, 0, 0, 0.2)',
            outline: 'none',
            backgroundColor: 'var(--bg-secondary)',
            color: 'var(--text-primary)',
            border: '1px solid var(--border-color)'
          }}
        />
      </div>
      <div ref={ref} id="map" style={{ height: '100%', width: '100%' }} />
    </div>
  );
};

const MapWrapper = (props) => {
  return (
    <Wrapper 
      apiKey={process.env.REACT_APP_GOOGLE_MAPS_API_KEY}
      libraries={['places']}
    >
      <Map {...props} />
    </Wrapper>
  );
};

export default MapWrapper;
