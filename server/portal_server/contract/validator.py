"""Stdlib validator for the JSON Schema 2020-12 subset used by the skeleton's `schemas/` (ADR-002 revision 2026-10-20).

Supported: $schema/$id/title/description (ignored), $ref (local `#/...` and sibling files), $defs, type, properties,
required, additionalProperties, items, const, enum, minLength, minimum, pattern, oneOf, not.
Any other keyword raises UnsupportedSchemaKeyword when the schemas are loaded, so drift is caught by CI.
"""
import json
import re
from pathlib import Path

IGNORED = {"$schema", "$id", "title", "description"}
SUPPORTED = IGNORED | {"$ref", "$defs", "type", "properties", "required", "additionalProperties", "items",
                       "const", "enum", "minLength", "minimum", "pattern", "oneOf", "not"}
TYPES = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


class UnsupportedSchemaKeyword(Exception):
    """A schema uses a keyword outside the supported subset (internal error: update the validator or the schema)."""


def check_subset(schema, where="#"):
    """Raise UnsupportedSchemaKeyword for any keyword outside SUPPORTED, walking only schema positions."""
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise UnsupportedSchemaKeyword("%s: a schema must be an object or boolean" % where)
    for key, value in schema.items():
        if key not in SUPPORTED:
            raise UnsupportedSchemaKeyword("%s: keyword %r is not in the supported subset" % (where, key))
        if key in ("properties", "$defs"):
            for name, sub in value.items():
                check_subset(sub, "%s/%s/%s" % (where, key, name))
        elif key in ("items", "not") or (key == "additionalProperties" and not isinstance(value, bool)):
            check_subset(value, "%s/%s" % (where, key))
        elif key == "oneOf":
            for i, sub in enumerate(value):
                check_subset(sub, "%s/oneOf/%d" % (where, i))


def load_schemas(directory) -> dict:
    """Load every `*.schema.json` in a directory, keyed by file name; each is checked against the subset."""
    schemas = {}
    for path in sorted(Path(directory).glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        check_subset(schema, path.name)
        schemas[path.name] = schema
    return schemas


def _same(a, b):
    """JSON equality: True is not 1."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_same(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_same(x, y) for x, y in zip(a, b))
    return a == b


def _is_type(value, name):
    if name == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return isinstance(value, TYPES[name]) and not (name != "boolean" and isinstance(value, bool))


class Validator:
    def __init__(self, schemas: dict):
        self.schemas = schemas

    def errors(self, instance, schema_name: str) -> list:
        """Violations as `path: message` strings (empty list = valid)."""
        root = self.schemas[schema_name]
        out = []
        self._check(instance, root, root, schema_name, "$", out)
        return out

    def _resolve(self, ref, root, current):
        file_part, _, pointer = ref.partition("#")
        doc_name = Path(file_part).name if file_part else current
        if doc_name not in self.schemas:
            raise UnsupportedSchemaKeyword("$ref %r points outside the loaded schemas" % ref)
        node = self.schemas[doc_name]
        for part in [p for p in pointer.split("/") if p]:
            node = node[part.replace("~1", "/").replace("~0", "~")]
        return node, doc_name

    def _check(self, value, schema, root, doc, path, out):
        if isinstance(schema, bool):
            if not schema:
                out.append("%s: not allowed" % path)
            return
        if "$ref" in schema:
            target, target_doc = self._resolve(schema["$ref"], root, doc)
            self._check(value, target, self.schemas[target_doc], target_doc, path, out)
        if "type" in schema:
            types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
            if not any(_is_type(value, t) for t in types):
                out.append("%s: expected %s, got %s" % (path, "/".join(types), type(value).__name__))
                return
        if "const" in schema and not _same(value, schema["const"]):
            out.append("%s: expected %r" % (path, schema["const"]))
        if "enum" in schema and not any(_same(value, e) for e in schema["enum"]):
            out.append("%s: not one of %r" % (path, schema["enum"]))
        if isinstance(value, str):
            if "minLength" in schema and len(value) < schema["minLength"]:
                out.append("%s: shorter than %d" % (path, schema["minLength"]))
            if "pattern" in schema and not re.search(schema["pattern"], value):
                out.append("%s: does not match %s" % (path, schema["pattern"]))
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if "minimum" in schema and value < schema["minimum"]:
                out.append("%s: below %r" % (path, schema["minimum"]))
        if isinstance(value, dict):
            for key in schema.get("required", []):
                if key not in value:
                    out.append("%s: missing required %r" % (path, key))
            props = schema.get("properties", {})
            for key, sub in props.items():
                if key in value:
                    self._check(value[key], sub, root, doc, "%s.%s" % (path, key), out)
            extra = schema.get("additionalProperties", True)
            for key in value:
                if key not in props:
                    if extra is False:
                        out.append("%s: unexpected %r" % (path, key))
                    elif isinstance(extra, dict):
                        self._check(value[key], extra, root, doc, "%s.%s" % (path, key), out)
        if isinstance(value, list) and "items" in schema:
            for i, item in enumerate(value):
                self._check(item, schema["items"], root, doc, "%s[%d]" % (path, i), out)
        if "not" in schema:
            probe = []
            self._check(value, schema["not"], root, doc, path, probe)
            if not probe:
                out.append("%s: matches a forbidden schema" % path)
        if "oneOf" in schema:
            matching = 0
            for sub in schema["oneOf"]:
                probe = []
                self._check(value, sub, root, doc, path, probe)
                matching += not probe
            if matching != 1:
                out.append("%s: matches %d of the oneOf alternatives (need exactly 1)" % (path, matching))
