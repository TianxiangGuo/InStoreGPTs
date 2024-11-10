import inspect
from datetime import datetime


def debug_print(debug: bool, *args: str) -> None:
    if not debug:
        return
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = " ".join(map(str, args))
    print(f"\033[97m[\033[90m{timestamp}\033[97m]\033[90m {message}\033[0m")


def merge_fields(target, source):
    for key, value in source.items():
        if isinstance(value, str):
            target[key] += value
        elif value is not None and isinstance(value, dict):
            merge_fields(target[key], value)


def merge_chunk(final_response: dict, delta: dict) -> None:
    delta.pop("role", None)
    merge_fields(final_response, delta)

    tool_calls = delta.get("tool_calls")
    if tool_calls and len(tool_calls) > 0:
        index = tool_calls[0].pop("index")
        merge_fields(final_response["tool_calls"][index], tool_calls[0])


def function_to_json(func) -> dict:
    """
    Converts a Python function into a JSON-serializable dictionary
    that describes the function's signature, including its name,
    description, and parameters.

    Args:
        func: The function to be converted.

    Returns:
        A dictionary representing the function's signature in JSON format.
    """
    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
        type(None): "null",
    }

    try:
        signature = inspect.signature(func)
    except ValueError as e:
        raise ValueError(
            f"Failed to get signature for function {func.__name__}: {str(e)}"
        )

    parameters = {}
    for param in signature.parameters.values():
        try:
            param_type = type_map.get(param.annotation, "string")
        except KeyError as e:
            raise KeyError(
                f"Unknown type annotation {param.annotation} for parameter {param.name}: {str(e)}"
            )
        parameters[param.name] = {"type": param_type}

    required = [
        param.name
        for param in signature.parameters.values()
        if param.default == inspect._empty
    ]

    return {
        "type": "function",
        "function": {
            "name": func.__name__,
            "description": func.__doc__ or "",
            "parameters": {
                "type": "object",
                "properties": parameters,
                "required": required,
            },
        },
    }

class TokenTracker:
    def __init__(self, cost_per_1m_input_tokens=2e-5, cost_per_1m_completion_tokens=2e-5):
        self.total_input_tokens = 0
        self.total_completion_tokens = 0
        self.total_tokens = 0
        self.estimated_cost = 0.0
        self.cost_per_1m_input_tokens = cost_per_1m_input_tokens
        self.cost_per_1m_completion_tokens = cost_per_1m_completion_tokens

    def update_tokens(self, input_tokens, completion_tokens):
        self.total_input_tokens += input_tokens
        self.total_completion_tokens += completion_tokens
        self.total_tokens += (input_tokens + completion_tokens)
        self._update_cost()

    def _update_cost(self):
        # Calculate estimated cost based on total tokens used
        self.estimated_cost = (self.total_input_tokens / 1e6) * self.cost_per_1m_input_tokens + (self.total_completion_tokens / 1e6) * self.cost_per_1m_completion_tokens

    def get_summary(self):
        return {
            "total_input_tokens": self.total_input_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost
        }

    def print_summary(self):
        summary = self.get_summary()
        print("Token Usage Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")