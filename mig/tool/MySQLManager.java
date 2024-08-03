import java.sql.*;
import java.util.*;
import java.io.*;

public class MySQLManager implements DatabaseManager {
    private final Properties config;

    public MySQLManager(Properties config) {
        this.config = config;
    }

    private Connection getConnection() throws SQLException {
        String url = "jdbc:mysql://" + config.getProperty("host") + ":" + config.getProperty("port") + "/" + config.getProperty("database");
        return DriverManager.getConnection(url, config.getProperty("user"), config.getProperty("password"));
    }

    @Override
    public void listAll() {
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SHOW TABLES")) {
            System.out.println("Current tables:");
            while (rs.next()) {
                System.out.println(rs.getString(1));
            }
        } catch (SQLException e) {
            System.out.println("Error listing tables: " + e.getMessage());
        }
    }

    @Override
    public void create(Scanner scanner) {
        System.out.print("Enter the new table name: ");
        String tableName = scanner.nextLine();
        System.out.print("Enter column names (comma-separated): ");
        String columns = scanner.nextLine();

        String[] columnArr = columns.split(",");
        StringBuilder createTableSQL = new StringBuilder("CREATE TABLE IF NOT EXISTS `" + tableName + "` (");
        createTableSQL.append("id INT AUTO_INCREMENT PRIMARY KEY, ");
        for (int i = 0; i < columnArr.length; i++) {
            createTableSQL.append("`").append(columnArr[i].trim()).append("` TEXT");
            if (i < columnArr.length - 1) {
                createTableSQL.append(", ");
            }
        }
        createTableSQL.append(")");

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute(createTableSQL.toString());
            System.out.println("Table '" + tableName + "' created in MySQL.");
        } catch (SQLException e) {
            System.out.println("Error creating table: " + e.getMessage());
        }
    }

    @Override
    public void uploadCSV(Scanner scanner) {
        System.out.print("Enter the CSV file name: ");
        String csvFile = scanner.nextLine();
        String tableName = csvFile.replace(".csv", "");

        try (BufferedReader br = new BufferedReader(new FileReader(csvFile));
             Connection conn = getConnection()) {
            String line = br.readLine();
            String[] columns = line.split(",");

            StringBuilder createTableSQL = new StringBuilder("CREATE TABLE IF NOT EXISTS `" + tableName + "` (");
            createTableSQL.append("id INT AUTO_INCREMENT PRIMARY KEY, ");
            for (int i = 0; i < columns.length; i++) {
                createTableSQL.append("`").append(columns[i].trim()).append("` TEXT");
                if (i < columns.length - 1) {
                    createTableSQL.append(", ");
                }
            }
            createTableSQL.append(")");

            try (Statement stmt = conn.createStatement()) {
                stmt.execute(createTableSQL.toString());
            }

            String insertSQL = "INSERT INTO `" + tableName + "` (" + String.join(",", columns) + ") VALUES (" + String.join(",", Collections.nCopies(columns.