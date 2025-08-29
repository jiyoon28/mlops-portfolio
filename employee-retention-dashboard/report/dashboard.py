from fasthtml.common import *
import matplotlib.pyplot as plt

# Import QueryBase, Employee, Team from employee_events
from employee_events.query_base import QueryBase
from employee_events.employee import Employee
from employee_events.team import Team

# import the load_model function from the utils.py file
from utils import load_model

"""
Below, we import the parent classes
you will use for subclassing
"""
from base_components import (
    Dropdown,
    BaseComponent,
    Radio,
    MatplotlibViz,
    DataTable
    )

from combined_components import FormGroup, CombinedComponent


# Create a subclass of base_components/dropdown
class ReportDropdown(Dropdown):
    """
    A dropdown component for selecting an entity.

    Methods:
        build_component(entity_id, model):
            Builds the dropdown HTML based on the provided entity and model.
        component_data(entity_id, model):
            Fetches the data required to populate the dropdown options.
    """
    
    def build_component(self, entity_id, model: QueryBase):
        """
        Build the HTML for the dropdown selector.
        
        Returns:
            str: The HTML string for the dropdown selector.
        """
        #  Set the `label` attribute so it is set
        #  to the `name` attribute for the model
        self.label = getattr(model, "name", "selector")
        # Return the output from the
        # parent class's build_component method
        return super().build_component(entity_id, model)
    
    def component_data(self, entity_id, model: QueryBase):
        """
        Fetch the data required to populate the dropdown.
        """
        # Using the model argument, call the employee_events method
        # that returns the user-type's
        # names and ids
        # (Employee.names() → [(full_name, id), ...]
        #  Team.names()     → [(team_name, id), ...])
        return model.names()


# Create a subclass of base_components/BaseComponent
class Header(BaseComponent):
    """
    A component for generating a dynamic report header.

    Methods:
        build_component(entity_id, model):
            Builds the header HTML for the report.
    """
    def build_component(self, entity_id, model: QueryBase):
        # Using the model argument for this method, return a fasthtml H1 object
        # containing the model's name attribute
        title = getattr(model, "name", "report").title()
        return H1(f"{title} Dashboard")

# Create a subclass of base_components/MatplotlibViz
class LineChart(MatplotlibViz):
    """
    A class for generating line charts visualizing cumulative events over time.

    Methods:
        visualization(model, entity_id):
            Prepares and saves a line chart based on the provided model and entity ID.
    """
    
    def visualization(self, asset_id, model: QueryBase):
        """
        Generate and save a line chart for cumulative events over time.

        Args:
            model (object): The model (Employee or Team) providing event data.
            asset_id (int): The ID of the entity whose events are visualized.

        Returns:
            str: Relative file path to the saved chart, or a message indicating no data is available.
        """
        # Pass the `asset_id` argument tothe model's `event_counts` method to
        # receive the x (Day) and y (event count)
        df = model.event_counts(asset_id)

        # Use the pandas .fillna method to fill nulls with 0
        df = df.fillna(0)

        # User the pandas .set_index method to set the date column as the index
        df = df.set_index("event_date")

        # Sort the index
        df = df.sort_index()

        # Use the .cumsum method to change the data in the dataframe to cumulative counts
        cols = [c for c in df.columns if "positive_events" in c or "negative_events" in c]
        df_cum = df[cols].cumsum()

        # Set the dataframe columns to the list ['Positive', 'Negative']
        pos_col = [c for c in df_cum.columns if "positive_events" in c][0]
        neg_col = [c for c in df_cum.columns if "negative_events" in c][0]
        df_cum = df_cum[[pos_col, neg_col]]
        df_cum.columns = ["Positive", "Negative"]

        # Initialize a pandas subplot and assign the figure and axis to variables
        fig, ax = plt.subplots()

        # call the .plot method for the cumulative counts dataframe
        df_cum.plot(ax=ax)

        # pass the axis variable to the `.set_axis_styling` method
        self.set_axis_styling(ax)

        # Set title and labels for x and y axis
        ax.set_title("Cumulative Positive/Negative Events")
        ax.set_xlabel("Date")
        ax.set_ylabel("Cumulative Count")

        return fig


