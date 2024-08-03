from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import configparser
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Create a ConfigParser object
config = configparser.ConfigParser()

# Read the configuration file
config.read(os.path.join(current_dir, 'db.ini'))

# Get the database configuration
db_config = config['postgresql']

# Construct the DATABASE_URL
DATABASE_URL = f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

# Create the SQLAlchemy engine with SSL requirement and extended timeout
engine = create_engine(
    DATABASE_URL,
    connect_args={
        'sslmode': 'require',
        'connect_timeout': 10
    }
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

# Test the connection
if __name__ == "__main__":
    try:
        with engine.connect() as connection:
            print("Successfully connected to the database!")
    except Exception as e:
        print(f"An error occurred: {e}")