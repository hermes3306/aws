import java.util.Properties;
import java.util.Scanner;
import java.io.FileInputStream;
import java.io.IOException;

public class DatabaseManagerApplication {

    private static final String CONFIG_FILE = "db2.ini";

    public static void main(String[] args) {
        Properties config = loadConfig();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            try {
                DatabaseUtility.printHeader("Database Manager");
                System.out.println("1. PostgreSQL");
                System.out.println("2. MySQL");
                System.out.println("3. MongoDB");
                System.out.println("4. Neo4j");
                System.out.println("5. Redis");
                System.out.println("6. Exit");
                System.out.print("Choose a database type (1-6): ");

                int choice = Integer.parseInt(scanner.nextLine());

                if (choice == 6) {
                    break;
                }

                DatabaseManager manager = createDatabaseManager(choice, config);
                if (manager != null) {
                    handleDatabaseOperations(manager, scanner);
                }

            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a number.");
            } catch (Exception e) {
                DatabaseUtility.handleException(e);
            }
        }

        System.out.println("Thank you for using the Database Manager.");
        scanner.close();
    }

    private static Properties loadConfig() {
        Properties properties = new Properties();
        try (FileInputStream fis = new FileInputStream(CONFIG_FILE)) {
            properties.load(fis);
        } catch (IOException e) {
            System.out.println("Error loading configuration file: " + e.getMessage());
            System.exit(1);
        }
        return properties;
    }

    private static DatabaseManager createDatabaseManager(int choice, Properties config) {
        String dbType;
        switch (choice) {
            case 1: dbType = "postgresql"; break;
            case 2: dbType = "mysql"; break;
            case 3: dbType = "mongodb"; break;
            case 4: dbType = "neo4j"; break;
            case 5: dbType = "redis"; break;
            default:
                System.out.println("Invalid choice.");
                return null;
        }

        Properties dbConfig = new Properties();
        for (String key : config.stringPropertyNames()) {
            if (key.startsWith(dbType + ".")) {
                dbConfig.setProperty(key.substring(dbType.length() + 1), config.getProperty(key));
            }
        }

        switch (dbType) {
            case "postgresql": return new PostgreSQLManager(dbConfig);
            case "mysql": return new MySQLManager(dbConfig);
            case "mongodb": return new MongoDBManager(dbConfig);
            case "neo4j": return new Neo4jManager(dbConfig);
            case "redis": return new RedisManager(dbConfig);
            default: return null;
        }
    }

    private static void handleDatabaseOperations(DatabaseManager manager, Scanner scanner) {
        while (true) {
            try {
                DatabaseUtility.printHeader("Database Operations");
                System.out.println("1. List all tables/collections/keys");
                System.out.println("2. Create new table/collection/key");
                System.out.println("3. Upload CSV");
                System.out.println("4. Download as CSV");
                System.out.println("5. Delete all data");
                System.out.println("6. Display structure");
                System.out.println("7. Execute custom query");
                System.out.println("8. Return to main menu");
                System.out.print("Choose an operation (1-8): ");

                int choice = Integer.parseInt(scanner.nextLine());

                switch (choice) {
                    case 1: manager.listAll(); break;
                    case 2: manager.create(scanner); break;
                    case 3: manager.uploadCSV(scanner); break;
                    case 4: manager.downloadCSV(scanner); break;
                    case 5:
                        DatabaseUtility.confirmOperation("delete all data");
                        manager.deleteAll(scanner);
                        break;
                    case 6: manager.displayStructure(scanner); break;
                    case 7: manager.executeCustomQuery(scanner); break;
                    case 8: return;
                    default:
                        System.out.println("Invalid choice. Please try again.");
                }

            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a number.");
            } catch (Exception e) {
                DatabaseUtility.handleException(e);
            }
        }
    }
}