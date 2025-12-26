import joblib
import pandas as pd
import re
import os
from analyzer.feature_extractor import extract_features



# Define base directory for backend
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_ml_explanations():
    """
    Returns a dictionary of explanations for common ML-related issues.
    """
    return {
        "model_not_found": {
            "title": "ML Model Not Found",
            "reason": "One or more of the required model files (.pkl) are missing from the 'models' directory.",
            "fix": "Please train the models first by running the `train_model.py` script. This will generate the necessary files."
        },
        "low_accuracy": {
            "title": "Low Model Accuracy",
            "reason": "The model's accuracy is below a reasonable threshold, which may lead to unreliable predictions.",
            "fix": "This can be caused by a small or unrepresentative dataset. Consider adding more diverse examples to the training data and retraining the models."
        },
        "prediction_failed": {
            "title": "Prediction Failed",
            "reason": "An unexpected error occurred during the prediction process.",
            "fix": "This could be due to an issue with the input file or a problem with the trained model. Check the file for syntax errors and consider retraining the models."
        }
    }

def get_model_accuracies():
    """
    Reads the training summary and returns a dictionary of model accuracies.
    """
    accuracies = {}
    summary_path = os.path.join(base_dir, "results", "training_summary.txt")
    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            for line in f:
                match = re.match(r"(.+?):\s+([\d\.]+)%", line)
                if match:
                    model_name = match.group(1).strip()
                    accuracy = float(match.group(2))
                    accuracies[model_name] = accuracy
    except FileNotFoundError:
        print(f"Warning: `{summary_path}` not found. Accuracies will not be displayed.")
    return accuracies

def detect_ml_smells(file_path):
    """
    Loads the best trained ML model and predicts smell types for a given Python file.
    Includes model accuracy and explanations for potential issues.
    """
    accuracies = get_model_accuracies()
    explanations = get_ml_explanations()
    models_dir = os.path.join(base_dir, "models")

    if not accuracies:
        return {
            "Error": "Accuracy information not found",
            "explanation": {
                "title": "Accuracy information not found",
                "reason": "The `training_summary.txt` file is missing or empty.",
                "fix": "Please train the models first by running the `train_model.py` script."
            }
        }

    # Find the best model
    best_model_name = max(accuracies, key=accuracies.get)
    model_file_map = {
        'Random Forest': 'random_forest_model.pkl',
        'Decision Tree': 'decision_tree_model.pkl',
        'SVM': 'svm_model.pkl',
        'KNN': 'knn_model.pkl'
    }
    
    model_file = model_file_map.get(best_model_name)
    if not model_file:
        return {
            "Error": "Best model not found",
            "explanation": {
                "title": "Best model not found",
                "reason": f"The best model '{best_model_name}' does not have a corresponding model file.",
                "fix": "Ensure the model names in `training_summary.txt` match the keys in `model_file_map`."
            }
        }

    try:
        # Load the best model and necessary files
        model = joblib.load(os.path.join(models_dir, model_file))
        feature_columns = joblib.load(os.path.join(models_dir, "feature_columns.pkl"))
        label_encoder_path = os.path.join(models_dir, "label_encoder.pkl")
        
        if not os.path.exists(label_encoder_path):
            raise FileNotFoundError(f"Label encoder not found at {label_encoder_path}")
            
        label_encoder = joblib.load(label_encoder_path)

        # Create a reverse mapping from index to label
        reverse_label_map = {v: k for k, v in label_encoder.items()}

        # Extract features from the code
        features = extract_features(file_path)
        df = pd.DataFrame([features])

        # Align columns to match training order
        for col in feature_columns:
            if col not in df.columns:
                df[col] = 0
        df = df[feature_columns]

        # Predict with the best model
        pred_idx = model.predict(df)[0]
        prediction = reverse_label_map.get(pred_idx, "Unknown")

        return {
            "predictions": {
                best_model_name: {
                    "prediction": prediction,
                    "accuracy": accuracies.get(best_model_name, 0)
                }
            }
        }

    except FileNotFoundError as e:
        return {
            "Error": explanations["model_not_found"]["title"],
            "explanation": explanations["model_not_found"]
        }
    except Exception as e:
        return {
            "Error": explanations["prediction_failed"]["title"],
            "explanation": {
                "title": explanations["prediction_failed"]["title"],
                "reason": str(e),
                "fix": explanations["prediction_failed"]["fix"]
            }
        }
    

 
