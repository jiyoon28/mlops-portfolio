import pickle
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
model_path = project_root / "assets" / "model.pkl"

def load_model():
    """
    Load a machine learning model from the model.pkl file.
    
    Returns:
        object: The loaded machine learning model.
    """

    with model_path.open('rb') as file:
        model = pickle.load(file)

    return model