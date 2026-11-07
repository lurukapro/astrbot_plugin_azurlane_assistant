import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp

PLUGIN_NAME = "azurlane_assistant"
API_BASE = "https://le3-api.game.bilibili.com/x/api/azurlane/get/"

# UI 还原模板与官方资源
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from blrender import TMPL_BUILD, TMPL_USER, NUM_STRIP, PAGE_BG  # noqa: E402

DEFAULT_AVATAR = "https://i0.hdslb.com/bfs/game-static/d284949d157e85878ddaa4e813969adc464bcd3b.png"
MAINTENANCE_IMG = "https://i0.hdslb.com/bfs/game-static/1102f5758036c05c91be1c2fed3f28ff06ce2289.png"
BUILD_PAGE_SIZE = 8          # 分页模式下每张建造卡的记录条数

# 懒人指令: az/azb/azs 前缀即可触发, 后面可零个或任意分隔符
CMD_RE = re.compile(r"^\s*[/!！]?\s*(azb|azs|az)(?=\s|$|\d|@|[^a-zA-Z]|bind|unbind|绑定|解绑|my|info|我的|帮助|help)", re.IGNORECASE)

BIND_WORDS = ("bind", "绑定")
UNBIND_WORDS = ("unbind", "解绑")
MY_WORDS = ("my", "info", "我的", "绑定信息")
HELP_WORDS = ("help", "帮助", "?", "？")


def _get_data_dir() -> Path:
    """兼容不同 AstrBot 版本：优先使用官方插件数据目录，失败则回退到 data/plugin_data。"""
    try:
        from astrbot.api.star import StarTools
        return Path(StarTools.get_data_dir(PLUGIN_NAME))
    except Exception:
        d = Path(os.getcwd()) / "data" / "plugin_data" / PLUGIN_NAME
        d.mkdir(parents=True, exist_ok=True)
        return d


def _fmt_date(ts) -> str:
    try:
        dt = datetime.fromtimestamp(int(ts))
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except Exception:
        return "-"


def _short_server(name: str) -> str:
    s = str(name or "")
    return s.split("-", 1)[-1] if "-" in s else s


