import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import webbrowser

# Strava API settings
CLIENT_ID = "67174"
REDIRECT_URI = "http://localhost:8000"
SCOPE = "activity:write,activity:read_all"

# Authorization URL
AUTH_URL = f"https://www.strava.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code&scope={SCOPE}"

# Global variable to store the authorization code
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
            print(f"Authorization Code: {auth_code}")
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"Authorization failed.")

def run_server():
    with socketserver.TCPServer(("", 8000), OAuthHandler) as httpd:
        print("Server started at http://localhost:8000")
        webbrowser.open(AUTH_URL)
        httpd.handle_request()  # Handle one request, then exit

if __name__ == "__main__":
    run_server()
    if auth_code:
        print("\nYou can now use this authorization code to request an access token.")
    else:
        print("\nFailed to obtain authorization code.")