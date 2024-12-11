import streamlit as st
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from datetime import datetime
import pickle
import time

# Flask App
app = Flask(__name__)
CORS(app)

# Load model
with open('models/trained_model.pkl', 'rb') as file:
    model = pickle.load(file)

def haversine(lat1, lon1, lat2, lon2):
    R = 3958.8
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        pickup_lat = data['pickup_latitude']
        pickup_lon = data['pickup_longitude']
        dropoff_lat = data['dropoff_latitude']
        dropoff_lon = data['dropoff_longitude']
        
        distance = haversine(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        
        current_date = datetime.now()
        model_input = np.array([[1, 1, distance, current_date.month, current_date.weekday(), current_date.hour]])
        
        log_predicted_duration = model.predict(model_input)[0]
        predicted_duration_seconds = np.expm1(log_predicted_duration)  
        predicted_duration_minutes = int(round(predicted_duration_seconds / 60))
        
        # Return result as JSON
        return jsonify({'predicted_duration_minutes': predicted_duration_minutes})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
def run_flask():
    app.run(port=5000)

# Replace this variable with your full D3 HTML code
D3_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NYC Taxi Trip Duration Predictor</title>
  <script src="https://d3js.org/d3.v7.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.6.2/axios.min.js"></script>
  <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f6f8fa;
      margin: 0;
      padding: 0;
    }

    h1 {
      text-align: center;
      padding: 20px 0;
      color: #333;
    }

    .container {
      max-width: 900px;
      margin: auto;
      padding: 20px;
    }

    .input-group {
      display: grid;
      grid-template-columns: 1fr;
      gap: 20px;
      margin-bottom: 20px;
    }

    .input-row {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .coordinates-display {
      font-size: 12px;
      color: #666;
      margin-top: 5px;
    }

    label {
      font-weight: bold;
    }

    input {
      padding: 10px;
      font-size: 16px;
      border: 1px solid #ccc;
      border-radius: 4px;
      width: 100%;
    }

    .button-group {
      display: flex;
      justify-content: center;
      gap: 20px;
      margin: 20px 0;
    }

    button {
      padding: 12px 20px;
      font-size: 16px;
      border: none;
      border-radius: 5px;
      cursor: pointer;
    }

    #predict-btn {
      background-color: #28a745;
      color: white;
    }

    #predict-btn:hover {
      background-color: #218838;
    }

    #clear-btn {
      background-color: #dc3545;
      color: white;
    }

    #clear-btn:hover {
      background-color: #c82333;
    }

    .instructions {
      text-align: center;
      color: #666;
      margin: 10px 0;
      font-style: italic;
    }

    #map {
      height: 600px;
      width: 800px;
      margin: auto;
      border: 1px solid #ccc;
    }

    .error {
      color: #dc3545;
      font-size: 14px;
      margin-top: 5px;
      text-align: center;
    }

    .leaflet-popup-content {
      font-size: 14px;
      font-weight: bold;
    }

    /* New pin marker style */
    .pin-marker {
      position: relative;
      width: 24px;
      height: 24px;
    }

    .pin-marker::after {
      content: '';
      position: absolute;
      width: 24px;
      height: 24px;
      background: currentColor;
      border-radius: 50% 50% 50% 0;
      transform: rotate(-45deg);
      left: 0;
      top: 0;
    }

    .pin-marker::before {
      content: '';
      position: absolute;
      width: 12px;
      height: 12px;
      background: white;
      border-radius: 50%;
      transform: rotate(-45deg);
      left: 6px;
      top: 6px;
      z-index: 1;
    }
  </style>
