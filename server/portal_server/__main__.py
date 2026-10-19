import sys

MIN_PYTHON = (3, 14)


def check_python(version=None, stderr=None):
    """Exit non-zero with a clear message when Python is older than 3.14."""
    version = version or sys.version_info
    if tuple(version[:2]) < MIN_PYTHON:
        (stderr or sys.stderr).write(
            "agentic-portal requires Python >= %d.%d (found %d.%d)\n"
            % (MIN_PYTHON + tuple(version[:2]))
        )
        raise SystemExit(1)


check_python()

from portal_server.app import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