@register("azurlane_assistant", "luruka_llk", "碧蓝航线助手", "1.1.0")
class AzurLaneAssistant(Star):
    def __init__(self, context: Context, config: AstrBotConfig):
        super().__init__(context)
        self.config = config
        self.server_map = {
            "莱茵演习": ("官网1服-莱茵演习", "101"), "夏威夷": ("ios1服-夏威夷", "201"),
            "巴巴罗萨": ("官网2服-巴巴罗萨", "102"), "珊瑚海": ("ios2服-珊瑚海", "202"),
            "霸王行动": ("官网3服-霸王行动", "103"), "中途岛": ("ios3服-中途岛", "203"),
            "冰山行动": ("官网4服-冰山行动", "104"), "铁底湾": ("ios4服-铁底湾", "204"),
            "彩虹计划": ("官网5服-彩虹计划", "105"), "所罗门": ("ios5服-所罗门", "205"),
            "发电机计划": ("官网6服-发电机计划", "106"), "马里亚纳": ("ios6服-马里亚纳", "206"),
            "瞭望台行动": ("官网7服-瞭望台行动", "107"), "莱特湾": ("ios7服-莱特湾", "207"),
            "十字路口行动": ("官网8服-十字路口行动", "108"), "硫磺岛": ("ios8服-硫磺岛", "208"),
            "朱诺行动": ("官网9服-朱诺行动", "109"), "冲绳岛": ("ios9服-冲绳岛", "209"),
            "杜立特空袭": ("官网10服-杜立特空袭", "110"), "阿留申群岛": ("ios10服-阿留申群岛", "210"),
            "地狱犬行动": ("官网11服-地狱犬行动", "111"), "马耳他": ("ios11服-马耳他", "211"),
            "开罗宣言": ("官网12服-开罗宣言", "112"), "奥林匹克行动": ("官网13服-奥林匹克行动", "113"),
            "小王冠行动": ("官网14服-小王冠行动", "114"), "波茨坦公告": ("官网15服-波茨坦公告", "115"),
            "白色方案": ("官网16服-白色方案", "116"), "瓦尔基里行动": ("官网17服-瓦尔基里行动", "117"),
            "曼哈顿计划": ("官网18服-曼哈顿计划", "118"), "八月风暴": ("官网19服-八月风暴", "119"),
            "秋季旅行": ("官网20服-秋季旅行", "120"), "水星行动": ("官网21服-水星行动", "121"),
            "莱茵河卫兵": ("官网22服-莱茵河卫兵", "122"), "北极光计划": ("官网23服-北极光计划", "123"),
            "长戟计划": ("官网24服-长戟计划", "124"), "暴雨行动": ("官网25服-暴雨行动", "125"),
            "水仙行动": ("官网26服-水仙行动", "126"), "冬月计划": ("官网27服-冬月计划", "127"),
            "长弓计划": ("官网28服-长弓计划", "128"), "裁决协议": ("官网29服-裁决协议", "129")
        }
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781",
            'content-type': "application/json",
            'referer': "https://servicewechat.com/wx3ee6dc49667f3444/26/page-frame.html",
        }
        # ---- 账号绑定 ----
        self._bind_path = _get_data_dir() / "bindings.json"
        self._bindings = {}
        self._bind_lock = asyncio.Lock()
        self._load_bindings()
        logger.info(f"[碧蓝助手] 绑定数据目录: {self._bind_path} (已加载 {len(self._bindings)} 条)")
        self._uid_servers = self._uid_cache_load()
        self._dynamic_servers = self._dynamic_cache_load()
        # ---- 查询缓存与冷却 ----
        self._detail_cache = {}
        self._build_cache = {}
        self._cooldowns = {}

    # ============ 数据持久化 ============

    def _load_bindings(self):
        if self._bind_path.exists():
            try:
                self._bindings = json.loads(self._bind_path.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"[碧蓝助手] 绑定数据读取失败，已重置: {e}")
                try:
                    self._bind_path.rename(self._bind_path.with_suffix(".json.bak"))
                except Exception:
                    pass
                self._bindings = {}
        else:
            self._bindings = {}

    async def _save_bindings(self):
        async with self._bind_lock:
            try:
                self._bind_path.parent.mkdir(parents=True, exist_ok=True)
                self._bind_path.write_text(
                    json.dumps(self._bindings, ensure_ascii=False, indent=2), encoding="utf-8"
                )
            except Exception as e:
                logger.error(f"[碧蓝助手] 绑定数据保存失败: {e}")

    async def terminate(self):
        await self._save_bindings()

    # ============ 通用工具 ============

    @staticmethod
    def _user_key(platform: str, sender_id: str) -> str:
        return f"{platform}:{sender_id}"

    def _get_binding(self, event: AstrMessageEvent, sender_id: str = None) -> Optional[dict]:
        sid = str(sender_id) if sender_id else str(event.get_sender_id())
        return self._bindings.get(self._user_key(event.get_platform_name(), sid))

    def _get_at_id(self, event: AstrMessageEvent) -> Optional[str]:
        """从消息链中取出第一个被@的用户QQ号（跳过@全体和@机器人自己）。"""
        self_id = str(event.get_self_id() or "")
        for seg in event.message_obj.message:
            if isinstance(seg, Comp.At):
                qq = str(getattr(seg, "qq", "") or "")
                if qq and qq != "all" and qq != self_id:
                    return qq
        return None

    def _cfg_int(self, key: str, default: int) -> int:
        try:
            return max(0, int(float(self.config.get(key, default))))
        except Exception:
            return default

    def _cfg_str(self, key: str, default: str) -> str:
        return str(self.config.get(key, default) or default)

    def _hit_cooldown(self, event: AstrMessageEvent) -> str:
        """同一用户的查询冷却，返回提示文案（空串表示通过）。"""
        cd = self._cfg_int("cooldown_seconds", 5)
        if cd <= 0:
            return ""
        key = self._user_key(event.get_platform_name(), str(event.get_sender_id()))
        now = time.time()
        remain = int(cd - (now - self._cooldowns.get(key, 0.0)))
        if remain > 0:
            return f"⏳ 查询太频繁啦，请 {remain} 秒后再试～"
        self._cooldowns[key] = now
        return ""

    def _cache_get(self, key: str) -> Optional[dict]:
        ttl = self._cfg_int("cache_seconds", 60)
        if ttl <= 0:
            return None
        item = self._detail_cache.get(key)
        if item and time.time() - item[0] < ttl:
            return item[1]
        return None

    def _cache_set(self, key: str, value):
        self._detail_cache[key] = (time.time(), value)
        if len(self._detail_cache) > 300:
            oldest = sorted(self._detail_cache.items(), key=lambda kv: kv[1][0])[:150]
            for k, _ in oldest:
                self._detail_cache.pop(k, None)

    # ============ 懒人解析 ============

    @staticmethod
    def _lazy_split(text: str) -> List[str]:
        """把指令参数切成 token，容忍不打空格/全角符号：
        'bind1347750182秋季旅行' -> ['bind','1347750182','秋季旅行']"""
        t = str(text or "")
        for ch in ("\u3000", "，", "、", ",", "；", ";", "？", "?"):
            t = t.replace(ch, " ")
        tokens: List[str] = []
        for tok in t.split():
            tokens.extend(re.findall(r"\d+|\D+", tok))
        return tokens

    @staticmethod
    def _take_uid(tokens: List[str]) -> Optional[str]:
        return next((t for t in tokens if t.isdigit() and len(t) >= 6), None)

    @staticmethod
    def _take_range(tokens: List[str]) -> Tuple[Optional[Tuple[int, int]], List[str]]:
        """从 token 中取出范围 [a-b]（如 100-200），返回 ((a,b), 剩余tokens)。
        两侧数字须 ≤4 位，避免把 'UID-服务器ID' 这类输入误判为范围。"""
        for i in range(1, len(tokens) - 1):
            if tokens[i] in ("-", "~", "～") and tokens[i - 1].isdigit() and tokens[i + 1].isdigit() \
                    and len(tokens[i - 1]) <= 4 and len(tokens[i + 1]) <= 4:
                a, b = int(tokens[i - 1]), int(tokens[i + 1])
                if a > b:
                    a, b = b, a
                rest = tokens[:i - 1] + tokens[i + 2:]
                return (a, b), rest
        return None, tokens

    # ============ 接口请求 ============

    def _make_headers(self) -> dict:
        return dict(self.headers)

    async def _api_get(self, endpoint: str, params: dict) -> dict:
        timeout = self._cfg_int("request_timeout", 15) or 15
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(API_BASE + endpoint, params=params, headers=self._make_headers())
            resp.raise_for_status()
            try:
                return resp.json()
            except Exception:
                snippet = (resp.text or "").strip()[:60]
                raise ValueError(f"接口返回异常（疑似触发风控或维护中），稍后再试 [{snippet!r}]")

    async def _fetch_user_detail(self, role_id: str, s_id: str) -> Tuple[Optional[dict], str, bool]:
        """返回 (数据, 错误信息, 是否缓存命中)，成功时错误信息为空。"""
        key = f"{role_id}:{s_id}"
        cached = self._cache_get(key)
        if cached is not None:
            return cached, "", True
        try:
            data = await self._api_get("user_detail", {
                "role_id": str(role_id), "server_id": s_id, "game_id": "182"
            })
        except Exception as e:
            return None, f"网络错误: {e}", False
        if data.get("code") != 0:
            return None, f"接口提示: {data.get('message')}", False
        self._cache_set(key, data)
        return data, "", False

    # ============ UI 卡片渲染 ============

    def _render_mode(self) -> str:
        return "text" if self._cfg_str("render_mode", "image") == "text" else "image"

    def _build_user_render_data(self, data: dict) -> dict:
        d = data.get("data") or {}
        u = d.get("user_info") or {}
        s = d.get("statistics") or {}
        p = d.get("progress_tracking") or {}
        c = d.get("combat_overview") or {}
        beacon = c.get("beacon_challenge") or {}
        return dict(
            page_bg=PAGE_BG, num_strip=NUM_STRIP,
            generated=datetime.now().strftime("%Y-%m-%d %H:%M"),
            avatar=u.get("avatar") or DEFAULT_AVATAR, default_avatar=DEFAULT_AVATAR,
            nickname=u.get("nickname") or "--", level=u.get("level") or "--",
            server=u.get("server") or "--", server_short=_short_server(u.get("server")),
            uid=u.get("uid") or "--",
            teamname=u.get("guild_name") or "无舰队",
            stats={
                "collection_rate": s.get("collection_rate") or "--",
                "mainline_progress": s.get("mainline_progress") or "--",
                "dorm_cur": s.get("dorm_interaction_current") or 0,
                "dorm_max": s.get("dorm_interaction_max") or 0,
                "oil_cur": s.get("oil_current") or 0, "oil_max": s.get("oil_max") or 0,
                "coins_cur": s.get("coins_current") or 0, "coins_max": s.get("coins_max") or 0,
                "food_cur": s.get("food_current") or 0, "food_max": s.get("food_max") or 0,
            },
            commissions=p.get("commissions") or {},
            research=p.get("research") or {},
            under_maintenance=bool(p.get("underMaintenance")),
            maintenance_img=MAINTENANCE_IMG,
            beacon_meta={"remain": beacon.get("meta_challenge_remain") or 0,
                         "max": beacon.get("meta_challenge_max") or 0},
            beacon_parse={"remain": beacon.get("beacon_parse_remain") or 0,
                          "max": beacon.get("beacon_parse_max") or 0},
            exercise={"remain": (c.get("exercise") or {}).get("today_remaining") or 0,
                      "max": (c.get("exercise") or {}).get("daily_max") or 0},
            hard_stage={"remain": (c.get("challenge_stage") or {}).get("hard_stage_extra_remain") or 0,
                        "max": (c.get("challenge_stage") or {}).get("hard_stage_extra_max") or 0},
            dailies=[{"name": ch.get("daily_challenge_name") or "--",
                      "remain": ch.get("daily_challenge_remaining_attempts") or 0,
                      "total": ch.get("daily_total_attempts") or 0}
                     for ch in (c.get("daily_challenges") or [])],
        )

    async def _render_local(self, html: str) -> Optional[str]:
        """本地 playwright 渲染 HTML，成功返回图片文件路径。"""
        out = _get_data_dir() / ("render_%d.png" % int(time.time() * 1000))
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.warning("[碧蓝助手] 未安装 playwright，跳过本地渲染 (pip install playwright && playwright install chromium)")
            return None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(args=["--no-sandbox", "--disable-gpu"])
                try:
                    page = await browser.new_page(viewport={"width": 750, "height": 1200}, device_scale_factor=1)
                    await page.set_content(html, wait_until="networkidle", timeout=120000)
                    await page.wait_for_timeout(1000)
                    await page.screenshot(path=str(out), full_page=True, timeout=120000)
                finally:
                    await browser.close()
            return str(out)
        except Exception as e:
            logger.warning(f"[碧蓝助手] 本地渲染失败: {e}")
            return None

    async def _render_card(self, tmpl: str, data: dict) -> Optional[str]:
        """渲染卡片。策略 auto=本地playwright优先、失败走远程t2i; local=仅本地; remote=仅远程。失败返回 None（回退文本）。"""
        strategy = self._cfg_str("render_strategy", "auto")
        try:
            from jinja2 import Template
            html = Template(tmpl).render(**data)
        except Exception as e:
            logger.warning(f"[碧蓝助手] 模板渲染失败: {e}")
            return None
        if strategy in ("auto", "local"):
            path = await self._render_local(html)
            if path:
                return path
            if strategy == "local":
                return None
        if strategy in ("auto", "remote"):
            try:
                if hasattr(self, "html_render"):
                    return await self.html_render(tmpl, data, options={"type": "png", "full_page": True})
            except Exception as e:
                logger.warning(f"[碧蓝助手] 远程渲染失败: {e}")
        return None

    async def _send_user_cards(self, event: AstrMessageEvent, data: dict, header: str = None):
        """按渲染模式发送玩家信息：图片卡（小程序同款 UI）或文本。"""
        if self._render_mode() == "image":
            url = await self._render_card(TMPL_USER, self._build_user_render_data(data))
            if url:
                if header:
                    yield event.plain_result(header)
                yield event.image_result(url)
                return
        text = self._render_user_detail(data)
        yield event.plain_result(f"{header}\n{text}" if header else text)

    # ============ UID 自动识别服务器 ============

    def _uid_cache_load(self) -> dict:
        p = _get_data_dir() / "uid_servers.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _uid_cache_save(self):
        try:
            p = _get_data_dir() / "uid_servers.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(self._uid_servers, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"[碧蓝助手] UID服务器缓存保存失败: {e}")

    async def _find_servers_by_uid(self, role_id: str) -> List[dict]:
        """并发探测全部服务器（含预留新服编号段），返回该UID存在的服务器列表（结果持久化缓存）。"""
        role_id = str(role_id)
        cached = self._uid_servers.get(role_id)
        if cached:
            return cached
        results = []
        items = self._candidate_servers()
        known_ids = {v[1] for k, v in self.server_map.items()}
        timeout = self._cfg_int("request_timeout", 15) or 15
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                for i in range(0, len(items), 8):   # 每批8个并发，降低触发风控的概率
                    batch = items[i:i + 8]

                    async def one(kv):
                        k, v = kv
                        try:
                            resp = await client.get(API_BASE + "user_detail",
                                                    params={"role_id": role_id, "server_id": v[1], "game_id": "182"},
                                                    headers=self._make_headers())
                            data = resp.json()
                        except Exception:
                            return None
                        if data.get("code") != 0:
                            return None
                        u = (data.get("data") or {}).get("user_info") or {}
                        if not u.get("uid"):
                            return None
                        if v[1] not in known_ids:
                            self._register_dynamic(v[1], u.get("server") or v[0])
                        return {"server_name": u.get("server") or v[0], "server_id": v[1],
                                "nickname": u.get("nickname") or "?", "level": u.get("level") or "?"}

                    got = await asyncio.gather(*(one(kv) for kv in batch))
                    results.extend([g for g in got if g])
        except Exception as e:
            logger.warning(f"[碧蓝助手] 自动识别服务器失败: {e}")
            return []
        if results:
            self._uid_servers[role_id] = results
            self._uid_cache_save()
        return results

    # ============ 动态新服识别 ============

    def _dynamic_cache_load(self) -> dict:
        p = _get_data_dir() / "dynamic_servers.json"
        if p.exists():
            try:
                return json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                return {}
        return {}

    def _dynamic_cache_save(self):
        try:
            p = _get_data_dir() / "dynamic_servers.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(self._dynamic_servers, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            logger.error(f"[碧蓝助手] 动态服务器缓存保存失败: {e}")

    def _register_dynamic(self, server_id: str, full_name: str):
        """发现并登记新服务器，持久化后 azs/服务器解析均自动认识。"""
        server_id = str(server_id)
        if not full_name or server_id in self._dynamic_servers:
            return
        self._dynamic_servers[server_id] = full_name
        self._dynamic_cache_save()
        logger.info(f"[碧蓝助手] 发现新服务器: {full_name} (ID:{server_id})，已登记")

    def _candidate_servers(self) -> list:
        """已知40服 + 预留新服编号段(官网130-137, iOS 212-217) + 动态发现的服。"""
        items = [(k, v) for k, v in self.server_map.items()]
        known = {v[1] for k, v in items}
        dyn = {v[1] for k, v in items}
        for sid in [str(130 + i) for i in range(8)] + [str(212 + i) for i in range(6)]:
            if sid in known or sid in dyn:
                continue
            guess = self._dynamic_servers.get(sid) or (f"官网新服{sid}" if sid.startswith("1") else f"iOS新服{sid}")
            items.append((guess, (guess, sid)))
        for sid, name in self._dynamic_servers.items():
            if sid not in known and sid not in dyn:
                items.append((name, (name, sid)))
        return items

    # ============ 服务器工具 ============

    def _resolve_server(self, name) -> Tuple[Optional[str], Optional[str]]:
        """支持：数字ID、中文简称、全名片段（如 官网20）、动态发现的新服"""
        if name is None:
            return None, None
        s = str(name).strip()
        if not s:
            return None, None
        if self._dynamic_servers:
            if s.isdigit():
                dn = self._dynamic_servers.get(s)
                if dn:
                    return dn, s
            for k, v in self._dynamic_servers.items():
                if s in k or k in s:
                    return k, s
        if s.endswith("服"):      # 去掉常见后缀，如 秋季服
            s = s[:-1]
            if not s:
                return None, None
        if s.isdigit():
            for k, v in self.server_map.items():
                if v[1] == s:
                    return v
            return f"ID:{s}", s
        for key, val in self.server_map.items():   # 输入是简名的一部分，如 秋季
            if s in key:
                return val
        for key, val in self.server_map.items():   # 输入包含简名，如 秋季服
            if key in s:
                return val
        for key, val in self.server_map.items():   # 全名片段，如 官网20
            if s in val[0]:
                return val
        return None, None

    def _server_list_text(self) -> str:
        cn = [f"{k}({v[1]})" for k, v in self.server_map.items() if v[1].startswith("1")]
        ios = [f"{k}({v[1]})" for k, v in self.server_map.items() if v[1].startswith("2")]
        txt = "官网服: " + "、".join(cn) + "\n\niOS服: " + "、".join(ios)
        if self._dynamic_servers:
            txt += "\n\n动态发现新服: " + "、".join(f"{k}({v})" for k, v in self._dynamic_servers.items())
        return txt

    # ============ 渲染（文本模式） ============

    def _render_user_detail(self, data: dict) -> str:
        d = data.get("data") or {}
        u = d.get("user_info") or {}
        s = d.get("statistics") or {}
        p = d.get("progress_tracking") or {}
        c = d.get("combat_overview") or {}
        com = p.get("commissions") or {}
        rs = p.get("research") or {}
        ex = (c.get("exercise") or {}).get("today_remaining", "-")
        res = [
            f"⚓指挥官: {u.get('nickname', '?')} (Lv.{u.get('level', '?')})",
            f"🌐服务器: {u.get('server', '?')} (UID:{u.get('uid', '?')})",
            f"📊收集率: {s.get('collection_rate', '?')} | 进度: {s.get('mainline_progress', '?')}",
            f"🏢舰队: {u.get('guild_name') or '无'}",
            "━━━━━━━━━━━━━━",
            f"💰物资: {s.get('coins_current', '?')} | ⛽石油: {s.get('oil_current', '?')}",
            f"🍱存粮: {s.get('food_current', '?')} | 🤺演习: {ex}/10",
            "━━━━━━━━━━━━━━",
            f"📡委托: 🏃{com.get('in_progress', '-')} | ✅{com.get('completed', '-')} | 💤{com.get('idle', '-')}",
            f"🧪科研: 🏃{rs.get('in_progress', '-')} | ✅{rs.get('completed', '-')} | 💤{rs.get('idle', '-')}"
        ]
        todo = [ch.get('daily_challenge_name') for ch in (c.get('daily_challenges') or [])
                if ch.get('daily_challenge_remaining_attempts', 0) > 0]
        res.append(f"⚔️待办副本: {', '.join(todo)}" if todo else "⚔️今日副本已全部完成！")
        return "\n".join(res)

    def _help_text(self) -> str:
        return "\n".join([
            "⚓ 碧蓝航线助手",
            "az bind <UID> [服务器] · 绑定",
            "az / az <UID> / az @好友 · 查信息",
            "azb [数量或100-200] · 查建造长图",
            "azs [服务器] · 查服ID",
            "💡 空格可省略: azbind<UID>秋季旅行、azb50",
            "💡 不填服务器会自动识别",
        ])

    # ============ 绑定操作 ============

    async def _do_bind(self, event: AstrMessageEvent, role_id: str, s_id: str, full_name: str, nickname: str):
        key = self._user_key(event.get_platform_name(), str(event.get_sender_id()))
        self._bindings[key] = {
            "uid": str(role_id),
            "server_id": s_id,
            "server_name": full_name,
            "nickname": nickname,
            "bound_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        await self._save_bindings()
        logger.info(f"[碧蓝助手] 绑定已保存: {key} -> UID:{role_id}@{s_id} (文件: {self._bind_path})")

    # ============ 指令入口（懒人正则分发） ============

    @filter.regex(CMD_RE)
    async def az_dispatcher(self, event: AstrMessageEvent):
        """统一入口: az / azb / azs，参数容忍缺空格、全角符号、粘连。"""
        raw = (event.message_str or "").strip()
        m = CMD_RE.match(raw)
        if not m:
            return
        cmd = m.group(1).lower()
        tokens = self._lazy_split(raw[m.end():])

        # azs 服务器查询
        if cmd == "azs":
            name = "".join(tokens).strip() or None
            async for r in self._cmd_azs(event, name):
                yield r
            return

        # @某人 查询（az / azb 通用）
        at_id = self._get_at_id(event)
        if at_id:
            if cmd == "azb":
                rng, tokens = self._take_range(tokens)
                count = self._take_count(tokens)
                async for r in self._cmd_azb_at(event, at_id, count, rng):
                    yield r
            else:
                async for r in self._cmd_az_at(event, at_id):
                    yield r
            return

        sub = tokens[0].lower() if tokens else ""
        if sub in BIND_WORDS:
            async for r in self._cmd_bind(event, tokens[1:]):
                yield r
        elif sub in UNBIND_WORDS:
            async for r in self._cmd_unbind(event):
                yield r
        elif sub in MY_WORDS:
            async for r in self._cmd_my(event):
                yield r
        elif sub in HELP_WORDS:
            yield event.plain_result(self._help_text())
        elif cmd == "az":
            async for r in self._cmd_az_query(event, tokens):
                yield r
        else:
            async for r in self._cmd_azb_query(event, tokens):
                yield r

    # ============ 子指令实现 ============

    async def _cmd_azs(self, event: AstrMessageEvent, name: Optional[str]):
        if not name:
            yield event.plain_result("🌐 全部服务器（名称 ID）\n━━━━━━━━━━━━━━\n" + self._server_list_text())
            return
        full_name, s_id = self._resolve_server(name)
        if full_name:
            yield event.plain_result(f"✅ 查询结果：{full_name} {s_id}")
        else:
            yield event.plain_result(f"❌ 未识别服务器: {name}\n💡 发送 azs 查看全部服务器")

    async def _cmd_az_at(self, event: AstrMessageEvent, at_id: str):
        other = self._get_binding(event, at_id)
        if not other:
            yield event.plain_result("📭 TA 还没有绑定碧蓝航线账号")
            return
        cd = self._hit_cooldown(event)
        if cd:
            yield event.plain_result(cd)
            return
        data, err, _ = await self._fetch_user_detail(other["uid"], other["server_id"])
        if err:
            yield event.plain_result(f"❌ 查询失败: {err}")
            return
        async for r in self._send_user_cards(event, data):
            yield r

    async def _cmd_azb_at(self, event: AstrMessageEvent, at_id: str, count: Optional[int], rng: Optional[Tuple[int, int]] = None):
        other = self._get_binding(event, at_id)
        if not other:
            yield event.plain_result("📭 TA 还没有绑定碧蓝航线账号")
            return
        cd = self._hit_cooldown(event)
        if cd:
            yield event.plain_result(cd)
            return
        n = min(count or 50, self._cfg_int("max_build_count", 500))
        if rng:
            n = max(n, min(rng[1], self._cfg_int("max_build_count", 500)))
        async for r in self._send_build(event, other["uid"], other["server_id"], n, rng):
            yield r

    async def _cmd_bind(self, event: AstrMessageEvent, tokens: List[str]):
        if not tokens:
            yield event.plain_result("用法: az bind <UID> [服务器]")
            return
        role_id = self._take_uid(tokens)
        if not role_id:
            yield event.plain_result("❌ UID 必须是纯数字")
            return
        server_name = "".join(t for t in tokens if t != role_id)
        if server_name:
            full_name, s_id = self._resolve_server(server_name)
            if not s_id:
                yield event.plain_result(f"❌ 不认识服务器: {server_name}（发 azs 查列表）")
                return
        else:
            # 未填服务器 → 自动识别
            yield event.plain_result(f"🔍 正在识别 UID:{role_id} 所在服…")
            matches = await self._find_servers_by_uid(role_id)
            if not matches:
                yield event.plain_result(f"❌ 没找到 UID {role_id}（40个服都查了）")
                return
            if len(matches) > 1:
                lst = "\n".join(f"• {m['server_name']} - {m['nickname']}" for m in matches)
                yield event.plain_result(f"❓ 该UID在多个服务器:\n{lst}\n指定一个: az bind {role_id} <服务器>")
                return
            full_name = matches[0]["server_name"]
            s_id = matches[0]["server_id"]
        data, err, _ = await self._fetch_user_detail(role_id, s_id)
        if err:
            if err.startswith("网络错误"):
                # 网络异常时仍允许绑定，但提示未验证
                await self._do_bind(event, role_id, s_id, full_name, "未知")
                yield event.plain_result(f"⚠️ 已绑定 UID:{role_id} → {full_name}（联网验证失败，稍后 az my 核对）")
            else:
                yield event.plain_result(f"❌ 绑定失败: {err}")
            return
        nickname = ((data.get("data") or {}).get("user_info") or {}).get("nickname", "未知")
        await self._do_bind(event, role_id, s_id, full_name, nickname)
        # 先秒回绑定成功，卡片渲染完成后单独发送
        yield event.plain_result(f"✅ 绑定成功！⚓ {nickname} (UID:{role_id}) 🌐 {full_name}")
        if self._render_mode() == "image":
            url = await self._render_card(TMPL_USER, self._build_user_render_data(data))
            if url:
                yield event.image_result(url)
                return
        yield event.plain_result(self._render_user_detail(data))

    async def _cmd_unbind(self, event: AstrMessageEvent):
        key = self._user_key(event.get_platform_name(), str(event.get_sender_id()))
        if key in self._bindings:
            old = self._bindings.pop(key)
            await self._save_bindings()
            yield event.plain_result(f"✅ 已解除绑定（UID:{old.get('uid')} {old.get('server_name')}）")
        else:
            yield event.plain_result("📭 还未绑定，发送 az bind <UID> 绑定")

    async def _cmd_my(self, event: AstrMessageEvent):
        b = self._get_binding(event)
        if not b:
            yield event.plain_result("📭 还未绑定，发送 az bind <UID> 绑定")
            return
        yield event.plain_result(
            f"🔗 当前绑定\n⚓ {b.get('nickname', '?')} (UID:{b.get('uid')})\n"
            f"🌐 {b.get('server_name')}\n🕐 绑定时间: {b.get('bound_at', '-')}\n"
            f"💡 发送 az 直接查询自己，az unbind 解除绑定"
        )

    async def _cmd_az_query(self, event: AstrMessageEvent, tokens: List[str]):
        uid = self._take_uid(tokens)
        names = "".join(t for t in tokens if not t.isdigit())
        server_name = names or next((t for t in tokens if t.isdigit() and len(t) < 6), None)
        b = self._get_binding(event)

        if uid is None:
            # 无 UID：只发了服务器名 → 查绑定的 UID；什么都没发 → 查自己
            if not b:
                yield event.plain_result(self._help_text() if not tokens
                                         else "📭 还未绑定，发送 az bind <UID> 绑定")
                return
            if tokens and not server_name:
                yield event.plain_result(self._help_text())
                return
            uid = b["uid"]
            server_name = server_name or b["server_id"]

        auto_used = False
        if not server_name:
            # 未指定服务器 → 自动识别
            cd = self._hit_cooldown(event)
            if cd:
                yield event.plain_result(cd)
                return
            yield event.plain_result(f"🔍 正在自动识别 UID:{uid} 所在服务器（40个）…")
            matches = await self._find_servers_by_uid(uid)
            if not matches:
                yield event.plain_result(f"❌ 没找到 UID {uid}（40个服都查了）")
                return
            if len(matches) > 1:
                lst = "\n".join(f"• {m['server_name']} - {m['nickname']}" for m in matches)
                yield event.plain_result(f"❓ 该UID在多个服务器:\n{lst}\n指定一个: az {uid} <服务器>")
                return
            server_name = matches[0]["server_name"]
            auto_used = True

        full_name, s_id = self._resolve_server(server_name)
        if not s_id:
            yield event.plain_result(f"❌ 不认识服务器: {server_name}")
            return
        if not auto_used:
            cd = self._hit_cooldown(event)
            if cd:
                yield event.plain_result(cd)
                return
        data, err, _ = await self._fetch_user_detail(uid, s_id)
        if err:
            yield event.plain_result(f"❌ 查询失败: {err}")
            return
        async for r in self._send_user_cards(event, data,
                header=("🔍 自动识别服务器: " + full_name) if auto_used else None):
            yield r

    @staticmethod
    def _take_count(tokens: List[str]) -> Optional[int]:
        """取最后一个 1~3 位纯数字 token 作为数量。"""
        for t in reversed(tokens):
            if t.isdigit() and len(t) <= 3:
                return int(t)
        return None

    async def _cmd_azb_query(self, event: AstrMessageEvent, tokens: List[str]):
        """azb 参数解析（容忍缺空格）：
        - azb / azb 50                → 自己绑定账号，默认50条
        - azb 100-200                 → 取第100~200条（多张长图打包合并转发）
        - azb <UID> [服务器] [数量]   → 指定查询（服务器可自动识别）"""
        rng, tokens = self._take_range(tokens)
        if rng:
            a, b = rng
            a = max(1, a)
            b = min(b, a + self._cfg_int("max_build_count", 500) - 1, self._cfg_int("max_build_count", 500))
            rng = (a, b)
        uid = self._take_uid(tokens)
        names = "".join(t for t in tokens if not t.isdigit())
        b = self._get_binding(event)
        max_n = self._cfg_int("max_build_count", 500)
        n = 50

        if uid is None:
            # 无 UID：可能只给了数量（短数字）
            if tokens and tokens[-1].isdigit() and len(tokens[-1]) <= 3:
                n = min(int(tokens[-1]), max_n)
            if not b:
                yield event.plain_result("📭 还未绑定，发送 az bind <UID> 绑定")
                return
            uid = b["uid"]
            server_name = names or b["server_id"]
        else:
            # 有 UID：末尾短数字可能是数量（去掉它仍有服务器名时才成立），两位时视为服务器ID
            rest = [t for t in tokens if t != uid]
            count_tok = None
            if len(tokens) == 2 and rest and rest[-1].isdigit():
                server_name = rest[-1]           # azb <UID> <服务器ID>
            else:
                if rest and rest[-1].isdigit() and len(rest[-1]) <= 3 and any(not t.isdigit() for t in rest[:-1]):
                    count_tok = rest[-1]         # azb <UID> <服务器名> <数量>
                server_name = "".join(t for t in rest if t != count_tok)
            if count_tok:
                n = min(int(count_tok), max_n)
            if not server_name and b:
                server_name = b["server_id"]

        if not server_name:
            if uid is None:
                if not b:
                    yield event.plain_result("❌ 缺少服务器，先 az bind 绑定")
                    return
                server_name = b["server_id"]
            else:
                cd = self._hit_cooldown(event)
                if cd:
                    yield event.plain_result(cd)
                    return
                yield event.plain_result(f"🔍 正在自动识别 UID:{uid} 所在服务器（40个）…")
                matches = await self._find_servers_by_uid(uid)
                if not matches:
                    yield event.plain_result(f"❌ 没找到 UID {uid}（40个服都查了）")
                    return
            if len(matches) > 1:
                lst = "\n".join(f"• {m['server_name']} - {m['nickname']}" for m in matches)
                yield event.plain_result(f"❓ 该UID在多个服务器:\n{lst}\n指定一个: azb {uid} <服务器>")
                return
            server_name = matches[0]["server_name"]

        full_name, s_id = self._resolve_server(server_name)
        if not s_id:
            yield event.plain_result(f"❌ 不认识服务器: {server_name}")
            return
        cd = self._hit_cooldown(event)
        if cd:
            yield event.plain_result(cd)
            return
        fetch_n = rng[1] if rng else n
        async for r in self._send_build(event, uid, s_id, fetch_n, rng):
            yield r

    # ============ 建造记录 ============

    async def _fetch_build_page(self, client, role_id: str, s_id: str, page: int, ps: int) -> Tuple[Optional[dict], str]:
        """拉取单页建造记录，返回 (响应dict, 错误信息)。"""
        try:
            resp = await client.get(
                API_BASE + "build_record",
                params={"role_id": str(role_id), "server_id": s_id, "page_num": str(page), "page_size": str(ps)},
                headers=self._make_headers(),
            )
            try:
                data = resp.json()
            except Exception:
                snippet = (resp.text or "").strip()[:60]
                return None, f"接口返回异常（疑似触发风控或维护中），稍后再试 [{snippet!r}]"
        except Exception as e:
            return None, f"网络错误: {e}"
        if data.get("code") != 0:
            return None, f"接口提示: {data.get('message')}"
        return data, ""

    def _build_cache_get(self, key: str) -> Optional[dict]:
        """建造记录缓存：数据本身有1小时延迟，缓存5分钟以减少请求、避免触发风控。"""
        ttl = max(self._cfg_int("cache_seconds", 60) * 5, 300)
        item = self._build_cache.get(key)
        if item and time.time() - item[0] < ttl:
            return item[1]
        return None

    def _build_cache_set(self, key: str, value):
        self._build_cache[key] = (time.time(), value)
        if len(self._build_cache) > 100:
            oldest = sorted(self._build_cache.items(), key=lambda kv: kv[1][0])[:50]
            for k, _ in oldest:
                self._build_cache.pop(k, None)

    async def _fetch_build_records(self, role_id: str, s_id: str, n: int) -> Tuple[Optional[dict], str]:
        """拉取建造记录原始数据，返回 (payload, 错误信息)。

        payload 额外带 risk=True 表示接口返回空但服务器确有记录（疑似触发风控）。"""
        cache_key = f"{role_id}:{s_id}:{n}"
        cached = self._build_cache_get(cache_key)
        if cached is not None:
            return cached, ""

        target_count = max(1, n)
        page_size = 50
        all_records = []
        nickname, real_uid, s_name, avatar, total_api = "?", str(role_id), "?", "", 0
        err_msg = ""
        risk_hit = False
        try:
            async with httpx.AsyncClient(timeout=self._cfg_int("request_timeout", 15) or 15) as client:
                max_pages = (target_count // page_size) + 2
                page = 1
                while page <= max_pages and len(all_records) < target_count:
                    ps = min(page_size, target_count - len(all_records))
                    data, err = await self._fetch_build_page(client, role_id, s_id, page, ps)
                    if data is None:
                        err_msg = err
                        break
                    d = data.get("data") or {}
                    br = d.get("buildRecords") or {}
                    nickname = d.get("nickname", nickname)
                    real_uid = d.get("uid", real_uid)
                    s_name = d.get("serverName", s_name)
                    avatar = d.get("avatar") or avatar
                    total_api = br.get("total_count", total_api)
                    rows = br.get("data") or []
                    if not rows:
                        if page == 1 and total_api:
                            # 首页为空但服务器确有记录：疑似触发风控，2秒后重试一次
                            risk_hit = True
                            logger.warning("[碧蓝助手] 建造接口返回空(总数%d)，疑似风控，2秒后重试一次", total_api)
                            await asyncio.sleep(2)
                            data, err = await self._fetch_build_page(client, role_id, s_id, page, ps)
                            if data is None:
                                err_msg = err
                                break
                            d = data.get("data") or {}
                            br = d.get("buildRecords") or {}
                            total_api = br.get("total_count", total_api)
                            rows = br.get("data") or []
                            if rows:
                                risk_hit = False
                        if not rows:
                            break
                    all_records.extend(rows)
                    page += 1
                    if page <= max_pages and len(all_records) < target_count:
                        await asyncio.sleep(0.4)   # 页间限速，降低触发风控的概率
        except Exception as e:
            err_msg = f"网络错误: {e}"

        if not all_records and err_msg:
            return None, err_msg
        payload = {
            "nickname": nickname, "uid": real_uid, "server": s_name, "avatar": avatar,
            "total": total_api, "records": all_records, "risk": risk_hit and not all_records,
        }
        if all_records:
            self._build_cache_set(cache_key, payload)
        return payload, ""

    @staticmethod
    def _build_stats(records: List[dict]) -> str:
        pools = {}
        for r in records:
            pool = str(r.get('taskName') or '').strip() or '未知'
            pools[pool] = pools.get(pool, 0) + 1
        return " | ".join(f"{k}×{v}" for k, v in sorted(pools.items(), key=lambda x: -x[1]))

    async def _send_build_cards(self, event: AstrMessageEvent, payload: dict, n: int):
        """建造记录输出：每100条一张长图（单张可直接发送的规格）；多张打包进一条合并转发消息；失败回退文本。"""
        records = payload["records"]
        total = payload.get("total", len(records))
        rng = payload.get("range")
        range_txt = f" · 第{rng[0]}-{rng[1]}条" if rng else ""
        stats = self._build_stats(records)
        head = (
            f"🏗️ 建造查询\n👤 {payload.get('nickname')} ({payload.get('uid')})\n🌐 {payload.get('server')}\n"
            f"📊 共{total}条，本次{len(records)}条{range_txt}" + (f"\n📊 舰池统计: {stats}" if stats else "")
        )

        if self._render_mode() == "image" and records:
            per = 100
            chunks = [records[i:i + per] for i in range(0, len(records), per)]
            page_total = len(chunks)
            gen = datetime.now().strftime("%Y-%m-%d %H:%M")
            urls = []
            for page_no, chunk in enumerate(chunks, 1):
                if not chunk:
                    break
                data = dict(
                    page_bg=PAGE_BG, generated=gen,
                    avatar=payload.get("avatar") or DEFAULT_AVATAR, default_avatar=DEFAULT_AVATAR,
                    nickname=payload.get("nickname") or "--",
                    server=payload.get("server") or "--", server_short=_short_server(payload.get("server")),
                    uid=payload.get("uid") or "--",
                    summary=f"共{total}条 · 本次{len(records)}条{range_txt} · {stats}",
                    page_no=page_no, page_total=page_total,
                    records=[{"taskName": (r.get("taskName") or "").strip() or "未知池",
                              "time": _fmt_date(r.get("buildStartTime")),
                              "avatarIcon": r.get("avatarIcon") or DEFAULT_AVATAR,
                              "name": (r.get("rarity") + "-" if r.get("rarity") else "") + (r.get("roleName") or "未知角色")}
                             for r in chunk],
                )
                url = await self._render_card(TMPL_BUILD, data)
                if not url:
                    break
                urls.append(url)
            if urls:
                if len(urls) == 1:
                    yield event.image_result(urls[0])
                else:
                    note = "" if len(urls) == page_total else f"\n⚠️ 渲染不完整: {len(urls)}/{page_total} 张"
                    content = [Comp.Plain(head + note)]
                    for u in urls:
                        if u.startswith("http"):
                            content.append(Comp.Image.fromURL(u))
                        else:
                            content.append(Comp.Image.fromFileSystem(u))
                    # 多张图放进同一条合并转发的同一个节点，确保只发一条转发消息
                    yield event.chain_result([Comp.Node(uin=event.get_self_id(), name="碧蓝助手",
                                                        content=content)])
                return
            # 渲染失败 → 文本回退

        # ---- 文本回退（统计+记录合并进同一个节点，确保只发一条转发） ----
        lines = [f"• {(r.get('taskName') or '').strip() or '未知'}-{r.get('roleName', '?')}" for r in records]
        text = head + "\n" + "\n".join(lines)
        if len(lines) <= 20:
            yield event.plain_result(text)
            return
        yield event.chain_result([Comp.Node(uin=event.get_self_id(), name="碧蓝助手",
                                            content=[Comp.Plain(text)])])

    async def _send_build(self, event: AstrMessageEvent, role_id: str, s_id: str, n: int, rng: Optional[Tuple[int, int]] = None):
        payload, err = await self._fetch_build_records(role_id, s_id, n)
        if payload is None:
            yield event.plain_result(f"❌ 查询失败，{err}")
            return
        all_records = payload["records"]
        if not all_records:
            total = payload.get("total") or 0
            if total or payload.get("risk"):
                yield event.plain_result("⚠️ 接口风控（查太频繁），几十分钟自动恢复")
            else:
                yield event.plain_result("📭 该UID没有建造记录（或接口风控中，稍后再试）")
            return

        if rng:
            start, end = rng
            if start > len(all_records):
                yield event.plain_result(f"⚠️ 范围超出：本次只有 {len(all_records)} 条记录")
                return
            end = min(end, len(all_records))
            payload = dict(payload, records=all_records[start - 1:end], range=(start, end))
        async for r in self._send_build_cards(event, payload, len(payload["records"])):
            yield r
