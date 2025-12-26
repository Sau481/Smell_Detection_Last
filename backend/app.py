from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json

# ✅ Import ML + analysis helpers
from analyzer.smell_detector import analyze_file
from analyzer.ml_detector import get_model_accuracies
from ai_routes import ai_bp

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

# Define base directory for backend
base_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['UPLOAD_FOLDER'] = os.path.join(base_dir, 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(base_dir, 'results')

# Register the AI blueprint
app.register_blueprint(ai_bp, url_prefix="/api")


@app.route('/api/model-accuracies')
def model_accuracies():
    accuracies = get_model_accuracies()
    return jsonify(accuracies)




# ✅ Route 1: Home Page
@app.route('/')
def home():
    return render_template('index.html')


# ✅ Route 2: Analyze Uploaded File
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return "No file uploaded"

    file = request.files['file']
    if file.filename == '':
        return "No selected file"

    # Save uploaded file
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)

    # Run combined analysis
    result_data = analyze_file(filepath)

    # Save results to a JSON file
    os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)
    result_filename = f"{file.filename}.json"
    result_filepath = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
    
    with open(result_filepath, 'w') as f:
        json.dump(result_data, f, indent=4)

    # Redirect to the result page
    return redirect(url_for('show_result', filename=file.filename))


# ✅ Route 3: Show Analysis Result
@app.route('/result/<filename>')
def show_result(filename):
    result_filename = f"{filename}.json"
    result_filepath = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(result_filepath):
        return "Result not found", 404

    with open(result_filepath, 'r') as f:
        result_data = json.load(f)

    with open(filepath, 'r', encoding='utf-8') as f:
        code_content = f.read()

    # Check if any smells were detected
    no_smells_detected = all(not result_data.get(key) for key in ['long_methods', 'large_classes', 'rule_based'])

    return render_template(
        'results.html',
        filename=filename,
        ml_result=result_data.get('ml_result', {}),
        long_methods=result_data.get('long_methods', []),
        large_classes=result_data.get('large_classes', []),
        rule_based=result_data.get('rule_based', []),
        code_content=code_content,
        summary=result_data.get('summary', {})
    )


# ✅ Start Flask App
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
