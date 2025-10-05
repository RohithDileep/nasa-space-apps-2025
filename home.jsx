import React, { useState, useEffect } from "react";
import MapSelector from "../components/MapSelector";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Page.css";

export default function Home() {
  const [location, setLocation] = useState(null);
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [weatherData, setWeatherData] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchCrops();
  }, []);

  const fetchCrops = async () => {
    try {
      const response = await axios.get('/api/crops');
      setCrops(response.data.crops);
    } catch (error) {
      console.error('Error fetching crops:', error);
    }
  };

  const handleLocationSelect = async (latlng) => {
    setLocation(latlng);
    
    // Fetch weather data for the selected location
    try {
      const response = await axios.get(`/api/weather/${latlng.lat}/${latlng.lng}`);
      setWeatherData(response.data);
    } catch (error) {
      console.error('Error fetching weather data:', error);
    }
  };

  const handlePredict = () => {
    if (!location || !selectedCrop) {
      alert("Please select both a location on the map and a crop!");
      return;
    }
    
    navigate("/result", { 
      state: { 
        location,
        selectedCrop,
        weatherData
      } 
    });
  };

  return (
    <div className="dashboard-container">
      <div className="planet-bg"></div>
      <h1 className="title">🌾 Smart Crop Suitability Dashboard</h1>
      
      <div className="content-container">
        <div className="map-section">
          <div className="map-container">
            <MapSelector onSelect={handleLocationSelect} />
          </div>
          
          {location && (
            <div className="location-display">
              <p className="coords">
                📍 Latitude: {location.lat.toFixed(4)}, Longitude: {location.lng.toFixed(4)}
              </p>
            </div>
          )}
        </div>

        <div className="controls-section">
          {weatherData && (
            <div className="weather-summary">
              <h3>🌤️ Weather Summary (Last 30 Days)</h3>
              <div className="weather-grid">
                <div className="weather-item">
                  <span className="weather-label">Avg Temperature:</span>
                  <span className="weather-value">{weatherData.avg_temperature}°C</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Total Rainfall:</span>
                  <span className="weather-value">{weatherData.total_rainfall}mm</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Avg Humidity:</span>
                  <span className="weather-value">{weatherData.avg_humidity}%</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Max Wind:</span>
                  <span className="weather-value">{weatherData.max_wind} km/h</span>
                </div>
              </div>
            </div>
          )}

          <div className="crop-selection">
            <h3>🌾 Select Crop</h3>
            <select 
              value={selectedCrop} 
              onChange={(e) => setSelectedCrop(e.target.value)}
              className="crop-select"
            >
              <option value="">Choose a crop...</option>
              {crops.map(crop => (
                <option key={crop} value={crop}>
                  {crop.charAt(0).toUpperCase() + crop.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <button className="btn predict-btn" onClick={handlePredict}>
            🚀 Predict Crop Suitability
          </button>
        </div>
      </div>
    </div>
  );
}
