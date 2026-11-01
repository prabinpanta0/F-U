import os

def _int(name, default):
    try:
        return int(os.getenv(name, default))
    except (TypeError, ValueError):
        return default

def _float(name, default):
    try:
        return float(os.getenv(name, default))
    except (TypeError, ValueError):
        return float(default)

def _bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}

# Credentials
GITHUB_TOKEN = os.getenv("TOKEN")
GITHUB_USERNAME = os.getenv("USERNAME")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# API behaviour
API_BASE = os.getenv("API_BASE", "https://api.github.com")
API_VERSION = "2022-11-28"
PER_PAGE = 100
REQUEST_TIMEOUT = _int("REQUEST_TIMEOUT", 30)

# Retry / backoff
MAX_RETRIES = _int("MAX_RETRIES", 5)
BASE_BACKOFF = _float("BASE_BACKOFF", 1.0)
MAX_BACKOFF = _float("MAX_BACKOFF", 60)
BACKOFF_JITTER = _float("BACKOFF_JITTER", 0.3)

# Rate limiting
RATE_LIMIT_RESERVE = _int("RATE_LIMIT_RESERVE", 10)

# Safety limits
MAX_ACTIONS_PER_RUN = _int("MAX_ACTIONS_PER_RUN", 0)  # 0 = unlimited
DRY_RUN = _bool("DRY_RUN", False)

# ETag cache (keep out of version control)
ETAG_CACHE_FILE = os.getenv("ETAG_CACHE_FILE", ".github_api_cache.json")

# Throttle between individual follow/unfollow calls (seconds)
ACTION_DELAY = _float("ACTION_DELAY", 2)
