import java.io.*;
import java.net.*;
import java.time.*;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;

import com.topografix.gpx.v1._1.*;
import javax.xml.bind.JAXBContext;
import javax.xml.bind.JAXBException;
import javax.xml.bind.Marshaller;
import org.apache.http.client.fluent.*;
import org.apache.http.client.methods.*;
import org.apache.http.entity.mime.*;
import org.apache.http.entity.mime.content.FileBody;
import org.apache.http.entity.mime.content.StringBody;

public class StravaUploader {

    private static final String CLIENT_ID = "67174";
    private static final String CLIENT_SECRET = "11deb64d5fc70d28aed865992a6792f28edce3c6";
    private static final String REDIRECT_URI = "http://localhost:8000";
    private static final String SCOPE = "activity:write,activity:read_all";

    private static final String AUTH_URL = String.format("https://www.strava.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=%s", CLIENT_ID, REDIRECT_URI, SCOPE);
    private static final String TOKEN_URL = "https://www.strava.com/oauth/token";
    private static final String UPLOAD_URL = "https://www.strava.com/api/v3/uploads";
    private static final String ACTIVITIES_URL = "https://www.strava.com/api/v3/activities";

    private static String authCode = null;

    public static void main(String[] args) {
        try {
            String accessToken = getAuthorization();
            System.out.println("Authorization successful!");

            System.out.println("Generating realistic 30-minute running route...");
            GPX gpx = generateRealisticRoute(30, 5);
            File gpxFile = saveGpxToFile(gpx);

            System.out.println("Checking for recent activities...");
            List<Map<String, Object>> recentActivities = getRecentActivities(accessToken);

            if (isDuplicateActivity(recentActivities, gpx)) {
                System.out.println("A similar activity already exists. Skipping upload to avoid duplication.");
                return;
            }

            System.out.println("Uploading activity to Strava...");
            String uploadId = uploadToStrava(accessToken, gpxFile);

            System.out.println("Checking upload status...");
            String activityId = checkUploadStatus(accessToken, uploadId);

            System.out.println("Retrieving activity details...");
            Map<String, Object> activityDetails = getActivityDetails(accessToken, activityId);

            System.out.println("\nActivity Details:");
            System.out.println("Name: " + activityDetails.get("name"));
            System.out.println("Type: " + activityDetails.get("type"));
            System.out.println("Distance: " + (Double.parseDouble(activityDetails.get("distance").toString()) / 1000) + " km");
            System.out.println("Moving Time: " + formatTime((Integer) activityDetails.get("moving_time")));
            System.out.println("Elapsed Time: " + formatTime((Integer) activityDetails.get("elapsed_time")));
            System.out.println("Total Elevation Gain: " + activityDetails.get("total_elevation_gain") + " meters");
            System.out.println("Start Date: " + activityDetails.get("start_date_local"));
            System.out.println("Activity URL: https://www.strava.com/activities/" + activityId);

            System.out.println("\nDisplaying activity details in web browser...");
            displayActivityInBrowser(activityDetails);

        } catch (Exception e) {
            System.err.println("An error occurred: " + e.getMessage());
        }
    }

    private static String getAuthorization() throws IOException {
        ServerSocket serverSocket = new ServerSocket(8000);
        Desktop.getDesktop().browse(URI.create(AUTH_URL));

        Socket clientSocket = serverSocket.accept();
        BufferedReader in = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
        String requestLine = in.readLine();
        serverSocket.close();

        String query = requestLine.split(" ")[1];
        authCode = URLDecoder.decode(query.split("=")[1], "UTF-8");

        if (authCode == null) {
            throw new RuntimeException("Failed to get authorization code");
        }

        Request request = Request.Post(TOKEN_URL)
                .bodyForm(
                        Form.form()
                                .add("client_id", CLIENT_ID)
                                .add("client_secret", CLIENT_SECRET)
                                .add("code", authCode)
                                .add("grant_type", "authorization_code")
                                .build());

        String response = request.execute().returnContent().asString();
        String accessToken = extractJsonField(response, "access_token");

        if (accessToken == null) {
            throw new RuntimeException("Failed to get access token");
        }

        return accessToken;
    }

    private static List<Map<String, Object>> getRecentActivities(String accessToken) throws IOException {
        String url = ACTIVITIES_URL + "?after=" + (System.currentTimeMillis() / 1000 - 86400) + "&per_page=30";
        String response = Request.Get(url)
                .addHeader("Authorization", "Bearer " + accessToken)
                .execute()
                .returnContent()
                .asString();

        return parseJsonArray(response);
    }

    private static boolean isDuplicateActivity(List<Map<String, Object>> recentActivities, GPX gpx) {
        // Custom implementation to check if the activity is a duplicate
        // based on recent activities and the GPX data provided
        return false;
    }

    private static GPX generateRealisticRoute(int durationMinutes, int intervalSeconds) {
        GPX gpx = new GPX();
        GPXTrk trk = new GPXTrk();
        gpx.getTrk().add(trk);
        GPXTrkSeg seg = new GPXTrkSeg();
        trk.getTrkseg().add(seg);

        LocalDateTime startTime = LocalDateTime.now().minusDays(new Random().nextInt(7));
        startTime = startTime.withHour(new Random().nextInt(15) + 6).withMinute(new Random().nextInt(60));

        double lat = 37.5185;
        double lon = 127.1230;
        double ele = 15.0;
        double pace = new Random().nextDouble() * (5.5 - 4.5) + 4.5;

        for (int i = 0; i < durationMinutes * 60; i += intervalSeconds) {
            LocalDateTime currentTime = startTime.plusSeconds(i);

            double angle = Math.toRadians(new Random().nextDouble() * 360);
            double distance = pace * intervalSeconds;
            lat += (distance / 111111) * Math.cos(angle);
            lon += (distance / (111111 * Math.cos(Math.toRadians(lat)))) * Math.sin(angle);
            ele += new Random().nextDouble() * 1 - 0.5;

            GPXTrkpt pt = new GPXTrkpt();
            pt.setLat(lat);
            pt.setLon(lon);
            pt.setEle(ele);
            pt.setTime(currentTime.format(DateTimeFormatter.ISO_DATE_TIME));
            seg.getTrkpt().add(pt);
        }

        return gpx;
    }

