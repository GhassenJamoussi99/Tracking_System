import configparser

# Initialize and read the config file
config = configparser.ConfigParser()
config.read('data_layer/config.ini')

# Accessing the database configuration
DATABASE_CONFIG = {
    'user': config['DATABASE']['User'],
    'password': config['DATABASE']['Password'],
    'host': config['DATABASE']['Host'],
    'database': config['DATABASE']['Database']
}

# If you need to access other configuration like Admin Password Hash
ADMIN_PASSWORD = config['DEFAULT']['AdminPassword']
