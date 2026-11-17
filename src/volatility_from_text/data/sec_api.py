"""Access to the SEC EDGAR API, with a local cache."""

import json
import os
from pathlib import Path
from time import sleep

import requests
from dotenv import load_dotenv

load_dotenv()


def sec_headers() -> dict[str, str]:
    """
    Return the HTTP headers required by the SEC, read from ``SEC_USER_AGENT``.

    Returns
    -------
    dict[str, str]
        Headers with the ``User-Agent`` set.
    """
    try:
        return {"User-Agent": os.environ["SEC_USER_AGENT"]}
    except KeyError:
        raise RuntimeError(
            'SEC_USER_AGENT is not set. Add SEC_USER_AGENT="Name email" to the .env file.'
        ) from None


def get_json(url: str, path: Path, headers: dict[str, str] | None = None) -> dict:
    """
    Read a JSON from disk if cached; otherwise download it and save it.

    After a download it waits 0.15 s to stay under the SEC limit of
    10 requests per second. Cache hits do not wait.

    Parameters
    ----------
    url : str
        URL of the JSON to download.
    path : pathlib.Path
        Local cache file. Parent directories are created if needed.
    headers : dict[str, str], optional
        HTTP headers. Defaults to ``sec_headers()``.

    Returns
    -------
    dict
        Parsed JSON.
    """
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    r = requests.get(url, headers=headers or sec_headers(), timeout=30)
    r.raise_for_status()
    sleep(0.15)                       # SEC limit: 10 requests per second

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(r.text, encoding="utf-8")
    return r.json()