import requests
import sqlite3
import pandas as pd
from datetime import datetime
from pricing_model import train_model, predict_price

DATABASE = 'dynamic_pricing.db'
WEATHER_API_KEY = 'YOUR_WEATHER_API_KEY'
ARTIST_TREND_API = 'https://api.artisttrends.com/latest'
TICKET_SALES_API = 'https://api.ticketingsystem.com/sales'

def get_weather_data(event_date, location):
    url = f"http://api.weather.com/v3/wx/conditions/current?apiKey={WEATHER_API_KEY}&geocode={location}&format=json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching weather data")
        return {}

def get_artist_trends(artist_name):
    response = requests.get(f"{ARTIST_TREND_API}?artist={artist_name}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching artist trend data")
        return {}

def get_ticket_sales(event_id):
    response = requests.get(f"{TICKET_SALES_API}?event_id={event_id}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching ticket sales data")
        return {}

def insert_data(conn, table, data_dict):
    placeholders = ', '.join(['?'] * len(data_dict))
    cols = ', '.join(data_dict.keys())
    sql = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
    conn.execute(sql, tuple(data_dict.values()))
    conn.commit()

def ingest_data():
    conn = sqlite3.connect(DATABASE)
    event_id = 123
    event_date = '2025-07-01'
    location = "40.7128,-74.0060"
    artist_name = "Popular Artist"
    sales_data = get_ticket_sales(event_id)
    weather_data = get_weather_data(event_date, location)
    trend_data = get_artist_trends(artist_name)
    event_data = {"event_id": event_id, "event_date": event_date, "location": location, "artist": artist_name}
    insert_data(conn, "events", event_data)
    sales_record = {"event_id": event_id, "sales": sales_data.get("tickets_sold", 0), "recorded_at": datetime.utcnow().isoformat()}
    insert_data(conn, "sales", sales_record)
    external_factor = {"event_id": event_id, "weather": weather_data.get("condition", "Unknown"), "temperature": weather_data.get("temperature", 0), "artist_trend_score": trend_data.get("trend_score", 0)}
    insert_data(conn, "external_factors", external_factor)
    conn.close()

def main():
    ingest_data()
    conn = sqlite3.connect(DATABASE)
    query = "SELECT s.sales, ef.temperature, ef.artist_trend_score FROM sales s JOIN external_factors ef ON s.event_id = ef.event_id"
    df = pd.read_sql(query, conn)
    conn.close()
    if df.empty:
        print("No data available for training.")
        return
    features = df[['temperature', 'artist_trend_score']]
    target = df['sales']
    model = train_model(features, target)
    features_input = [[75, 0.8]]
    predicted_sales = predict_price(model, features_input)
    print(f"Predicted optimal sales volume: {predicted_sales}")

if __name__ == "__main__":
    main() 
