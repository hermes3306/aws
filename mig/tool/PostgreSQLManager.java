import java.sql.*;
import java.util.*;
import java.io.*;

public class PostgreSQLManager implements DatabaseManager {
    private final Properties config;

    public PostgreSQLManager(Properties config) {
        this.config = config;
    }

    private Connection getConnection() throws SQLException {
        String url = "jdbc:postgresql://" + config.getProperty("host") + ":" + config.getProperty("port") + "/" + config.getProperty("database");
        return DriverManager.getConnection(url, config.getProperty("user"), config.getProperty("password"));
    }

    @Override
    public void listAll() {
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")) {
            System.out.println("Current tables:");
            while (rs.next()) {
                System.out.println(rs.getString("table_name"));
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
        StringBuilder createTableSQL = new StringBuilder("CREATE TABLE IF NOT EXISTS " + tableName + " (");
        for (int i = 0; i < columnArr.length; i++) {
            createTableSQL.append(columnArr[i].trim()).append(" TEXT");
            if (i < columnArr.length - 1) {
                createTableSQL.append(", ");
            }
        }
        createTableSQL.append(")");

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {
            stmt.execute(createTableSQL.toString());
            System.out.println("Table '" + tableName + "' created in PostgreSQL.");
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

            StringBuilder createTableSQL = new StringBuilder("CREATE TABLE IF NOT EXISTS " + tableName + " (");
            for (int i = 0; i < columns.length; i++) {
                createTableSQL.append(columns[i].trim()).append(" TEXT");
                if (i < columns.length - 1) {
                    createTableSQL.append(", ");
                }
            }
            createTableSQL.append(")");

            try (Statement stmt = conn.createStatement()) {
                stmt.execute(createTableSQL.toString());
            }

            String insertSQL = "INSERT INTO " + tableName + " VALUES (" + String.join(",", Collections.nCopies(columns.length, "?")) + ")";
            try (PreparedStatement pstmt = conn.prepareStatement(insertSQL)) {
                while ((line = br.readLine()) != null) {
                    String[] values = line.split(",");
                    for (int i = 0; i < values.length; i++) {
                        pstmt.setString(i + 1, values[i]);
                    }
                    pstmt.executeUpdate();
                }
            }
            System.out.println("Data from '" + csvFile + "' uploaded to PostgreSQL table '" + tableName + "'.");
        } catch (IOException | SQLException e) {
            System.out.println("Error uploading CSV: " + e.getMessage());
        }
    }

    @Override
    public void downloadCSV(Scanner scanner) {
        System.out.print("Enter the table name to download: ");
        String tableName = scanner.nextLine();

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM " + tableName);
             FileWriter fw = new FileWriter(tableName + ".csv")) {

            ResultSetMetaData rsmd = rs.getMetaData();
            int columnCount = rsmd.getColumnCount();

            // Write header
            for (int i = 1; i <= columnCount; i++) {
                fw.append(rsmd.getColumnName(i));
                if (i < columnCount) {
                    fw.append(",");
                }
            }
            fw.append("\n");

            // Write data
            while (rs.next()) {
                for (int i = 1; i <= columnCount; i++) {
                    fw.append(rs.getString(i));
                    if (i < columnCount) {
                        fw.append(",");
                    }
                }
                fw.append("\n");
            }

            System.out.println("Table '" + tableName + "' downloaded as CSV.");
        } catch (SQLException | IOException e) {
            System.out.println("Error downloading CSV: " + e.getMessage());
        }
    }

    @Override
    public void deleteAll(Scanner scanner) {
        System.out.print("Are you sure you want to delete all data? (yes/no): ");
        String confirm = scanner.nextLine();
        if (confirm.equalsIgnoreCase("yes")) {
            try (Connection conn = getConnection();
                 Statement stmt = conn.createStatement()) {
                stmt.execute("DO $$ DECLARE r RECORD; BEGIN FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE'; END LOOP; END $$;");
                System.out.println("All tables have been dropped successfully.");
            } catch (SQLException e) {
                System.out.println("Error deleting all tables: " + e.getMessage());
            }
        } else {
            System.out.println("Operation cancelled.");
        }
    }

    @Override
    public void displayStructure(Scanner scanner) {
        System.out.print("Enter the table name to display its structure: ");
        String tableName = scanner.nextLine();

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT column_name, data_type, character_maximum_length FROM information_schema.columns WHERE table_name = '" + tableName + "' ORDER BY ordinal_position")) {

            System.out.println("\nStructure of table '" + tableName + "':");
            System.out.printf("%-30s %-20s %-10s\n", "Column Name", "Data Type", "Max Length");
            System.out.println("-".repeat(70));

            while (rs.next()) {
                String columnName = rs.getString("column_name");
                String dataType = rs.getString("data_type");
                String maxLength = rs.getString("character_maximum_length");
                maxLength = (maxLength == null) ? "N/A" : maxLength;
                System.out.printf("%-30s %-20s %-10s\n", columnName, dataType, maxLength);
            }
        } catch (SQLException e) {
            System.out.println("Error displaying structure: " + e.getMessage());
        }
    }

    @Override
    public void executeCustomQuery(Scanner scanner) {
        System.out.print("Enter your query: ");
        String query = scanner.nextLine();

        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(query)) {

            ResultSetMetaData rsmd = rs.getMetaData();
            int columnCount = rsmd.getColumnCount();

            // Print column names
            for (int i = 1; i <= columnCount; i++) {
                System.out.print(rsmd.getColumnName(i) + "\t");
            }
            System.out.println();

            // Print rows
            while (rs.next()) {
                for (int i = 1; i <= columnCount; i++) {
                    System.out.print(rs.getString(i) + "\t");
                }
                System.out.println();
            }
        } catch (SQLException e) {
            System.out.println("Error executing query: " + e.getMessage());
        }
    }

    @Override
    public void close() {
        // No need to close anything for PostgreSQL as we're using try-with-resources
    }
}