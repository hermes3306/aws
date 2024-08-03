import redis
from configparser import ConfigParser
import logging
import ssl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = ConfigParser()
config.read('db.ini')

redis_config = config['redis']

def get_redis():
    try:
        client = redis.from_url(
            redis_config['url'],
            decode_responses=True,
            ssl_cert_reqs="none"
        )
        # Test the connection
        client.ping()
        logger.info("Successfully connected to Redis")
        return client
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when connecting to Redis: {e}")
        raise