import requests
import json
import csv
from datetime import datetime

# RunKeeper API 설정
BASE_URL = "https://api.runkeeper.com/fitnessActivities"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/vnd.com.runkeeper.FitnessActivity+json"
}

def get_activities():
    activities = []
    page = 0
    while True:
        response = requests.get(f"{BASE_URL}?page={page}", headers=headers)
        data = response.json()
        activities.extend(data['items'])
        if not data.get('next'):
            break
        page += 1
    return activities

def get_activity_details(uri):
    response = requests.get(f"{BASE_URL}{uri}", headers=headers)
    return response.json()

def save_activities_list(activities):
    with open('activities_list.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Type', 'Duration', 'Distance'])
        for activity in activities:
            writer.writerow([
                activity['start_time'],
                activity['type'],
                activity['duration'],
                activity.get('total_distance', 'N/A')
            ])

def save_gps_data(activity):
    filename = f"gps_data_{activity['start_time'].replace(':', '-')}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Latitude', 'Longitude', 'Altitude'])
        for point in activity.get('path', []):
            writer.writerow([
                point['timestamp'],
                point['latitude'],
                point['longitude'],
                point.get('altitude', 'N/A')
            ])

def main():
    print("Fetching activities...")
    activities = get_activities()
    
    print(f"Saving activities list ({len(activities)} activities)...")
    save_activities_list(activities)
    
    print("Fetching and saving GPS data for each activity...")
    for activity in activities:
        details = get_activity_details(activity['uri'])
        save_gps_data(details)
        print(f"Saved GPS data for activity on {activity['start_time']}")

    print("Data download complete!")

if __name__ == "__main__":
    main()