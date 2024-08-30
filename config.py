import os

class Config:
    DEBUG = os.getenv('DEBUG', True)
    # Add other configuration variables here