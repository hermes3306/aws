import java.util.Scanner;
import java.io.Console;

public class DatabaseUtility {

    public static String getSecureInput(String prompt) {
        Console console = System.console();
        if (console == null) {
            Scanner scanner = new Scanner(System.in);
            System.out.print(prompt);
            return scanner.nextLine();
        } else {
            return new String(console.readPassword(prompt));
        }
    }

    public static void printDivider() {
        System.out.println("----------------------------------------");
    }

    public static void printHeader(String header) {
        printDivider();
        System.out.println(header);
        printDivider();
    }

    public static void confirmOperation(String operation) throws Exception {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Are you sure you want to " + operation + "? (yes/no): ");
        String confirmation = scanner.nextLine().trim().toLowerCase();
        if (!confirmation.equals("yes")) {
            throw new Exception("Operation cancelled by user.");
        }
    }

    public static void handleException(Exception e) {
        System.out.println("An error occurred: " + e.getMessage());
        e.printStackTrace();
    }
}