class BarChart(MatplotlibViz):
    """
    A class for generating bar charts visualizing predicted recruitment risk.

    Attributes:
        predictor: The trained model used to predict probabilities for the bar chart.

    Methods:
        visualization(model, entity_id):
            Prepares and saves a bar chart based on the provided model and entity ID.
    """

    # Create a `predictor` class attribute
    # assign the attribute to the output
    # of the `load_model` utils function
    predictor = load_model()

    # Overwrite the parent class `visualization` method
    # Use the same parameters as the parent
    def visualization(self, asset_id, model: QueryBase):

        # Using the model and asset_id arguments
        # pass the `asset_id` to the `.model_data` method
        # to receive the data that can be passed to the machine
        # learning model
        df = model.model_data(asset_id)
        
        # Using the predictor class attribute
        # pass the data to the `predict_proba` method
        proba = self.predictor.predict_proba(df)
        
        # Index the second column of predict_proba output
        # The shape should be (<number of records>, 1)
        probs = proba[:, 1]
        
        
        # Below, create a `pred` variable set to
        # the number we want to visualize
        #
        # If the model's name attribute is "team"
        # We want to visualize the mean of the predict_proba output
        if getattr(model, "name", "") == "team":
            pred = float(probs.mean())
            
        # Otherwise set `pred` to the first value
        # of the predict_proba output
        else:
            pred = float(probs[0])
        
        # Initialize a matplotlib subplot
        fig, ax = plt.subplots()
        
        # Run the following code unchanged
        ax.barh([''], [pred])
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=20)
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(ax)

        return fig

# Create a subclass of combined_components/CombinedComponent
class Visualizations(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing an initialized
    # instance of `LineChart` and `BarChart`
    children = [
        LineChart(),
        BarChart(),
    ]

    # Leave this line unchanged
    outer_div_type = Div(cls='grid')
            
# Create a subclass of base_components/DataTable
class NotesTable(DataTable):

    # Overwrite the `component_data` method
    # using the same parameters as the parent class
    def component_data(self, entity_id, model: QueryBase):
        
        # Using the model and entity_id arguments
        # pass the entity_id to the model's .notes 
        # method. Return the output
        return model.notes(entity_id)
    

class DashboardFilters(FormGroup):

    id = "top-filters"
    action = "/update_data"
    method="POST"

    children = [
        Radio(
            values=["Employee", "Team"],
            name='profile_type',
            hx_get='/update_dropdown',
            hx_target='#selector'
            ),
        ReportDropdown(
            id="selector",
            name="user-selection")
        ]
    
# Create a subclass of CombinedComponents
class Report(CombinedComponent):

    # Set the `children`
    # class attribute to a list
    # containing initialized instances 
    # of the header, dashboard filters,
    # data visualizations, and notes table
    children = [
        Header(),
        DashboardFilters(),
        Visualizations(),
        NotesTable(),
    ]

# Initialize a fasthtml app 
app = FastHTML()

# Initialize the `Report` class
report = Report()


# Create a route for a get request
# Set the route's path to the root
@app.get('/')
def index():

    # Call the initialized report
    # pass the integer 1 and an instance
    # of the Employee class as arguments
    # Return the result
    return report(1, Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for an employee ID so `/employee/2`
# will return the page for the employee with
# an ID of `2`. 
# parameterize the employee ID 
# to a string datatype
@app.get('/employee/{emp_id}')
def employee(emp_id: str):

    # Call the initialized report
    # pass the ID and an instance
    # of the Employee SQL class as arguments
    # Return the result
    return report(int(emp_id), Employee())

# Create a route for a get request
# Set the route's path to receive a request
# for a team ID so `/team/2`
# will return the page for the team with
# an ID of `2`. 
# parameterize the team ID 
# to a string datatype
@app.get('/team/{team_id}')
def team(team_id: str):

    # Call the initialized report
    # pass the id and an instance
    # of the Team SQL class as arguments
    # Return the result
    return report(int(team_id), Team())


# Keep the below code unchanged!
@app.get('/update_dropdown{r}')
def update_dropdown(r):
    dropdown = DashboardFilters.children[1]
    print('PARAM', r.query_params['profile_type'])
    if r.query_params['profile_type'] == 'Team':
        return dropdown(None, Team())
    elif r.query_params['profile_type'] == 'Employee':
        return dropdown(None, Employee())


@app.post('/update_data')
async def update_data(r):
    from fasthtml.common import RedirectResponse
    data = await r.form()
    profile_type = data._dict['profile_type']
    id = data._dict['user-selection']
    if profile_type == 'Employee':
        return RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == 'Team':
        return RedirectResponse(f"/team/{id}", status_code=303)
    


serve(reload=False)
