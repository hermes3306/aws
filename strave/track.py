import os
from pathlib import Path
from dotenv import load_dotenv
import requests
import time
import webbrowser
from datetime import datetime
import gpxpy
import gpxpy.gpx
from urllib.parse import urlparse, parse_qs
import logging

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_env(path):
    with open(path, 'r') as file:
        for line in file:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

# Use absolute path to .env file
env_path = Path(__file__).resolve().parent / '.env'
print(f"Absolute path to .env: {env_path}")
print(f".env file exists: {env_path.exists()}")

if env_path.exists():
    load_env(env_path)
else:
    print("Error: .env file not found!")

# Debug prints
print("\nEnvironment variables loaded:")
print(f"STRAVA_CLIENT_ID: {os.getenv('STRAVA_CLIENT_ID')}")
print(f"STRAVA_CLIENT_SECRET: {os.getenv('STRAVA_CLIENT_SECRET')}")
print(f"STRAVA_REDIRECT_URI: {os.getenv('STRAVA_REDIRECT_URI')}")

# Strava API settings
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REDIRECT_URI = os.getenv('STRAVA_REDIRECT_URI', 'http://localhost')
SCOPE = "activity:write,activity:read_all"

AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}&approval_prompt=force"
TOKEN_URL = "https://www.strava.com/oauth/token"
UPLOAD_URL = "https://www.strava.com/api/v3/uploads"

print(f"\nValues used in the app:")
print(f"CLIENT_ID: {CLIENT_ID}")
print(f"REDIRECT_URI: {REDIRECT_URI}")
print(f"\nGenerated AUTH_URL: {AUTH_URL}")

class GPSTracker:
    def __init__(self):
        self.gpx = gpxpy.gpx.GPX()
        self.track = gpxpy.gpx.GPXTrack()
        self.segment = gpxpy.gpx.GPXTrackSegment()
        self.gpx.tracks.append(self.track)
        self.track.segments.append(self.segment)
        self.start_time = None

    def start_tracking(self):
        self.start_time = datetime.now()

    def add_point(self, lat, lon, ele=None):
        if self.start_time:
            point = gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon, elevation=ele, time=datetime.now())
            self.segment.points.append(point)

    def stop_tracking(self):
        return self.gpx.to_xml()

class MockGPS:
    def __init__(self):
        self.lat = 37.7749  # Starting latitude (San Francisco)
        self.lon = -122.4194  # Starting longitude
        self.on_location_callback = None

    def configure(self, on_location):
        self.on_location_callback = on_location

    def start(self, minTime, minDistance):
        Clock.schedule_interval(self._update_location, 1)  # Update every second

    def stop(self):
        Clock.unschedule(self._update_location)

    def _update_location(self, dt):
        # Simulate movement
        self.lat += 0.0001
        self.lon += 0.0001
        if self.on_location_callback:
            self.on_location_callback(lat=self.lat, lon=self.lon)

