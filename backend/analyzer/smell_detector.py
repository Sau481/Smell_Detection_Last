import subprocess
import json
from analyzer.feature_extractor import find_long_methods, find_large_classes
from analyzer.ml_detector import detect_ml_smells


# --------------------------------------------------------
# 🔹 Get descriptive reason for a smell
# --------------------------------------------------------
def get_smell_reason(smell_type: str) -> dict:
    """
    Returns a descriptive reason and suggested fix for a given smell type.
    """
    reasons = {
        "LongMethod": {
            "reason": "This method is too long, making it hard to read, understand, and maintain.",
            "fix": "Break it into smaller, focused functions to improve clarity."
        },
        "LargeClass": {
            "reason": "This class has too many responsibilities or lines of code, violating the Single Responsibility Principle.",
            "fix": "Split it into smaller, more cohesive classes."
        },
        "CleanCode": {
            "reason": "No code smells were detected. The file follows good design and coding practices.",
            "fix": "No action needed."
        }
    }
    return reasons.get(
        smell_type,
        {"reason": "No specific reason available.", "fix": "General refactoring principles may apply."}
    )


# --------------------------------------------------------
# 🔹 Run Pylint and capture issues
# --------------------------------------------------------
def run_pylint_analysis(file_path: str) -> list:
    """
    Runs pylint on a given file and returns structured issues.
    Only critical issues (error, warning, refactor) are kept.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        result = subprocess.run(
            ["pylint", file_path, "--output-format=json", "--score=n"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=30
        )

        output = result.stdout.strip()
        if not output:
            return [{"category": "No issues found", "type": "Clean Code", "details": "", "line": "-"}]

        issues = json.loads(output)

        # Keep only significant issue categories
        critical_types = {"error", "warning", "refactor"}
        filtered_issues = [i for i in issues if i.get("type", "").lower() in critical_types]

        if not filtered_issues:
            return [{"category": "No issues found", "type": "Clean Code", "details": "", "line": "-"}]

        formatted = []
        for issue in filtered_issues:
            line_num = issue.get("line", 1)
            snippet = lines[line_num - 1].strip() if 1 <= line_num <= len(lines) else ""
            formatted.append({
                "category": issue.get("type", "N/A").capitalize(),
                "type": issue.get("symbol", "N/A"),
                "details": issue.get("message", "N/A"),
                "line": line_num,
                "code_snippet": snippet
            })

        return formatted

    except subprocess.TimeoutExpired:
        return [{"category": "Error", "type": "Pylint Timeout", "details": "Pylint took too long to analyze.", "line": "-"}]
    except Exception as e:
        return [{"category": "Error", "type": "Pylint Failed", "details": str(e), "line": "-"}]


# --------------------------------------------------------
# 🔹 Combine ML + AST + Pylint in one unified analysis
# --------------------------------------------------------
def analyze_file(file_path: str) -> dict:
    """
    Runs ML-based prediction, AST-based smell detection, and Pylint static analysis.
    Returns a unified structured dictionary for frontend visualization.
    """
    print(f"\n🚀 Analyzing file: {file_path}")

    # ✅ 1. ML-based prediction
    ml_result = detect_ml_smells(file_path)

    # ✅ 2. AST-based smell localization (Adaptive thresholds)
    long_methods = find_long_methods(file_path, threshold=12)
    large_classes = find_large_classes(file_path, method_threshold=4, line_threshold=25)

    # Attach human-readable reasons
    for method in long_methods:
        method["reason"] = get_smell_reason("LongMethod")

    for cls in large_classes:
        cls["reason"] = get_smell_reason("LargeClass")

    # ✅ 3. Rule-based analysis (Pylint)
    pylint_results = run_pylint_analysis(file_path)

    # ✅ 4. Detect if the file is clean
    no_smells_detected = (
        not long_methods and
        not large_classes and
        "Error" not in str(ml_result) and
        any("Clean Code" in i.get("type", "") for i in pylint_results)
    )

    # ✅ 5. If everything is clean, mark it
    if no_smells_detected:
        return {
            "ml_result": {"predictions": {"status": "Clean Code"}},
            "long_methods": [],
            "large_classes": [],
            "rule_based": [{"category": "Clean", "type": "Clean Code", "details": "No issues found.", "line": "-"}],
            "summary": get_smell_reason("CleanCode")
        }

    # ✅ 6. Otherwise, return combined analysis
    return {
        "ml_result": ml_result,
        "long_methods": long_methods,
        "large_classes": large_classes,
        "rule_based": pylint_results,
        "summary": {
            "smell_count": len(long_methods) + len(large_classes) + len(pylint_results),
            "status": "Smells Detected" if (long_methods or large_classes) else "Minor Issues",
        }
    }
