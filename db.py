import sqlite3
from contextlib import contextmanager
import os

DATABASE = 'data/app.db'

# Create the database directory if it doesn't exist
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# Create a connection pool with a maximum of 5 connections
class DatabaseConnectionPool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []

    def get_connection(self):
        # If we have available connections, return one
        if self.connections:
            return self.connections.pop()

        # Otherwise, create a new connection
        if len(self.connections) < self.max_connections:
            return sqlite3.connect(self.db_path, timeout=10.0)
        else:
            raise Exception("No available database connections")

    def release_connection(self, connection):
        # Return the connection to the pool
        self.connections.append(connection)

    @contextmanager
    def connection(self):
        conn = self.get_connection()
        try:
            yield conn
        finally:
            self.release_connection(conn)

# Create a global connection pool
db_pool = DatabaseConnectionPool(DATABASE)