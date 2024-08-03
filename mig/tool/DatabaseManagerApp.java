import java.util.Scanner;
import java.util.List;
import java.io.FileInputStream;
import java.util.Properties;

public class DatabaseManagerApp {
    public static void main(String[] args) {
        Properties config = loadConfig("db2.ini");
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("\nAvailable databases:");
            List<String> databases = config.stringPropertyNames().stream().toList();
            for (int i = 0; i < databases.size(); i++) {
                System.out.println((i + 1) + ". " + databases.get(i));
            }
            System.out.print("Choose a database (or 'q' to quit): ");
            String choice = scanner.nextLine();

            if (choice.equalsIgnoreCase("q")) {
                break;
            }

            try {
                int index = Integer.parseInt(choice) - 1;
                String dbLabel = databases.get(index);
                Properties dbConfig = getDbConfig(config, dbLabel);
                String dbType = dbConfig.getProperty("dbtype");

                DatabaseManager manager = createManager(dbType, dbConfig);
                if (manager != null) {
                    handleDatabaseOperations(manager, scanner);
                }
            } catch (NumberFormatException | IndexOutOfBoundsException e) {
                System.out.println("Invalid choice. Please try again.");
            }
        }

        scanner.close();
    }

    private static Properties loadConfig(String filename) {
        Properties prop = new Properties();
        try (FileInputStream fis = new FileInputStream(filename)) {
            prop.load(fis);
        } catch (Exception e) {
            System.out.println("Error loading configuration: " + e.getMessage());
        }
        return prop;
    }

    private static Properties getDbConfig(Properties config, String dbLabel) {
        Properties dbConfig = new Properties();
        for (String key : config.stringPropertyNames()) {
            if (key.startsWith(dbLabel + ".")) {
                String newKey = key.substring(dbLabel.length() + 1);
                dbConfig.setProperty(newKey, config.getProperty(key));
            }
        }
        return dbConfig;
    }

    private static DatabaseManager createManager(String dbType, Properties dbConfig) {
        switch (dbType.toLowerCase()) {
            case "postgresql":
                return new PostgreSQLManager(dbConfig);
            case "neo4j":
                return new Neo4jManager(dbConfig);
            case "mongodb":
                return new MongoDBManager(dbConfig);
            case "mysql":
                return new MySQLManager(dbConfig);
            case "redis":
                return new RedisManager(dbConfig);
            default:
                System.out.println("Unsupported database type: " + dbType);
                return null;
        }
    }

    private static void handleDatabaseOperations(DatabaseManager manager, Scanner scanner) {
        while (true) {
            displayMenu();
            String choice = scanner.nextLine();

            try {
                switch (choice) {
                    case "1":
                        manager.listAll();
                        break;
                    case "2":
                        manager.create(scanner);
                        break;
                    case "3":
                        manager.uploadCSV(scanner);
                        break;
                    case "4":
                        manager.downloadCSV(scanner);
                        break;
                    case "5":
                        manager.deleteAll(scanner);
                        break;
                    case "6":
                        manager.displayStructure(scanner);
                        break;
                    case "7":
                        manager.executeCustomQuery(scanner);
                        break;
                    case "8":
                        return;
                    default:
                        System.out.println("Invalid choice. Please try again.");
                }
            } catch (Exception e) {
                System.out.println("An error occurred: " + e.getMessage());
            }
        }
    }

    private static void displayMenu() {
        System.out.println("\n--- Database Manager ---");
        System.out.println("1. List all tables/labels/collections");
        System.out.println("2. Create a new table/node/collection");
        System.out.println("3. Upload CSV");
        System.out.println("4. Download as CSV");
        System.out.println("5. Delete all tables/nodes/collections");
        System.out.println("6. Display structure");
        System.out.println("7. Execute custom query");
        System.out.println("8. Exit");
        System.out.print("Enter your choice (1-8): ");
    }
}