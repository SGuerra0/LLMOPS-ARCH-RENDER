from models.model import load_model

# Load the AI Model
model = load_model()

def run_inference(input_text: str):
    """
    Function to run inference with the model.
    """
    # Preprocess and predict
    prediction = model.predict(input_text)
    return prediction