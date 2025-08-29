# Import the QueryBase class
from .query_base import QueryBase

# Import dependencies needed for sql execution
from .sql_execution import QueryMixin

# Define a subclass of QueryBase
class Employee(QueryBase, QueryMixin):
    """
    A class for querying employee-related data.
    
    Attributes:
    ----------
    name(str) : The table name associated with employees.
    """

    name = "employee"


    def names(self):
        """
        Returns a list of all employees with their full names and IDs.
        
        Returns:
        -------
        list[tuple] : A list of tuples containing
            - full name(srt)
            - employee ID (int)
        """
        sql = """
            SELECT (first_name || ' ' || last_name) AS full_name,
                employee_id
            FROM employee
            ORDER BY last_name, first_name;
        """
        return self.query(sql)
    

    def user_name(self, id: int):
        """
        Returns:
        --------
        list[tuple] : A list containing a single tuple with the full name of the employee.
        """
        sql = """
            SELECT (first_name || ' ' || last_name) AS full_name
            FROM employee
            WHERE employee_id = {id};
        """
        return self.query(sql)


    def model_data(self, id):
        """
        Returns aggregated event data for a specific employee.
        """
        sql =f"""
                SELECT SUM(positive_events) positive_events, 
                    SUM(negative_events) negative_events
                FROM {self.name}
                JOIN employee_events
                    USING({self.name}_id)
                WHERE {self.name}.{self.name}_id = {id}
            """
        return self.pandas_query(sql)