class RunTrackerApp(App):
    def build(self):
        self.access_token = None
        self.is_tracking = False
        self.gps_tracker = GPSTracker()
        self.gps = MockGPS()
        
        layout = BoxLayout(orientation='vertical')
        self.status_label = Label(text="Ready to authenticate")
        self.auth_button = Button(text="Authenticate with Strava", on_press=self.start_auth)
        self.auth_input = TextInput(hint_text="Paste the full callback URL here")
        self.auth_submit = Button(text="Submit Auth Code", on_press=self.complete_auth)
        self.toggle_button = Button(text="Start Tracking", on_press=self.toggle_tracking)
        self.upload_button = Button(text="Upload to Strava", on_press=self.upload_to_strava)
        
        layout.add_widget(self.status_label)
        layout.add_widget(self.auth_button)
        layout.add_widget(self.auth_input)
        layout.add_widget(self.auth_submit)
        layout.add_widget(self.toggle_button)
        layout.add_widget(self.upload_button)
        
        return layout

    def start_auth(self, instance):
        logger.info(f"Opening auth URL: {AUTH_URL}")
        webbrowser.open(AUTH_URL)
        self.status_label.text = "Strava auth page opened. Please authorize and paste the FULL callback URL here."

    def complete_auth(self, instance):
        full_url = self.auth_input.text.strip()
        if not full_url:
            self.status_label.text = "Please enter the full callback URL"
            return

        try:
            code = self.extract_code_from_url(full_url)
            if not code:
                self.status_label.text = "Failed to extract authorization code from URL"
                return

            logger.info(f"Extracted code: {code}")
            token_response = self.exchange_code_for_token(code)
            if token_response:
                self.access_token = token_response['access_token']
                self.status_label.text = f"Authentication successful! Token: {self.access_token[:10]}..."
                logger.info("Authentication successful")
            else:
                self.status_label.text = "Failed to obtain access token. Please try again."
        except Exception as e:
            logger.exception("Error during authentication")
            self.status_label.text = f"Authentication error: {str(e)}"

    def extract_code_from_url(self, url):
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        return query_params.get('code', [None])[0]

    def exchange_code_for_token(self, code):
        data = {
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code,
            'grant_type': 'authorization_code'
        }
        logger.info(f"Sending token request with data: {data}")
        response = requests.post(TOKEN_URL, data=data)
        logger.info(f"Token response status: {response.status_code}")
        logger.info(f"Token response content: {response.text}")
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Token exchange failed. Status: {response.status_code}, Response: {response.text}")
            return None

    def toggle_tracking(self, instance):
        if not self.is_tracking:
            self.start_tracking()
        else:
            self.stop_tracking()

    def start_tracking(self):
        self.is_tracking = True
        self.toggle_button.text = "Stop Tracking"
        self.status_label.text = "Tracking..."
        self.gps_tracker.start_tracking()
        self.gps.configure(on_location=self.on_location)
        self.gps.start(minTime=1000, minDistance=1)

    def stop_tracking(self):
        self.is_tracking = False
        self.toggle_button.text = "Start Tracking"
        self.status_label.text = "Tracking stopped"
        self.gps.stop()
        self.gpx_data = self.gps_tracker.stop_tracking()

    def on_location(self, **kwargs):
        lat = kwargs.get('lat', 0)
        lon = kwargs.get('lon', 0)
        self.gps_tracker.add_point(lat, lon)
        self.status_label.text = f"Location: {lat}, {lon}"


    def upload_to_strava(self, instance):
        if not hasattr(self, 'gpx_data'):
            self.status_label.text = "No tracking data to upload"
            return

        if not self.access_token:
            self.status_label.text = "Please authenticate with Strava first"
            return

        files = {'file': ('activity.gpx', self.gpx_data)}
        data = {
            'data_type': 'gpx',
            'activity_type': 'run'
        }
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.post(UPLOAD_URL, files=files, data=data, headers=headers)
        if response.status_code == 201:
            upload_response = response.json()
            self.status_label.text = "Activity uploaded to Strava! Fetching details..."
            self.fetch_and_display_activity(upload_response['id'])
        else:
            self.status_label.text = f"Upload failed: {response.content}"

    def fetch_and_display_activity(self, upload_id):
        # Poll the upload status until it's complete
        for _ in range(60):  # Try for up to 60 seconds
            status_response = requests.get(
                f"https://www.strava.com/api/v3/uploads/{upload_id}",
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
            if status_response.status_code == 200:
                status = status_response.json()
                if status['activity_id']:
                    self.display_activity_result(status['activity_id'])
                    return
            time.sleep(1)
        
        self.status_label.text = "Timed out waiting for activity to process"

    def display_activity_result(self, activity_id):
        # Fetch the activity details
        activity_url = f"https://www.strava.com/api/v3/activities/{activity_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(activity_url, headers=headers)
        
        if response.status_code == 200:
            activity = response.json()
            
            # Create a popup to display the results
            content = BoxLayout(orientation='vertical', padding=10, spacing=10)
            content.add_widget(Label(text=f"Activity: {activity['name']}"))
            content.add_widget(Label(text=f"Distance: {activity['distance']/1000:.2f} km"))
            content.add_widget(Label(text=f"Duration: {activity['moving_time']/60:.0f} minutes"))
            content.add_widget(Label(text=f"Elevation Gain: {activity['total_elevation_gain']} meters"))
            
            view_button = Button(text="View on Strava", size_hint=(1, 0.2))
            view_button.bind(on_press=lambda x: webbrowser.open(f"https://www.strava.com/activities/{activity_id}"))
            content.add_widget(view_button)
            
            close_button = Button(text="Close", size_hint=(1, 0.2))
            popup = Popup(title="Activity Uploaded Successfully", 
                          content=content,
                          size_hint=(0.8, 0.8))
            close_button.bind(on_press=popup.dismiss)
            content.add_widget(close_button)
            
            popup.open()
        else:
            self.status_label.text = f"Failed to fetch activity details: {response.content}"


if __name__ == '__main__':
    RunTrackerApp().run()