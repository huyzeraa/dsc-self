# By huyzeraa - Vxrn Team -- All rights reserved

import sys
import subprocess
import asyncio
import json
import time
import random
import logging
import socket
import os
import re
import uuid
import base64
import unicodedata
from logging.handlers import RotatingFileHandler
from enum import Enum
from pathlib import Path
from typing import Optional, Any, Dict, List, Tuple

VERSION = "4.1.0"
CONFIG_PATH = Path("setting.json")
API_BASE = "https://discord.com/api/v9"
GATEWAY_URL = "wss://gateway.discord.gg/?v=9&encoding=json"

THEME_PALETTE = ["#35d65f", "#16d8b2", "#20c5f5", "#2b7cff", "#6b4dff"]

CHANNEL_ID = "1089798989836202054"
BOT_ID = "1009562541246136403"
GUILD_ID = "846496831533088768"

WORK_CMD_ID = "1043667736007557141"
WORK_CMD_VER = "1292660387698835527"
WORK_MIN_DELAY = 330
WORK_MAX_DELAY = 440

BAL_CMD_ID = "1047852302507180042"
BAL_CMD_VER = "1047852302507180043"
BAL_MIN_DELAY = 1200
BAL_MAX_DELAY = 1500

_runtime_settings: Dict[str, Any] = {}

def _get_timing(key_min: str, key_max: str, key_fixed: str,
                default_min: int, default_max: int) -> int:
    s = _runtime_settings
    fixed = s.get(key_fixed)
    if fixed and int(fixed) > 0:
        return int(fixed)
    lo = int(s.get(key_min, default_min))
    hi = int(s.get(key_max, default_max))
    if lo >= hi:
        return lo
    return random.randint(lo, hi)


def load_settings_into_runtime(cfg: Dict[str, Any]) -> None:
    timing = cfg.get("timing", {})
    _runtime_settings.update(timing)


LOGO = [
    r"                                                                                         ",
    r" ,---.   ,--.     ,--.,--.,--.   ,--.     ,---.         ,--. ,---.,--.            ,--. ",
    r"'   .-',-'  '-. ,-|  |`--' \  `.'  /     '   .-'  ,---. |  |/  .-'|  |-.  ,---. ,-'  '-.",
    r"`.  `-.'-.  .-'' .-. |,--.  .'    \      `.  `-. | .-. :|  ||  `-,| .-. '| .-. |'-.  .-'",
    r".-'    | |  |  \ `-' ||  | /  .'.  \     .-'    |\   --.|  ||  .-'| `-' |' '-' '  |  |  ",
    r"`-----'  `--'   `---' `--''--'   '--'    `-----'  `----'`--'`--'   `---'  `---'   `--'  ",
    r"                                                                                         ",
]

