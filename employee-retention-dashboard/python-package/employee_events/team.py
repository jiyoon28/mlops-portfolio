# Import the QueryBase class
from .query_base import QueryBase

# Import dependencies for sql execution
from .sql_execution import QueryMixin

# Create a subclass of QueryBase
class Team(QueryBase, QueryMixin):
    """
    A class for querying team-related data.
    
    Attributes:
    ----------
    name(str) : The table name associated with teams.
    """
    name = "team"

    def names(self):
        """
        Returns a list of all teams with thier names and IDs.
        
        Returns:
        --------
        list[tuple] : A list of tuples where each tuple containts
            - Team name (str)
            - Team ID (int)
        """
        sql = """
            SELECT team_name, team_id
            FROM team
            ORDER BY team_name;
        """
        return self.query(sql)
    

    def username(self, id: int):
        """
        Returns the name of a team by its ID.
        
        Returns:
        --------
        list[tuple] : A list containing a single tuple with the team name.
        """
        sql = f"""
            SELECT team_name
            FROM team
            WHERE team_id = {id};
        """
        return self.query(sql)


    def model_data(self, id):
        """
        Returns model data for a given team.
        
        Returns:
        --------
        pandas.DataFrame: A DataFrame containing
            - Positive events count
            - Negative events count
        """
        sql = f"""
            SELECT positive_events, negative_events FROM (
                    SELECT employee_id
                         , SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                    GROUP BY employee_id
                   )
        """
        return self.pandas_query(sql)