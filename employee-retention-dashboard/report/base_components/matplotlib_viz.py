from .base_component import BaseComponent

import matplotlib.pyplot
from fasthtml.common import Img
import matplotlib.pylab as plt
import matplotlib
import io
import base64

# This is necessary to prevent matplotlib from causing memory leaks
# https://stackoverflow.com/questions/31156578/matplotlib-doesnt-release-memory-after-savefig-and-close
matplotlib.use('Agg')

# Set dark style for professional look
plt.style.use('dark_background')

# Configure save settings
matplotlib.rcParams['savefig.format'] = 'png'
matplotlib.rcParams['savefig.facecolor'] = '#1a1a2e'
matplotlib.rcParams['savefig.edgecolor'] = '#1a1a2e'
matplotlib.rcParams['figure.facecolor'] = '#1a1a2e'
matplotlib.rcParams['axes.facecolor'] = '#16213e'
matplotlib.rcParams['axes.edgecolor'] = '#e94560'
matplotlib.rcParams['axes.labelcolor'] = '#ffffff'
matplotlib.rcParams['text.color'] = '#ffffff'
matplotlib.rcParams['xtick.color'] = '#ffffff'
matplotlib.rcParams['ytick.color'] = '#ffffff'
matplotlib.rcParams['grid.color'] = '#0f3460'
matplotlib.rcParams['legend.facecolor'] = '#16213e'
matplotlib.rcParams['legend.edgecolor'] = '#e94560'


def matplotlib2fasthtml(func):
    '''
    Copy of https://github.com/koaning/fh-matplotlib, which is currently hardcoding the 
    image format as jpg. png or svg is needed here.
    '''
    def wrapper(*args, **kwargs):
        # Reset the figure to prevent accumulation. Maybe we need a setting for this?
        fig = plt.figure()

        # Run function as normal
        func(*args, **kwargs)

        # Store it as base64 and put it into an image.
        my_stringIObytes = io.BytesIO()
        plt.savefig(my_stringIObytes, bbox_inches='tight', dpi=150)
        my_stringIObytes.seek(0)
        my_base64_jpgData = base64.b64encode(my_stringIObytes.read()).decode()

        # Close the figure to prevent memory leaks
        plt.close(fig)
        plt.close('all')
        return Img(src=f'data:image/png;base64, {my_base64_jpgData}')
    return wrapper


class MatplotlibViz(BaseComponent):

    @matplotlib2fasthtml
    def build_component(self, entity_id, model):
        return self.visualization(entity_id, model)
    
    
    def visualization(self, entity_id, model):
        pass

    def set_axis_styling(self, ax):
        """Apply professional styling to chart axes."""
        
        # Set colors
        fontcolor = '#ffffff'
        bordercolor = '#e94560'
        
        # Title and labels
        ax.title.set_color(fontcolor)
        ax.title.set_fontweight('bold')
        ax.xaxis.label.set_color(fontcolor)
        ax.yaxis.label.set_color(fontcolor)

        # Tick styling
        ax.tick_params(axis='both', colors=fontcolor, labelsize=10)
        
        # Spine styling
        for spine in ax.spines.values():
            spine.set_edgecolor(bordercolor)
            spine.set_linewidth(1.5)

        # Keep solid lines (don't change to dashdot)
        for line in ax.get_lines():
            line.set_linewidth(2.5)
