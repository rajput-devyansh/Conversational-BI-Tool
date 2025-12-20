import json
from pathlib import Path

SCHEMA_PATH = Path("metadata/schema.json")
BUSINESS_RULES_PATH = Path("metadata/business_rules.json")


def load_schema_context() -> str:
    with open(SCHEMA_PATH, "r") as f:
        schema = json.load(f)

    lines = []
    for table, meta in schema["tables"].items():
        lines.append(f"Table: {table}")
        lines.append(f"Description: {meta.get('description')}")
        for col, desc in meta.get("columns", {}).items():
            lines.append(f"  - {col}: {desc}")
        if "business_notes" in meta:
            lines.append("Business Notes:")
            for note in meta["business_notes"]:
                lines.append(f"  * {note}")
        lines.append("")

    return "\n".join(lines)


def load_business_rules_context() -> str:
    with open(BUSINESS_RULES_PATH, "r") as f:
        rules = json.load(f)

    # Keep this concise on purpose
    important_rules = [
        rules["metrics"]["revenue"],
        rules["customer_identity"],
        rules["category_handling"]
    ]

    return json.dumps(important_rules, indent=2)