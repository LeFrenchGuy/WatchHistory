import sqlite3

class PlexDBUtility:
  def __init__(self, db_path):
    """
    Initialize the database utility with the path to the SQLite database.
    """
    self.db_path = db_path
    self.conn = None
    self.cursor = None

  def connect(self):
    """
    Connect to the SQLite database.
    """
    if not self.conn:
      self.conn = sqlite3.connect(self.db_path)
      self.cursor = self.conn.cursor()

  def execute_query(self, query, params=None):
    """
    Execute a query and return the results.

    :param query: The SQL query to execute.
    :param params: Optional parameters for the query.
    :return: The result of the query.
    """
    if not self.conn:
      raise RuntimeError("Database connection is not established. Call connect() first.")
    
    if params is None:
      params = ()

    self.cursor.execute(query, params)
    return self.cursor.fetchall()

  def close(self):
    """
    Close the database connection.
    """
    if self.conn:
      self.cursor.close()
      self.conn.close()
      self.conn = None
      self.cursor = None
