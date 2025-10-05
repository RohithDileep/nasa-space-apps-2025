from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
from datetime import datetime, timedelta
import math

app = Flask(__name__)
CORS(app)

# Weather API configuration (using OpenWeatherMap as example)
WEATHER_API_KEY = "302486dd16dac715e24801cb31a265d1"  # Replace with actual API key
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

# Crop database with growth requirements
CROP_DATABASE = {
    "rice": {
        "name": "Rice",
        "min_temp": 20,
        "max_temp": 35,
        "optimal_temp": 28,
        "min_rainfall": 1000,
        "max_rainfall": 2500,
        "optimal_rainfall": 1500,
        "min_humidity": 70,
        "max_humidity": 90,
        "growth_period_days": 120,
        "wind_tolerance": 20,  # km/h
        "cyclone_resistance": "low"
    },
    "wheat": {
        "name": "Wheat",
        "min_temp": 10,
        "max_temp": 25,
        "optimal_temp": 18,
        "min_rainfall": 500,
        "max_rainfall": 1000,
        "optimal_rainfall": 750,
        "min_humidity": 40,
        "max_humidity": 70,
        "growth_period_days": 150,
        "wind_tolerance": 30,
        "cyclone_resistance": "medium"
    },
    "corn": {
        "name": "Corn",
        "min_temp": 15,
        "max_temp": 30,
        "optimal_temp": 22,
        "min_rainfall": 600,
        "max_rainfall": 1200,
        "optimal_rainfall": 900,
        "min_humidity": 50,
        "max_humidity": 80,
        "growth_period_days": 100,
        "wind_tolerance": 25,
        "cyclone_resistance": "medium"
    },
    "tomato": {
        "name": "Tomato",
        "min_temp": 18,
        "max_temp": 30,
        "optimal_temp": 24,
        "min_rainfall": 400,
        "max_rainfall": 800,
        "optimal_rainfall": 600,
        "min_humidity": 60,
        "max_humidity": 85,
        "growth_period_days": 90,
        "wind_tolerance": 15,
        "cyclone_resistance": "low"
    },
    "potato": {
        "name": "Potato",
        "min_temp": 10,
        "max_temp": 25,
        "optimal_temp": 18,
        "min_rainfall": 300,
        "max_rainfall": 700,
        "optimal_rainfall": 500,
        "min_humidity": 60,
        "max_humidity": 80,
        "growth_period_days": 110,
        "wind_tolerance": 20,
        "cyclone_resistance": "medium"
    }
}

def get_weather_data(lat, lon, days=365):
    """Get historical weather data for a location"""
    try:
        # For demo purposes, we'll simulate weather data
        # In production, you would call actual weather APIs
        
        # More realistic weather simulation based on location
        # Temperature varies significantly by latitude and season
        if lat > 30:  # Northern regions (cooler)
            base_temp = 15 + (abs(lat - 45) * 0.8)
        elif lat < -20:  # Southern regions (cooler)
            base_temp = 12 + (abs(lat + 35) * 0.7)
        else:  # Tropical/subtropical regions (warmer)
            base_temp = 25 + (abs(lat - 15) * 0.6)
        
        # Rainfall varies by location (coastal vs inland, latitude)
        if abs(lon) > 100:  # Inland areas (less rainfall)
            base_rainfall = 400 + (abs(lat - 30) * 15)
        else:  # Coastal areas (more rainfall)
            base_rainfall = 800 + (abs(lat - 20) * 25)
        
        # Wind patterns vary by location
        base_wind = 8 + (abs(lat) * 0.3) + (abs(lon) * 0.1)
        
        weather_data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            
            # More realistic seasonal variations
            day_of_year = date.timetuple().tm_yday
            
            # Temperature with seasonal variation (more realistic)
            seasonal_temp = base_temp + 12 * math.sin(2 * math.pi * (day_of_year - 80) / 365)
            daily_variation = math.sin(2 * math.pi * i / 7) * 3  # Weekly pattern
            random_temp = (hash(str(lat) + str(lon) + str(i)) % 100 - 50) / 10  # Random variation
            
            # Rainfall with seasonal and random variation
            seasonal_rain = base_rainfall + 300 * math.sin(2 * math.pi * (day_of_year - 150) / 365)
            random_rain = (hash(str(lat) + str(lon) + str(i) + "rain") % 200 - 100)
            
            # Wind speed with realistic variation
            seasonal_wind = base_wind + 5 * math.sin(2 * math.pi * day_of_year / 365)
            daily_wind = math.sin(2 * math.pi * i / 3) * 2  # More frequent variation
            random_wind = (hash(str(lat) + str(lon) + str(i) + "wind") % 60 - 30) / 3
            
            # Humidity varies with temperature and season
            temp_factor = seasonal_temp + daily_variation + random_temp
            base_humidity = 70 - (temp_factor - 20) * 1.5  # Higher temp = lower humidity
            seasonal_humidity = base_humidity + 15 * math.sin(2 * math.pi * (day_of_year - 100) / 365)
            
            weather_data.append({
                "date": date.strftime("%Y-%m-%d"),
                "temperature": round(max(-10, min(45, seasonal_temp + daily_variation + random_temp)), 1),
                "rainfall": max(0, round(seasonal_rain + random_rain, 1)),
                "humidity": round(max(20, min(95, seasonal_humidity + (hash(str(i)) % 20 - 10))), 1),
                "wind_speed": round(max(0, min(50, seasonal_wind + daily_wind + random_wind)), 1),
                "cyclone_risk": "high" if (abs(lat) < 30 and random_wind > 10 and i % 100 < 8) else "low"
            })
        
        return weather_data
    except Exception as e:
        print(f"Error getting weather data: {e}")
        return []