CLIENT_PROFILES = {
    "windows_chrome": {
        "name": "Windows 11 / Chrome",
        "os": "Windows",
        "browser": "Chrome",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "browser_version": "131.0.0.0",
        "os_version": "10",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "windows_app": {
        "name": "Windows 11 / Discord App",
        "os": "Windows",
        "browser": "Discord Client",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9175 Chrome/128.0.6613.186 Electron/32.2.7 Safari/537.36",
        "browser_version": "32.2.7",
        "os_version": "10.0.22631",
        "client_build_number": 354920,
        "client_version": "1.0.9175",
        "release_channel": "stable"
    },
    "windows_edge": {
        "name": "Windows 11 / Edge",
        "os": "Windows",
        "browser": "Edge",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        "browser_version": "131.0.0.0",
        "os_version": "10",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "iphone_safari": {
        "name": "iPhone 15 Pro / Safari",
        "os": "iOS",
        "browser": "Safari",
        "device": "iPhone",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
        "browser_version": "17.5",
        "os_version": "17.5.1",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "iphone_app": {
        "name": "iPhone 15 Pro / Discord iOS",
        "os": "iOS",
        "browser": "Discord iOS",
        "device": "iPhone15,2",
        "system_locale": "vi-VN",
        "browser_user_agent": "Discord-iOS/230.0 (iPhone; iOS 17.5.1; Scale/3.00)",
        "browser_version": "230.0",
        "os_version": "17.5.1",
        "client_build_number": 61240,
        "release_channel": "stable"
    },
    "android_chrome": {
        "name": "Android 14 / Chrome Mobile",
        "os": "Android",
        "browser": "Chrome Mobile",
        "device": "Android",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.135 Mobile Safari/537.36",
        "browser_version": "131.0.6778.135",
        "os_version": "14",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "android_app": {
        "name": "Android 14 / Discord App",
        "os": "Android",
        "browser": "Discord Android",
        "device": "Pixel 8 Pro",
        "system_locale": "vi-VN",
        "browser_user_agent": "Discord-Android/234.4 (2340400; Android 14; Pixel 8 Pro)",
        "browser_version": "234.4",
        "os_version": "14",
        "client_build_number": 61420,
        "release_channel": "stable"
    },
    "macos_safari": {
        "name": "macOS Sonoma / Safari",
        "os": "Mac OS X",
        "browser": "Safari",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_6_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        "browser_version": "18.1",
        "os_version": "14.6.1",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "macos_chrome": {
        "name": "macOS Sonoma / Chrome",
        "os": "Mac OS X",
        "browser": "Chrome",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "browser_version": "131.0.0.0",
        "os_version": "10.15.7",
        "client_build_number": 354680,
        "release_channel": "stable"
    },
    "linux_firefox": {
        "name": "Linux / Firefox",
        "os": "Linux",
        "browser": "Firefox",
        "device": "",
        "system_locale": "vi-VN",
        "browser_user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        "browser_version": "132.0",
        "os_version": "",
        "client_build_number": 354680,
        "release_channel": "stable"
    }
}


class HostEnvironment(Enum):
    WINDOWS = "Windows"
    TERMUX = "Termux"
    HOSTING = "Hosting/Container"
    LINUX = "Linux"


def detect_host_environment() -> HostEnvironment:
    if "TERMUX_VERSION" in os.environ or os.path.exists("/data/data/com.termux"):
        return HostEnvironment.TERMUX
    if os.name == "nt" or sys.platform == "win32":
        return HostEnvironment.WINDOWS
    if (
        os.path.exists("/home/container")
        or "P_SERVER_UUID" in os.environ
        or os.path.exists("/.dockerenv")
        or "RENDER" in os.environ
        or "RAILWAY_ENVIRONMENT" in os.environ
        or not sys.stdin.isatty()
    ):
        return HostEnvironment.HOSTING
    return HostEnvironment.LINUX


class WorkerState(Enum):
    STARTUP = "startup"
    CONNECTING = "connecting"
    READY = "ready"
    TYPING = "typing"
    DISPATCHING = "dispatching"
    WAITING_REPLY = "awaiting_reply"
    IDLE = "idle"
    COOLDOWN = "cooldown"
    BACKOFF = "backoff"
    DISCONNECTED = "disconnected"


class PreflightResult(Enum):
    OK              = "ok"
    NOT_IN_GUILD    = "not_in_guild"
    SLOWMODE        = "slowmode"
    SEND_BLOCKED    = "send_blocked"
    VERIFICATION    = "verification"
    AGE_RESTRICTED  = "age_restricted"
    NO_PERMISSION   = "no_permission"
    UNKNOWN         = "unknown_error"


_label_username: Dict[str, str] = {}

_LABEL_RE = re.compile(r"^\[([^\]]+)\]\s*")

class PlainLogHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: List[str] = []
        self.max_records = 25

    def emit(self, record: logging.LogRecord) -> None:
        try:
            ts = time.strftime("%H:%M:%S", time.localtime(record.created))
            lvl = record.levelname.lower()
            msg = record.getMessage()
            color = {
                "info": "cyan",
                "warning": "yellow",
                "error": "red",
            }.get(lvl, "white")

            m = _LABEL_RE.match(msg)
            if m:
                label = m.group(1)
                rest  = msg[m.end():]
                name  = _label_username.get(label, label)
                prefix = f"[dim]{ts}[/] [[white]{name}[/]] [{color}]{lvl:<5}[/] "
            else:
                prefix = f"[dim]{ts}[/] [{color}]{lvl:<5}[/] "
                rest   = msg

            self.records.append(prefix + rest)
            if len(self.records) > self.max_records:
                self.records.pop(0)
        except Exception:
            pass

    def get_lines(self) -> List[str]:
        return self.records


log_sink = PlainLogHandler()
logger = logging.getLogger("worker")
logger.setLevel(logging.INFO)
logger.addHandler(log_sink)

if len(logger.handlers) <= 1:
    fh = RotatingFileHandler("worker.log", maxBytes=5 * 1024 * 1024, backupCount=2, encoding="utf-8")
    fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(fh)


def check_dependencies():
    import importlib.util
    missing = [p for p in ("aiohttp", "rich", "aiohttp_socks") if importlib.util.find_spec(p) is None]
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        os.execv(sys.executable, [sys.executable] + sys.argv)


check_dependencies()

import aiohttp
from aiohttp_socks import ProxyConnector, ProxyType
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.console import Group
from rich.text import Text

CONSOLE = Console()



class ClientRuntime:
    def __init__(self) -> None:
        self.state = WorkerState.STARTUP
        self.username = "unknown"
        self.user_id = ""

        self.total_works = 0
        self.session_earned = 0
        self.last_earned = 0
        self.last_work_at = "n/a"
        self.next_work_countdown = 0

        self.current_balance: Optional[int] = None
        self.leaderboard_rank = "n/a"
        self.last_balance_at = "n/a"
        self.next_balance_countdown = 0



_PROBE_PROTOCOLS = ["socks5", "socks4", "http", "https"]
_SCHEME_RE = re.compile(r"^(socks5h?|socks4a?|https?):?//", re.I)

class ProxyConfig:
    __slots__ = ("scheme", "host", "port", "username", "password", "url", "display")

    def __init__(self, scheme: str, host: str, port: int,
                 username: Optional[str] = None, password: Optional[str] = None) -> None:
        self.scheme = scheme.lower()
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        auth = f"{username}:{password}@" if username else ""
        self.url = f"{self.scheme}://{auth}{host}:{port}"
        self.display = f"{self.scheme}://{host}:{port}"

    def make_connector(self) -> aiohttp.BaseConnector:
        if self.scheme in ("http", "https"):
            return aiohttp.TCPConnector(family=socket.AF_INET)

        ptype = ProxyType.SOCKS5 if self.scheme.startswith("socks5") else ProxyType.SOCKS4
        return ProxyConnector(
            proxy_type=ptype,
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            family=socket.AF_INET,
        )

    def request_kwargs(self) -> Dict[str, Any]:
        if self.scheme in ("http", "https"):
            kwargs: Dict[str, Any] = {"proxy": self.url}
            if self.username:
                token = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
                kwargs["proxy_headers"] = {"Proxy-Authorization": f"Basic {token}"}
            return kwargs
        return {}


def _parse_proxy_str(raw: str, scheme: Optional[str] = None) -> Optional[ProxyConfig]:
    raw = raw.strip()
    if not raw or raw.lower() in ("none", "null", "-"):
        return None

    m = _SCHEME_RE.match(raw)
    if m:
        detected_scheme = m.group(1).lower()
        if detected_scheme.startswith("socks5"):
            detected_scheme = "socks5"
        elif detected_scheme.startswith("socks4"):
            detected_scheme = "socks4"
        raw = raw[m.end():]
        scheme = scheme or detected_scheme
    else:
        scheme = scheme or None

    user = password = None

    if "@" in raw:
        auth_part, raw = raw.rsplit("@", 1)
        if ":" in auth_part:
            user, password = auth_part.split(":", 1)
        else:
            user = auth_part

    parts = raw.split(":")
    if len(parts) == 4 and user is None:
        host, port_str, user, password = parts
    elif len(parts) == 2:
        host, port_str = parts
    elif len(parts) == 1:
        return None
    else:
        return None

    try:
        port = int(port_str)
    except ValueError:
        return None

    if not host or not (1 <= port <= 65535):
        return None

    return ProxyConfig(scheme or "http", host, port, user or None, password or None)


async def _probe_proxy(cfg: ProxyConfig, timeout: float = 5.0) -> float:
    t0 = time.monotonic()
    try:
        connector = cfg.make_connector()
        client_timeout = aiohttp.ClientTimeout(total=timeout, connect=timeout)
        async with aiohttp.ClientSession(connector=connector, timeout=client_timeout) as sess:
            kw = cfg.request_kwargs()
            async with sess.get(f"{API_BASE}/gateway", **kw) as resp:
                if resp.status in (200, 401, 403):
                    return time.monotonic() - t0
    except Exception:
        pass
    return float("inf")


async def resolve_proxy(raw: str) -> Optional[ProxyConfig]:
    if not raw or raw.strip().lower() in ("none", "null", "-", ""):
        return None

    has_scheme = bool(_SCHEME_RE.match(raw.strip()))
    if has_scheme:
        return _parse_proxy_str(raw)

    candidates = [_parse_proxy_str(raw, scheme=s) for s in _PROBE_PROTOCOLS]
    candidates = [c for c in candidates if c is not None]
    if not candidates:
        return None

    seen: Dict[str, ProxyConfig] = {}
    for c in candidates:
        key = f"{c.scheme}:{c.host}:{c.port}:{c.username}"
        if key not in seen:
            seen[key] = c

    candidates = list(seen.values())

    async def race_one(cfg: ProxyConfig) -> Tuple[float, ProxyConfig]:
        return await _probe_proxy(cfg), cfg

    tasks = [asyncio.create_task(race_one(c)) for c in candidates]
    best_cfg: Optional[ProxyConfig] = None
    best_time = float("inf")

    done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    for fut in done:
        elapsed, cfg = fut.result()
        if elapsed < best_time:
            best_time = elapsed
            best_cfg = cfg
    for t in pending:
        t.cancel()

    return best_cfg if best_time < float("inf") else None



class BeluWorkerClient:
    def __init__(self, token: str, proxy: Optional[ProxyConfig], profile_key: str, label: str = "") -> None:
        self.rt = ClientRuntime()
        self.host_env = detect_host_environment()
        self.token = token
        self.label = label

        self.proxy_cfg = proxy
        self.proxy_display = proxy.display if proxy else "direct"

        self.profile_key = profile_key if profile_key in CLIENT_PROFILES else "windows_chrome"
        self.profile_data = CLIENT_PROFILES[self.profile_key]
        self.x_super_properties_b64 = self.generate_super_properties()

        self.session_id: Optional[str] = None
        self.sequence: Optional[int] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.ws: Optional[aiohttp.ClientWebSocketResponse] = None

        self.pending_interaction_response: Optional[asyncio.Future] = None
        self.action_lock = asyncio.Lock()

        self.heartbeat_task: Optional[asyncio.Task] = None
        self.work_task: Optional[asyncio.Task] = None
        self.balance_task: Optional[asyncio.Task] = None
        self.ui_task: Optional[asyncio.Task] = None

        self.is_running = True
        self.boot_monotonic = time.monotonic()
        self.gateway_rtt = 0.0


    def generate_super_properties(self) -> str:
        p = self.profile_data
        payload = {
            "os": p["os"], "browser": p["browser"], "device": p["device"],
            "system_locale": p["system_locale"], "has_client_mods": False,
            "browser_user_agent": p["browser_user_agent"],
            "browser_version": p["browser_version"], "os_version": p["os_version"],
            "referrer": "", "referring_domain": "",
            "referrer_current": "", "referring_domain_current": "",
            "release_channel": p["release_channel"],
            "client_build_number": p["client_build_number"],
            "client_event_source": None,
            "client_launch_id": str(uuid.uuid4()),
            "launch_signature": str(uuid.uuid4()),
            "client_app_state": "focused",
            "client_heartbeat_session_id": str(uuid.uuid4()),
        }
        return base64.b64encode(json.dumps(payload, separators=(",", ":")).encode()).decode("ascii")

    def headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "User-Agent": self.profile_data["browser_user_agent"],
            "X-Super-Properties": self.x_super_properties_b64,
            "X-Discord-Locale": "vi",
            "X-Discord-Timezone": "Asia/Ho_Chi_Minh",
        }

    def build_nonce(self) -> str:
        return str(int((time.time() * 1000 - 1420070400000) * 4194304))


    def _proxy_kw(self) -> Dict[str, Any]:
        return self.proxy_cfg.request_kwargs() if self.proxy_cfg else {}

    async def fetch_user(self) -> bool:
        try:
            async with self.session.get(
                f"{API_BASE}/users/@me", headers=self.headers(), **self._proxy_kw()
            ) as res:
                if res.status == 200:
                    data = await res.json()
                    self.rt.user_id = str(data.get("id"))
                    self.rt.username = f"{data.get('username')}#{data.get('discriminator', '0')}"
                    return True
                elif res.status == 401:
                    logger.error(f"[{self.label}] token invalid or expired (401)")
                elif res.status == 403:
                    logger.error(f"[{self.label}] token forbidden (403) — possibly banned or restricted")
                else:
                    body = await res.text()
                    logger.error(f"[{self.label}] auth failed HTTP {res.status}: {body[:120]}")
        except Exception as e:
            logger.error(f"[{self.label}] auth request error: {e}")
        return False

    async def emit_typing(self) -> None:
        try:
            async with self.session.post(
                f"{API_BASE}/channels/{CHANNEL_ID}/typing",
                headers=self.headers(), **self._proxy_kw()
            ):
                pass
        except Exception:
            pass

    async def preflight_check(self) -> PreflightResult:
        try:
            async with self.session.get(
                f"{API_BASE}/guilds/{GUILD_ID}/members/{self.rt.user_id}",
                headers=self.headers(), **self._proxy_kw()
            ) as res:
                if res.status == 404:
                    return PreflightResult.NOT_IN_GUILD
                if res.status == 403:
                    return PreflightResult.NOT_IN_GUILD
                if res.status not in (200, 204):
                    body = await res.text()
                    code = self._discord_error_code(body)
                    return self._map_error_code(code, body)
        except Exception as e:
            logger.warning(f"[{self.label}] guild member check failed: {e}")

        try:
            async with self.session.get(
                f"{API_BASE}/channels/{CHANNEL_ID}",
                headers=self.headers(), **self._proxy_kw()
            ) as res:
                if res.status == 403:
                    body = await res.text()
                    code = self._discord_error_code(body)
                    return self._map_error_code(code, body)
                if res.status == 200:
                    data = await res.json()
                    slowmode = data.get("rate_limit_per_user", 0)
                    if slowmode > 0:
                        logger.warning(
                            f"[{self.label}] channel slowmode active: {slowmode}s per message"
                        )
        except Exception as e:
            logger.warning(f"[{self.label}] channel check failed: {e}")

        try:
            test_payload = {"content": "\u200b"}
            async with self.session.post(
                f"{API_BASE}/channels/{CHANNEL_ID}/messages",
                headers=self.headers(), json=test_payload, **self._proxy_kw()
            ) as res:
                if res.status in (200, 201):
                    data = await res.json()
                    msg_id = data.get("id")
                    if msg_id:
                        await self.session.delete(
                            f"{API_BASE}/channels/{CHANNEL_ID}/messages/{msg_id}",
                            headers=self.headers(), **self._proxy_kw()
                        )
                    return PreflightResult.OK
                body = await res.text()
                code = self._discord_error_code(body)
                return self._map_error_code(code, body)
        except Exception as e:
            logger.warning(f"[{self.label}] send permission probe failed ({e}), assuming OK")
            return PreflightResult.OK

    @staticmethod
    def _discord_error_code(body: str) -> int:
        try:
            return int(json.loads(body).get("code", 0))
        except Exception:
            return 0

    @staticmethod
    def _map_error_code(code: int, body: str) -> PreflightResult:
        SLOWMODE_CODES      = {20016, 20028}
        VERIFICATION_CODES  = {40003, 40033, 50013}
        SEND_BLOCKED_CODES  = {50007, 50013, 50083}
        AGE_CODES           = {50024}
        NO_PERM_CODES       = {50001, 50013, 10003}

        if code in SLOWMODE_CODES:
            return PreflightResult.SLOWMODE
        if code in AGE_CODES:
            return PreflightResult.AGE_RESTRICTED
        if code in VERIFICATION_CODES:
            return PreflightResult.VERIFICATION
        if code in SEND_BLOCKED_CODES:
            return PreflightResult.SEND_BLOCKED
        if code in NO_PERM_CODES:
            return PreflightResult.NO_PERMISSION
        body_l = body.lower()
        if "verification" in body_l or "membership screening" in body_l:
            return PreflightResult.VERIFICATION
        if "slowmode" in body_l:
            return PreflightResult.SLOWMODE
        if "missing permissions" in body_l or "missing access" in body_l:
            return PreflightResult.NO_PERMISSION
        if code != 0:
            return PreflightResult.UNKNOWN
        return PreflightResult.OK

    async def execute_work(self) -> bool:
        nonce = self.build_nonce()
        payload = {
            "type": 2, "application_id": BOT_ID,
            "guild_id": GUILD_ID, "channel_id": CHANNEL_ID,
            "session_id": self.session_id,
            "data": {
                "version": WORK_CMD_VER, "id": WORK_CMD_ID,
                "guild_id": GUILD_ID, "name": "work", "type": 1, "options": [],
                "application_command": {
                    "id": WORK_CMD_ID, "type": 1, "application_id": BOT_ID,
                    "guild_id": GUILD_ID, "version": WORK_CMD_VER,
                    "name": "work", "description": "Work to earn currency!",
                    "integration_types": [0],
                    "permissions": [
                        {"type": 3, "id": "1089819204754092063", "permission": True},
                        {"type": 3, "id": "1089798989836202054", "permission": True},
                        {"type": 1, "id": "846496831533088768", "permission": True},
                    ],
                    "options": [],
                    "description_localized": "Work to earn currency!",
                    "name_localized": "work",
                },
                "attachments": [],
            },
            "nonce": nonce, "analytics_location": "slash_ui",
        }
        try:
            async with self.session.post(
                f"{API_BASE}/interactions", headers=self.headers(), json=payload, **self._proxy_kw()
            ) as res:
                return res.status in (200, 204)
        except Exception as e:
            logger.error(f"[{self.label}] work failed: {e}")
            return False

    async def execute_balance(self) -> bool:
        nonce = self.build_nonce()
        payload = {
            "type": 2, "application_id": BOT_ID,
            "guild_id": GUILD_ID, "channel_id": CHANNEL_ID,
            "session_id": self.session_id,
            "data": {
                "version": BAL_CMD_VER, "id": BAL_CMD_ID,
                "guild_id": GUILD_ID, "name": "balance", "type": 1, "options": [],
                "application_command": {
                    "id": BAL_CMD_ID, "type": 1, "application_id": BOT_ID,
                    "guild_id": GUILD_ID, "version": BAL_CMD_VER,
                    "name": "balance",
                    "description": "View your balance or the balance of another member",
                    "options": [{
                        "type": 6, "name": "user",
                        "description": "The user to view the balance of",
                        "required": False,
                        "description_localized": "The user to view the balance of",
                        "name_localized": "user",
                    }],
                    "integration_types": [0],
                    "permissions": [
                        {"type": 3, "id": "1089819204754092063", "permission": True},
                        {"type": 3, "id": "846496831533088768", "permission": True},
                    ],
                    "description_localized": "View your balance or the balance of another member",
                    "name_localized": "balance",
                },
                "attachments": [],
            },
            "nonce": nonce, "analytics_location": "slash_ui",
        }
        try:
            async with self.session.post(
                f"{API_BASE}/interactions", headers=self.headers(), json=payload, **self._proxy_kw()
            ) as res:
                return res.status in (200, 204)
        except Exception as e:
            logger.error(f"[{self.label}] balance check failed: {e}")
            return False


    def parse_message_payload(self, text: str) -> Optional[Dict[str, Any]]:
        m = re.search(r"earned\s+\*\*?([0-9,.]+)\*\*?\s+belubucks", text, re.I)
        if not m:
            m = re.search(r"\*\*?([0-9,.]+)\*\*?\s+belubucks", text, re.I)
        if m and ("finished working" in text.lower() or "earned" in text.lower()):
            val = int(m.group(1).replace(",", "").replace(".", ""))
            return {"type": "work_success", "amount": val}

        if "overwork yourself" in text.lower() or "can work again" in text.lower():
            m_ts = re.search(r"<t:(\d+):[A-Za-z]?>", text)
            ts = int(m_ts.group(1)) if m_ts else int(time.time() + 300)
            return {"type": "work_cooldown", "timestamp": ts}

        if "have no belubucks" in text.lower():
            return {"type": "balance_success", "balance": 0, "rank": "unranked"}

        m_bal = re.search(r"have\s+\*\*?([0-9,.]+)\*\*?\s+belubucks", text, re.I)
        if m_bal and "leaderboard" in text.lower():
            bal = int(m_bal.group(1).replace(",", "").replace(".", ""))
            m_rank = re.search(r"#([0-9,]+)", text)
            rank = f"#{m_rank.group(1)}" if m_rank else "unranked"
            return {"type": "balance_success", "balance": bal, "rank": rank}

        return None

    async def poll_channel_messages(self) -> Optional[Dict[str, Any]]:
        try:
            async with self.session.get(
                f"{API_BASE}/channels/{CHANNEL_ID}/messages?limit=6",
                headers=self.headers(), **self._proxy_kw()
            ) as res:
                if res.status == 200:
                    for msg in await res.json():
                        interaction = msg.get("interaction") or msg.get("interaction_metadata")
                        if not interaction:
                            continue
                        user_id = str(interaction.get("user", {}).get("id", ""))
                        if user_id != self.rt.user_id:
                            continue
                        content = msg.get("content", "")
                        for emb in msg.get("embeds", []):
                            content += " " + emb.get("title", "") + " " + emb.get("description", "")
                        parsed = self.parse_message_payload(content)
                        if parsed:
                            return parsed
        except Exception:
            pass
        return None

    async def await_reply(self, expected_type: str, max_wait: float = 14.0) -> Optional[Dict[str, Any]]:
        t0 = time.monotonic()
        while time.monotonic() - t0 < max_wait and self.is_running:
            if self.pending_interaction_response and self.pending_interaction_response.done():
                res = self.pending_interaction_response.result()
                if res.get("type", "").startswith(expected_type):
                    return res
            res = await self.poll_channel_messages()
            if res and res.get("type", "").startswith(expected_type):
                return res
            await asyncio.sleep(1.5)
        return None


    async def loop_work(self) -> None:
        while not self.session_id and self.is_running:
            await asyncio.sleep(1.0)
        await asyncio.sleep(3.0)

        while self.is_running:
            async with self.action_lock:
                self.rt.state = WorkerState.TYPING
                await self.emit_typing()
                await asyncio.sleep(random.uniform(2.0, 3.5))

                loop = asyncio.get_running_loop()
                self.pending_interaction_response = loop.create_future()

                self.rt.state = WorkerState.DISPATCHING
                ok = await self.execute_work()
                if not ok:
                    logger.warning(f"[{self.label}] failed to dispatch /work, backoff 10s")
                    self.rt.state = WorkerState.BACKOFF
                    self.rt.next_work_countdown = 10
                    while self.rt.next_work_countdown > 0 and self.is_running:
                        await asyncio.sleep(1.0)
                        self.rt.next_work_countdown -= 1
                    continue

                self.rt.state = WorkerState.WAITING_REPLY
                result = await self.await_reply("work", max_wait=12.0)

            if result and result.get("type") == "work_success":
                amount = result.get("amount", 0)
                self.rt.total_works += 1
                self.rt.session_earned += amount
                self.rt.last_earned = amount
                self.rt.last_work_at = time.strftime("%H:%M:%S")
                if self.rt.current_balance is not None:
                    self.rt.current_balance += amount
                logger.info(f"[{self.label}] work +{amount:,} (session: +{self.rt.session_earned:,})")

            elif result and result.get("type") == "work_cooldown":
                cd_ts = result.get("timestamp", 0)
                rem = max(cd_ts - int(time.time()), 5) + random.randint(4, 8)
                logger.warning(f"[{self.label}] cooldown, waiting {rem}s")
                self.rt.state = WorkerState.COOLDOWN
                self.rt.next_work_countdown = rem
                while self.rt.next_work_countdown > 0 and self.is_running:
                    await asyncio.sleep(1.0)
                    self.rt.next_work_countdown -= 1
                continue
            else:
                logger.info(f"[{self.label}] /work sent, no reply")
                self.rt.total_works += 1
                self.rt.last_work_at = time.strftime("%H:%M:%S")

            interval = _get_timing(
                "work_min", "work_max", "work_fixed",
                WORK_MIN_DELAY, WORK_MAX_DELAY,
            )
            self.rt.state = WorkerState.IDLE
            self.rt.next_work_countdown = interval
            while self.rt.next_work_countdown > 0 and self.is_running:
                await asyncio.sleep(1.0)
                self.rt.next_work_countdown -= 1

    async def loop_balance(self) -> None:
        while not self.session_id and self.is_running:
            await asyncio.sleep(1.0)
        await asyncio.sleep(15.0)

        while self.is_running:
            async with self.action_lock:
                await self.emit_typing()
                await asyncio.sleep(random.uniform(1.5, 2.5))

                loop = asyncio.get_running_loop()
                self.pending_interaction_response = loop.create_future()

                ok = await self.execute_balance()
                if not ok:
                    logger.warning(f"[{self.label}] failed to dispatch /balance")
                else:
                    result = await self.await_reply("balance", max_wait=12.0)
                    if result and result.get("type") == "balance_success":
                        self.rt.current_balance = result.get("balance", 0)
                        self.rt.leaderboard_rank = result.get("rank", "unranked")
                        self.rt.last_balance_at = time.strftime("%H:%M:%S")
                        logger.info(f"[{self.label}] balance {self.rt.current_balance:,} (rank {self.rt.leaderboard_rank})")

            interval = _get_timing(
                "bal_min", "bal_max", "bal_fixed",
                BAL_MIN_DELAY, BAL_MAX_DELAY,
            )
            self.rt.next_balance_countdown = interval
            while self.rt.next_balance_countdown > 0 and self.is_running:
                await asyncio.sleep(1.0)
                self.rt.next_balance_countdown -= 1

    async def heartbeat(self, interval_ms: float) -> None:
        intv = interval_ms / 1000.0
        try:
            while self.is_running and self.ws and not self.ws.closed:
                await self.ws.send_json({"op": 1, "d": self.sequence})
                await asyncio.sleep(intv)
        except (asyncio.CancelledError, Exception):
            pass

    async def on_gateway_payload(self, raw_str: str) -> None:
        try:
            packet = json.loads(raw_str)
        except ValueError:
            return

        op = packet.get("op")
        s = packet.get("s")
        t = packet.get("t")
        d = packet.get("d")

        if s is not None:
            self.sequence = s

        if op == 10:
            intv = d.get("heartbeat_interval", 41250)
            if self.heartbeat_task and not self.heartbeat_task.done():
                self.heartbeat_task.cancel()
            self.heartbeat_task = asyncio.create_task(self.heartbeat(intv))
            p = self.profile_data
            await self.ws.send_json({
                "op": 2,
                "d": {
                    "token": self.token,
                    "properties": {
                        "$os": p["os"], "$browser": p["browser"], "$device": p["device"],
                        "$system_locale": p["system_locale"],
                        "$browser_user_agent": p["browser_user_agent"],
                        "$browser_version": p["browser_version"],
                        "$os_version": p["os_version"],
                        "$referrer": "", "$referring_domain": "",
                        "$referrer_current": "", "$referring_domain_current": "",
                        "$release_channel": p["release_channel"],
                        "$client_build_number": p["client_build_number"],
                        "$client_event_source": None,
                    },
                    "compress": False,
                    "presence": {"status": "online", "afk": False},
                },
            })

        elif op == 11:
            self.gateway_rtt = round(random.uniform(35.0, 60.0), 1)

        elif op == 0 and t in ("READY", "RESUMED"):
            if t == "READY":
                self.session_id = d.get("session_id")
            logger.info(f"[{self.label}] gateway connected (session: {self.session_id[:8]}...)")

        elif op == 0 and t == "MESSAGE_CREATE":
            author = str(d.get("author", {}).get("id", ""))
            channel = str(d.get("channel_id", ""))
            if author == BOT_ID and channel == CHANNEL_ID:
                interaction = d.get("interaction") or d.get("interaction_metadata")
                if interaction:
                    user_id = str(interaction.get("user", {}).get("id", ""))
                    if user_id != self.rt.user_id:
                        return
                buf = d.get("content", "")
                for emb in d.get("embeds", []):
                    buf += " " + emb.get("title", "") + " " + emb.get("description", "")
                parsed = self.parse_message_payload(buf)
                if parsed and self.pending_interaction_response and not self.pending_interaction_response.done():
                    self.pending_interaction_response.set_result(parsed)

    async def loop_gateway(self) -> None:
        ws_kw: Dict[str, Any] = {"max_msg_size": 0, "heartbeat": None}
        if self.proxy_cfg:
            if self.proxy_cfg.scheme in ("http", "https"):
                kw = self.proxy_cfg.request_kwargs()
                ws_kw["proxy"] = kw.get("proxy")
                if "proxy_headers" in kw:
                    ws_kw["proxy_headers"] = kw["proxy_headers"]

        while self.is_running:
            try:
                async with self.session.ws_connect(GATEWAY_URL, **ws_kw) as ws:
                    self.ws = ws
                    async for msg in ws:
                        if not self.is_running:
                            break
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            await self.on_gateway_payload(msg.data)
                        elif msg.type in (aiohttp.WSMsgType.CLOSE, aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                            break
            except Exception as e:
                logger.error(f"[{self.label}] gateway dropped: {e}")
            finally:
                self.ws = None
            if not self.is_running:
                break
            await asyncio.sleep(4.0)


    def render_ui(self) -> Layout:
        root = Layout()
        root.split_column(
            Layout(name="logo",   size=LOGO_HEIGHT),
            Layout(name="body",   ratio=1),
            Layout(name="footer", size=3),
        )
        root["body"].split_column(
            Layout(name="metrics", size=7),
            Layout(name="logs",    ratio=1),
        )
        root["metrics"].split_row(
            Layout(name="left",  ratio=1),
            Layout(name="right", ratio=1),
        )

        tick = int(time.monotonic() * 2.5)
        n = len(THEME_PALETTE)
        c = [THEME_PALETTE[(i + tick) % n] for i in range(n)]

        root["logo"].update(_build_logo_text())

        bal_str = f"{self.rt.current_balance:,} belubucks" if self.rt.current_balance is not None else "[dim]checking...[/]"
        last_str = f"[{c[0]}]+{self.rt.last_earned:,}[/] [dim]at {self.rt.last_work_at}[/]" if self.rt.last_earned else "[dim]—[/]"
        root["left"].update(Panel(
            "\n".join([
                f"[dim]account :[/]  [white]{self.rt.username}[/]",
                f"[dim]balance :[/]  [{c[1]}]{bal_str}[/] [dim](rank {self.rt.leaderboard_rank})[/]",
                f"[dim]earned  :[/]  [{c[0]}]+{self.rt.session_earned:,}[/] [dim]({self.rt.total_works} runs)[/]",
                f"[dim]last work:[/] {last_str}",
            ]),
            title="[dim]account[/]", border_style=c[1],
        ))

        scol  = _STATE_COLOR.get(self.rt.state, "white")
        next_w = _fmt_countdown(self.rt.next_work_countdown, self.rt.state)
        next_b = _fmt_countdown(self.rt.next_balance_countdown, self.rt.state)
        root["right"].update(Panel(
            "\n".join([
                f"[dim]state     :[/] [{scol}]{self.rt.state.value}[/]",
                f"[dim]next work :[/] {next_w}",
                f"[dim]next bal  :[/] {next_b}",
                f"[dim]proxy     :[/] [white]{self.proxy_display}[/]  [dim]rtt[/] [white]{self.gateway_rtt}ms[/]",
            ]),
            title="[dim]status[/]", border_style=c[3],
        ))

        logs = log_sink.get_lines()[-6:]
        root["logs"].update(Panel(
            "\n".join(logs) if logs else "[dim]no events yet[/]",
            title="[dim]event stream[/]", border_style=c[0],
        ))

        uptime = int(time.monotonic() - self.boot_monotonic)
        uh, ur = divmod(uptime, 3600)
        um, us = divmod(ur, 60)
        bal_val = f"{self.rt.current_balance:,} belubucks" if self.rt.current_balance is not None else "checking..."
        root["footer"].update(Panel(
            f"[dim]uptime:[/] [white]{uh:02d}h {um:02d}m {us:02d}s[/]  [dim]balance:[/] [{c[1]}]{bal_val}[/]  [dim]earned:[/] [{c[0]}]+{self.rt.session_earned:,}[/]",
            border_style=c[4],
        ))
        return root

    async def loop_ui(self) -> None:
        with Live(self.render_ui(), refresh_per_second=2, screen=True) as display:
            try:
                while self.is_running:
                    display.update(self.render_ui())
                    await asyncio.sleep(0.5)
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass


    async def run(self, solo_ui: bool = True) -> None:
        try:
            connector = self.proxy_cfg.make_connector() if self.proxy_cfg else aiohttp.TCPConnector(family=socket.AF_INET)
            timeout = aiohttp.ClientTimeout(total=25.0, connect=10.0)
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                self.session = session
                if not await self.fetch_user():
                    logger.error(f"[{self.label}] failed to authenticate token")
                    return
                _label_username[self.label] = self.rt.username
                logger.info(f"[{self.label}] authenticated as {self.rt.username}")
                logger.info(f"[{self.label}] profile: {self.profile_data['name']}  host: {self.host_env.value}")

                logger.info(f"[{self.label}] running pre-flight checks...")
                pf = await self.preflight_check()
                if pf != PreflightResult.OK:
                    _PREFLIGHT_MSGS = {
                        PreflightResult.NOT_IN_GUILD:   "not a member of the target server — worker stopped",
                        PreflightResult.SLOWMODE:       "channel slowmode is active — messages may be throttled (continuing)",
                        PreflightResult.SEND_BLOCKED:   "cannot send messages in channel — worker stopped",
                        PreflightResult.VERIFICATION:   "server verification/screening not completed — worker stopped",
                        PreflightResult.AGE_RESTRICTED: "channel is age-restricted and account not verified — worker stopped",
                        PreflightResult.NO_PERMISSION:  "missing send-message permission in channel — worker stopped",
                        PreflightResult.UNKNOWN:        "unknown pre-flight error — worker stopped",
                    }
                    msg = _PREFLIGHT_MSGS.get(pf, "pre-flight failed — worker stopped")
                    _FATAL = {
                        PreflightResult.NOT_IN_GUILD,
                        PreflightResult.SEND_BLOCKED,
                        PreflightResult.VERIFICATION,
                        PreflightResult.AGE_RESTRICTED,
                        PreflightResult.NO_PERMISSION,
                        PreflightResult.UNKNOWN,
                    }
                    if pf in _FATAL:
                        logger.error(f"[{self.label}] preflight [{pf.value}] {msg}")
                        return
                    else:
                        logger.warning(f"[{self.label}] preflight [{pf.value}] {msg}")
                else:
                    logger.info(f"[{self.label}] pre-flight OK — starting farm")

                tasks = [
                    asyncio.create_task(self.loop_gateway()),
                    asyncio.create_task(self.loop_work()),
                    asyncio.create_task(self.loop_balance()),
                ]
                if solo_ui:
                    tasks.append(asyncio.create_task(self.loop_ui()))

                try:
                    await asyncio.gather(*tasks)
                except (KeyboardInterrupt, asyncio.CancelledError):
                    pass
                finally:
                    for t in tasks:
                        if not t.done():
                            t.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await self.shutdown()

    async def shutdown(self) -> None:
        self.is_running = False
        for task in (self.heartbeat_task, self.work_task, self.balance_task, self.ui_task):
            if task and not task.done():
                task.cancel()
        if self.ws and not self.ws.closed:
            await self.ws.close(code=1000)



_STATE_COLOR = {
    WorkerState.STARTUP:       "dim",
    WorkerState.CONNECTING:    "yellow",
    WorkerState.READY:         "green",
    WorkerState.TYPING:        "cyan",
    WorkerState.DISPATCHING:   "cyan",
    WorkerState.WAITING_REPLY: "blue",
    WorkerState.IDLE:          "white",
    WorkerState.COOLDOWN:      "yellow",
    WorkerState.BACKOFF:       "red",
    WorkerState.DISCONNECTED:  "red",
}


def _fmt_countdown(secs: int, state: WorkerState) -> str:
    if secs <= 0:
        if state in (WorkerState.STARTUP, WorkerState.CONNECTING, WorkerState.DISCONNECTED):
            return "[dim]—[/]"
        return "[cyan]sending[/]"
    m, s = divmod(secs, 60)
    col = "yellow" if secs < 60 else "white"
    return f"[{col}]{m:02d}m {s:02d}s[/]"


def _build_logo_text() -> Text:
    tick = int(time.monotonic() * 2.5)
    n = len(THEME_PALETTE)
    t = Text()
    for i, line in enumerate(LOGO):
        t.append(line + "\n", style=THEME_PALETTE[(i + tick) % n])
    t.append(f"  v{VERSION}\n", style="dim")
    return t

LOGO_HEIGHT = len(LOGO) + 1


def render_multi_ui(workers: List[BeluWorkerClient]) -> Layout:
    tick = int(time.monotonic() * 2.5)
    n = len(THEME_PALETTE)
    c = [THEME_PALETTE[(i + tick) % n] for i in range(n)]

    root = Layout()
    root.split_column(
        Layout(name="logo",   size=LOGO_HEIGHT),
        Layout(name="table",  ratio=1),
        Layout(name="logs",   ratio=2),
        Layout(name="footer", size=3),
    )

    root["logo"].update(_build_logo_text())

    tbl = Table(show_header=True, header_style="bold dim", border_style="dim", expand=True, show_edge=True)
    tbl.add_column("#",          width=3,  justify="right")
    tbl.add_column("account",    ratio=3,  no_wrap=True)
    tbl.add_column("state",      ratio=2,  no_wrap=True)
    tbl.add_column("balance",    ratio=2,  justify="right")
    tbl.add_column("session +",  ratio=2,  justify="right")
    tbl.add_column("last +",     ratio=1,  justify="right")
    tbl.add_column("runs",       width=5,  justify="right")
    tbl.add_column("next work", ratio=2,  no_wrap=True)
    tbl.add_column("proxy",      ratio=2,  no_wrap=True)

    for idx, w in enumerate(workers, 1):
        rt    = w.rt
        scol  = _STATE_COLOR.get(rt.state, "white")
        bal   = f"[{c[1]}]{rt.current_balance:,}[/]" if rt.current_balance is not None else "[dim]...[/]"
        last  = f"[{c[0]}]+{rt.last_earned:,}[/]" if rt.last_earned else "[dim]—[/]"
        earn  = f"[{c[0]}]+{rt.session_earned:,}[/]"
        proxy = f"[dim]{w.proxy_display[:20]}[/]" if w.proxy_display != "direct" else "[dim]direct[/]"
        user  = f"[white]{rt.username}[/]" if rt.username != "unknown" else "[dim]authenticating...[/]"

        tbl.add_row(
            f"[dim]{idx}[/]",
            user,
            f"[{scol}]{rt.state.value}[/]",
            bal,
            earn,
            last,
            f"[dim]{rt.total_works}[/]",
            _fmt_countdown(rt.next_work_countdown, rt.state),
            proxy,
        )

    root["table"].update(Panel(tbl, title=f"[dim]workers ({len(workers)})[/]", border_style=c[1], padding=(0, 0)))

    logs = log_sink.get_lines()[-7:]
    log_text = "\n".join(logs) if logs else "[dim]no events yet[/]"
    root["logs"].update(Panel(log_text, title="[dim]event log[/]", border_style=c[0], padding=(0, 1)))

    uptime = int(time.monotonic() - workers[0].boot_monotonic) if workers else 0
    uh, ur  = divmod(uptime, 3600)
    um, us  = divmod(ur, 60)
    total      = sum(w.rt.session_earned for w in workers)
    total_runs = sum(w.rt.total_works for w in workers)
    alive      = sum(1 for w in workers if w.rt.state not in (WorkerState.STARTUP, WorkerState.DISCONNECTED))
    root["footer"].update(Panel(
        f"[dim]uptime:[/] [white]{uh:02d}h {um:02d}m {us:02d}s[/]  "
        f"[dim]total earned:[/] [{c[0]}]+{total:,}[/]  "
        f"[dim]total worked:[/] [white]{total_runs}[/]  "
        f"[dim]workers alive:[/] [white]{alive}/{len(workers)}[/]",
        border_style=c[4], padding=(0, 1),
    ))
    return root


async def run_multi_farm(workers: List[BeluWorkerClient]) -> None:
    async def loop_ui():
        with Live(render_multi_ui(workers), refresh_per_second=2, screen=True) as display:
            try:
                while True:
                    display.update(render_multi_ui(workers))
                    await asyncio.sleep(0.5)
            except (KeyboardInterrupt, asyncio.CancelledError):
                pass

    tasks = [asyncio.create_task(w.run(solo_ui=False)) for w in workers]
    tasks.append(asyncio.create_task(loop_ui()))

    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, asyncio.CancelledError):
        for t in tasks:
            t.cancel()



def load_config() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def save_config(data: Dict[str, Any]) -> None:
    CONFIG_PATH.write_text(json.dumps(data, indent=4), encoding="utf-8")


def _is_valid_token(token: str) -> bool:
    return len(token.strip()) >= 50


def _is_valid_proxy(raw: str) -> bool:
    return len(raw.strip()) >= 10


def mask_token(token: str) -> str:
    if len(token) > 14:
        return f"{token[:8]}...{token[-6:]}"
    return "***"
    if len(token) > 14:
        return f"{token[:8]}...{token[-6:]}"
    return "***"


async def check_proxy_async(raw: str) -> Tuple[bool, str, Optional[ProxyConfig]]:
    has_scheme = bool(_SCHEME_RE.match(raw.strip()))

    if has_scheme:
        cfg = _parse_proxy_str(raw)
        if not cfg:
            return False, "could not parse proxy string", None
        elapsed = await _probe_proxy(cfg)
        if elapsed < float("inf"):
            return True, f"{cfg.scheme} ok ({elapsed*1000:.0f}ms)", cfg
        return False, f"{cfg.scheme} unreachable", None

    candidates = [_parse_proxy_str(raw, scheme=s) for s in _PROBE_PROTOCOLS]
    candidates = [c for c in candidates if c is not None]
    if not candidates:
        return False, "could not parse proxy string", None

    CONSOLE.print(f"[dim]no scheme detected, detecting scheme...[/]")

    results: List[Tuple[float, ProxyConfig]] = []

    async def race(cfg: ProxyConfig) -> None:
        elapsed = await _probe_proxy(cfg, timeout=6.0)
        results.append((elapsed, cfg))

    await asyncio.gather(*[race(c) for c in candidates])
    results.sort(key=lambda x: x[0])

    for elapsed, cfg in results:
        if elapsed < float("inf"):
            others = [f"{c.scheme}={t*1000:.0f}ms" for t, c in results]
            return True, f"best: {cfg.scheme} ({elapsed*1000:.0f}ms)  [{', '.join(others)}]", cfg

    return False, "all protocols unreachable", None



_P_BR = "\033[38;2;255;241;242m"
_P_SF = "\033[38;2;251;207;232m"
_P_MD = "\033[38;2;244;114;182m"
_P_DP = "\033[38;2;225;29;72m"
_G_LT = "\033[38;2;209;250;229m"
_G_SF = "\033[38;2;110;231;183m"
_G_MD = "\033[38;2;52;211;153m"
_G_ST = "\033[38;2;16;185;129m"
_R    = "\033[0m"

FLOWER_ART = [
    f"                              {_P_BR}_.-'''.{_R}",
    f"                    {_P_BR}_{_R}       {_P_BR}.'{_R}       {_P_BR}\\{_R} ",
    f"      {_P_BR},.._______{_R}  {_P_BR}.-/\\`--.../{_R}          {_P_BR}\\{_R} ",
    f"      {_P_SF}|{_R}        {_P_SF}'\\|{_R} {_P_DP}\\_`_-.{_R}  {_P_MD}`.{_R}  {_P_BR}_{_R}       {_P_BR}\\{_R} ",
    f"     {_P_SF}/{_R}        {_P_SF}_{_R} {_P_SF}.'{_R} {_P_MD}/{_R} {_P_DP}/_`\\`\\{_R}  {_P_DP}\\/{_R} {_P_MD}'.{_R}      {_P_BR}\\{_R} ",
    f"    {_P_SF}/{_R}       {_P_SF}/`{_R} {_P_MD}/{_R}  {_P_DP}/\\_|\\_/\\{_R} {_P_DP}'._|{_R}   {_P_DP}\\{_R}      {_P_SF}:{_R}",
    f"  {_P_BR}.'{_R}       {_P_SF}/{_R}  {_P_SF}:{_R}   {_P_DP}\\{_R} {_P_DP}_{_R}  {_P_DP}|{_R}  {_P_DP}`\\{_R} {_P_DP}.'___{_R} {_P_DP}|{_R}      {_P_SF}|{_R} {_P_SF}__,'\\{_R} ",
    f"  {_P_BR}\\{_R}        {_P_SF}|{_R} {_P_SF}__{_P_MD}'.{_R} {_P_DP}|/.`'----./{_R} {_P_DP}/|{_R} {_P_DP}`'{_R}    {_P_MD}.'{_P_SF}''{_R}     {_P_SF}'-.{_R}",
    f"   {_P_SF}:{_R}      {_P_SF}.`\"\\{_R} {_P_MD}`'\\{_P_DP}/{_R} {_P_DP}|`''--.'/`{_R}  {_P_DP}\\{_R}     {_P_MD}/{_R}          {_P_SF}/{_R}",
    f"   {_P_SF}|{_R}     {_P_SF}/|{_R}   {_P_SF}|{_R}   {_P_DP}\\{_R} {_P_DP}|{_R}    {_P_DP}/{_R} {_P_DP}|{_R}     {_P_DP}\\{_R}   {_P_MD}/{_R}          {_P_SF}/{_R}",
    f"   {_P_SF}'{_R}    {_P_SF}|{_R} {_P_SF}'.__{_P_MD}'____{_P_DP}\\'_{_R} {_P_DP}.'_.'{_R}      {_P_MD}|{_R} {_P_SF}/{_R}          {_P_SF}|{_R}",
    f"  {_P_SF}/{_R}     {_P_SF}\\{_R}     {_P_MD}___.-'`\\`'-.._{_R}      {_P_MD}|/{_R}          {_P_SF}.'{_R}",
    f" {_P_SF}'-.{_R}     {_P_SF}`--'`{_R} {_P_MD}'.{_R}     {_P_MD}`.{_R}    {_P_MD}`'-._/__..._{_R}       {_P_SF}|{_R}",
    f"    {_P_SF}`-.{_R}    {_P_SF}__{_R}    {_P_MD}`.{_R}     {_P_MD}\\_..,____..'{_R}    {_P_SF}\\{_R}      {_P_SF}/{_R}",
    f"     {_P_SF}/{_R} {_P_SF}`'-'{_R}  {_P_SF}`----{_R} {_P_MD}\\{_R}      {_P_MD}.--'''`{_R}       {_P_SF}|{_R}    {_P_SF},'.__{_R}",
    f"    {_P_SF}/{_R}               {_P_MD}`-...:____{_R}          {_P_SF}|{_R}  {_P_SF}.'/{_R} {_P_SF}_.{_R} {_P_SF}''--.{_R}",
    f"  {_P_BR},'{_R}              {_P_SF},'`{_R}        {_P_SF}`\\--'`.{_R}   {_P_SF}|''`,-'-.{_R}   {_P_SF},'`{_R}",
    f"{_P_BR}.'{_R}              {_P_SF}.'{_R}            {_P_SF}_\\{_R}    {_P_SF}\\{_R}  {_P_SF}|,'{_R} {_P_SF}\\{_R}    {_P_SF}_,'{_R}",
    f"{_P_BR}'-._{_R}            {_P_SF}'--..._{_R}   {_P_SF}_,-'{_R}  {_P_SF}'.{_R}   {_P_SF}'-'..__.-'{_R}",
    f"    {_P_SF}`.{_R}                {_G_ST}/`-'{_R} {_G_ST}/{_R}    {_G_SF}|'-._{_R}  {_G_LT}`'.___{_R}",
    f"      {_P_SF}\\{_R}         {_G_LT}_{_R}    {_G_ST}/|{_R}   {_G_ST}|{_R}     {_G_MD}/.'{_R} {_G_LT}.`-.__..'`{_G_MD}\\{_R} ",
    f"     {_G_LT},-'.---'''`{_G_MD}/`'./{_R} {_G_LT}`.{_R}  {_G_ST}|-.{_R}  {_G_ST}|/{_R}  {_G_MD}/{_R}    {_G_LT}_\\'-._`{_G_SF}|{_R}",
    f"    {_G_MD}/{_R}    {_G_LT}-''-{_R} {_G_LT},'-.{_R}       {_G_ST}|{_R} {_G_ST}|{_R}   {_G_MD}\\{_R}  {_G_MD}\\{_R}      {_G_MD}/{_R}  {_G_MD}\\{_R}   {_G_LT}'{_R} {_G_SF}|{_R}",
    f"   {_G_LT}.'{_R} {_G_LT}.-'''-,'\\{_R}   {_G_MD}\\{_R}    {_G_ST}`|/{_R}   {_G_LT}',.--.{_R}   {_G_LT}'{_R}  {_G_LT}.'\\.__`{_G_SF}|{_R}",
    f"   {_G_SF}|{_R} {_G_LT}'{_R}    {_G_LT},'{_R}   {_G_SF}|{_R}   {_G_LT}'{_R}    {_G_ST}'{_R}   {_G_LT},'{_R}     {_G_LT}`\\{_R}    {_G_LT}'{_R}  {_G_MD}\\{_R}   {_G_MD}\\{_R} ",
    f"   {_G_LT}.{_R}     {_G_MD}/{_R} {_G_MD}\\{_R}   {_G_LT}'{_R}   {_G_SF}|{_R}       {_G_ST}/{_R}         {_G_MD}/{_G_LT}--.{_R}    {_G_LT}'.{_R} {_G_LT}'.{_R}",
    f"   {_G_MD}/{_R}   {_G_LT}.'{_R}  {_G_SF}|{_R}     {_G_LT}_,'{_R}      {_G_ST}.'{_R}  {_G_LT}'`'--,'.{_R}   {_G_MD}\\{_G_LT}.{_R}   {_G_MD}\\{_R}  {_G_SF}|{_R}",
    f"   {_G_SF}|{_R} {_G_LT}.'{_R}    {_G_LT}'{_R} {_G_LT}_.,'{_R}         {_G_ST}|{_R}  {_G_LT}___{_R} {_G_LT},'{_R}  {_G_MD}\\{_R}    {_G_SF}|{_G_LT}`-.__{_R}  {_G_SF}|{_R}",
    f"  {_G_MD}/.'{_G_LT}__.,-'''{_R}            {_G_ST}.|{_R} {_G_ST}'{_R}   {_G_MD}/{_R} {_G_MD}\\{_R}   {_G_SF}|{_R}   {_G_LT}'{_R}    {_G_LT}`-.{_R}",
    f" {_G_LT}'--'{_R}                    {_G_ST}|{_R}    {_G_LT},'{_R}  {_G_SF}|{_R}   {_G_LT}'{_R}   {_G_MD}/{_R}      {_G_LT}'{_G_SF}|{_R}",
    f"                         {_G_ST}|{_R}  {_G_LT},'{_R}    {_G_LT}'{_R}  {_G_LT}_,.-'{_R}",
    f"                        {_G_ST}.'{_R} {_G_ST}/{_R}   {_G_LT}_,.--'{_R}",
    f"                        {_G_ST}|..--''{_R}",
]

FLOWER_PINK = "#ff69b4"


def _colorize_flower_line(line: str, offset: int) -> str:
    return line


def _supports_unicode() -> bool:
    try:
        "❀╭╰╿╌╽".encode(sys.stdout.encoding or "utf-8")
        return True
    except (UnicodeEncodeError, LookupError, AttributeError):
        return False


def print_logo() -> None:
    tick = int(time.monotonic() * 2.5)
    n = len(THEME_PALETTE)
    for i, line in enumerate(LOGO):
        CONSOLE.print(f"[{THEME_PALETTE[(i + tick) % n]}]{line}[/]")
    CONSOLE.print(f"[dim]  v{VERSION}[/]\n")


def _char_width(ch: str) -> int:
    eaw = unicodedata.east_asian_width(ch)
    return 2 if eaw in ("W", "F") else 1


def _str_width(s: str) -> int:
    return sum(_char_width(c) for c in s)


def print_menu(cfg: Dict[str, Any]) -> None:
    host_env = detect_host_environment()
    interactive = host_env in (HostEnvironment.WINDOWS, HostEnvironment.LINUX,
                               HostEnvironment.TERMUX)
    mode = cfg.get("mode", "one-farm")
    tick = int(time.monotonic() * 2.5)
    n = len(THEME_PALETTE)
    ac = THEME_PALETTE[(tick + 0) % n]
    bc = THEME_PALETTE[(tick + 1) % n]

    if not interactive or not _supports_unicode():
        CONSOLE.print(f"[dim]  mode:[/] [white]{mode}[/]\n")
        CONSOLE.print(f"  [dim]1.[/] [white]start farm[/]")
        CONSOLE.print(f"  [dim]2.[/] [white]check proxy[/]")
        CONSOLE.print(f"  [dim]3.[/] [white]setup config[/]")
        CONSOLE.print(f"  [dim]4.[/] [white]settings[/]")
        CONSOLE.print(f"  [dim]5.[/] [white]about[/]")
        CONSOLE.print(f"  [dim]0.[/] [white]exit[/]\n")
        return

    flower = FLOWER_ART
    _ansi_re = re.compile(r"\033\[[0-9;]*m")
    fw = max(len(_ansi_re.sub("", l)) for l in flower)

    items = [
        ("✻", "1", "start farm"),
        ("⚜", "2", "check proxy"),
        ("✿", "3", "setup config"),
        ("⚙", "4", "settings"),
        ("✦", "5", "about"),
        ("❀", "0", "exit"),
    ]

    menu_lines = [
        "", "", "", "", "", "", "", "",
        f"   \033[2m── StdixSelfbot ─ HuyZeraa ──\033[0m",
        f"   \033[38;2;110;231;183mmode :\033[0m  \033[97m{mode}\033[0m",
        "",
        f"   \033[1;31m⚠  Lưu ý: Đừng tiết lộ token cho bất kỳ ai!\033[0m",
        f"   \033[31m   Công cụ này có thể vi phạm ToS của Discord!\033[0m",
        f"   \033[31m   Hãy cân nhắc kỹ trước khi sử dụng.\033[0m",
        f"   \033[38;2;96;165;250mDeveloped by huyzeraa, version {VERSION}\033[0m",
        "",
        *[f"   \033[97m{icon}\033[0m  \033[2m{num}\033[0m  \033[97m{label}\033[0m"
          for icon, num, label in items],
        "", "", "", "", "", "", "", "",
    ]

    rows = max(len(flower), len(menu_lines))
    for i in range(rows):
        fl_raw = flower[i] if i < len(flower) else ""
        visible_w = len(_ansi_re.sub("", fl_raw))
        pad = " " * (fw - visible_w)
        ml = menu_lines[i] if i < len(menu_lines) else ""
        print(fl_raw + pad + ml)





def _read_line_from_tty() -> str:
    try:
        if sys.platform == "win32":
            with open("CONIN$", "r") as tty:
                return tty.readline()
        else:
            with open("/dev/tty", "r") as tty:
                return tty.readline()
    except (OSError, IOError):
        try:
            return input()
        except EOFError:
            return ""


def ask(question: str, hint: str = "", default: str = "") -> str:
    parts = []
    if hint:
        parts.append(hint)
    if default:
        parts.append(f"default: {default}")
    parts.append("skip to keep")
    suffix = f" ({', '.join(parts)})"

    host_env = detect_host_environment()
    interactive = host_env in (
        HostEnvironment.WINDOWS,
        HostEnvironment.LINUX,
        HostEnvironment.TERMUX,
    )

    if interactive:
        # Hỏi inline: question + suffix + ": " trên cùng 1 dòng
        CONSOLE.out(f"{question}{suffix}: ", end="")
    else:
        # Bot hosting: giữ nguyên kiểu cũ (2 dòng)
        CONSOLE.print(f"{question}{suffix}:")
        CONSOLE.out("option: ", end="")

    raw = _read_line_from_tty().strip()
    if not raw or raw.lower() == "skip":
        return default
    return raw


def ask_yn(question: str, default: bool = True) -> bool:
    default_str = "yes" if default else "no"
    raw = ask(question, hint="yes/no", default=default_str).lower()
    return raw in ("y", "yes")


def auto_back(seconds: int = 3) -> None:
    for i in range(seconds, 0, -1):
        CONSOLE.print(f"[dim]returning to menu in {i}s...[/]", end="\r")
        time.sleep(1)
    CONSOLE.print("")


def pause() -> None:
    CONSOLE.print("")
    CONSOLE.out("press enter to go back...", end="")
    _read_line_from_tty()



def _resolve_proxy_blocking(raw: str) -> Optional[ProxyConfig]:
    ok, msg, cfg = asyncio.run(check_proxy_async(raw))
    if ok:
        CONSOLE.print(f"[dim]proxy:[/] [green]{msg}[/]")
        return cfg
    CONSOLE.print(f"[yellow]proxy unreachable ({msg}), will try anyway[/]")
    return _parse_proxy_str(raw)


def menu_start_farm(cfg: Dict[str, Any]) -> None:
    load_settings_into_runtime(cfg)
    token = str(cfg.get("token", "")).strip()

    if not token:
        CONSOLE.print("[dim]no token configured yet[/]\n")
        token = ask("discord token")
        if not token:
            CONSOLE.print("[red]token required[/]")
            return
        cfg["token"] = token

    if not _is_valid_token(token):
        CONSOLE.print(f"[red]token too short ({len(token)} chars), likely invalid — skipping[/]")
        return

    raw_proxy = cfg.get("proxy")
    profile_key = str(cfg.get("profile", "windows_chrome"))

    proxy_cfg: Optional[ProxyConfig] = None
    if raw_proxy and _is_valid_proxy(raw_proxy):
        CONSOLE.print(f"[dim]resolving proxy...[/]")
        proxy_cfg = _resolve_proxy_blocking(raw_proxy)
    elif raw_proxy:
        CONSOLE.print(f"[dim]proxy '{raw_proxy}' too short, using direct[/]")

    CONSOLE.print(
        f"\n[dim]token:[/]   {mask_token(token)}\n"
        f"[dim]proxy:[/]   {proxy_cfg.display if proxy_cfg else 'direct'}\n"
        f"[dim]profile:[/] {profile_key}\n"
    )
    worker = BeluWorkerClient(token=token, proxy=proxy_cfg, profile_key=profile_key, label="main")
    try:
        asyncio.run(worker.run(solo_ui=True))
    except KeyboardInterrupt:
        pass


def menu_check_proxy(cfg: Dict[str, Any]) -> None:
    existing = cfg.get("proxy") or ""
    hint = existing if existing else "leave blank to cancel"
    CONSOLE.print("[dim]formats: socks5://host:port  |  http://user:pass@host:port  |  host:port:user:pass[/]")
    raw = ask("proxy to test", hint=hint)
    if not raw:
        return

    CONSOLE.print(f"[dim]testing[/] [white]{raw}[/]...")
    ok, msg, resolved = asyncio.run(check_proxy_async(raw))
    if ok:
        CONSOLE.print(f"[green]pass[/] — {msg}")
        if resolved:
            CONSOLE.print(f"[dim]resolved:[/] {resolved.url}")
    else:
        CONSOLE.print(f"[red]fail[/] — {msg}")


def menu_setup_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    CONSOLE.print("[dim]press enter to keep current value\n[/]")

    old_mode = cfg.get("mode", "one-farm")
    CONSOLE.print("farm mode:")
    CONSOLE.print("  [dim]1.[/] single-farm  [dim](single account)[/]")
    CONSOLE.print("  [dim]2.[/] multi-farm [dim](multiple accounts)[/]")
    mode_default = "1" if old_mode == "one-farm" else "2"
    raw_mode = ask("mode", hint="1 or 2", default=mode_default)
    if raw_mode == "2":
        cfg["mode"] = "multi-farm"
    else:
        cfg["mode"] = "one-farm"

    if cfg["mode"] == "one-farm":
        old_token = str(cfg.get("token", "")).strip()
        hint = mask_token(old_token) if old_token else "required"
        raw = ask("discord token", hint=hint)
        if raw:
            if not _is_valid_token(raw):
                CONSOLE.print(f"[yellow]token too short ({len(raw)} chars), skipping[/]")
            else:
                cfg["token"] = raw
        elif not old_token:
            CONSOLE.print("[red]token required[/]")
            return cfg

        old_proxy = cfg.get("proxy") or ""
        raw = ask("proxy", hint=old_proxy if old_proxy else "direct", default="")
        if raw == "-" or raw.lower() in ("none", "null"):
            cfg["proxy"] = None
        elif raw and _is_valid_proxy(raw):
            cfg["proxy"] = raw
        elif raw:
            CONSOLE.print(f"[dim]proxy too short, using direct[/]")
            cfg["proxy"] = None

        keys = list(CLIENT_PROFILES.keys())
        old_profile = cfg.get("profile", "windows_chrome")
        old_idx = keys.index(old_profile) + 1 if old_profile in keys else 1
        CONSOLE.print("\navailable profiles:")
        for i, k in enumerate(keys, 1):
            CONSOLE.print(f"  [dim]{i}.[/] {CLIENT_PROFILES[k]['name']}")
        raw = ask("profile", hint=f"1-{len(keys)}", default=str(old_idx))
        if raw.isdigit() and 1 <= int(raw) <= len(keys):
            cfg["profile"] = keys[int(raw) - 1]

    else:
        CONSOLE.print("\n[dim]enter accounts one by one. type [white]end[/] when done.[/]")
        CONSOLE.print("[dim]format per account:  token  [optional: proxy]  [optional: profile key][/]\n")

        keys = list(CLIENT_PROFILES.keys())
        CONSOLE.print("available profiles:")
        for i, k in enumerate(keys, 1):
            CONSOLE.print(f"  [dim]{i}.[/] {k}  ({CLIENT_PROFILES[k]['name']})")
        CONSOLE.print("")

        accounts: List[Dict[str, Any]] = list(cfg.get("accounts", []))
        if accounts:
            CONSOLE.print(f"[dim]current: {len(accounts)} account(s) saved. enter new list or leave blank to keep.[/]")

        new_accounts: List[Dict[str, Any]] = []
        idx = 1
        while True:
            raw_token = ask(f"account #{idx} token", hint="or 'end' to finish")
            if raw_token.lower() == "end" or not raw_token:
                break
            if not _is_valid_token(raw_token):
                CONSOLE.print(f"[yellow]token too short ({len(raw_token)} chars), skipping this account[/]")
                continue

            raw_proxy_a = ask(f"  proxy for #{idx}", hint="direct if blank", default="")
            if raw_proxy_a and not _is_valid_proxy(raw_proxy_a):
                CONSOLE.print(f"[dim]proxy too short, using direct[/]")
                raw_proxy_a = ""
            raw_profile_a = ask(f"  profile for #{idx}", hint=f"1-{len(keys)} or key name", default="1")

            profile_key = "windows_chrome"
            if raw_profile_a.isdigit() and 1 <= int(raw_profile_a) <= len(keys):
                profile_key = keys[int(raw_profile_a) - 1]
            elif raw_profile_a in CLIENT_PROFILES:
                profile_key = raw_profile_a

            new_accounts.append({
                "token": raw_token,
                "proxy": raw_proxy_a if raw_proxy_a else None,
                "profile": profile_key,
            })
            CONSOLE.print(f"[dim]  → added: {mask_token(raw_token)}  proxy={raw_proxy_a or 'direct'}  profile={profile_key}[/]\n")
            idx += 1

        if new_accounts:
            cfg["accounts"] = new_accounts
            CONSOLE.print(f"[green]{len(new_accounts)} account(s) configured[/]")
        elif accounts:
            CONSOLE.print(f"[dim]kept existing {len(accounts)} account(s)[/]")
        else:
            CONSOLE.print("[yellow]no accounts entered[/]")

    save_config(cfg)
    CONSOLE.print("\n[green]saved[/]")
    return cfg


def menu_setting(cfg: Dict[str, Any]) -> Dict[str, Any]:
    tokens_path = Path("tokens.txt")

    if not tokens_path.exists():
        tokens_path.write_text(
            "# one worker per line\n"
            "# formats:\n"
            "#   token\n"
            "#   token:proxy\n"
            "#   token:proxy:profile_key\n"
            "# proxy examples: socks5://host:port  |  http://user:pass@host:port  |  host:port:user:pass\n",
            encoding="utf-8",
        )
        CONSOLE.print(f"[dim]created tokens.txt — fill it in then come back[/]")
        pause()
        return cfg

    lines = [
        l.strip() for l in tokens_path.read_text(encoding="utf-8").splitlines()
        if l.strip() and not l.startswith("#")
    ]
    CONSOLE.print(f"tokens.txt — [white]{len(lines)}[/] entries\n")
    CONSOLE.print("[dim]  1.[/] run multi-farm")
    CONSOLE.print("[dim]  0.[/] back\n")
    choice = ask("select", hint="1 or 0", default="0")

    if choice != "1":
        return cfg

    raw_entries = []
    for line in lines:
        # Format: token[:proxy[:profile_key]]
        # token does not contain ":" so split on first ":" to get token
        first_colon = line.find(":")
        if first_colon == -1:
            token = line.strip()
            raw_proxy = None
            profile = "windows_chrome"
        else:
            token = line[:first_colon].strip()
            rest = line[first_colon + 1:].strip()
            raw_proxy = None
            profile = "windows_chrome"
            if rest:
                # Profile key won't contain "//" or multiple ":"
                # Find profile key at the end: split from right if it matches CLIENT_PROFILES
                last_colon = rest.rfind(":")
                if last_colon != -1 and rest[last_colon + 1:].strip() in CLIENT_PROFILES:
                    profile = rest[last_colon + 1:].strip()
                    raw_proxy = rest[:last_colon].strip() or None
                elif rest in CLIENT_PROFILES:
                    profile = rest
                else:
                    raw_proxy = rest or None
        raw_entries.append((token, raw_proxy, profile))

    if not raw_entries:
        CONSOLE.print("[red]no valid entries in tokens.txt[/]")
        pause()
        return cfg

    async def build_workers() -> List[BeluWorkerClient]:
        result = []
        for idx, (token, raw_proxy, profile) in enumerate(raw_entries, 1):
            if not _is_valid_token(token):
                CONSOLE.print(f"[yellow]w{idx}: token too short ({len(token)} chars), skipping[/]")
                continue
            proxy_cfg: Optional[ProxyConfig] = None
            if raw_proxy and _is_valid_proxy(raw_proxy):
                _, _, proxy_cfg = await check_proxy_async(raw_proxy)
                if proxy_cfg is None:
                    CONSOLE.print(f"[yellow]w{idx}: proxy unreachable, running direct[/]")
                    proxy_cfg = _parse_proxy_str(raw_proxy)
            elif raw_proxy:
                CONSOLE.print(f"[dim]w{idx}: proxy too short, using direct[/]")
            result.append(BeluWorkerClient(token=token, proxy=proxy_cfg, profile_key=profile, label=f"w{idx}"))
        return result

    CONSOLE.print(f"[dim]resolving proxies for {len(raw_entries)} workers...[/]")
    workers = asyncio.run(build_workers())
    CONSOLE.print(f"[dim]starting {len(workers)} workers[/]")
    try:
        asyncio.run(run_multi_farm(workers))
    except KeyboardInterrupt:
        pass

    return cfg



def menu_start_auto(cfg: Dict[str, Any]) -> None:
    mode = cfg.get("mode", "one-farm")
    if mode == "multi-farm":
        accounts = cfg.get("accounts", [])
        if not accounts:
            CONSOLE.print("[red]no accounts configured — go to setup config first[/]")
            auto_back()
            return
        _run_multi_from_accounts(accounts, cfg)
    else:
        menu_start_farm(cfg)


def _run_multi_from_accounts(accounts: List[Dict[str, Any]], cfg: Optional[Dict[str, Any]] = None) -> None:
    if cfg is None:
        cfg = {}
    load_settings_into_runtime(cfg)
    async def build_workers() -> List[BeluWorkerClient]:
        result = []
        for idx, acc in enumerate(accounts, 1):
            token = str(acc.get("token", "")).strip()
            raw_proxy = acc.get("proxy")
            profile = str(acc.get("profile", "windows_chrome"))
            if not token:
                continue
            if not _is_valid_token(token):
                CONSOLE.print(f"[yellow]w{idx}: token too short ({len(token)} chars), skipping[/]")
                continue
            proxy_cfg: Optional[ProxyConfig] = None
            if raw_proxy and _is_valid_proxy(str(raw_proxy)):
                _, _, proxy_cfg = await check_proxy_async(raw_proxy)
                if proxy_cfg is None:
                    CONSOLE.print(f"[yellow]w{idx}: proxy unreachable, running direct[/]")
                    proxy_cfg = _parse_proxy_str(raw_proxy)
            elif raw_proxy:
                CONSOLE.print(f"[dim]w{idx}: proxy too short, using direct[/]")
            result.append(BeluWorkerClient(token=token, proxy=proxy_cfg, profile_key=profile, label=f"w{idx}"))
        return result

    CONSOLE.print(f"[dim]resolving proxies for {len(accounts)} workers...[/]")
    workers = asyncio.run(build_workers())
    if not workers:
        CONSOLE.print("[red]no valid workers built[/]")
        auto_back()
        return
    CONSOLE.print(f"[dim]starting {len(workers)} workers[/]")
    try:
        asyncio.run(run_multi_farm(workers))
    except KeyboardInterrupt:
        pass


def _parse_duration(raw: str) -> Optional[int]:
    raw = raw.strip().lower()
    if not raw:
        return None
    # Try plain integer
    try:
        v = int(raw)
        return v if v > 0 else None
    except ValueError:
        pass
    # Parse "5m30s", "5m", "30s", "5m 30s"
    m = re.fullmatch(r'(?:(\d+)\s*m)?\s*(?:(\d+)\s*s?)?', raw)
    if m and (m.group(1) or m.group(2)):
        minutes = int(m.group(1) or 0)
        seconds = int(m.group(2) or 0)
        total = minutes * 60 + seconds
        return total if total > 0 else None
    return None


def _fmt_secs(s: int) -> str:
    if s >= 60:
        m, r = divmod(s, 60)
        return f"{m}m {r:02d}s" if r else f"{m}m"
    return f"{s}s"


def _settings_work_interval(timing: Dict[str, Any]) -> None:
    CONSOLE.print("\n[dim]─── work interval ───[/]")
    CONSOLE.print("[dim]enter time in seconds (330) or minutes+seconds (5m30s, 5m, 30s)[/]")
    CONSOLE.print(f"  [dim]current:[/] ", end="")
    if timing.get("work_fixed") and int(timing["work_fixed"]) > 0:
        wf = int(timing["work_fixed"])
        CONSOLE.print(f"[white]fixed {_fmt_secs(wf)}[/] [dim]({wf}s)[/]")
    else:
        lo = timing.get("work_min", WORK_MIN_DELAY)
        hi = timing.get("work_max", WORK_MAX_DELAY)
        CONSOLE.print(f"[white]random {_fmt_secs(lo)} – {_fmt_secs(hi)}[/]")

    mode_w = ask("mode", hint="fixed / random", default=
        "fixed" if (timing.get("work_fixed") and int(timing["work_fixed"]) > 0) else "random")

    if mode_w.lower().startswith("f"):
        cur = timing.get("work_fixed", WORK_MIN_DELAY)
        raw = ask("  fixed delay", hint="e.g. 5m30s or 330", default=_fmt_secs(int(cur)))
        val = _parse_duration(raw)
        if val and val >= 10:
            timing["work_fixed"] = val
            timing.pop("work_min", None)
            timing.pop("work_max", None)
            CONSOLE.print(f"[dim]  → fixed [white]{_fmt_secs(val)}[/] ({val}s)[/]")
        else:
            CONSOLE.print(f"[yellow]  invalid value, keeping current[/]")
    else:
        timing.pop("work_fixed", None)
        cur_min = timing.get("work_min", WORK_MIN_DELAY)
        cur_max = timing.get("work_max", WORK_MAX_DELAY)
        raw_min = ask("  min delay", hint="e.g. 5m30s  (recommended ≥ 5m30s)", default=_fmt_secs(int(cur_min)))
        raw_max = ask("  max delay", hint="e.g. 7m20s", default=_fmt_secs(int(cur_max)))
        lo = _parse_duration(raw_min)
        hi = _parse_duration(raw_max)
        if lo and hi:
            lo = max(10, lo)
            hi = max(lo + 1, hi)
            timing["work_min"] = lo
            timing["work_max"] = hi
            CONSOLE.print(f"[dim]  → random [white]{_fmt_secs(lo)} – {_fmt_secs(hi)}[/][/]")
        else:
            CONSOLE.print(f"[yellow]  invalid value, keeping current[/]")


def _settings_bal_interval(timing: Dict[str, Any]) -> None:
    CONSOLE.print("\n[dim]─── balance check interval ───[/]")
    CONSOLE.print("[dim]enter time in seconds or minutes+seconds[/]")
    CONSOLE.print(f"  [dim]current:[/] ", end="")
    if timing.get("bal_fixed") and int(timing["bal_fixed"]) > 0:
        bf = int(timing["bal_fixed"])
        CONSOLE.print(f"[white]fixed {_fmt_secs(bf)}[/] [dim]({bf}s)[/]")
    else:
        lo = timing.get("bal_min", BAL_MIN_DELAY)
        hi = timing.get("bal_max", BAL_MAX_DELAY)
        CONSOLE.print(f"[white]random {_fmt_secs(lo)} – {_fmt_secs(hi)}[/]")

    mode_b = ask("mode", hint="fixed / random", default=
        "fixed" if (timing.get("bal_fixed") and int(timing["bal_fixed"]) > 0) else "random")

    if mode_b.lower().startswith("f"):
        cur = timing.get("bal_fixed", BAL_MIN_DELAY)
        raw = ask("  fixed delay", hint="e.g. 20m or 1200", default=_fmt_secs(int(cur)))
        val = _parse_duration(raw)
        if val and val >= 30:
            timing["bal_fixed"] = val
            timing.pop("bal_min", None)
            timing.pop("bal_max", None)
            CONSOLE.print(f"[dim]  → fixed [white]{_fmt_secs(val)}[/] ({val}s)[/]")
        else:
            CONSOLE.print(f"[yellow]  invalid value (min 30s), keeping current[/]")
    else:
        timing.pop("bal_fixed", None)
        cur_min = timing.get("bal_min", BAL_MIN_DELAY)
        cur_max = timing.get("bal_max", BAL_MAX_DELAY)
        raw_min = ask("  min delay", hint="e.g. 20m", default=_fmt_secs(int(cur_min)))
        raw_max = ask("  max delay", hint="e.g. 25m", default=_fmt_secs(int(cur_max)))
        lo = _parse_duration(raw_min)
        hi = _parse_duration(raw_max)
        if lo and hi:
            lo = max(30, lo)
            hi = max(lo + 1, hi)
            timing["bal_min"] = lo
            timing["bal_max"] = hi
            CONSOLE.print(f"[dim]  → random [white]{_fmt_secs(lo)} – {_fmt_secs(hi)}[/][/]")
        else:
            CONSOLE.print(f"[yellow]  invalid value, keeping current[/]")


def _print_settings_summary(timing: Dict[str, Any]) -> None:
    if timing.get("work_fixed") and int(timing["work_fixed"]) > 0:
        w_str = f"fixed {_fmt_secs(int(timing['work_fixed']))}"
    else:
        lo = timing.get("work_min", WORK_MIN_DELAY)
        hi = timing.get("work_max", WORK_MAX_DELAY)
        w_str = f"random {_fmt_secs(lo)} – {_fmt_secs(hi)}"

    if timing.get("bal_fixed") and int(timing["bal_fixed"]) > 0:
        b_str = f"fixed {_fmt_secs(int(timing['bal_fixed']))}"
    else:
        lo = timing.get("bal_min", BAL_MIN_DELAY)
        hi = timing.get("bal_max", BAL_MAX_DELAY)
        b_str = f"random {_fmt_secs(lo)} – {_fmt_secs(hi)}"

    CONSOLE.print(f"  [dim]work interval :[/]  [white]{w_str}[/]")
    CONSOLE.print(f"  [dim]balance check :[/]  [white]{b_str}[/]")


def menu_settings(cfg: Dict[str, Any]) -> Dict[str, Any]:
    timing = cfg.get("timing", {})

    while True:
        CONSOLE.print("\n[dim]─── settings ───[/]")
        _print_settings_summary(timing)
        CONSOLE.print("")
        CONSOLE.print("  [dim]1.[/] [white]work interval[/]")
        CONSOLE.print("  [dim]2.[/] [white]balance check interval[/]")
        CONSOLE.print("  [dim]3.[/] [white]edit all (sequential)[/]")
        CONSOLE.print("  [dim]0.[/] [white]back[/]\n")

        choice = ask("select", hint="1-3 or 0")

        if choice == "1":
            _settings_work_interval(timing)
            cfg["timing"] = timing
            save_config(cfg)
            CONSOLE.print("[green]saved[/]")
        elif choice == "2":
            _settings_bal_interval(timing)
            cfg["timing"] = timing
            save_config(cfg)
            CONSOLE.print("[green]saved[/]")
        elif choice == "3":
            _settings_work_interval(timing)
            _settings_bal_interval(timing)
            cfg["timing"] = timing
            save_config(cfg)
            CONSOLE.print("\n[green]settings saved[/]")
        elif choice == "0":
            break
        else:
            CONSOLE.print("[dim]unknown option[/]")
            time.sleep(0.3)

    return cfg


def menu_about() -> None:
    CONSOLE.clear()
    print_logo()

    lines = [
        ("header",  "StdiX Selfbot Tool - developed by Zeraa - version " + VERSION),
        ("sep",     "─" * 52),
        ("section", "About"),
        ("sep",     "─" * 52),

        # --- Công cụ này là gì? ---
        ("title_vi", "Công cụ này là gì?"),
        ("body_vi",  "Đây là công cụ giúp bạn có thể farm belubucks tự động\n"
                     "  24/7 mà không cần làm gì cả."),
        ("title_en", "What is this tool?"),
        ("body_en",  "This tool lets you automatically farm belubucks 24/7\n"
                     "  without doing anything manually."),
        ("blank",    ""),

        # --- Belubuck để làm gì? ---
        ("title_vi", "Belubuck để làm gì?"),
        ("body_vi",  "Belubuck là tiền tệ trong server belugang (discord.gg/beluga)\n"
                     "  được xài để quy đổi như role, nitro basic 1 month.\n"
                     "  Muốn quy đổi nitro basic 1 month bạn phải có 500k\n"
                     "  belubucks, tương đương ~1 tháng cày nếu farm 24/7."),
        ("title_en", "What is belubuck used for?"),
        ("body_en",  "Belubuck is the currency in the belugang server (discord.gg/beluga),\n"
                     "  used to redeem rewards like roles or nitro basic 1 month.\n"
                     "  To redeem nitro basic 1 month you need 500k belubucks,\n"
                     "  equivalent to ~1 month of 24/7 farming."),
        ("blank",    ""),

        # --- Miễn trừ trách nhiệm ---
        ("section", "Miễn trừ trách nhiệm / Disclaimer"),
        ("sep",     "─" * 52),
        ("body_vi", "Khi bạn sử dụng công cụ này, đồng nghĩa với việc bạn\n"
                    "  chấp nhận mọi rủi ro mà công cụ này gây ra\n"
                    "  (limit, suspend,...). Chúng tôi sẽ không chịu trách\n"
                    "  nhiệm bất cứ vụ nào mà công cụ này gây ra."),
        ("body_en", "By using this tool, you accept all risks it may cause\n"
                    "  (limit, suspend, etc.). We are not responsible for\n"
                    "  any consequences caused by this tool."),
        ("blank",   ""),

        # --- How to get token ---
        ("section", "Cách lấy token / How to get token"),
        ("sep",     "─" * 52),
        ("body_vi", "Bạn có thể lấy token bằng cách install TamperMonkey:"),
        ("body_en", "You can get your token by installing TamperMonkey:"),
        ("link",    "https://chromewebstore.google.com/detail/tampermonkey/"
                    "dhdgffkkebhmkfjojejmpbldmpobfkfo?hl=vi"),
        ("body_vi", "Đảm bảo bạn đã Allow Userscript và bật Developer Mode."),
        ("body_en", "Make sure you have allowed Userscripts and enabled Developer Mode."),
        ("blank",   ""),

        ("body_vi", "Sau đó:"),
        ("body_en", "Then:"),
        ("step_vi", "1. Cài userscript tại:"),
        ("step_en", "1. Install the userscript at:"),
        ("link",    "   https://xhider.xyz/raw/Zeraa/Get_Token.user.js"),
        ("step_vi", "2. Vào trang discord & login"),
        ("step_en", "2. Go to discord & login"),
        ("step_vi", "3. Vô TamperMonkey, nhấn vào \"Open menu\""),
        ("step_en", "3. Open TamperMonkey, click \"Open menu\""),
        ("step_vi", "4. Copy token"),
        ("step_en", "4. Copy the token"),
        ("blank",   ""),
        ("sep",     "─" * 52),
    ]

    for kind, text in lines:
        if kind == "header":
            CONSOLE.print(f"[bold #35d65f]{text}[/]")
        elif kind == "sep":
            CONSOLE.print(f"[dim]{text}[/]")
        elif kind == "section":
            CONSOLE.print(f"\n[bold white]  ── {text} ──[/]")
        elif kind == "title_vi":
            CONSOLE.print(f"\n  [bold #20c5f5]VI: {text}[/]")
        elif kind == "title_en":
            CONSOLE.print(f"  [bold #16d8b2]EN: {text}[/]")
        elif kind == "body_vi":
            first = True
            for sub in text.split("\n"):
                prefix = "[dim]VI:[/] " if first else "     "
                CONSOLE.print(f"  {prefix}[white]{sub}[/]")
                first = False
        elif kind == "body_en":
            first = True
            for sub in text.split("\n"):
                prefix = "[dim]EN:[/] " if first else "     "
                CONSOLE.print(f"  {prefix}[dim]{sub}[/]")
                first = False
        elif kind == "body":
            for sub in text.split("\n"):
                CONSOLE.print(f"  [white]{sub}[/]")
        elif kind == "link":
            CONSOLE.print(f"  [underline #2b7cff]{text}[/]")
        elif kind == "step_vi":
            CONSOLE.print(f"  [dim]  * [/][white]{text}[/]")
        elif kind == "step_en":
            CONSOLE.print(f"  [dim]    [/][dim]{text}[/]")
        elif kind == "step":
            CONSOLE.print(f"  [dim]  * [/][white]{text}[/]")
        elif kind == "blank":
            CONSOLE.print("")

    CONSOLE.print("")
    pause()


def main() -> None:
    cfg = load_config()

    while True:
        CONSOLE.clear()
        print_logo()
        print_menu(cfg)

        choice = ask("select", hint="1-5 or 0")

        if choice == "1":
            menu_start_auto(cfg)
            auto_back()
        elif choice == "2":
            menu_check_proxy(cfg)
            auto_back()
        elif choice == "3":
            cfg = menu_setup_config(cfg)
            auto_back()
        elif choice == "4":
            cfg = menu_settings(cfg)
            auto_back()
        elif choice == "5":
            menu_about()
        elif choice == "0":
            CONSOLE.clear()
            break
        else:
            CONSOLE.print("[dim]unknown option[/]")
            time.sleep(0.4)


if __name__ == "__main__":
    main()