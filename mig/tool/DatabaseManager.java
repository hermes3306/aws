import java.util.Scanner;

public interface DatabaseManager {
    void listAll();
    void create(Scanner scanner);
    void uploadCSV(Scanner scanner);
    void downloadCSV(Scanner scanner);
    void deleteAll(Scanner scanner);
    void displayStructure(Scanner scanner);
    void executeCustomQuery(Scanner scanner);
    void close();
}