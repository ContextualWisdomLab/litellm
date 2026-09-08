"""Exercise the reusable workflow's real Bash test-path expansion."""

import os
from pathlib import Path
import subprocess
import textwrap

import pytest


@pytest.mark.parametrize(
    "selector,expected,exit_code",
    [
        ("test_*.py", {"test_first.py", "test_second.py"}, 0),
        (
            "test_first.py::test_case --ignore=test_second.py",
            {"test_first.py::test_case", "--ignore=test_second.py"},
            0,
        ),
        ("missing_*.py", set(), 1),
    ],
)
def test_workflow_expands_paths_without_evaluating_shell(
    selector, expected, exit_code, tmp_path
):
    """Globs collect files, node IDs remain literal, and empty matches fail."""
    workflow = (
        Path(__file__).parents[1] / ".github/workflows/_test-unit-base.yml"
    ).read_text()
    start = workflow.index("          read -r -a test_args")
    end = workflow.index("          poetry run pytest", start)
    script = textwrap.dedent(workflow[start:end])
    for name in ("test_first.py", "test_second.py"):
        (tmp_path / name).touch()
    result = subprocess.run(
        ["bash", "-e", "-c", script + '\nprintf "%s\\n" "${expanded_test_args[@]}"'],
        cwd=tmp_path,
        env={**os.environ, "TEST_PATH": selector},
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == exit_code
    assert set(result.stdout.splitlines()) == expected
