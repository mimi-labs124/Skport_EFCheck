import unittest
from pathlib import Path


class ReleaseDocsTests(unittest.TestCase):
    def test_required_docs_exist(self) -> None:
        required_files = [
            Path("CHANGELOG.md"),
            Path("CONTRIBUTING.md"),
            Path("docs/release.md"),
            Path("docs/packaging.md"),
            Path("docs/repo-metadata.md"),
            Path(".github/ISSUE_TEMPLATE/config.yml"),
            Path(".github/ISSUE_TEMPLATE/bug_report.yml"),
            Path(".github/ISSUE_TEMPLATE/bug_report.md"),
            Path(".github/ISSUE_TEMPLATE/feature_request.md"),
            Path(".github/pull_request_template.md"),
        ]

        for path in required_files:
            self.assertTrue(path.exists(), f"Missing required doc file: {path}")

    def test_release_docs_reference_v030_and_onedir_recommendation(self) -> None:
        changelog = Path("CHANGELOG.md").read_text(encoding="utf-8")
        release_doc = Path("docs/release.md").read_text(encoding="utf-8")
        readme = Path("README.md").read_text(encoding="utf-8")

        self.assertIn("Skport_Signin", changelog)
        self.assertIn("Skport_Signin", release_doc)
        self.assertIn("recommend **onedir** first", release_doc)
        self.assertIn("enabled: true/false", readme)
        self.assertIn("same-day completion state", readme)
        self.assertIn("Skport_Signin", readme)

    def test_ci_covers_windows_ruff_tests_and_packaging_smoke(self) -> None:
        ci_text = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")

        self.assertIn("windows-latest", ci_text)
        self.assertIn("ruff", ci_text)
        self.assertIn("python -m unittest discover -s tests", ci_text)
        self.assertIn("packaging-smoke-windows", ci_text)
        self.assertIn("python -m skport_signin package onedir", ci_text)
        self.assertIn("skport_signin.exe --help", ci_text)

    def test_package_version_matches_pyproject_toml(self) -> None:
        import skport_signin

        pyproject = Path("pyproject.toml").read_text(encoding="utf-8")
        for line in pyproject.splitlines():
            stripped = line.strip()
            if stripped.startswith("version"):
                pyproject_version = stripped.split("=", 1)[1].strip().strip('"')
                break
        else:
            self.fail("No version found in pyproject.toml")

        self.assertEqual(
            skport_signin.__version__,
            pyproject_version,
            "__init__.__version__ must match pyproject.toml version",
        )

    def test_register_task_name_matches_powershell_script_default(self) -> None:
        from skport_signin.commands.register_task import DEFAULT_TASK_NAME

        ps1_text = Path("register_logon_task.ps1").read_text(encoding="utf-8")
        self.assertIn(
            DEFAULT_TASK_NAME,
            ps1_text,
            "Python DEFAULT_TASK_NAME must match PowerShell script default",
        )


