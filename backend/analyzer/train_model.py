
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os



def train_models():
    # Define base directory for backend
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

    # ✅ Step 1: Load dataset
    dataset_path = os.path.join(base_dir, "dataset", "merged_dataset.csv")
    df = pd.read_csv(dataset_path)
    print(f"✅ Dataset loaded. Shape: {df.shape}")


    # ✅ Step 2: Define full 19-feature set
    selected_features = [
        "lloc", "sloc", "scloc",
        "comments", "single_com", "multi_comr",
        "blanks", "h1", "h2", "n1", "n2",
        "vocabulary", "length", "volume",
        "difficulty", "effort", "maintainability_index",
        "smell_type"
    ]


    # ✅ Step 3: Ensure all expected columns exist
    for col in selected_features:
        if col not in df.columns and col != "smell_type":
            df[col] = 0


    df = df[[col for col in selected_features if col in df.columns]]


    # ✅ Step 4: Separate features (X) and labels (y)
    if "smell_type" not in df.columns:
        raise ValueError("❌ 'smell_type' column not found in dataset!")


    X = df.drop(columns=["smell_type"])
    y = df["smell_type"]


    feature_columns = list(X.columns)
    print(f"✅ Using features: {feature_columns}")


    # ✅ Step 5: Preprocess
    X.fillna(0, inplace=True)

    # Store original labels for reference
    label_encoder = {label: idx for idx, label in enumerate(y.unique())}
    y_encoded = y.map(label_encoder)
    num_classes = len(label_encoder)

    print(f"✅ Number of classes: {num_classes}")
    print(f"✅ Label mapping: {label_encoder}")


    # ✅ Step 6: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42
    )


    # Create models directory
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)


    # Dictionary to store model results
    results = {}


    print("\n" + "="*60)
    print("🚀 TRAINING MULTIPLE MODELS")
    print("="*60)


    # ✅ Model 1: Random Forest
    print("\n📊 Training Random Forest Classifier...")
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    rf_pred = rf_model.predict(X_test)
    rf_accuracy = accuracy_score(y_test, rf_pred) * 100
    results['Random Forest'] = rf_accuracy

    print(f"🎯 Random Forest Accuracy: {rf_accuracy:.2f}%")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, rf_pred))

    joblib.dump(rf_model, os.path.join(models_dir, "random_forest_model.pkl"))
    print(f"✅ Saved: {os.path.join(models_dir, 'random_forest_model.pkl')}")


    # ✅ Model 2: Decision Tree
    print("\n" + "-"*60)
    print("🌳 Training Decision Tree Classifier...")
    dt_model = DecisionTreeClassifier(criterion='gini', random_state=42)
    dt_model.fit(X_train, y_train)
    dt_pred = dt_model.predict(X_test)
    dt_accuracy = accuracy_score(y_test, dt_pred) * 100
    results['Decision Tree'] = dt_accuracy

    print(f"🎯 Decision Tree Accuracy: {dt_accuracy:.2f}%")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, dt_pred))

    joblib.dump(dt_model, os.path.join(models_dir, "decision_tree_model.pkl"))
    print(f"✅ Saved: {os.path.join(models_dir, 'decision_tree_model.pkl')}")


    # ✅ Model 3: Support Vector Machine (SVM)
    print("\n" + "-"*60)
    print("🔷 Training SVM Classifier...")
    svm_model = SVC(kernel='rbf', C=1.0, gamma='scale', random_state=42)
    svm_model.fit(X_train, y_train)
    svm_pred = svm_model.predict(X_test)
    svm_accuracy = accuracy_score(y_test, svm_pred) * 100
    results['SVM'] = svm_accuracy

    print(f"🎯 SVM Accuracy: {svm_accuracy:.2f}%")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, svm_pred))

    joblib.dump(svm_model, os.path.join(models_dir, "svm_model.pkl"))
    print(f"✅ Saved: {os.path.join(models_dir, 'svm_model.pkl')}")


    # ✅ Model 4: K-Nearest Neighbors (KNN)
    print("\n" + "-"*60)
    print("🔵 Training KNN Classifier...")
    knn_model = KNeighborsClassifier(n_neighbors=5, weights='uniform', algorithm='auto')
    knn_model.fit(X_train, y_train)
    knn_pred = knn_model.predict(X_test)
    knn_accuracy = accuracy_score(y_test, knn_pred) * 100
    results['KNN'] = knn_accuracy

    print(f"🎯 KNN Accuracy: {knn_accuracy:.2f}%")
    print("\n📊 Classification Report:")
    print(classification_report(y_test, knn_pred))

    joblib.dump(knn_model, os.path.join(models_dir, "knn_model.pkl"))
    print(f"✅ Saved: {os.path.join(models_dir, 'knn_model.pkl')}")


    # ✅ Save feature columns and label encoder
    joblib.dump(feature_columns, os.path.join(models_dir, "feature_columns.pkl"))
    joblib.dump(label_encoder, os.path.join(models_dir, "label_encoder.pkl"))
    print(f"\n✅ Saved: {os.path.join(models_dir, 'feature_columns.pkl')}")
    print(f"✅ Saved: {os.path.join(models_dir, 'label_encoder.pkl')}")


    # ✅ Display final comparison
    print("\n" + "="*60)
    print("📈 MODEL COMPARISON SUMMARY")
    print("="*60)
    for model_name, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"{model_name:20s}: {acc:.2f}%")
    print("="*60)

    best_model = max(results, key=results.get)
    print(f"\n🏆 Best Model: {best_model} with {results[best_model]:.2f}% accuracy")


    # ✅ Save comparison summary to file
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)
    summary_path = os.path.join(results_dir, "training_summary.txt")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write("="*60 + "\n")
        f.write("📈 MODEL COMPARISON SUMMARY\n")
        f.write("="*60 + "\n")
        for model_name, acc in sorted(results.items(), key=lambda x: x[1], reverse=True):
            f.write(f"{model_name:20s}: {acc:.2f}%\n")
        f.write("="*60 + "\n")
        best_model = max(results, key=results.get)
        f.write(f"\n🏆 Best Model: {best_model} with {results[best_model]:.2f}% accuracy\n")

    print(f"\n✅ Training summary saved to: {summary_path}")



if __name__ == "__main__":
    train_models()