    private static File saveGpxToFile(GPX gpx) throws JAXBException, IOException {
        File file = File.createTempFile("activity", ".gpx");
        JAXBContext jaxbContext = JAXBContext.newInstance(GPX.class);
        Marshaller jaxbMarshaller = jaxbContext.createMarshaller();
        jaxbMarshaller.setProperty(Marshaller.JAXB_FORMATTED_OUTPUT, true);
        jaxbMarshaller.marshal(gpx, file);
        return file;
    }

    private static String uploadToStrava(String accessToken, File gpxFile) throws IOException {
        HttpEntity entity = MultipartEntityBuilder.create()
                .addPart("file", new FileBody(gpxFile))
                .addPart("data_type", new StringBody("gpx", ContentType.TEXT_PLAIN))
                .addPart("activity_type", new StringBody("run", ContentType.TEXT_PLAIN))
                .build();

        HttpPost uploadRequest = new HttpPost(UPLOAD_URL);
        uploadRequest.addHeader("Authorization", "Bearer " + accessToken);
        uploadRequest.setEntity(entity);

        String response = Request.Post(UPLOAD_URL)
                .addHeader("Authorization", "Bearer " + accessToken)
                .body(entity)
                .execute()
                .returnContent()
                .asString();

        return extractJsonField(response, "id");
    }

    private static String checkUploadStatus(String accessToken, String uploadId) throws IOException, InterruptedException {
        String url = UPLOAD_URL + "/" + uploadId;
        for (int i = 0; i < 60; i++) {
            String response = Request.Get(url)
                    .addHeader("Authorization", "Bearer " + accessToken)
                    .execute()
                    .returnContent()
                    .asString();

            String status = extractJsonField(response, "status");
            String error = extractJsonField(response, "error");

            if ("Your activity is ready.".equals(status)) {
                return extractJsonField(response, "activity_id");
            } else if (error != null) {
                throw new RuntimeException("Upload failed: " + error);
            }

            TimeUnit.SECONDS.sleep(5);
        }

        throw new RuntimeException("Upload processing timed out");
    }

    private static Map<String, Object> getActivityDetails(String accessToken, String activityId) throws IOException {
        String url = ACTIVITIES_URL + "/" + activityId;
        String response = Request.Get(url)
                .addHeader("Authorization", "Bearer " + accessToken)
                .execute()
                .returnContent()
                .asString();

        return parseJsonObject(response);
    }

    private static void displayActivityInBrowser(Map<String, Object> activityDetails) throws IOException {
        String htmlContent = String.format("""
            <html>
            <head>
                <title>Strava Activity Upload Result</title>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }
                    h1 { color: #FC4C02; }
                    .details { background-color: #f4f4f4; padding: 20px; border-radius: 5px; }
                </style>
            </head>
            <body>
                <h1>Activity Upload Successful!</h1>
                <div class="details">
                    <h2>Activity Details:</h2>
                    <p><strong>Name:</strong> %s</p>
                    <p><strong>Type:</strong> %s</p>
                    <p><strong>Distance:</strong> %.2f km</p>
                    <p><strong>Moving Time:</strong> %s</p>
                    <p><strong>Elapsed Time:</strong> %s</p>
                    <p><strong>Total Elevation Gain:</strong> %s meters</p>
                    <p><strong>Start Date:</strong> %s</p>
                    <p><strong>Activity URL:</strong> <a href="https://www.strava.com/activities/%s" target="_blank">View on Strava</a></p>
                </div>
            </body>
            </html>
            """,
                activityDetails.get("name"),
                activityDetails.get("type"),
                (Double.parseDouble(activityDetails.get("distance").toString()) / 1000),
                formatTime((Integer) activityDetails.get("moving_time")),
                formatTime((Integer) activityDetails.get("elapsed_time")),
                activityDetails.get("total_elevation_gain"),
                activityDetails.get("start_date_local"),
                activityDetails.get("id")
        );

        File htmlFile = File.createTempFile("activity_result", ".html");
        try (FileWriter writer = new FileWriter(htmlFile)) {
            writer.write(htmlContent);
        }

        Desktop.getDesktop().browse(htmlFile.toURI());
    }

    private static String extractJsonField(String json, String fieldName) {
        int startIndex = json.indexOf("\"" + fieldName + "\":") + fieldName.length() + 3;
        int endIndex = json.indexOf(",", startIndex);
        if (endIndex == -1) {
            endIndex = json.indexOf("}", startIndex);
        }
        String fieldValue = json.substring(startIndex, endIndex).replace("\"", "").trim();
        return fieldValue.equals("null") ? null : fieldValue;
    }

    private static List<Map<String, Object>> parseJsonArray(String json) {
        // Custom implementation to parse a JSON array
        return new ArrayList<>();
    }

    private static Map<String, Object> parseJsonObject(String json) {
        // Custom implementation to parse a JSON object
        return new HashMap<>();
    }

    private static String formatTime(int totalSeconds) {
        return String.format("%02d:%02d:%02d", totalSeconds / 3600, (totalSeconds % 3600) / 60, totalSeconds % 60);
    }
}
