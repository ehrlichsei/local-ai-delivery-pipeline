"""Tiny application used by the AI delivery pipeline demo."""


def calculate(operation: str, left: float, right: float) -> float:
    """Apply a basic arithmetic operation, rejecting invalid input."""
    if operation == "add":
        return left + right
    if operation == "subtract":
        return left - right
    if operation == "multiply":
        return left * right
    if operation == "power":
        return left ** right
    if operation == "divide":
        if right == 0:
            raise ValueError("Cannot divide by zero")
        return left / right
    if operation == "modulo":
        if right == 0:
            raise ValueError("Cannot divide by zero")
        return left % right
    raise ValueError(f"Unknown operation: {operation}")
