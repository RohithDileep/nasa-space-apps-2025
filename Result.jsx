import React, { useEffect, useState } from "react";
import axios from "axios";
import { useLocation, useNavigate } from "react-router-dom";
import "./Page.css";

export default function Result() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!state?.location || !state?.selectedCrop) {
      navigate("/");
      return;
    }

    const fetchData = async () => {
      try {
        setLoading(true);
        const res = await axios.post("/api/predict", {
          latitude: state.location.lat,
          longitude: state.location.lng,
          crop: state.selectedCrop,
        });
        setData(res.data);
      } catch (err) {
        console.error(err);
        setError("Failed to fetch prediction data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [state, navigate]);

  const getAccuracyColor = (accuracy) => {
    if (accuracy >= 80) return "#4CAF50"; // Green
    if (accuracy >= 60) return "#8BC34A"; // Light Green
    if (accuracy >= 40) return "#FFC107"; // Yellow
    return "#F44336"; // Red
  };

  const getScoreColor = (score) => {
    if (score >= 80) return "#4CAF50";
    if (score >= 60) return "#8BC34A";
    if (score >= 40) return "#FFC107";
    return "#F44336";
  };

  return (
    <div className="dashboard-container">
      <div className="planet-bg"></div>
      <h1 className="title">🌾 Crop Suitability Results</h1>

      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Analyzing crop suitability...</p>
        </div>
      ) : error ? (
        <div className="error-container">
          <p>❌ {error}</p>
          <button className="btn" onClick={() => navigate("/")}>
            ← Back to Map
          </button>
        </div>
      ) : (
        <div className="results-container">
          <div className="main-result-card">
            <div className="crop-header">
              <h2>{data?.crop_name}</h2>
              <div 
                className="accuracy-badge"
                style={{ backgroundColor: getAccuracyColor(data?.overall_accuracy) }}
              >
                {data?.overall_accuracy}% Suitability
              </div>
            </div>
            
            <div className="recommendation-card">
              <h3>📋 Recommendation</h3>
              <p className="recommendation-text">{data?.recommendation}</p>
            </div>

            <div className="growth-info">
              <div className="info-item">
                <span className="info-label">Growth Period:</span>
                <span className="info-value">{data?.survival_period}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Location:</span>
                <span className="info-value">
                  {state.location.lat.toFixed(4)}, {state.location.lng.toFixed(4)}
                </span>
              </div>
            </div>
          </div>

          <div className="scores-section">
            <h3>📊 Environmental Scores</h3>
            <div className="scores-grid">
              <div className="score-card">
                <div className="score-icon">🌡️</div>
                <div className="score-content">
                  <span className="score-label">Temperature</span>
                  <span 
                    className="score-value"
                    style={{ color: getScoreColor(data?.temperature_score) }}
                  >
                    {data?.temperature_score}%
                  </span>
                </div>
              </div>
              
              <div className="score-card">
                <div className="score-icon">🌧️</div>
                <div className="score-content">
                  <span className="score-label">Rainfall</span>
                  <span 
                    className="score-value"
                    style={{ color: getScoreColor(data?.rainfall_score) }}
                  >
                    {data?.rainfall_score}%
                  </span>
                </div>
              </div>
              
              <div className="score-card">
                <div className="score-icon">💧</div>
                <div className="score-content">
                  <span className="score-label">Humidity</span>
                  <span 
                    className="score-value"
                    style={{ color: getScoreColor(data?.humidity_score) }}
                  >
                    {data?.humidity_score}%
                  </span>
                </div>
              </div>
              
              <div className="score-card">
                <div className="score-icon">💨</div>
                <div className="score-content">
                  <span className="score-label">Wind</span>
                  <span 
                    className="score-value"
                    style={{ color: getScoreColor(data?.wind_score) }}
                  >
                    {data?.wind_score}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {data?.weather_summary && (
            <div className="weather-summary-card">
              <h3>🌤️ Weather Summary</h3>
              <div className="weather-grid">
                <div className="weather-item">
                  <span className="weather-label">Avg Temperature:</span>
                  <span className="weather-value">{data.weather_summary.avg_temperature}°C</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Total Rainfall:</span>
                  <span className="weather-value">{data.weather_summary.total_rainfall}mm</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Avg Humidity:</span>
                  <span className="weather-value">{data.weather_summary.avg_humidity}%</span>
                </div>
                <div className="weather-item">
                  <span className="weather-label">Max Wind:</span>
                  <span className="weather-value">{data.weather_summary.max_wind} km/h</span>
                </div>
              </div>
            </div>
          )}

          {data?.risk_factors && data.risk_factors.length > 0 && (
            <div className="risk-factors-card">
              <h3>⚠️ Risk Factors</h3>
              <ul className="risk-list">
                {data.risk_factors.map((risk, index) => (
                  <li key={index} className="risk-item">{risk}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <button className="btn back-btn" onClick={() => navigate("/")}>
        ← Back to Map Selection
      </button>
    </div>
  );
}
