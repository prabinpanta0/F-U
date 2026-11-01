import email.utils
import json
import os
import random
import time

import requests

import config


class ApiResult:
    """Normalised result so callers can inspect status and parsed payload."""

    def __init__(self, status_code, headers, data):
        self.status_code = status_code
        self.headers = headers or {}
        self.data = data

    @property
    def ok(self):
        return 200 <= self.status_code < 300

    def __repr__(self):
        return f"ApiResult(status={self.status_code}, data={self.data!r})"


class GitHubClient:
    """Small GitHub REST client with pagination, ETag caching and backoff."""

    def __init__(self, token=None, base_url=None, session=None):
        self.token = token or config.GITHUB_TOKEN
        self.base_url = (base_url or config.API_BASE).rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": config.API_VERSION,
                "User-Agent": "F-U-automation",
            }
        )
        self._cache = self._load_cache()

    # ------------------------------------------------------------------ cache
    def _load_cache(self):
        try:
            with open(config.ETAG_CACHE_FILE, encoding="utf-8") as handle:
                return json.load(handle)
        except (FileNotFoundError, ValueError, OSError):
            return {}

    def _save_cache(self):
        tmp_path = f"{config.ETAG_CACHE_FILE}.tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as handle:
                json.dump(self._cache, handle)
            os.replace(tmp_path, config.ETAG_CACHE_FILE)
        except OSError as exc:
            print(f"Could not persist API cache: {exc}")

    # ---------------------------------------------------------------- helpers
    def _url(self, path):
        return path if path.startswith("http") else f"{self.base_url}{path}"

    @staticmethod
    def _retry_after_seconds(response):
        header = response.headers.get("Retry-After")
        if header:
            try:
                return max(float(header), 0.0)
            except ValueError:
                try:
                    when = email.utils.parsedate_to_datetime(header).timestamp()
                    return max(when - time.time(), 0.0)
                except (TypeError, ValueError):
                    pass
        reset = response.headers.get("X-RateLimit-Reset")
        if reset and response.headers.get("X-RateLimit-Remaining") == "0":
            try:
                return max(float(reset) - time.time(), 0.0) + 2
            except ValueError:
                pass
        return None

    @staticmethod
    def _backoff_delay(attempt):
        delay = min(config.BASE_BACKOFF * (2 ** attempt), config.MAX_BACKOFF)
        return delay + random.uniform(0, delay * config.BACKOFF_JITTER)

    @staticmethod
    def _warn_low_quota(response):
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is None:
            return
        try:
            remaining = int(remaining)
        except ValueError:
            return
        if 0 < remaining <= config.RATE_LIMIT_RESERVE:
            print(f"Warning: only {remaining} API requests left this hour.")

    def _wait_for_rate_limit(self, response):
        if response.headers.get("X-RateLimit-Remaining") == "0":
            wait = self._retry_after_seconds(response)
            if wait is None:
                wait = min(config.MAX_BACKOFF, 60)
            print(f"Primary rate limit exhausted, sleeping {wait:.0f}s.")
            time.sleep(wait)
            return True
        return False

    # ---------------------------------------------------------------- request
    def request(self, method, path, use_etag=False, **kwargs):
        """Send a request, retrying transient errors with exponential backoff."""
        url = self._url(path)
        kwargs.setdefault("timeout", config.REQUEST_TIMEOUT)

        cache_key = _cache_key(method, url, kwargs.get("params"))
        cached = self._cache.get(cache_key) if use_etag else None
        if cached and cached.get("etag"):
            kwargs["headers"] = dict(
                kwargs.get("headers") or {}, **{"If-None-Match": cached["etag"]}
            )

        last_error = None
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                response = self.session.request(method, url, **kwargs)
            except requests.RequestException as exc:
                last_error = exc
                if attempt == config.MAX_RETRIES:
                    raise
                delay = self._backoff_delay(attempt)
                print(f"Request error ({exc.__class__.__name__}), retrying in {delay:.1f}s.")
                time.sleep(delay)
                continue

            if use_etag and response.status_code == 304 and cached:
                return ApiResult(200, response.headers, cached["body"])

            if response.status_code < 400:
                self._warn_low_quota(response)
                data = _parse_json(response)
                if use_etag and response.headers.get("ETag"):
                    self._cache[cache_key] = {
                        "etag": response.headers["ETag"],
                        "body": data,
                    }
                    self._save_cache()
                return ApiResult(response.status_code, response.headers, data)

            if self._wait_for_rate_limit(response):
                continue

            retry_after = self._retry_after_seconds(response)
            if retry_after is not None:
                print(f"Server asked to retry in {retry_after:.0f}s.")
                time.sleep(retry_after)
                continue

            retryable = response.status_code in (408, 429) or response.status_code >= 500
            if retryable and attempt < config.MAX_RETRIES:
                delay = self._backoff_delay(attempt)
                print(f"HTTP {response.status_code}, retrying in {delay:.1f}s.")
                time.sleep(delay)
                continue

            return ApiResult(response.status_code, response.headers, _parse_json(response))

        raise last_error if last_error else RuntimeError("request failed")

    def paginate(self, path, params=None, use_etag=True):
        """Yield every item across all pages, following the Link header."""
        url = self._url(path)
        query = dict(params or {})
        query.setdefault("per_page", config.PER_PAGE)

        while url:
            result = self.request("GET", url, params=query, use_etag=use_etag)
            if not result.ok:
                print(f"Could not fetch {url}: HTTP {result.status_code}")
                return
            if not isinstance(result.data, list):
                return
            for item in result.data:
                yield item
            url = _next_link(result.headers)
            query = None

    # --------------------------------------------------------------- actions
    def get_following(self):
        return [
            user["login"]
            for user in self.paginate(f"/users/{config.GITHUB_USERNAME}/following")
        ]

    def get_followers(self):
        return [
            user["login"]
            for user in self.paginate(f"/users/{config.GITHUB_USERNAME}/followers")
        ]

    def is_following(self, user, target):
        """True if `user` currently follows `target`."""
        return self.request("GET", f"/users/{user}/following/{target}").status_code == 204

    def is_follower(self, user, target):
        """True if `user` is currently followed by `target`."""
        return self.request("GET", f"/users/{user}/followers/{target}").status_code == 204

    def follow(self, user):
        return self.request("PUT", f"/user/following/{user}").ok

    def unfollow(self, user):
        return self.request("DELETE", f"/user/following/{user}").ok


def _cache_key(method, url, params=None):
    if not params:
        return f"{method.upper()} {url}"
    query = "&".join(f"{key}={value}" for key, value in sorted(params.items()))
    return f"{method.upper()} {url}?{query}"


def _parse_json(response):
    if response.status_code == 204 or not response.content:
        return {}
    try:
        return response.json()
    except ValueError:
        return {}


def _next_link(headers):
    link_header = headers.get("Link") if headers else None
    if not link_header:
        return None
    for part in link_header.split(","):
        segments = part.split(";")
        if len(segments) < 2:
            continue
        url = segments[0].strip().strip("<>")
        if any(attr.strip() == 'rel="next"' for attr in segments[1:]):
            return url
    return None
