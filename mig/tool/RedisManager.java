import redis.clients.jedis.*;
import redis.clients.jedis.exceptions.JedisException;

import java.util.*;
import java.io.*;

public class RedisManager implements DatabaseManager, AutoCloseable {
    private final JedisPool pool;

    public RedisManager(Properties config) {
        JedisPoolConfig poolConfig = new JedisPoolConfig();
        poolConfig.setMaxTotal(10);
        poolConfig.setMaxIdle(5);
        poolConfig.setMinIdle(1);
        poolConfig.setTestOnBorrow(true);
        poolConfig.setTestOnReturn(true);
        poolConfig.setTestWhileIdle(true);

        this.pool = new JedisPool(poolConfig, 
                                  config.getProperty("host"),
                                  Integer.parseInt(config.getProperty("port")),
                                  Protocol.DEFAULT_TIMEOUT,
                                  config.getProperty("password"),
                                  config.getProperty("user"),
                                  true);  // SSL enabled
    }

    @Override
    public void listAll() {
        try (Jedis jedis = pool.getResource()) {
            Set<String> keys = jedis.keys("*");
            System.out.println("Current keys:");
            for (String key : keys) {
                System.out.println(key);
            }
        } catch (JedisException e) {
            System.out.println("Error listing keys: " + e.getMessage());
        }
    }

    @Override
    public void create(Scanner scanner) {
        System.out.print("Enter the key: ");
        String key = scanner.nextLine();
        System.out.print("Enter the value: ");
        String value = scanner.nextLine();

        try (Jedis jedis = pool.getResource()) {
            jedis.set(key, value);
            System.out.println("Key-value pair created.");
        } catch (JedisException e) {
            System.out.println("Error creating key-value pair: " + e.getMessage());
        }
    }

    @Override
    public void uploadCSV(Scanner scanner) {
        System.out.print("Enter the CSV file name: ");
        String csvFile = scanner.nextLine();

        try (BufferedReader br = new BufferedReader(new FileReader(csvFile));
             Jedis jedis = pool.getResource()) {
            String line;
            while ((line = br.readLine()) != null) {
                String[] values = line.split(",");
                if (values.length >= 2) {
                    jedis.set(values[0], values[1]);
                }
            }
            System.out.println("Data from '" + csvFile + "' uploaded to Redis.");
        } catch (IOException | JedisException e) {
            System.out.println("Error uploading CSV: " + e.getMessage());
        }
    }

    @Override
    public void downloadCSV(Scanner scanner) {
        System.out.print("Enter the pattern to match keys (e.g., user:*): ");
        String pattern = scanner.nextLine();

        try (Jedis jedis = pool.getResource();
             FileWriter fw = new FileWriter(pattern.replace("*", "all") + ".csv")) {
            Set<String> keys = jedis.keys(pattern);
            for (String key : keys) {
                String value = jedis.get(key);
                fw.append(key).append(",").append(value).append("\n");
            }
            System.out.println("Keys matching '" + pattern + "' downloaded as CSV.");
        } catch (IOException | JedisException e) {
            System.out.println("Error downloading CSV: " + e.getMessage());
        }
    }

    @Override
    public void deleteAll(Scanner scanner) {
        System.out.print("Are you sure you want to delete all keys? (yes/no): ");
        String confirm = scanner.nextLine();
        if (confirm.equalsIgnoreCase("yes")) {
            try (Jedis jedis = pool.getResource()) {
                jedis.flushAll();
                System.out.println("All keys have been deleted.");
            } catch (JedisException e) {
                System.out.println("Error deleting all keys: " + e.getMessage());
            }
        } else {
            System.out.println("Operation cancelled.");
        }
    }

    @Override
    public void displayStructure(Scanner scanner) {
        System.out.println("Redis is a key-value store and does not have a fixed structure.");
        System.out.print("Enter a key to display its type and value: ");
        String key = scanner.nextLine();

        try (Jedis jedis = pool.getResource()) {
            String type = jedis.type(key);
            System.out.println("Key: " + key);
            System.out.println("Type: " + type);

            switch (type) {
                case "string":
                    System.out.println("Value: " + jedis.get(key));
                    break;
                case "list":
                    System.out.println("Values: " + jedis.lrange(key, 0, -1));
                    break;
                case "set":
                    System.out.println("Values: " + jedis.smembers(key));
                    break;
                case "zset":
                    System.out.println("Values: " + jedis.zrange(key, 0, -1));
                    break;
                case "hash":
                    System.out.println("Fields: " + jedis.hgetAll(key));
                    break;
                default:
                    System.out.println("Unsupported type or key does not exist.");
            }
        } catch (JedisException e) {
            System.out.println("Error displaying key info: " + e.getMessage());
        }
    }

    @Override
    public void executeCustomQuery(Scanner scanner) {
        System.out.println("Enter your Redis command:");
        String command = scanner.nextLine();

        try (Jedis jedis = pool.getResource()) {
            String[] parts = command.split("\\s+");
            List<String> args = new ArrayList<>(Arrays.asList(parts));
            String cmd = args.remove(0).toLowerCase();

            Object result = jedis.sendCommand(Protocol.Command.valueOf(cmd.toUpperCase()), args.toArray(new String[0]));
            System.out.println("Result: " + result);
        } catch (JedisException e) {
            System.out.println("Error executing command: " + e.getMessage());
        }
    }

    @Override
    public void close() {
        if (pool != null && !pool.isClosed()) {
            pool.close();
        }
    }
}