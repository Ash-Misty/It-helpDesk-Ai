from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    result: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0.0
    simulated: bool = True
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseTool:
    name: str = ""
    description: str = ""
    safe: bool = True
    simulated: bool = True
    input_schema: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self):
        if not self.name:
            self.name = self.__class__.__name__.lower()

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        raise NotImplementedError("Subclasses must implement execute()")

    def validate_arguments(self, arguments: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        schema = self.input_schema
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        if not isinstance(arguments, dict):
            return False, "Arguments must be a JSON object."

        for field_name in required:
            if field_name not in arguments:
                return False, f"Missing required argument: '{field_name}'"

        allowed_keys = set(properties.keys())
        for key in arguments:
            if key not in allowed_keys:
                return False, f"Unknown argument: '{key}' is not a valid parameter for '{self.name}'."

        for field_name, value in arguments.items():
            prop_schema = properties.get(field_name, {})
            field_type = prop_schema.get("type")
            error = self._validate_type_and_constraints(field_name, value, field_type, prop_schema)
            if error:
                return False, error

        return True, None

    def _validate_type_and_constraints(
        self, field_name: str, value: Any, field_type: Optional[str], prop_schema: Dict[str, Any]
    ) -> Optional[str]:
        if value is None:
            return None

        if field_type == "string":
            if not isinstance(value, str):
                return f"Argument '{field_name}' must be a string."
            min_len = prop_schema.get("minLength")
            max_len = prop_schema.get("maxLength")
            if min_len is not None and len(value) < min_len:
                return f"Argument '{field_name}' must be at least {min_len} character(s) long."
            if max_len is not None and len(value) > max_len:
                return f"Argument '{field_name}' must be at most {max_len} character(s) long."
        elif field_type == "integer":
            if not isinstance(value, int) or isinstance(value, bool):
                return f"Argument '{field_name}' must be an integer."
            min_val = prop_schema.get("minimum")
            max_val = prop_schema.get("maximum")
            if min_val is not None and value < min_val:
                return f"Argument '{field_name}' must be >= {min_val}."
            if max_val is not None and value > max_val:
                return f"Argument '{field_name}' must be <= {max_val}."
        elif field_type == "number":
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                return f"Argument '{field_name}' must be a number."
        elif field_type == "boolean":
            if not isinstance(value, bool):
                return f"Argument '{field_name}' must be a boolean."
        elif field_type == "array":
            if not isinstance(value, list):
                return f"Argument '{field_name}' must be an array."
            min_items = prop_schema.get("minItems")
            max_items = prop_schema.get("maxItems")
            if min_items is not None and len(value) < min_items:
                return f"Argument '{field_name}' must have at least {min_items} items."
            if max_items is not None and len(value) > max_items:
                return f"Argument '{field_name}' must have at most {max_items} items."
        elif field_type == "object":
            if not isinstance(value, dict):
                return f"Argument '{field_name}' must be an object."

        return None

    def describe(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "safe": self.safe,
            "simulated": self.simulated,
            "input_schema": self.input_schema,
        }
