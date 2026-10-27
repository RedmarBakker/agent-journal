from dataclasses import dataclass, field

# the Python type each JSON schema type asks for
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "integer": int}


@dataclass(frozen=True)
class SchemaNode:
    """One node of the command table's JSON schema: the type it asks for, the definition it points to, the node an array's items follow, an object's named keys with their nodes, the keys it requires, whether keys it does not name are refused, and the node they follow when they are not; it names the faults a value holds against it, each by where it stands."""

    type: str = ""
    reference: str = ""
    items: tuple["SchemaNode", ...] = ()
    properties: dict[str, "SchemaNode"] = field(default_factory=dict)
    required: tuple[str, ...] = ()
    closed: bool = False
    extra_keys: tuple["SchemaNode", ...] = ()

    @classmethod
    def parsed(cls, data: dict) -> "SchemaNode":
        additional = data.get("additionalProperties", {})
        return cls(type=data.get("type", ""), reference=data.get("$ref", "").rsplit("/", 1)[-1], items=tuple(cls.parsed(data[key]) for key in ("items",) if key in data),
                   properties={name: cls.parsed(node) for name, node in data.get("properties", {}).items()}, required=tuple(data.get("required", ())),
                   closed=additional is False, extra_keys=(cls.parsed(additional),) if isinstance(additional, dict) and additional else ())

    def faults(self, value, path: str, definitions: dict[str, "SchemaNode"]) -> list[str]:
        if self.reference:
            return definitions[self.reference].faults(value, path, definitions)
        if not isinstance(value, TYPES.get(self.type, object)):
            return [f"{path}: not {self.type}"]
        if isinstance(value, list):
            return [fault for index, item in enumerate(value) for node in self.items for fault in node.faults(item, f"{path}[{index}]", definitions)]
        return self.object_faults(value, path, definitions) if isinstance(value, dict) else []

    def object_faults(self, value: dict, path: str, definitions: dict[str, "SchemaNode"]) -> list[str]:
        missing = [f"{path}: {key} missing" for key in self.required if key not in value]
        refused = [f"{path}: {key} is not allowed" for key in value if key not in self.properties and self.closed]
        return missing + refused + [fault for key, item in value.items() for node in self.key_nodes(key) for fault in node.faults(item, f"{path}.{key}", definitions)]

    def key_nodes(self, key: str) -> tuple["SchemaNode", ...]:
        return (self.properties[key],) if key in self.properties else self.extra_keys
