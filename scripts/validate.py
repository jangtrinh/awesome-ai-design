"""Validate data/tools.yaml against data/schema/tool.schema.json.
Reports every problem at once, with the entry slug and the field path, then exits 1 if any were found."""
import json, pathlib, sys
import jsonschema, yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data/tools.yaml"
SCHEMA = ROOT / "data/schema/tool.schema.json"


def validate(data, schema):
    errors = []
    if not isinstance(data, dict) or not isinstance(data.get("tools"), list):
        return ["top level must be a mapping with a `tools:` list"]
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    seen = {}
    for i, t in enumerate(data["tools"]):
        where = f"tools[{i}]"
        if isinstance(t, dict) and t.get("slug"):
            where += f" ({t['slug']})"
            if t["slug"] in seen:
                errors.append(f"{where}: duplicate slug, first used at tools[{seen[t['slug']]}]")
            seen.setdefault(t["slug"], i)
        for e in sorted(validator.iter_errors(t), key=lambda e: list(e.path)):
            field = ".".join(str(p) for p in e.path) or "(entry)"
            errors.append(f"{where}: {field}: {e.message}")
    return errors


def main():
    try:
        data = yaml.safe_load(DATA.read_text())
    except yaml.YAMLError as e:
        print(f"::error file=data/tools.yaml::YAML does not parse: {e}")
        return 1
    errors = validate(data, json.loads(SCHEMA.read_text()))
    for e in errors:
        print(f"::error file=data/tools.yaml::{e}")
    if errors:
        print(f"\n{len(errors)} problem(s) in data/tools.yaml. Fix them there; the schema is data/schema/tool.schema.json.")
        return 1
    print(f"ok: {len(data['tools'])} entries match the schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