</head>
<body>
  <h1>NYC Taxi Trip Duration Predictor</h1>
  <div class="container">
    <div class="input-group">
      <div class="input-row">
        <label for="pickup-address">Pickup Address:</label>
        <input type="text" id="pickup-address" placeholder="Enter pickup address in NYC or click on map" />
        <div id="pickup-coords" class="coordinates-display"></div>
        <div id="pickup-error" class="error"></div>
      </div>
      <div class="input-row">
        <label for="dropoff-address">Dropoff Address:</label>
        <input type="text" id="dropoff-address" placeholder="Enter dropoff address in NYC or click on map" />
        <div id="dropoff-coords" class="coordinates-display"></div>
        <div id="dropoff-error" class="error"></div>
      </div>
    </div>
    <p class="instructions">You can either enter addresses above or click directly on the map to set pickup and dropoff points</p>
    <div class="button-group">
      <button id="predict-btn">Predict Duration</button>
      <button id="clear-btn">Clear</button>
    </div>
    <div id="result" class="error"></div>
    <div id="map"></div>
  </div>

  <script>
    let pickupMarker = null;
    let dropoffMarker = null;
    let routeLine = null;
    let tempLine = null;
    let pickupCoords = null;
    let dropoffCoords = null;
    let map;

    function initMap() {
      map = L.map('map').setView([40.7128, -74.0060], 12);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
      }).addTo(map);
    }

    initMap();

    function addMarker(lat, lng, isPickup) {
      const marker = L.marker([lat, lng], {
        icon: L.divIcon({
          className: 'custom-div-icon',
          html: `<div class="pin-marker" style="color: ${isPickup ? '#4CAF50' : '#f44336'}"></div>`,
          iconSize: [24, 24],
          iconAnchor: [12, 24],
          popupAnchor: [0, -20]
        })
      }).addTo(map);

      marker.bindPopup(isPickup ? 'Pickup' : 'Dropoff');
      return marker;
    }

    async function reverseGeocode(lat, lng) {
      try {
        const response = await axios.get('https://nominatim.openstreetmap.org/reverse', {
          params: {
            lat,
            lon: lng,
            format: 'json'
          },
          headers: {
            'Accept-Language': 'en'
          }
        });
        return response.data.display_name;
      } catch (error) {
        return 'Address not found';
      }
    }

    async function geocodeAddress(address) {
      try {
        const fullAddress = `${address}, New York City, NY`;
        const response = await axios.get('https://nominatim.openstreetmap.org/search', {
          params: {
            q: fullAddress,
            format: 'json',
            limit: 1
          },
          headers: {
            'Accept-Language': 'en'
          }
        });

        if (response.data && response.data.length > 0) {
          const result = response.data[0];
          return {
            lat: parseFloat(result.lat),
            lng: parseFloat(result.lon),
            display_name: result.display_name
          };
        }
        throw new Error('Address not found');
      } catch (error) {
        throw new Error('Failed to geocode address');
      }
    }

    function updateCoordinatesDisplay(type, lat, lng) {
      const displayElement = document.getElementById(`${type}-coords`);
      if (lat && lng) {
        displayElement.textContent = `Latitude: ${lat.toFixed(6)}, Longitude: ${lng.toFixed(6)}`;
      } else {
        displayElement.textContent = '';
      }
    }

    async function updateAddressInput(type, lat, lng) {
      const address = await reverseGeocode(lat, lng);
      document.getElementById(`${type}-address`).value = address;
    }

    function drawLine(start, end) {
      if (routeLine) {
        map.removeLayer(routeLine);
      }
      routeLine = L.polyline([start, end], {
        color: '#2196F3',
        weight: 3,
        opacity: 0.8
      }).addTo(map);
    }

    async function handleMapClick(e) {
      const lat = e.latlng.lat;
      const lng = e.latlng.lng;

      if (!pickupCoords) {
        if (pickupMarker) {
          map.removeLayer(pickupMarker);
        }
        pickupMarker = addMarker(lat, lng, true);
        pickupCoords = { lat, lng };
        updateCoordinatesDisplay('pickup', lat, lng);
        await updateAddressInput('pickup', lat, lng);
        document.getElementById('pickup-error').textContent = '';
      } else if (!dropoffCoords) {
        if (dropoffMarker) {
          map.removeLayer(dropoffMarker);
        }
        dropoffMarker = addMarker(lat, lng, false);
        dropoffCoords = { lat, lng };
        updateCoordinatesDisplay('dropoff', lat, lng);
        await updateAddressInput('dropoff', lat, lng);
        document.getElementById('dropoff-error').textContent = '';
        drawLine([pickupCoords.lat, pickupCoords.lng], [lat, lng]);
      } else {
        if (pickupMarker) map.removeLayer(pickupMarker);
        if (dropoffMarker) map.removeLayer(dropoffMarker);
        if (routeLine) map.removeLayer(routeLine);
        
        pickupMarker = addMarker(lat, lng, true);
        pickupCoords = { lat, lng };
        dropoffCoords = null;
        dropoffMarker = null;
        
        updateCoordinatesDisplay('pickup', lat, lng);
        await updateAddressInput('pickup', lat, lng);
        document.getElementById('pickup-error').textContent = '';
        document.getElementById('dropoff-address').value = '';
        document.getElementById('dropoff-coords').textContent = '';
      }
    }

    map.on('click', handleMapClick);

    async function getTripDuration(pickupLat, pickupLng, dropoffLat, dropoffLng) {
      try {
        const response = await fetch('http://127.0.0.1:5000/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            pickup_latitude: pickupLat,
            pickup_longitude: pickupLng,
            dropoff_latitude: dropoffLat,
            dropoff_longitude: dropoffLng
          }),
        });

        const data = await response.json();
        return data.predicted_duration_minutes;
      } catch (error) {
        throw new Error('Failed to predict trip duration');
      }
    }

    async function handleAddressInput(type) {
      const addressInput = document.getElementById(`${type}-address`);
      const errorElement = document.getElementById(`${type}-error`);
      const address = addressInput.value.trim();

      if (!address) {
        errorElement.textContent = 'Please enter an address';
        return;
      }

      try {
        const coords = await geocodeAddress(address);
        updateCoordinatesDisplay(type, coords.lat, coords.lng);

        if (type === 'pickup') {
          if (pickupMarker) map.removeLayer(pickupMarker);
          pickupMarker = addMarker(coords.lat, coords.lng, true);
          pickupCoords = { lat: coords.lat, lng: coords.lng };
          
          if (dropoffCoords) {
            drawLine([coords.lat, coords.lng], [dropoffCoords.lat, dropoffCoords.lng]);
          }
        } else {
          if (dropoffMarker) map.removeLayer(dropoffMarker);
          dropoffMarker = addMarker(coords.lat, coords.lng, false);
          dropoffCoords = { lat: coords.lat, lng: coords.lng };
          
          if (pickupCoords) {
            drawLine([pickupCoords.lat, pickupCoords.lng], [coords.lat, coords.lng]);
          }
        }

        errorElement.textContent = '';
        return coords;
      } catch (error) {
        errorElement.textContent = error.message;
        return null;
      }
    }

    document.getElementById('pickup-address').addEventListener('change', () => handleAddressInput('pickup'));
    document.getElementById('dropoff-address').addEventListener('change', () => handleAddressInput('dropoff'));

    document.getElementById('predict-btn').addEventListener('click', async function() {
      if (pickupCoords && dropoffCoords) {
        try {
          const duration = await getTripDuration(
            pickupCoords.lat,
            pickupCoords.lng,
            dropoffCoords.lat,
            dropoffCoords.lng
          );

          const midpoint = L.latLng(
            (pickupCoords.lat + dropoffCoords.lat) / 2,
            (pickupCoords.lng + dropoffCoords.lng) / 2
          );

          L.popup()
            .setLatLng(midpoint)
            .setContent(`${duration} min`)
            .openOn(map);

          document.getElementById('result').textContent = '';
        } catch (error) {
          document.getElementById('result').textContent = error.message;
        }
      } else {
        document.getElementById('result').textContent = 'Please set both pickup and dropoff points';
      }
    });

    document.getElementById('clear-btn').addEventListener('click', function() {
      document.getElementById('pickup-address').value = '';
      document.getElementById('dropoff-address').value = '';
      document.getElementById('pickup-coords').textContent = '';
      document.getElementById('dropoff-coords').textContent = '';
      document.getElementById('pickup-error').textContent = '';
      document.getElementById('dropoff-error').textContent = '';
      document.getElementById('result').textContent = '';
      
      if (pickupMarker) map.removeLayer(pickupMarker);
      if (dropoffMarker) map.removeLayer(dropoffMarker);
      if (routeLine) map.removeLayer(routeLine);
      
      pickupCoords = null;
      dropoffCoords = null;
      pickupMarker = null;
      dropoffMarker = null;
      routeLine = null;
    });
  </script>
</body>
</html>
"""

def main():
    st.set_page_config(page_title="NYC Taxi Trip Duration Predictor", layout="wide")
    
    
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    time.sleep(2)
    
    # Embed D3 visualization directly
    st.components.v1.html(D3_HTML, height=1200, scrolling=False)

if __name__ == "__main__":
    main()
