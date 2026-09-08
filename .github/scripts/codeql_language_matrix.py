"""Select CodeQL languages from tracked source on the checked-out revision."""

import json
from pathlib import PurePosixPath
import subprocess


def language_matrix(source_paths):
    """Keep supported source languages without scheduling empty databases."""
    extensions = {PurePosixPath(path).suffix for path in source_paths}
    language_extensions = {
        "javascript-typescript": {
            ".js",
            ".jsx",
            ".mjs",
            ".cjs",
            ".ts",
            ".tsx",
            ".mts",
            ".cts",
        },
        "python": {".py"},
        "go": {".go"},
        "ruby": {".rb"},
        "rust": {".rs"},
    }
    rows = [{"language": "actions", "build-mode": "none"}]
    for language, suffixes in language_extensions.items():
        if extensions & suffixes:
            rows.append(
                {
                    "language": language,
                    "build-mode": "autobuild" if language == "go" else "none",
                }
            )
    return {"include": rows}


if __name__ == "__main__":
    tracked_paths = (
        subprocess.check_output(["git", "ls-files", "-z"]).decode().split("\0")
    )
    print(json.dumps(language_matrix(tracked_paths), separators=(",", ":")))
