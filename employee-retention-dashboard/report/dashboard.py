from fasthtml.common import *
from starlette.staticfiles import StaticFiles
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
        df_cum.columns = ["Positive Events", "Negative Events"]

        # Initialize a pandas subplot with smaller figure size
        fig, ax = plt.subplots(figsize=(8, 4))

        # Custom colors for better visibility
        colors = ['#00d9ff', '#ff6b6b']  # Cyan for positive, coral for negative
        
        # Plot with custom styling
        for i, col in enumerate(df_cum.columns):
            ax.plot(df_cum.index, df_cum[col], color=colors[i], linewidth=2.5, 
                   label=col, marker='', alpha=0.9)
            
            # Add end point annotation
            last_val = df_cum[col].iloc[-1]
            ax.annotate(f'{int(last_val)}', 
                       xy=(df_cum.index[-1], last_val),
                       xytext=(5, 0), textcoords='offset points',
                       fontsize=11, fontweight='bold', color=colors[i])

        # Apply axis styling
        self.set_axis_styling(ax)

        # Set title and labels with improved styling
        ax.set_title("Cumulative Events Over Time", fontsize=18, fontweight='bold', pad=20)
        ax.set_xlabel("Date", fontsize=13, fontweight='bold', labelpad=12)
        ax.set_ylabel("Cumulative Event Count", fontsize=13, fontweight='bold', labelpad=12)
        
        # Format x-axis to show fewer date labels
        tick_positions = list(range(0, len(df_cum.index), max(1, len(df_cum.index) // 6)))
        ax.set_xticks([df_cum.index[i] for i in tick_positions])
        ax.set_xticklabels([df_cum.index[i] for i in tick_positions], rotation=45, ha='right')
        
        # Add grid for better readability
        ax.grid(True, linestyle='--', alpha=0.4)
        
        # Improve legend - positioned in upper left with styled box
        legend = ax.legend(loc='upper left', fontsize=11, framealpha=0.95)
        legend.get_frame().set_linewidth(1.5)
        
        # Tight layout to prevent label cutoff
        plt.tight_layout()

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
        
        # Initialize a matplotlib subplot with smaller size
        fig, ax = plt.subplots(figsize=(8, 2.5))
        
        # Determine color based on risk level
        if pred < 0.3:
            bar_color = '#4CAF50'  # Green - Low risk
            risk_level = 'Low Risk'
        elif pred < 0.6:
            bar_color = '#FF9800'  # Orange - Medium risk
            risk_level = 'Medium Risk'
        else:
            bar_color = '#F44336'  # Red - High risk
            risk_level = 'High Risk'
        
        # Create horizontal bar with custom styling
        bars = ax.barh(['Recruitment Risk'], [pred], color=bar_color, height=0.5, edgecolor='white', linewidth=2)
        
        # Add percentage text on the bar
        ax.text(pred + 0.02, 0, f'{pred*100:.1f}%', va='center', fontsize=14, fontweight='bold', color='white')
        
        # Add risk level indicator
        ax.text(0.5, -0.4, f'Risk Level: {risk_level}', transform=ax.transAxes, 
                ha='center', fontsize=11, color='white', style='italic')
        
        ax.set_xlim(0, 1)
        ax.set_title('Predicted Recruitment Risk', fontsize=16, fontweight='bold', pad=15, color='white')
        
        # Add x-axis labels as percentages
        ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xticklabels(['0%', '25%', '50%', '75%', '100%'])
        ax.set_xlabel('Probability', fontsize=12, labelpad=10)
        
        # Add vertical grid lines
        ax.grid(True, axis='x', linestyle='--', alpha=0.3, color='white')
        
        # pass the axis variable
        # to the `.set_axis_styling`
        # method
        self.set_axis_styling(ax)
        
        # Tight layout
        plt.tight_layout()

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

# Initialize a fasthtml app with custom CSS
from pathlib import Path
css_path = Path(__file__).parent.parent / 'assets' / 'report.css'
app = FastHTML(hdrs=[Link(rel='stylesheet', href='/static/report.css')])

# Mount static files
app.mount('/static', StaticFiles(directory=str(css_path.parent)), name='static')

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
    

# Use PORT from environment variable for Render deployment
import os
port = int(os.environ.get("PORT", 5001))
serve(reload=False, port=port, host="0.0.0.0")
