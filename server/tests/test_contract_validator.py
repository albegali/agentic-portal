import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from portal_server.contract.validator import (  # noqa: E402
    UnsupportedSchemaKeyword, Validator, check_subset, load_schemas)

SCHEMAS_DIR = Path(__file__).resolve().parents[2] / "schemas"


def v(schema, **extra):
    return Validator({"t.schema.json": schema, **extra})


def errs(schema, instance):
    return v(schema).errors(instance, "t.schema.json")


class KeywordTest(unittest.TestCase):
    def test_type_string_and_list(self):
        self.assertEqual(errs({"type": "string"}, "a"), [])
        self.assertTrue(errs({"type": "string"}, 1))
        self.assertEqual(errs({"type": ["string", "null"]}, None), [])
        self.assertTrue(errs({"type": "integer"}, True))
        self.assertTrue(errs({"type": "number"}, True))
        self.assertEqual(errs({"type": "number"}, 1.5), [])

    def test_required_properties_additional(self):
        s = {"type": "object", "required": ["a"], "properties": {"a": {"type": "string"}}, "additionalProperties": False}
        self.assertEqual(errs(s, {"a": "x"}), [])
        self.assertTrue(errs(s, {}))
        self.assertTrue(errs(s, {"a": 1}))
        self.assertTrue(errs(s, {"a": "x", "b": 1}))
        s["additionalProperties"] = {"type": "integer"}
        self.assertEqual(errs(s, {"a": "x", "b": 1}), [])
        self.assertTrue(errs(s, {"a": "x", "b": "no"}))

    def test_items_const_enum(self):
        self.assertTrue(errs({"type": "array", "items": {"type": "string"}}, ["a", 1]))
        self.assertTrue(errs({"const": "x"}, "y"))
        self.assertTrue(errs({"const": 1}, True))
        self.assertEqual(errs({"enum": ["a", "b"]}, "b"), [])
        self.assertTrue(errs({"enum": ["a"]}, "c"))

    def test_string_and_number_limits(self):
        self.assertTrue(errs({"minLength": 2}, "a"))
        self.assertTrue(errs({"pattern": r"^1\.\d+$"}, "2.0"))
        self.assertEqual(errs({"pattern": r"^1\.\d+$"}, "1.3"), [])
        self.assertTrue(errs({"minimum": 0}, -1))
        self.assertEqual(errs({"minimum": 0}, 0), [])

    def test_one_of_and_not(self):
        s = {"oneOf": [{"type": "string"}, {"type": "integer"}]}
        self.assertEqual(errs(s, "a"), [])
        self.assertTrue(errs(s, 1.5))
        self.assertTrue(errs({"oneOf": [{"type": "string"}, {"minLength": 1}]}, "a"))  # both match
        self.assertTrue(errs({"not": {"required": ["error"]}}, {"error": 1}))
        self.assertEqual(errs({"not": {"required": ["error"]}}, {}), [])

    def test_refs_local_and_sibling(self):
        shared = {"$defs": {"c": {"type": "string", "pattern": "^1"}}}
        main = {"properties": {"a": {"$ref": "shared.schema.json#/$defs/c"}, "b": {"$ref": "#/$defs/n"}},
                "$defs": {"n": {"type": "integer"}}}
        val = v(main, **{"shared.schema.json": shared})
        self.assertEqual(val.errors({"a": "1.0", "b": 2}, "t.schema.json"), [])
        self.assertTrue(val.errors({"a": "2.0", "b": 2}, "t.schema.json"))
        self.assertTrue(val.errors({"a": "1", "b": "x"}, "t.schema.json"))

    def test_ignored_keywords_accepted(self):
        check_subset({"$schema": "x", "$id": "y", "title": "t", "description": "d", "type": "object"})

    def test_unsupported_keyword_raises_at_load(self):
        for bad in ({"anyOf": []}, {"properties": {"a": {"format": "uri"}}}, {"items": {"minItems": 1}},
                    {"oneOf": [{"allOf": []}]}, {"$defs": {"x": {"if": {}}}}):
            with self.assertRaises(UnsupportedSchemaKeyword, msg=bad):
                check_subset(bad)
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "x.schema.json").write_text(json.dumps({"type": "object", "patternProperties": {}}))
            with self.assertRaises(UnsupportedSchemaKeyword):
                load_schemas(d)


class SkeletonSchemasTest(unittest.TestCase):
    def test_every_schema_file_stays_inside_the_subset(self):  # AC8
        self.assertTrue(SCHEMAS_DIR.is_dir(), "schemas/ missing")
        loaded = load_schemas(SCHEMAS_DIR)
        self.assertTrue({"envelope.schema.json", "version.schema.json"} <= set(loaded))

    def test_envelope_schema_accepts_and_rejects(self):
        val = Validator(load_schemas(SCHEMAS_DIR))
        ok = {"contract": "1.0", "tool": "version", "data": {"skeleton": "1.2.0", "contract": "1.0"}}
        self.assertEqual(val.errors(ok, "envelope.schema.json"), [])
        self.assertEqual(val.errors(ok, "version.schema.json"), [])
        self.assertTrue(val.errors({**ok, "tool": "next"}, "version.schema.json"))  # wrong tool (AC5)
        self.assertTrue(val.errors({"contract": "2.0", "tool": "x", "data": {}}, "envelope.schema.json"))
        self.assertTrue(val.errors({"contract": "1.0", "tool": "x"}, "envelope.schema.json"))
        self.assertTrue(val.errors({**ok, "error": {"code": "a", "message": "b"}}, "envelope.schema.json"))


if __name__ == "__main__":
    unittest.main()
