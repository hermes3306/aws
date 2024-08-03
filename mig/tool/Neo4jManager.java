import org.neo4j.driver.*;
import org.neo4j.driver.exceptions.Neo4jException;

import java.io.*;
import java.util.*;

public class Neo4jManager implements DatabaseManager, AutoCloseable {
    private final Driver driver;

    public Neo4jManager(Properties config) {
        String uri = config.getProperty("url");
        String user = config.getProperty("user");
        String password = config.getProperty("password");
        this.driver = GraphDatabase.driver(uri, AuthTokens.basic(user, password));
    }

    @Override
    public void listAll() {
        try (Session session = driver.session()) {
            Result result = session.run("CALL db.labels()");
            System.out.println("Current node labels:");
            while (result.hasNext()) {
                Record record = result.next();
                System.out.println(record.get("label").asString());
            }
        } catch (Neo4jException e) {
            System.out.println("Error listing labels: " + e.getMessage());
        }
    }

    @Override
    public void create(Scanner scanner) {
        System.out.print("Enter the node label: ");
        String label = scanner.nextLine();
        
        Map<String, Object> properties = new HashMap<>();
        while (true) {
            System.out.print("Enter property name (or press Enter to finish): ");
            String key = scanner.nextLine();
            if (key.isEmpty()) {
                break;
            }
            System.out.print("Enter value for " + key + ": ");
            String value = scanner.nextLine();
            properties.put(key, value);
        }

        try (Session session = driver.session()) {
            session.writeTransaction(tx -> {
                String query = "CREATE (n:" + label + " $props) RETURN n";
                tx.run(query, Values.parameters("props", properties));
                return null;
            });
            System.out.println("Node with label '" + label + "' created.");
        } catch (Neo4jException e) {
            System.out.println("Error creating node: " + e.getMessage());
        }
    }

    @Override
    public void uploadCSV(Scanner scanner) {
        System.out.print("Enter the CSV file name: ");
        String csvFile = scanner.nextLine();
        String label = csvFile.replace(".csv", "");

        try (BufferedReader br = new BufferedReader(new FileReader(csvFile));
             Session session = driver.session()) {
            String line = br.readLine();
            String[] headers = line.split(",");

            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                Map<String, Object> properties = new HashMap<>();
                for (int i = 0; i < headers.length; i++) {
                    properties.put(headers[i], values[i]);
                }

                session.writeTransaction(tx -> {
                    String query = "CREATE (n:" + label + " $props)";
                    tx.run(query, Values.parameters("props", properties));
                    return null;
                });
            }
            System.out.println("Data from '" + csvFile + "' uploaded as nodes with label '" + label + "'.");
        } catch (IOException | Neo4jException e) {
            System.out.println("Error uploading CSV: " + e.getMessage());
        }
    }

    @Override
    public void downloadCSV(Scanner scanner) {
        System.out.print("Enter the node label to download: ");
        String label = scanner.nextLine();

        try (Session session = driver.session();
             FileWriter fw = new FileWriter(label + ".csv")) {
            Result result = session.run("MATCH (n:" + label + ") RETURN properties(n) AS props");
            
            if (!result.hasNext()) {
                System.out.println("No nodes found with label '" + label + "'");
                return;
            }

            Record firstRecord = result.peek();
            List<String> keys = new ArrayList<>(firstRecord.get("props").asMap().keySet());

            // Write header
            fw.append(String.join(",", keys)).append("\n");

            // Write data
            while (result.hasNext()) {
                Record record = result.next();
                Map<String, Object> props = record.get("props").asMap();
                for (int i = 0; i < keys.size(); i++) {
                    fw.append(props.getOrDefault(keys.get(i), "").toString());
                    if (i < keys.size() - 1) {
                        fw.append(",");
                    }
                }
                fw.append("\n");
            }

            System.out.println("Nodes with label '" + label + "' downloaded as CSV.");
        } catch (IOException | Neo4jException e) {
            System.out.println("Error downloading CSV: " + e.getMessage());
        }
    }

    @Override
    public void deleteAll(Scanner scanner) {
        System.out.print("Are you sure you want to delete all nodes and relationships? (yes/no): ");
        String confirm = scanner.nextLine();
        if (confirm.equalsIgnoreCase("yes")) {
            try (Session session = driver.session()) {
                session.writeTransaction(tx -> {
                    tx.run("MATCH (n) DETACH DELETE n");
                    return null;
                });
                System.out.println("All nodes and relationships have been deleted.");
            } catch (Neo4jException e) {
                System.out.println("Error deleting all nodes: " + e.getMessage());
            }
        } else {
            System.out.println("Operation cancelled.");
        }
    }

    @Override
    public void displayStructure(Scanner scanner) {
        System.out.print("Enter the node label to display its structure: ");
        String label = scanner.nextLine();

        try (Session session = driver.session()) {
            Result result = session.run("MATCH (n:" + label + ") RETURN properties(n) AS props LIMIT 1");
            
            if (result.hasNext()) {
                Record record = result.next();
                Map<String, Object> props = record.get("props").asMap();

                System.out.println("\nStructure of nodes with label '" + label + "':");
                System.out.printf("%-30s %-20s\n", "Property Name", "Sample Value");
                System.out.println("-".repeat(50));

                for (Map.Entry<String, Object> entry : props.entrySet()) {
                    String sampleValue = entry.getValue().toString();
                    if (sampleValue.length() > 20) {
                        sampleValue = sampleValue.substring(0, 17) + "...";
                    }
                    System.out.printf("%-30s %-20s\n", entry.getKey(), sampleValue);
                }
            } else {
                System.out.println("No nodes found with label '" + label + "'");
            }
        } catch (Neo4jException e) {
            System.out.println("Error displaying structure: " + e.getMessage());
        }
    }

    @Override
    public void executeCustomQuery(Scanner scanner) {
        System.out.print("Enter your Cypher query: ");
        String query = scanner.nextLine();

        try (Session session = driver.session()) {
            Result result = session.run(query);
            
            if (!result.hasNext()) {
                System.out.println("Query executed successfully, but returned no results.");
                return;
            }

            List<String> keys = result.keys();
            
            // Print header
            for (String key : keys) {
                System.out.printf("%-20s", key);
            }
            System.out.println();

            // Print data
            while (result.hasNext()) {
                Record record = result.next();
                for (String key : keys) {
                    String value = record.get(key).toString();
                    if (value.length() > 20) {
                        value = value.substring(0, 17) + "...";
                    }
                    System.out.printf("%-20s", value);
                }
                System.out.println();
            }
        } catch (Neo4jException e) {
            System.out.println("Error executing query: " + e.getMessage());
        }
    }

    @Override
    public void close() {
        driver.close();
    }
}