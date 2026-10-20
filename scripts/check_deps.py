"""Fail if a Python package imports anything outside the standard library or itself.

Usage: python scripts/check_deps.py <dir> [<dir> ...]
Test-only: `jsonschema` is allowed under a `tests/` directory (contract tests), never in runtime code.
Local names: top-level modules/packages found inside the checked directories
(including tests importing the package under test).
"""
import ast
import sys
from pathlib import Path


TEST_ONLY = {"jsonschema", "referencing"}


def local_names(roots):
    names = set()
    for root in roots:
        for p in Path(root).iterdir():
            if p.is_dir() and (p / "__init__.py").exists():
                names.add(p.name)
            elif p.suffix == ".py":
                names.add(p.stem)
    return names


def imports(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                yield node.lineno, a.name.split(".")[0]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            yield node.lineno, node.module.split(".")[0]


def check(roots):
    allowed = set(sys.stdlib_module_names) | local_names(roots)
    violations = []
    for root in roots:
        for path in sorted(Path(root).rglob("*.py")):
            for line, mod in imports(path):
                if mod in TEST_ONLY and "tests" in path.parts:
                    continue
                if mod not in allowed:
                    violations.append("%s:%d: third-party import %r" % (path, line, mod))
    return violations


def main(argv=None):
    roots = argv if argv is not None else sys.argv[1:]
    if not roots:
        print("usage: check_deps.py <dir> ...", file=sys.stderr)
        return 2
    violations = check(roots)
    for v in violations:
        print(v, file=sys.stderr)
    if violations:
        return 1
    print("dependency check OK: stdlib only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
