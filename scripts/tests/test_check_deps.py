import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import check_deps  # noqa: E402

REPO = Path(__file__).resolve().parents[2]


class CheckDepsTest(unittest.TestCase):
    def pkg(self, source):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        (root / "mypkg").mkdir()
        (root / "mypkg" / "__init__.py").write_text("")
        (root / "mypkg" / "mod.py").write_text(source)
        return str(root)

    def test_fails_on_third_party(self):
        self.assertEqual(check_deps.main([self.pkg("import requests\n")]), 1)
        self.assertEqual(check_deps.main([self.pkg("from yaml import safe_load\n")]), 1)

    def test_passes_stdlib_local_relative(self):
        src = "import json\nfrom pathlib import Path\nfrom mypkg import mod\nfrom . import x\n"
        self.assertEqual(check_deps.main([self.pkg(src)]), 0)

    def test_jsonschema_only_under_tests(self):
        root = Path(self.pkg("import jsonschema\n"))
        self.assertEqual(check_deps.main([str(root)]), 1)
        (root / "tests").mkdir()
        (root / "tests" / "test_x.py").write_text("import jsonschema\n")
        (root / "mypkg" / "mod.py").write_text("")
        self.assertEqual(check_deps.main([str(root)]), 0)

    def test_server_is_clean(self):
        self.assertEqual(check_deps.main([str(REPO / "server")]), 0)


if __name__ == "__main__":
    unittest.main()
