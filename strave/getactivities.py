import http.server
import socketserver
import webbrowser
from urllib.parse import urlparse, parse_qs
import requests
import json
import os
import time

# Strava API settings
CLIENT_ID = "67174"
CLIENT_SECRET = "11deb64d5fc70d28aed865992a6792f28edce3c6"
REDIRECT_URI = "http://localhost:8000"
SCOPE = "activity:read_all"
AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"
TOKEN_URL = "https://www.strava.com/oauth/token"
ACTIVITIES_URL = "https://www.strava.com/api/v3/athlete/activities"

auth_code = None

class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urlparse(self.path).query
        query_components = parse_qs(query)
        if 'code' in query_components:
            auth_code = query_components['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization successful! You can close this window now.")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

def get_authorization():
    with socketserver.TCPServer(("", 8000), OAuthHandler) as httpd:
        print("Please authorize the app by visiting:", AUTH_URL)
        webbrowser.open(AUTH_URL)
        httpd.handle_request()
    
    if not auth_code:
        raise Exception("Failed to get authorization code")
    
    response = requests.post(TOKEN_URL, data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': auth_code,
        'grant_type': 'authorization_code'
    })
    if response.status_code != 200:
        raise Exception(f"Failed to get token: {response.content}")
    return response.json()['access_token']

def get_all_activities(access_token):
    all_activities = []
    page = 1
    per_page = 200

    while True:
        params = {'page': page, 'per_page': per_page}
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(ACTIVITIES_URL, headers=headers, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve activities: {response.content}")
        
        activities = response.json()
        if not activities:
            break
        
        all_activities.extend(activities)
        page += 1
        time.sleep(1)  # To avoid hitting rate limits

    return all_activities

def save_activities(activities):
    if not os.path.exists('strava_activities'):
        os.makedirs('strava_activities')
    
    for activity in activities:
        filename = f"strava_activities/activity_{activity['id']}.json"
        with open(filename, 'w') as f:
            json.dump(activity, f, indent=2)
        print(f"Saved activity {activity['id']} to {filename}")

def main():
    try:
        access_token = get_authorization()
        print("Authorization successful!")

        print("Retrieving all activities...")
        activities = get_all_activities(access_token)
        print(f"Retrieved {len(activities)} activities.")

        print("Saving activities...")
        save_activities(activities)

        print("All activities have been saved successfully!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()