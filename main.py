import httpx
import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp

@register("azurlane_assistant", "luruka_llk", "碧蓝航线助手", "1.0.0")
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

    def _resolve_server(self, name):
        """核心修复：强制转为字符串，规避 AttributeError"""
        if name is None: return None, None
        name_str = str(name).strip()
        if name_str.isdigit():
            for k, v in self.server_map.items():
                if v[1] == name_str: return v
            return f"ID:{name_str}", name_str
        for key, val in self.server_map.items():
            if name_str in key: return val
        return None, None

    @filter.command("azs")
    async def az_server_query(self, event: AstrMessageEvent, name: str):
        """【独立指令】服务器查询：azs <名称/ID>"""
        full_name, s_id = self._resolve_server(name)
        if full_name:
            yield event.plain_result(f"✅ 查询结果：\n{full_name} {s_id}")
        else:
            yield event.plain_result(f"❌ 未识别服务器: {name}")

    @filter.command("az")
    async def az_user(self, event: AstrMessageEvent, arg1: str = "help", arg2: str = None):
        """【独立指令】用户查询或帮助"""
        # 情况1：az 或 az help
        if arg1.lower() == "help":
            help_msg = [
                "⚓ 碧蓝航线助手帮助",
                "━━━━━━━━━━━━━━",
                "👤 查玩家: az <UID> <服务器名/ID>",
                "🏗️ 查建造: azb <UID> <服务器/ID> [数量]",
                "🌐 查服ID: azs <服务器名/ID>",
                "━━━━━━━━━━━━━━",
                "💡 UID是游戏内UID，服务器可输（如 120、秋季旅行、秋季）"
            ]
            yield event.plain_result("\n".join(help_msg))
            return

        # 情况2：az <UID> <服务器>
        if arg2 is None:
            yield event.plain_result("❌ 缺少服务器参数！\n格式: az <UID> <服务器>\n或输入 az help")
            return

        role_id, server_input = str(arg1), arg2
        full_name, s_id = self._resolve_server(server_input)

        if not s_id:
            yield event.plain_result(f"❌ 未识别服务器: {server_input}"); return
            
        url = "https://le3-api.game.bilibili.com/x/api/azurlane/get/user_detail"
        params = {'role_id': role_id, 'server_id': s_id, 'game_id': "182"}
        headers = self.headers.copy()
        headers['Cookie'] = self.config.get("cookie", "")
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, headers=headers)
                data = resp.json()
            except Exception as e:
                yield event.plain_result(f"❌ 网络错误: {str(e)}"); return

        if data.get("code") != 0:
            yield event.plain_result(f"❌ 接口提示: {data.get('message')}"); return
            
        d = data['data']; u = d['user_info']; s = d['statistics']; p = d['progress_tracking']; c = d['combat_overview']
        res = [
            f"⚓指挥官: {u['nickname']} (Lv.{u['level']})",
            f"🌐服务器: {u['server']} (UID:{u['uid']})",
            f"📊收集率: {s['collection_rate']} | 进度: {s['mainline_progress']}",
            f"🏢舰队: {u['guild_name'] or '无'}",
            "━━━━━━━━━━━━━━",
            f"💰物资: {s['coins_current']} | ⛽石油: {s['oil_current']}",
            f"🍱存粮: {s['food_current']} | 🤺演习: {c['exercise']['today_remaining']}/10",
            "━━━━━━━━━━━━━━",
            f"📡委托: 🏃{p['commissions']['in_progress']} | ✅{p['commissions']['completed']} | 💤{p['commissions']['idle']}",
            f"🧪科研: 🏃{p['research']['in_progress']} | ✅{p['research']['completed']} | 💤{p['research']['idle']}"
        ]
        todo = [ch['daily_challenge_name'] for ch in c['daily_challenges'] if ch['daily_challenge_remaining_attempts'] > 0]
        res.append(f"⚔️待办副本: {', '.join(todo)}" if todo else "⚔️今日副本已全部完成！")
        yield event.plain_result("\n".join(res))

    @filter.command("azb")
    async def az_build(self, event: AstrMessageEvent, uid: str, server: str, count: int = 10):
        """【独立指令】建造记录查询"""
        full_name, s_id = self._resolve_server(server)
        if not s_id:
            yield event.plain_result(f"❌ 未识别服务器: {server}"); return

        target_count = min(count, 500)
        page_size, all_records = 50, []
        headers = self.headers.copy(); headers['Cookie'] = self.config.get("cookie", "")
        url = "https://le3-api.game.bilibili.com/x/api/azurlane/get/build_record"

        async with httpx.AsyncClient() as client:
            for page in range(1, (target_count // page_size) + 2):
                if len(all_records) >= target_count: break
                ps = min(page_size, target_count - len(all_records))
                try:
                    resp = await client.get(url, params={'role_id': str(uid), 'server_id': s_id, 'page_num': str(page), 'page_size': str(ps)}, headers=headers)
                    data = resp.json()
                    if data.get("code") != 0: break
                    d = data['data']
                    nickname, real_uid, s_name, total_api = d['nickname'], d['uid'], d['serverName'], d['buildRecords']['total_count']
                    if not d['buildRecords']['data']: break
                    all_records.extend(d['buildRecords']['data'])
                except: break

        if not all_records:
            yield event.plain_result("📭 未查到记录。"); return

        head = f"🏗️ 建造查询\n👤 {nickname} ({real_uid})\n🌐 {s_name}\n📊 共{total_api}条，拉取{len(all_records)}条\n━━━━━━━━━━━━━━"
        lines = [f"• {r['roleName']} [{r['taskName']}]" for r in all_records]

        if len(lines) <= 20:
            yield event.plain_result(head + "\n" + "\n".join(lines))
        else:
            nodes = [Comp.Node(uin=event.get_self_id(), name="碧蓝助手", content=[Comp.Plain(head)])]
            for i in range(0, len(lines), 100):
                nodes.append(Comp.Node(uin=event.get_self_id(), name="记录详情", content=[Comp.Plain("\n".join(lines[i:i+100]))]))
            yield event.chain_result(nodes)