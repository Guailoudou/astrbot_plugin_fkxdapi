# import requests
import aiohttp,asyncio
import json
import subprocess
import os
import sys
import shutil
from collections import defaultdict
import pandas as pd
from datetime import datetime
from astrbot.api import logger
# ====================== 全局配置 ======================
class Config:
    # API配置
    BASE_URL = ''
    API_KEY = ''
    DAEMON_ID = ''
    INSTANCE_ID = ''
    FILE_PATH = '/Block Ops/data/scoreboard.dat'
    
    # 文件路径
    NBT_DIR = r"./"
    JS_FILE = r"./nbtfile_lib_tester.js"
    #OUTPUT_DIR = r"D:\python-tools\MC\玩家数据报告"  # 玩家报告输出目录
    
    # 计分板项目映射（根据实际数据调整）
    OBJECTIVE_MAPPING = {
        # 生涯数据
        "levels": "等级",
        "rank_exp": "升级所需经验", 
        "player_exp": "当前拥有经验",
        "round_played": "总游玩场次",
        "win_counter": "获胜场次",
        "lost_counter": "失败场次",
        "totalscores": "生涯累计得分",
        "life_kill": "生涯击杀数",
        "life_death": "生涯死亡数",
        
        # 职业数据
        "classkill_1": "特种兵熟练度",
        "classkill_2": "特工熟练度",
        "classkill_3": "执法者熟练度", 
        "classkill_4": "牛仔熟练度",
        "classkill_5": "狙击手熟练度",
        "classkill_6": "战地医生熟练度",
        "classkill_7": "泰坦熟练度",
        "classkill_8": "冲锋手熟练度",
        
        # 载具数据
        "vehiclekill_ground": "陆地载具熟练度",
        "vehiclekill_air": "空中载具熟练度", 
        "vehiclekill_sea": "海上载具熟练度",
        "vehiclekill_stationary": "定点武器熟练度"
    }

