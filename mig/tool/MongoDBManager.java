import com.mongodb.client.*;
import com.mongodb.client.model.Filters;
import org.bson.Document;
import org.bson.conversions.Bson;

import java.io.*;
import java.util.*;

public class MongoDBManager implements DatabaseManager, AutoCloseable {
    private final MongoClient mongoClient;
    private final MongoDatabase database;

    public MongoDBManager(Properties config) {
        String connectionString = String.format("mongodb+srv://%s:%s@%s/%s?retryWrites=true&w=majority",
                config.getProperty("user"),
                config.getProperty("password"),
                config.getProperty("host"),
                config.getProperty("database"));
        this.mongoClient = MongoClients.create(connectionString);
        this.database = mongoClient.getDatabase(config.getProperty("database"));
    }

    @Override
    public void listAll() {
        try {
            System.out.println("Current collections:");
            for (String collectionName : database.listCollectionNames()) {
                System.out.println(collectionName);
            }
        } catch (Exception e) {
            System.out.println("Error listing collections: " + e.getMessage());
        }
    }

    @Override
    public void create(Scanner scanner) {
        System.out.print("Enter the new collection name: ");
        String collectionName = scanner.nextLine();

        try {
            database.createCollection(collectionName);
            System.out.println("Collection '" + collectionName + "' created.");
        } catch (Exception e) {
            System.out.println("Error creating collection: " + e.getMessage());
        }
    }

    @Override
    public void uploadCSV(Scanner scanner) {
        System.out.print("Enter the CSV file name: ");
        String csvFile = scanner.nextLine();
        String collectionName = csvFile.replace(".csv", "");

        try (BufferedReader br = new BufferedReader(new FileReader(csvFile))) {
            String line = br.readLine();
            String[] headers = line.split(",");

            MongoCollection<Document> collection = database.getCollection(collectionName);

            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                Document doc = new Document();
                for (int i = 0; i < headers.length; i++) {
                    doc.append(headers[i], values[i]);
                }
                collection.insertOne(doc);
            }
            System.out.println("Data from '" + csvFile + "' uploaded to MongoDB collection '" + collectionName + "'.");
        } catch (IOException e) {
            System.out.println("Error uploading CSV: " + e.getMessage());
        }
    }

    @Override
    public void downloadCSV(Scanner scanner) {
        System.out.print("Enter the collection name to download: ");
        String collectionName = scanner.nextLine();

        try (FileWriter fw = new FileWriter(collectionName + ".csv")) {
            MongoCollection<Document> collection = database.getCollection(collectionName);
            
            // Get all field names from the collection
            Set<String> fieldNames = new HashSet<>();
            for (Document doc : collection.find().limit(100)) {
                fieldNames.addAll(doc.keySet());
            }
            fieldNames.remove("_id");  // Exclude the MongoDB-specific _id field
            List<String> headers = new ArrayList<>(fieldNames);

            // Write header
            fw.append(String.join(",", headers)).append("\n");

            // Write data
            for (Document doc : collection.find()) {
                for (int i = 0; i < headers.size(); i++) {
                    String value = doc.get(headers.get(i), "").toString();
                    fw.append(value.replace(",", "\\,"));  // Escape commas in the data
                    if (i < headers.size() - 1) {
                        fw.append(",");
                    }
                }
                fw.append("\n");
            }

            System.out.println("Collection '" + collectionName + "' downloaded as CSV.");
        } catch (IOException e) {
            System.out.println("Error downloading CSV: " + e.getMessage());
        }
    }

    @Override
    public void deleteAll(Scanner scanner) {
        System.out.print("Are you sure you want to delete all collections? (yes/no): ");
        String confirm = scanner.nextLine();
        if (confirm.equalsIgnoreCase("yes")) {
            try {
                for (String collectionName : database.listCollectionNames()) {
                    database.getCollection(collectionName).drop();
                }
                System.out.println("All collections have been dropped.");
            } catch (Exception e) {
                System.out.println("Error deleting all collections: " + e.getMessage());
            }
        } else {
            System.out.println("Operation cancelled.");
        }
    }

    @Override
    public void displayStructure(Scanner scanner) {
        System.out.print("Enter the collection name to display its structure: ");
        String collectionName = scanner.nextLine();

        try {
            MongoCollection<Document> collection = database.getCollection(collectionName);
            Document sampleDoc = collection.find().first();

            if (sampleDoc != null) {
                System.out.println("\nStructure of collection '" + collectionName + "':");
                System.out.printf("%-30s %-20s\n", "Field Name", "Sample Value");
                System.out.println("-".repeat(50));

                for (Map.Entry<String, Object> entry : sampleDoc.entrySet()) {
                    String fieldName = entry.getKey();
                    String sampleValue = entry.getValue().toString();
                    if (sampleValue.length() > 20) {
                        sampleValue = sampleValue.substring(0, 17) + "...";
                    }
                    System.out.printf("%-30s %-20s\n", fieldName, sampleValue);
                }
            } else {
                System.out.println("No documents found in collection '" + collectionName + "'");
            }
        } catch (Exception e) {
            System.out.println("Error displaying structure: " + e.getMessage());
        }
    }

    @Override
    public void executeCustomQuery(Scanner scanner) {
        System.out.println("Enter your MongoDB query (in JSON format):");
        String queryString = scanner.nextLine();
        System.out.print("Enter the collection name to query: ");
        String collectionName = scanner.nextLine();

        try {
            MongoCollection<Document> collection = database.getCollection(collectionName);
            Document queryDoc = Document.parse(queryString);
            
            FindIterable<Document> result = collection.find(queryDoc);

            for (Document doc : result) {
                System.out.println(doc.toJson());
            }
        } catch (Exception e) {
            System.out.println("Error executing query: " + e.getMessage());
        }
    }

    @Override
    public void close() {
        if (mongoClient != null) {
            mongoClient.close();
        }
    }
}