def calculate_crop_suitability(crop_data, weather_data):
    """Calculate crop growth suitability based on weather conditions"""
    
    # Calculate averages and extremes from weather data
    avg_temp = sum(day["temperature"] for day in weather_data) / len(weather_data)
    avg_rainfall = sum(day["rainfall"] for day in weather_data) / len(weather_data)
    avg_humidity = sum(day["humidity"] for day in weather_data) / len(weather_data)
    avg_wind = sum(day["wind_speed"] for day in weather_data) / len(weather_data)
    
    max_wind = max(day["wind_speed"] for day in weather_data)
    cyclone_days = sum(1 for day in weather_data if day["cyclone_risk"] == "high")
    
    # Calculate suitability scores (0-100)
    temp_score = 0
    if crop_data["min_temp"] <= avg_temp <= crop_data["max_temp"]:
        temp_diff = abs(avg_temp - crop_data["optimal_temp"])
        temp_score = max(0, 100 - (temp_diff * 5))
    else:
        temp_score = 0
    
    rain_score = 0
    if crop_data["min_rainfall"] <= avg_rainfall <= crop_data["max_rainfall"]:
        rain_diff = abs(avg_rainfall - crop_data["optimal_rainfall"])
        rain_score = max(0, 100 - (rain_diff / 20))
    else:
        rain_score = 0
    
    humidity_score = 0
    if crop_data["min_humidity"] <= avg_humidity <= crop_data["max_humidity"]:
        humidity_diff = abs(avg_humidity - (crop_data["min_humidity"] + crop_data["max_humidity"]) / 2)
        humidity_score = max(0, 100 - (humidity_diff * 2))
    else:
        humidity_score = 0
    
    wind_score = 100
    if max_wind > crop_data["wind_tolerance"]:
        wind_score = max(0, 100 - ((max_wind - crop_data["wind_tolerance"]) * 3))
    
    cyclone_penalty = 0
    if cyclone_days > 10:
        cyclone_penalty = 20
    elif cyclone_days > 5:
        cyclone_penalty = 10
    
    # Calculate overall accuracy
    overall_score = (temp_score * 0.3 + rain_score * 0.3 + humidity_score * 0.2 + wind_score * 0.2) - cyclone_penalty
    overall_score = max(0, min(100, overall_score))
    
    return {
        "overall_accuracy": round(overall_score, 1),
        "temperature_score": round(temp_score, 1),
        "rainfall_score": round(rain_score, 1),
        "humidity_score": round(humidity_score, 1),
        "wind_score": round(wind_score, 1),
        "cyclone_penalty": cyclone_penalty,
        "recommendation": "Highly Suitable" if overall_score >= 80 else "Suitable" if overall_score >= 60 else "Moderately Suitable" if overall_score >= 40 else "Not Suitable",
        "survival_period": f"{crop_data['growth_period_days']} days",
        "risk_factors": get_risk_factors(crop_data, avg_temp, avg_rainfall, avg_humidity, max_wind, cyclone_days)
    }