# ====================== 文件下载模块 ======================
async def download_scoreboard_file():
    """下载scoreboard.dat文件"""
    
    def get_headers():
        return {
            "Content-Type": "application/json; charset=utf-8",
            "X-Requested-With": "XMLHttpRequest"
        }
    async def get_download_file(instance_id, file_path):
        """获取下载文件参数"""
        url = f"{Config.BASE_URL}files/download?apikey={Config.API_KEY}"
        params = {"daemonId": Config.DAEMON_ID, "uuid": instance_id ,"file_name": file_path}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=get_headers(), timeout=30) as response:
                if response.status >= 400:
                    text = await response.text()
                    logger.error(f"HTTP 错误 {response.status}: {text}")
                    return {"success": False, "error": f"HTTP {response.status}"}
                result = await response.json()
                if result.get("status") == 200:
                    return result.get("data", "")
                else:
                    message = result.get("message", "未知错误")
                    logger.error(f"下载失败: {message}")
                    return {"success": False, "error": message}
    async def download_file(instance_id, file_path):
        """从指定实例下载文件"""
        download_result = await get_download_file(instance_id, file_path)
        url = f"{download_result.get('addr', '')}/download/{download_result.get('password', '')}/scoreboard.dat"
        # url = f"{Config.BASE_URL}files?apikey={Config.API_KEY}"
        # params = {"daemonId": Config.DAEMON_ID, "uuid": instance_id}
        # data = {"target": file_path}
        logger.info(f"开始下载文件...")
        logger.info(f"实例ID: {instance_id}")
        logger.info(f"文件路径: {file_path}")
        logger.info(f"url: {url}")
        
        headers = get_headers()  # 假设 get_headers 是一个函数，调用后返回 dict

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    # 检查 HTTP 状态是否成功（类似 raise_for_status）
                    if response.status >= 400:
                        text = await response.text()
                        logger.error(f"HTTP 错误 {response.status}: {text}")
                        return {"success": False, "error": f"HTTP {response.status}"}
                    # logger.info(f"response={response.text}")
                    # text = await response.text()
                    # result = json.loads(text)
                    file_content = await response.read()  # bytes
                    logger.info(f"文件下载成功! 大小: {len(file_content)} 字节")

                    filename = os.path.basename(file_path)
                    local_filename = filename

                    # ✅ 以二进制模式写入（scoreboard.dat 是二进制 NBT 文件！）
                    with open(local_filename, 'wb') as f:
                        f.write(file_content)

                    full_path = os.path.abspath(local_filename)
                    logger.info(f"文件已保存到: {full_path}")

                    return {
                        "success": True,
                        "filename": local_filename,
                        "size": len(file_content),
                        "full_path": full_path
                    }
                    # if result.get("status") == 200:
                    #     logger.info("文件下载成功!")

                    #     file_content = result.get("data", "")
                    #     if file_content is not None:
                    #         logger.info(f"文件内容大小: {len(str(file_content))} 字节")

                    #         filename = os.path.basename(file_path)
                    #         local_filename = filename  # 或加时间戳避免冲突

                    #         # 同步写入（若需完全异步，可用 aiofiles）
                    #         with open(local_filename, 'w', encoding='utf-8') as f:
                    #             if isinstance(file_content, (dict, list)):
                    #                 json.dump(file_content, f, ensure_ascii=False, indent=2)
                    #             else:
                    #                 f.write(str(file_content))

                    #         full_path = os.path.abspath(local_filename)
                    #         logger.info(f"文件已保存到: {full_path}")

                    #         return {
                    #             "success": True,
                    #             "filename": local_filename,
                    #             "size": len(str(file_content)),
                    #             "full_path": full_path
                    #         }
                    #     else:
                    #         logger.warning("警告: 文件内容为空")
                    #         return {"success": True, "content": None}
                    # else:
                    #     message = result.get("message", "未知错误")
                    #     logger.error(f"下载失败: {message}")
                    #     return {"success": False, "error": message}

            except asyncio.TimeoutError:
                logger.error("请求超时（30秒）")
                return {"success": False, "error": "请求超时"}
            except aiohttp.ClientError as e:
                logger.error(f"aiohttp 客户端错误: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                logger.exception("发生未预期的异常")
                return {"success": False, "error": str(e)}

    
    logger.info("=" * 50)
    logger.info("下载scoreboard.dat文件")
    logger.info("=" * 50)
    
    result = await download_file(Config.INSTANCE_ID, Config.FILE_PATH)
    
    logger.info("=" * 50)
    logger.info("下载结果:"+json.dumps(result, indent=2, ensure_ascii=False))
    logger.info("=" * 50)
    
    return result

# ====================== 解析模块 ======================
def check_nodejs_installation():
    """检查Node.js是否安装"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"✅ Node.js 已安装，版本: {result.stdout.strip()}")
            return True
        else:
            logger.info("❌ Node.js 检查失败")
            return False
    except FileNotFoundError:
        logger.info("❌ 未找到 Node.js，请先安装 Node.js")
        logger.info("下载地址: https://nodejs.org/")
        return False

def parse_nbt_file():
    """解析NBT文件为JSON"""
    
    if not os.path.exists(Config.JS_FILE):
        logger.info(f"错误: 文件不存在 - {Config.JS_FILE}")
        return {"success": False, "error": f"文件不存在: {Config.JS_FILE}"}
    
    js_dir = os.path.dirname(Config.JS_FILE)
    
    try:
        logger.info(f"正在启动 Node.js 脚本: {Config.JS_FILE}")
        
        # 检查scoreboard.dat是否在NBTools目录
        dat_file = os.path.join(Config.NBT_DIR, "scoreboard.dat")
        if not os.path.exists(dat_file):
            # 尝试从当前目录复制
            current_dat = os.path.join(os.getcwd(), "scoreboard.dat")
            if os.path.exists(current_dat):
                logger.info(f"复制 scoreboard.dat 到 NBTools 目录")
                shutil.copy2(current_dat, dat_file)
            else:
                logger.info(f"错误: 找不到 scoreboard.dat 文件")
                return {"success": False, "error": "找不到 scoreboard.dat 文件"}
        
        # 执行Node.js脚本
        result = subprocess.run(
            ['node', Config.JS_FILE],
            cwd=js_dir,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8'
        )
        
        logger.info("=" * 60)
        logger.info("Node.js 脚本输出:")
        logger.info("=" * 60)
        logger.info(result.stdout)
        
        if result.stderr:
            logger.info("=" * 60)
            logger.info("错误输出:")
            logger.info("=" * 60)
            logger.info(result.stderr)
        
        logger.info(f"退出代码: {result.returncode}")
        
        # 检查输出文件
        output_json = os.path.join(js_dir, "scoreboard.json")
        if os.path.exists(output_json):
            logger.info(f"✅ 已生成输出文件: {output_json}")
            logger.info(f"文件大小: {os.path.getsize(output_json)} 字节")
            
            try:
                with open(output_json, 'r', encoding='utf-8') as f:
                    parsed_data = json.load(f)
                logger.info(f"成功解析数据，JSON对象大小: {len(str(parsed_data))} 字符")
                return {
                    "success": True, 
                    "data": parsed_data, 
                    "output_file": output_json,
                    "file_size": os.path.getsize(output_json)
                }
            except json.JSONDecodeError as e:
                logger.info(f"❌ 读取JSON文件失败: {e}")
                return {"success": False, "error": f"JSON解析失败: {e}"}
        else:
            logger.info("❌ 未找到输出文件 scoreboard.json")
            return {"success": False, "error": "输出文件未生成"}
            
    except subprocess.TimeoutExpired:
        error_msg = "Node.js 脚本执行超时 (30秒)"
        logger.info(f"❌ {error_msg}")
        return {"success": False, "error": error_msg}
    except FileNotFoundError:
        error_msg = "❌ 未找到 Node.js 命令"
        logger.info(error_msg)
        return {"success": False, "error": error_msg}
    except Exception as e:
        error_msg = f"❌ 执行脚本时发生错误: {e}"
        logger.info(error_msg)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": error_msg}

# ====================== 数据解析与查询模块 ======================
class ScoreboardAnalyzer:
    """计分板数据分析器"""
    
    def __init__(self, json_data):
        self.json_data = json_data
        self.player_stats = defaultdict(dict)
        self.all_players = set()
        self._parse_data()
    
    def _parse_data(self):
        """解析JSON数据"""
        player_scores = self.json_data.get("data", {}).get("PlayerScores", [])
        
        for entry in player_scores:
            player_name = entry.get("Name")
            objective = entry.get("Objective")
            score = entry.get("Score")
            
            if player_name and objective is not None and score is not None:
                self.player_stats[player_name][objective] = score
                self.all_players.add(player_name)
    
    def get_all_players(self):
        """获取所有玩家列表"""
        return sorted(list(self.all_players))
    
    def player_exists(self, player_name):
        """检查玩家是否存在"""
        return player_name in self.player_stats
    
    def get_life_stats(self, player_name):
        """获取玩家生涯数据"""
        if not self.player_exists(player_name):
            return None
        
        stats = {}
        player_data = self.player_stats[player_name]
        
        # 基础生涯数据
        stats["等级"] = player_data.get("levels", 0)
        stats["升级所需经验"] = player_data.get("rank_exp", 0)
        stats["当前拥有经验"] = player_data.get("player_exp", 0)
        stats["总游玩场次"] = player_data.get("round_played", 0)
        stats["获胜场次"] = player_data.get("win_counter", 0)
        stats["失败场次"] = player_data.get("lost_counter", 0)
        stats["生涯累计得分"] = player_data.get("totalscores", 0)
        stats["生涯击杀数"] = player_data.get("life_kill", 0)
        stats["生涯死亡数"] = player_data.get("life_death", 0)
        
        # 计算K/D
        kills = stats["生涯击杀数"]
        deaths = stats["生涯死亡数"]
        if deaths > 0:
            stats["K/D"] = round(kills / deaths, 2)
        else:
            stats["K/D"] = kills if kills > 0 else 0
        
        # 计算胜率
        total_games = stats["总游玩场次"]
        wins = stats["获胜场次"]
        if total_games > 0:
            stats["胜率"] = f"{round(wins / total_games * 100, 1)}%"
        else:
            stats["胜率"] = "0%"
        
        return stats
    
    def get_class_stats(self, player_name):
        """获取玩家职业数据"""
        if not self.player_exists(player_name):
            return None
        
        stats = {}
        player_data = self.player_stats[player_name]
        
        # 职业熟练度
        class_mapping = {
            "特种兵熟练度": "classkill_1",
            "特工熟练度": "classkill_2", 
            "执法者熟练度": "classkill_3",
            "牛仔熟练度": "classkill_4",
            "狙击手熟练度": "classkill_5",
            "战地医生熟练度": "classkill_6",
            "泰坦熟练度": "classkill_7",
            "冲锋手熟练度": "classkill_8"
        }
        
        for name_cn, name_en in class_mapping.items():
            stats[name_cn] = player_data.get(name_en, 0)
        
        return stats
    
    def get_vehicle_stats(self, player_name):
        """获取玩家载具数据"""
        if not self.player_exists(player_name):
            return None
        
        stats = {}
        player_data = self.player_stats[player_name]
        
        # 载具熟练度
        vehicle_mapping = {
            "陆地载具熟练度": "vehiclekill_ground",
            "空中载具熟练度": "vehiclekill_air",
            "海上载具熟练度": "vehiclekill_sea",
            "定点武器熟练度": "vehiclekill_stationary"
        }
        
        for name_cn, name_en in vehicle_mapping.items():
            stats[name_cn] = player_data.get(name_en, 0)
        
        return stats
    
    def get_complete_stats(self, player_name):
        """获取玩家完整数据"""
        life_stats = self.get_life_stats(player_name)
        class_stats = self.get_class_stats(player_name)
        vehicle_stats = self.get_vehicle_stats(player_name)
        
        if not life_stats:
            return None
        
        complete_stats = {
            "玩家名": player_name,
            "查询时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "生涯数据": life_stats,
            "职业数据": class_stats or {},
            "载具数据": vehicle_stats or {}
        }
        
        return complete_stats
    
    def generate_leaderboard(self, category="生涯累计得分", top_n=10):
        """生成排行榜"""
        leaderboard = []
        
        for player_name in self.get_all_players():
            player_data = self.player_stats[player_name]
            
            if category in player_data:
                leaderboard.append({
                    "玩家名": player_name,
                    "分数": player_data[category]
                })
            elif category == "K/D":
                # 计算K/D
                kills = player_data.get("life_kill", 0)
                deaths = player_data.get("life_death", 1)
                kd = kills / deaths if deaths > 0 else kills
                leaderboard.append({
                    "玩家名": player_name,
                    "分数": round(kd, 2)
                })
            elif category == "胜率":
                # 计算胜率
                total = player_data.get("round_played", 0)
                wins = player_data.get("win_counter", 0)
                win_rate = wins / total * 100 if total > 0 else 0
                leaderboard.append({
                    "玩家名": player_name,
                    "分数": round(win_rate, 2)
                })
        
        # 排序
        leaderboard.sort(key=lambda x: x["分数"], reverse=True)
        return leaderboard[:top_n]

# ====================== 报告生成模块 ======================
# class ReportGenerator:
#     """报告生成器"""
    
#     def __init__(self, output_dir=Config.OUTPUT_DIR):
#         self.output_dir = output_dir
#         os.makedirs(output_dir, exist_ok=True)
    
#     def generate_player_report(self, player_name, stats):
#         """为单个玩家生成报告"""
#         if not stats:
#             return False
        
#         # 创建玩家目录
#         player_dir = os.path.join(self.output_dir, player_name)
#         os.makedirs(player_dir, exist_ok=True)
        
#         # 生成报告文件
#         report_file = os.path.join(player_dir, f"{player_name}_数据报告.md")
        
#         with open(report_file, 'w', encoding='utf-8') as f:
#             # 标题
#             f.write(f"# BLOCK-OPS 玩家数据报告\n\n")
#             f.write(f"**查询玩家:** {player_name}\n")
#             f.write(f"**生成时间:** {stats['查询时间']}\n\n")
            
#             # 生涯数据
#             f.write("## 生涯数据\n")
#             f.write("| 项目 | 数值 |\n")
#             f.write("|------|------|\n")
#             for key, value in stats['生涯数据'].items():
#                 f.write(f"| {key} | {value} |\n")
#             f.write("\n")
            
#             # 职业数据
#             if stats['职业数据']:
#                 f.write("## 职业数据\n")
#                 f.write("| 职业 | 熟练度 |\n")
#                 f.write("|------|--------|\n")
#                 for class_name, skill in stats['职业数据'].items():
#                     f.write(f"| {class_name} | {skill} |\n")
#                 f.write("\n")
            
#             # 载具数据
#             if stats['载具数据']:
#                 f.write("## 载具数据\n")
#                 f.write("| 载具类型 | 熟练度 |\n")
#                 f.write("|----------|--------|\n")
#                 for vehicle_type, skill in stats['载具数据'].items():
#                     f.write(f"| {vehicle_type} | {skill} |\n")
#                 f.write("\n")
            
#             # 数据摘要
#             f.write("## 数据摘要\n")
#             life_stats = stats['生涯数据']
#             f.write(f"- **总场次:** {life_stats.get('总游玩场次', 0)}\n")
#             f.write(f"- **胜率:** {life_stats.get('胜率', '0%')}\n")
#             f.write(f"- **K/D比:** {life_stats.get('K/D', 0)}\n")
#             f.write(f"- **总得分:** {life_stats.get('生涯累计得分', 0)}\n")
#             f.write(f"- **等级:** {life_stats.get('等级', 0)}\n")
        
#         logger.info(f"✅ 已生成玩家报告: {report_file}")
#         return report_file
    
#     def generate_global_leaderboard(self, analyzer):
#         """生成全局排行榜"""
#         leaderboard_file = os.path.join(self.output_dir, "排行榜.md")
        
#         with open(leaderboard_file, 'w', encoding='utf-8') as f:
#             f.write("# BLOCK-OPS 排行榜\n\n")
#             f.write(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
#             f.write(f"**总玩家数:** {len(analyzer.get_all_players())}\n\n")
            
#             # 总得分排行榜
#             f.write("## 总得分排行榜\n")
#             f.write("| 排名 | 玩家名 | 总得分 |\n")
#             f.write("|------|--------|--------|\n")
#             leaderboard = analyzer.generate_leaderboard("totalscores", 20)
#             for i, entry in enumerate(leaderboard, 1):
#                 f.write(f"| {i} | {entry['玩家名']} | {entry['分数']} |\n")
#             f.write("\n")
            
#             # K/D排行榜
#             f.write("## K/D排行榜\n")
#             f.write("| 排名 | 玩家名 | K/D |\n")
#             f.write("|------|--------|-----|\n")
#             leaderboard = analyzer.generate_leaderboard("K/D", 20)
#             for i, entry in enumerate(leaderboard, 1):
#                 f.write(f"| {i} | {entry['玩家名']} | {entry['分数']} |\n")
#             f.write("\n")
            
#             # 胜率排行榜
#             f.write("## 胜率排行榜\n")
#             f.write("| 排名 | 玩家名 | 胜率 |\n")
#             f.write("|------|--------|------|\n")
#             leaderboard = analyzer.generate_leaderboard("胜率", 20)
#             for i, entry in enumerate(leaderboard, 1):
#                 f.write(f"| {i} | {entry['玩家名']} | {entry['分数']}% |\n")
#             f.write("\n")
            
#             # 击杀排行榜
#             f.write("## 击杀排行榜\n")
#             f.write("| 排名 | 玩家名 | 击杀数 |\n")
#             f.write("|------|--------|--------|\n")
#             leaderboard = analyzer.generate_leaderboard("life_kill", 20)
#             for i, entry in enumerate(leaderboard, 1):
#                 f.write(f"| {i} | {entry['玩家名']} | {entry['分数']} |\n")
            
#             # 等级排行榜
#             f.write("\n## 等级排行榜\n")
#             f.write("| 排名 | 玩家名 | 等级 |\n")
#             f.write("|------|--------|------|\n")
#             leaderboard = analyzer.generate_leaderboard("levels", 20)
#             for i, entry in enumerate(leaderboard, 1):
#                 f.write(f"| {i} | {entry['玩家名']} | {entry['分数']} |\n")
        
#         logger.info(f"✅ 已生成全局排行榜: {leaderboard_file}")
#         return leaderboard_file

# ====================== API接口模块 ======================
class BlockOpsAPI:
    """方块行动查询API"""
    
    def __init__(self, analyzer):
        self.analyzer = analyzer
    
    def query_life_stats(self, player_name):
        """查询生涯数据"""
        stats = self.analyzer.get_life_stats(player_name)
        
        if not stats:
            return {
                "success": False,
                "message": f"你所查询的玩家不在方块行动官方数据库中。\n可能原因如下：\n1. 你输入了错误的玩家ID\n2. 官方数据库还未更新\n3. 该玩家ID并未在方块行动官方服务器中游玩。"
            }
        
        response = f"""BLOCK-OPS生涯数据查询

查询玩家：{player_name}

等级：{stats.get('等级', 0)} 升级所需经验：{stats.get('升级所需经验', 0)} 当前拥有经验：{stats.get('当前拥有经验', 0)}

总游玩场次：{stats.get('总游玩场次', 0)} 获胜场次：{stats.get('获胜场次', 0)} 失败场次: {stats.get('失败场次', 0)}

生涯累计得分：{stats.get('生涯累计得分', 0)}

击杀数：{stats.get('生涯击杀数', 0)} 死亡数：{stats.get('生涯死亡数', 0)} K/D：{stats.get('K/D', 0)}

胜率：{stats.get('胜率', '0%')}"""
        
        return {"success": True, "data": response, "stats": stats}
    
    def query_class_stats(self, player_name):
        """查询职业数据"""
        stats = self.analyzer.get_class_stats(player_name)
        
        if not stats:
            return {
                "success": False,
                "message": f"你所查询的玩家不在方块行动官方数据库中。\n可能原因如下：\n1. 你输入了错误的玩家ID\n2. 官方数据库还未更新\n3. 该玩家ID并未在方块行动官方服务器中游玩。"
            }
        
        response_lines = [f"BLOCK-OPS 职业数据查询", f"", f"查询玩家：{player_name}", f""]
        
        for class_name, skill in stats.items():
            response_lines.append(f"{class_name}: {skill}")
        
        response = "\n".join(response_lines)
        return {"success": True, "data": response, "stats": stats}
    
    def query_vehicle_stats(self, player_name):
        """查询载具数据"""
        stats = self.analyzer.get_vehicle_stats(player_name)
        
        if not stats:
            return {
                "success": False,
                "message": f"你所查询的玩家不在方块行动官方数据库中。\n可能原因如下：\n1. 你输入了错误的玩家ID\n2. 官方数据库还未更新\n3. 该玩家ID并未在方块行动官方服务器中游玩。"
            }
        
        response_lines = [f"BLOCK-OPS 载具数据查询", f"", f"查询玩家：{player_name}", f""]
        
        for vehicle_type, skill in stats.items():
            response_lines.append(f"{vehicle_type}: {skill}")
        
        response = "\n".join(response_lines)
        return {"success": True, "data": response, "stats": stats}
    
    def query_all_stats(self, player_name):
        """查询所有数据"""
        life_result = self.query_life_stats(player_name)
        class_result = self.query_class_stats(player_name)
        vehicle_result = self.query_vehicle_stats(player_name)
        
        complete_stats = self.analyzer.get_complete_stats(player_name)
        
        if not complete_stats:
            return {
                "success": False,
                "message": f"你所查询的玩家不在方块行动官方数据库中。"
            }
        
        return {
            "success": True,
            "player": player_name,
            "life_stats": life_result.get("stats") if life_result["success"] else None,
            "class_stats": class_result.get("stats") if class_result["success"] else None,
            "vehicle_stats": vehicle_result.get("stats") if vehicle_result["success"] else None,
            "complete_stats": complete_stats
        }