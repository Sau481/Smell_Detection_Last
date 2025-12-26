from flask import Blueprint, request, jsonify
import google.generativeai as genai
from dotenv import load_dotenv
import os

ai_bp = Blueprint("ai", __name__)
load_dotenv()

# Set up the Gemini API key
gemini_api_key = os.getenv("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)
else:
    print("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")

def ask_gemini(prompt, model="gemini-2.5-flash"):
    """
    Sends a prompt to the Gemini API and returns the response.
    """
    if not gemini_api_key:
        return "Error: Gemini API key is not configured."
    
    try:
        gemini = genai.GenerativeModel(model)
        response = gemini.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        # Log the error for debugging
        print(f"Gemini API Error: {e}")
        # Provide a user-friendly error message
        return f"An error occurred while communicating with the AI service: {e}"

@ai_bp.route("/explain", methods=["POST"])
def explain():
    """
    Explain what the given Python code does.
    """
    code = request.json.get("code", "")
    if not code:
        return jsonify({"success": False, "error": "No code provided"}), 400

    prompt = f"Explain clearly and concisely what this Python code does, highlighting potential issues or improvements:\n\n```python\n{code}\n```"
    
    explanation = ask_gemini(prompt)
    
    return jsonify({
        "success": True,
        "type": "explanation",
        "result": explanation
    })

@ai_bp.route("/optimize", methods=["POST"])
def optimize():
    """
    Optimize the given Python code to be more efficient and Pythonic.
    """
    code = request.json.get("code", "")
    if not code:
        return jsonify({"success": False, "error": "No code provided"}), 400

    prompt = f"Please refactor the following Python code to make it more efficient, clean, and Pythonic. Return only the optimized code block without any explanations or comments:\n\n```python\n{code}\n```"
    
    optimized_code = ask_gemini(prompt)
    
    return jsonify({
        "success": True,
        "type": "optimization",
        "result": optimized_code
    })

@ai_bp.route("/refactor", methods=["POST"])
def refactor():
    """
    Refactor the given Python code to address a specific code smell.
    """
    code = request.json.get("code", "")
    smell = request.json.get("smell_type", "a general smell")
    if not code:
        return jsonify({"success": False, "error": "No code provided"}), 400

    prompt = f"The following Python code is identified as having a '{smell}' code smell. Please refactor it to fix the issue while preserving its original functionality. Return only the refactored code block:\n\n```python\n{code}\n```"
    
    refactored_code = ask_gemini(prompt)
    
    return jsonify({
        "success": True,
        "type": "refactor",
        "result": refactored_code
    })
