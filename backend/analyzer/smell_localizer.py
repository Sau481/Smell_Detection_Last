import ast

def find_long_methods(file_path, threshold=50):
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)
    long_methods = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno
            # Try getting the last line of the function
            end_line = max([n.lineno for n in ast.walk(node) if hasattr(n, 'lineno')], default=start_line)
            length = end_line - start_line + 1

            if length > threshold:
                long_methods.append({
                    "function": node.name,
                    "start": start_line,
                    "end": end_line,
                    "length": length
                })

    return long_methods
