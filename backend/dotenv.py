import os


def load_dotenv(path: str = ".env") -> None:
    """
    Minimal .env loader (no external dependency).
    - Only sets keys that are not already in os.environ.
    - Supports KEY=VALUE with optional quotes.
    - Ignores comments and empty lines.
    """
    if not os.path.exists(path):
        return

    try:
        with open(path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue

                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()

                if not key or key in os.environ:
                    continue

                # Remove surrounding quotes
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
                    value = value[1:-1]

                os.environ[key] = value
    except Exception:
        # Never crash the app due to dotenv parsing
        return

