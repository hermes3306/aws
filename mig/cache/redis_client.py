import redis
import configparser
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read(os.path.join(current_dir, 'db.ini'))

# Get the Redis configuration
redis_config = config['redis']

redis_client = redis.Redis(
    host=redis_config['host'],
    port=int(redis_config['port']),
    db=int(redis_config['db']),
    username=redis_config['user'],
    password=redis_config['password']
)

def get_redis():
    return redis_client