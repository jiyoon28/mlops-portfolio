from sqlite3 import connect
from pathlib import Path
from functools import wraps
import pandas as pd

db_path = Path(__file__).parent / "employee_events.db"

# Define a class called `QueryMixin`
class QueryMixin:
    
    """
    A mixin class providing methods to execute SQL queries
    and returns results as pandas DataFrames or lists of tuples.
    """
    
    def pandas_query(self, sql_query: str) -> pd.DataFrame:
        """
        Excutes a SQL query and returns the result as a pandas DataFrame.
        
        Parameters:
        -----------
        sql_query(str) : The SQL query to be executed.
        
        Returns:
        --------
        pandas.DataFrame : The query result as a DataFrame.
        """
        with connect(db_path) as con:
            return pd.read_sql_query(sql_query, con)

    def query(self, sql_query: str):
        """
        Executes a SQL query and returns the result as a list of tuples.
        
        Parameters:
        ----------
        sql_query(str) : The SQL query to excute.
        
        Returns:
        --------
        list[tuple] : The query result as list of tuples.
        """
        print(f"Executing SQL Query: {sql_query}")
        print(f"Using Database Path: {db_path}")
        with connect(db_path) as con:
            cur = con.cursor()
            return cur.execute(sql_query).fetchall()


def query(func):
    """
    Decorator that runs a standard sql execution
    and returns a list of tuples
    """

    @wraps(func)
    def run_query(*args, **kwargs):
        query_string = func(*args, **kwargs)
        connection = connect(db_path)
        cursor = connection.cursor()
        result = cursor.execute(query_string).fetchall()
        connection.close()
        return result
    
    return run_query
