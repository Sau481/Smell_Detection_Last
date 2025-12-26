import ast
from radon.raw import analyze
from radon.metrics import h_visit, mi_visit

# --------------------------------------------------------------------
# 🔹 1. Extract 19 software metrics for ML detection
# --------------------------------------------------------------------
def extract_features(file_path):
    """
    Extracts 19 detailed features (dataset-aligned) using Radon + AST.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    # ✅ Basic metrics
    raw_metrics = analyze(source)

    lloc = raw_metrics.lloc
    sloc = raw_metrics.sloc
    scloc = raw_metrics.sloc
    comments = raw_metrics.comments
    multi_comr = raw_metrics.multi
    single_com = comments - multi_comr
    blanks = raw_metrics.blank

    # ✅ Halstead metrics
    try:
        h_reports = h_visit(source)
        if isinstance(h_reports, list) and len(h_reports) > 0:
            h_data = h_reports[0]._asdict()
        elif hasattr(h_reports, "total"):
            h_data = h_reports.total._asdict()
        elif hasattr(h_reports, "_asdict"):
            h_data = h_reports._asdict()
        else:
            h_data = {}
    except Exception as e:
        print(f"⚠️ Halstead metric extraction failed: {e}")
        h_data = {}
 
    h1 = h_data.get("h1", 0)
    h2 = h_data.get("h2", 0)
    n1 = h_data.get("n1", 0)
    n2 = h_data.get("n2", 0)
    vocabulary = h_data.get("vocabulary", 0)
    length = h_data.get("length", 0)
    volume = h_data.get("volume", 0)
    difficulty = h_data.get("difficulty", 0)
    effort = h_data.get("effort", 0)

    # ✅ Maintainability index
    maintainability_index = mi_visit(source, True)

    # ✅ Combine everything
    features = {
        "lloc": lloc, "sloc": sloc, "scloc": scloc, "comments": comments,
        "single_com": single_com, "multi_comr": multi_comr, "blanks": blanks,
        "h1": h1, "h2": h2, "n1": n1, "n2": n2, "vocabulary": vocabulary,
        "length": length, "volume": volume, "difficulty": difficulty,
        "effort": effort, "maintainability_index": maintainability_index
    }
    print("\n🔍 Extracted 19 Features from:", file_path)
    for k, v in features.items():
        print(f"   {k:<25}: {v}")
    print(f"➡️ Total Features Extracted: {len(features)}\n")

    return features

# --------------------------------------------------------------------
# 🔹 2. Detect Long Methods via AST
# --------------------------------------------------------------------
def find_long_methods(file_path, threshold=10):
    """
    Detects Long Method smells using AST traversal.
    Returns a list of functions that exceed 'threshold' lines.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        long_methods = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start_line = node.lineno
                end_line = max(
                    [n.lineno for n in ast.walk(node) if hasattr(n, "lineno")],
                    default=start_line
                )
                length = end_line - start_line + 1

                if length >= threshold:
                    lines = source.split('\n')
                    snippet = '\n'.join(lines[start_line-1:end_line])
                    long_methods.append({
                        "function": node.name, "start": start_line, "end": end_line,
                        "length": length, "code_snippet": snippet
                    })

        print(f"\n🔍 AST Long Method Detection Results for {file_path}:")
        if not long_methods:
            print("   ⚠️ No long methods found.")
        else:
            for m in long_methods:
                print(f"   🧩 {m['function']} → Lines {m['start']}-{m['end']} ({m['length']} lines)")

        return long_methods

    except Exception as e:
        print(f"❌ Error in find_long_methods: {e}")
        return [{"error": str(e)}]

# --------------------------------------------------------------------
# 🔹 3. Detect Large Classes via AST
# --------------------------------------------------------------------
def find_large_classes(file_path, method_threshold=8, line_threshold=50):
    """
    Detects classes that are too large (many methods or lines).
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        tree = ast.parse(source)
        large_classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start = node.lineno
                end = max([n.lineno for n in ast.walk(node) if hasattr(n, "lineno")], default=start)
                total_lines = end - start + 1
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                num_methods = len(methods)

                if total_lines > line_threshold or num_methods > method_threshold:
                    lines = source.split('\n')
                    snippet = '\n'.join(lines[start-1:end])
                    large_classes.append({
                        "class": node.name, "start": start, "end": end,
                        "lines": total_lines, "num_methods": num_methods,
                        "code_snippet": snippet
                    })

        return large_classes

    except Exception as e:
        return [{"error": str(e)}]