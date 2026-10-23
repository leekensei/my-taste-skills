"""Run with python3 -m unittest discover -s tests -v; never touches user settings."""

import json
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ApplyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taste-apply-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.repo = self.work / "checkout with spaces"
        shutil.copytree(ROOT, self.repo, ignore=shutil.ignore_patterns(".git", "__pycache__", "node_modules", "results"))
        self.config = self.work / "config"
        self.config.mkdir()
        self.settings = self.config / "settings.json"

    def apply(self, *roles):
        return subprocess.run(
            [str(self.repo / "bin/apply"), *roles],
            cwd=self.work,
            env={**os.environ, "CLAUDE_CONFIG_DIR": str(self.config)},
            capture_output=True, text=True,
        )

    def read_settings(self):
        return json.loads(self.settings.read_text())

    def test_frontend_preserves_other_settings_and_resolves_checkout(self):
        original = {
            "env": {"KEEP": "yes"}, "permissions": {"allow": []},
            "hooks": {}, "enabledPlugins": {"other@external": True},
            "extraKnownMarketplaces": {"external": {"source": {"source": "github", "repo": "example/external"}}},
        }
        self.settings.write_text(json.dumps(original))
        result = self.apply("frontend")
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = self.read_settings()
        for key in ("env", "permissions", "hooks"):
            self.assertEqual(actual[key], original[key])
        self.assertEqual(actual["enabledPlugins"], {
            "other@external": False, "react-composition@my-taste-skills": True,
            "feature-sliced-design@my-taste-skills": True,
            "vercel-react-best-practices@my-taste-skills": True,
        })
        self.assertEqual(actual["extraKnownMarketplaces"]["external"], original["extraKnownMarketplaces"]["external"])
        source = actual["extraKnownMarketplaces"]["my-taste-skills"]["source"]
        self.assertEqual(source, {"source": "directory", "path": str(self.repo)})
        self.assertEqual(len(list(self.config.glob("settings.json.before-apply.*"))), 1)

    def test_new_settings_union_repeat_and_role_switch(self):
        (self.repo / "roles/extra.json").write_text('{"other@omc":true}')
        result = self.apply("frontend", "extra")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.read_settings()["enabledPlugins"], {
            "react-composition@my-taste-skills": True, "other@omc": True,
            "feature-sliced-design@my-taste-skills": True,
            "vercel-react-best-practices@my-taste-skills": True,
        })
        before = self.settings.read_bytes()
        result = self.apply("frontend", "extra")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.settings.read_bytes(), before)
        self.assertEqual(list(self.config.glob("settings.json.before-apply.*")), [])
        result = self.apply("uiux")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(all(value is False for value in self.read_settings()["enabledPlugins"].values()))

    def test_invalid_role_inputs_leave_settings_untouched(self):
        self.settings.write_text('{"env":{"KEEP":"yes"}}')
        (self.repo / "roles/undeclared.json").write_text('{"plugin@missing":true}')
        (self.repo / "roles/broken.json").write_text('{')
        before = self.settings.read_bytes()
        for roles in ((), ("missing",), ("../frontend",), ("undeclared",), ("broken",)):
            with self.subTest(roles=roles):
                self.assertNotEqual(self.apply(*roles).returncode, 0)
                self.assertEqual(self.settings.read_bytes(), before)
        self.assertEqual(list(self.config.glob("settings.json.before-apply.*")), [])

    def test_invalid_directory_source_leaves_settings_untouched(self):
        self.settings.write_text('{}')
        before = self.settings.read_bytes()
        file = self.repo / "marketplaces.json"
        markets = json.loads(file.read_text())
        for path in (None, "", 42):
            with self.subTest(path=path):
                markets["my-taste-skills"]["source"]["path"] = path
                file.write_text(json.dumps(markets))
                self.assertNotEqual(self.apply("frontend").returncode, 0)
                self.assertEqual(self.settings.read_bytes(), before)
        self.assertEqual(list(self.config.glob("settings.json.before-apply.*")), [])

    def test_invalid_settings_are_preserved(self):
        self.settings.write_text('{"enabledPlugins":[]}')
        before = self.settings.read_bytes()
        self.assertNotEqual(self.apply("frontend").returncode, 0)
        self.assertEqual(self.settings.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
