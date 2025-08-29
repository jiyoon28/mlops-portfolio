# Import any dependencies needed to execute sql queries
import pandas as pd
from .sql_execution import QueryMixin

# Define a class called QueryBase
class QueryBase(QueryMixin):
    """
    Base class for excuting SQL queries related to employee or team data.
    
    Attributes:
    -----------
    name(str) : Name of the table related to the query.
    db_path(str) : Path to the SQLite database.
    """

    name: str = ""

    @staticmethod
    def names() -> list:
        """
        Returns a list of names associated with the class
        
        Returns:
        -------
        list : An empty list as the default implementation
        """
        return []

    # Define an `event_counts` method
    def event_counts(self, id: int) -> pd.DataFrame:
        """
        Returns the total positive and negative events grouped by date for a specific ID.
        
        Parameters:
        ----------
        id(int) : The unique identifier for the employee or team.
        
        Returns:
        --------
        pandas.DataFrame : A DataFrame containing `event_date`, `total_positive_events`, and `total_negative_events`.
        """

        id_col = f"{self.name}_id"
        sql = f"""
        SELECT ee.event_date,
            SUM(ee.positive_events) AS positive_events,
            SUM(ee.negative_events) AS negative_events
        FROM employee_events AS ee
        JOIN {self.name} AS t
        ON ee.{id_col} = t.{id_col}
        WHERE t.{id_col} = {id}
        GROUP BY ee.event_date
        ORDER BY ee.event_date;
        """
        return self.pandas_query(sql)
            
    

    # Define a `notes` method that receives an id argument
    def notes(self, id: int) -> pd.DataFrame:
        """
        Returns notes associated with a specific ID, ordered by date.
        
        Parameters:
        ----------
        id(int) : The unique identifier for the employee or team.

        Returns:
        -------
        pandas.DataFrame : A DataFrame containing `note_date` and `note`.
        """
        id_col = f"{self.name}_id"
        sql = f"""
        SELECT n.note_date, n.note
        FROM notes AS n
        JOIN {self.name} AS t
        ON n.{id_col} = t.{id_col}
        WHERE t.{id_col} = {id}
        ORDER BY n.note_date;
        """
        return self.pandas_query(sql)