def get_risk_factors(crop_data, avg_temp, avg_rainfall, avg_humidity, max_wind, cyclone_days):
    """Identify potential risk factors for crop growth"""
    risks = []
    
    if avg_temp < crop_data["min_temp"]:
        risks.append(f"Temperature too low (avg: {avg_temp:.1f}°C, min required: {crop_data['min_temp']}°C)")
    elif avg_temp > crop_data["max_temp"]:
        risks.append(f"Temperature too high (avg: {avg_temp:.1f}°C, max allowed: {crop_data['max_temp']}°C)")
    
    if avg_rainfall < crop_data["min_rainfall"]:
        risks.append(f"Insufficient rainfall (avg: {avg_rainfall:.1f}mm, min required: {crop_data['min_rainfall']}mm)")
    elif avg_rainfall > crop_data["max_rainfall"]:
        risks.append(f"Excessive rainfall (avg: {avg_rainfall:.1f}mm, max allowed: {crop_data['max_rainfall']}mm)")
    
    if avg_humidity < crop_data["min_humidity"]:
        risks.append(f"Low humidity (avg: {avg_humidity:.1f}%, min required: {crop_data['min_humidity']}%)")
    elif avg_humidity > crop_data["max_humidity"]:
        risks.append(f"High humidity (avg: {avg_humidity:.1f}%, max allowed: {crop_data['max_humidity']}%)")
    
    if max_wind > crop_data["wind_tolerance"]:
        risks.append(f"High wind speeds (max: {max_wind:.1f} km/h, tolerance: {crop_data['wind_tolerance']} km/h)")
    
    if cyclone_days > 5:
        risks.append(f"High cyclone risk ({cyclone_days} days with cyclone risk)")
    
    return risks

@app.route('/api/crops', methods=['GET'])
def get_crops():
    """Get list of available crops"""
    return jsonify({"crops": list(CROP_DATABASE.keys())})

@app.route('/api/crop-details/<crop_name>', methods=['GET'])
def get_crop_details(crop_name):
    """Get detailed information about a specific crop"""
    if crop_name not in CROP_DATABASE:
        return jsonify({"error": "Crop not found"}), 404
    
    return jsonify(CROP_DATABASE[crop_name])

@app.route('/api/predict', methods=['POST'])
def predict_crop_growth():
    """Predict crop growth suitability for a location"""
    try:
        data = request.get_json()
        lat = float(data['latitude'])
        lon = float(data['longitude'])
        crop_name = data['crop']
        
        if crop_name not in CROP_DATABASE:
            return jsonify({"error": "Crop not found"}), 404
        
        # Get weather data for the location
        weather_data = get_weather_data(lat, lon)
        
        if not weather_data:
            return jsonify({"error": "Unable to fetch weather data"}), 500
        
        # Calculate crop suitability
        crop_data = CROP_DATABASE[crop_name]
        prediction = calculate_crop_suitability(crop_data, weather_data)
        
        # Add location and crop info
        prediction.update({
            "location": {"latitude": lat, "longitude": lon},
            "crop": crop_name,
            "crop_name": crop_data["name"],
            "weather_summary": {
                "avg_temperature": round(sum(day["temperature"] for day in weather_data) / len(weather_data), 1),
                "total_rainfall": round(sum(day["rainfall"] for day in weather_data), 1),
                "avg_humidity": round(sum(day["humidity"] for day in weather_data) / len(weather_data), 1),
                "max_wind": max(day["wind_speed"] for day in weather_data),
                "cyclone_days": sum(1 for day in weather_data if day["cyclone_risk"] == "high")
            }
        })
        
        return jsonify(prediction)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weather/<lat>/<lon>', methods=['GET'])
def get_weather_summary(lat, lon):
    """Get weather summary for a location"""
    try:
        weather_data = get_weather_data(float(lat), float(lon), 30)  # Last 30 days
        
        if not weather_data:
            return jsonify({"error": "Unable to fetch weather data"}), 500
        
        summary = {
            "avg_temperature": round(sum(day["temperature"] for day in weather_data) / len(weather_data), 1),
            "total_rainfall": round(sum(day["rainfall"] for day in weather_data), 1),
            "avg_humidity": round(sum(day["humidity"] for day in weather_data) / len(weather_data), 1),
            "max_wind": max(day["wind_speed"] for day in weather_data),
            "cyclone_risk_days": sum(1 for day in weather_data if day["cyclone_risk"] == "high"),
            "recent_data": weather_data[:7]  # Last 7 days
        }
        
        return jsonify(summary)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
