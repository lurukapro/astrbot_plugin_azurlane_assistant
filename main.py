import httpx
import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger, AstrBotConfig
import astrbot.api.message_components as Comp

@register("azurlane_assistant", "Developer", "碧蓝航线助手", "1.7.0")
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
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090a13) UnifiedPCWindowsWechat(0xf254173b) XWEB/19027",
            'xweb_xhr': "1",
            'content-type': "application/json",
            'referer': "https://servicewechat.com/wx3ee6dc49667f3444/26/page-frame.html",
        }

    def _resolve_server(self, name: str):
        if name.isdigit():
            for k, v in self.server_map.items():
                if v[1] == name: return v
            return f"ID:{name}", name
        for key, val in self.server_map.items():
            if name in key: return val
        return None, None

    @filter.command("azs")
    async def az_server_query(self, event: AstrMessageEvent, server_input: str):
        full_name, s_id = self._resolve_server(server_input)
        if full_name: yield event.plain_result(f"✅ 查询结果：\n{full_name} {s_id}")
        else: yield event.plain_result(f"❌ 未找到服务器。")

    @filter.command("az")
    async def az_user(self, event: AstrMessageEvent, role_id: str, server_name: str = None):
        if server_name is None:
            full_name, s_id = self._resolve_server(role_id)
            if full_name: yield event.plain_result(f"{full_name} {s_id}")
            else: yield event.plain_result(f"❌ 请输入: az <UID> <服务器> 或 azs <名称>")
            return

        full_name, s_id = self._resolve_server(server_name)
        if not s_id: yield event.plain_result(f"❌ 未识别服务器: {server_name}"); return
            
        url = "https://le3-api.game.bilibili.com/x/api/azurlane/get/user_detail"
        params = {'role_id': role_id, 'server_id': s_id, 'game_id': "182"}
        headers = self.headers.copy(); headers['Cookie'] = self.config.get("cookie", "")
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, params=params, headers=headers)
                data = resp.json()
            except Exception: yield event.plain_result("❌ 网络请求失败"); return

        if data.get("code") != 0: yield event.plain_result(f"❌ 错误: {data.get('message')}"); return
            
        d = data['data']; u = d['user_info']; s = d['statistics']; p = d['progress_tracking']; c = d['combat_overview']
        res = [f"⚓指挥官: {u['nickname']} (Lv.{u['level']})", f"🌐服务器: {u['server']} (UID:{u['uid']})", f"📊收集率: {s['collection_rate']} | 进度: {s['mainline_progress']}", f"🏢舰队: {u['guild_name'] or '无'}", "━━━━━━━━━━━━━━", f"💰物资: {s['coins_current']} | ⛽石油: {s['oil_current']}", f"🍱存粮: {s['food_current']} | 🤺演习: {c['exercise']['today_remaining']}/10", "━━━━━━━━━━━━━━", f"📡委托: 🏃{p['commissions']['in_progress']} | ✅{p['commissions']['completed']} | 💤{p['commissions']['idle']}", f"🧪科研: 🏃{p['research']['in_progress']} | ✅{p['research']['completed']} | 💤{p['research']['idle']}"]
        todo = [ch['daily_challenge_name'] for ch in c['daily_challenges'] if ch['daily_challenge_remaining_attempts'] > 0]
        res.append(f"⚔️待办副本: {', '.join(todo)}" if todo else "⚔️今日副本已全部完成！")
        yield event.plain_result("\n".join(res))

    @filter.command("azb")
    async def az_build(self, event: AstrMessageEvent, role_id: str, server_name: str, count: int = 10):
        full_name, s_id = self._resolve_server(server_name)
        if not s_id: yield event.plain_result(f"❌ 未识别服务器: {server_name}"); return

        target_count = min(count, 500)
        page_size = 50 
        all_records = []
        nickname, uid, s_name, total_in_api = "", "", "", 0
        headers = self.headers.copy(); headers['Cookie'] = self.config.get("cookie", "")
        url = "https://le3-api.game.bilibili.com/x/api/azurlane/get/build_record"

        async with httpx.AsyncClient() as client:
            for page in range(1, (target_count // page_size) + 2):
                if len(all_records) >= target_count: break
                current_p_size = min(page_size, target_count - len(all_records))
                if current_p_size <= 0: break
                params = {'role_id': role_id, 'server_id': s_id, 'page_num': str(page), 'page_size': str(current_p_size)}
                try:
                    resp = await client.get(url, params=params, headers=headers)
                    data = resp.json()
                    if data.get("code") != 0: break
                    d = data['data']
                    nickname, uid, s_name = d['nickname'], d['uid'], d['serverName']
                    total_in_api = d['buildRecords']['total_count']
                    page_data = d['buildRecords']['data']
                    if not page_data: break
                    all_records.extend(page_data)
                except Exception: break

        if not all_records: yield event.plain_result("📭 未查询到记录。"); return

        header_text = (f"🏗️ 碧蓝航线建造查询\n👤 指挥官: {nickname} (UID: {uid})\n🌐 服务器: {s_name}\n📊 记录总数: {total_in_api}\n📈 本次拉取: {len(all_records)} 条\n━━━━━━━━━━━━━━")
        record_lines = [f"• {r['roleName']} [{r['taskName']}]" for r in all_records]

        # 逻辑：20条以内直接发，超过20条使用 Node 发送合并转发消息
        if len(record_lines) <= 20:
            yield event.plain_result(header_text + "\n" + "\n".join(record_lines))
        else:
            # 根据文档使用 Comp.Node
            # 如果是 QQ 平台，uin 可以传机器人自己的 ID 或 0，name 为显示的名字
            nodes = []
            
            # 第一条：头部信息
            nodes.append(Comp.Node(uin=event.get_self_id(), name="碧蓝航线助手", content=[Comp.Plain(header_text)]))
            
            # 分段将建造记录放入 Node，每 100 条放一个 Node 节点
            for i in range(0, len(record_lines), 100):
                chunk = record_lines[i:i+100]
                nodes.append(Comp.Node(
                    uin=event.get_self_id(), 
                    name="建造记录详情", 
                    content=[Comp.Plain("\n".join(chunk))]
                ))
            
            yield event.chain_result(nodes)