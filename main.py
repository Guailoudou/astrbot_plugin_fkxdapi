from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register,StarTools
from astrbot.api import logger,AstrBotConfig
from .fklib import *
# import random
# from datetime import datetime
# from zoneinfo import ZoneInfo
@register("fkxdapi", "Guailoudou", "方块行动查询插件", "0.0.1")
class fkxdApi(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        logger.info("\n🔍 检查环境...")
        if not check_nodejs_installation():
            logger.info("错误，环境不可用")
            return
        logger.info("开始获取配置文件")
        self.config = config
        self.data_dir = StarTools.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        logger.info("开始初始化")
        Config.API_KEY = self.config.API_KEY
        Config.BASE_URL = self.config.BASE_URL
        Config.DAEMON_ID = self.config.DAEMON_ID
        Config.INSTANCE_ID = self.config.INSTANCE_ID
        Config.FILE_PATH = self.config.FILE_PATH
        Config.NBT_DIR = self.data_dir
        await self.get_data()
    async def get_data(self):
        # 下载文件
        logger.info("\n📥 第一步：下载 scoreboard.dat 文件...")
        download_result = await download_scoreboard_file()
        
        if not download_result.get("success"):
            logger.info(f"\n❌ 下载失败: {download_result.get('error')}")
            return
        
        # 解析文件
        logger.info("\n🔧 第二步：解析NBT文件...")
        parse_result = parse_nbt_file()
        
        if not parse_result.get("success"):
            logger.info(f"\n❌ 解析失败: {parse_result.get('error')}")
            return
        
        # 创建分析器
        json_data = parse_result["data"]
        self.analyzer = ScoreboardAnalyzer(json_data)
        
        logger.info(f"\n✅ 数据加载完成!")
        logger.info(f"- 总玩家数: {len(self.analyzer.get_all_players())}")
        
        # 创建API
        self.fkapi = BlockOpsAPI(self.analyzer)
        
        # 创建报告生成器
        # self.report_gen = ReportGenerator()
    @filter.command("life_stats", alias={'生涯'})
    async def cmd_lifecx(self, event: AstrMessageEvent, player_name: str):
        '''查询生涯数据'''
        if player_name:
            logger.info(f"\n查询玩家: {player_name}")
            
            # 查询所有数据
            result = self.fkapi.query_all_stats(player_name)
            
            if result["success"]:
                # 显示生涯数据
                life_result = self.fkapi.query_life_stats(player_name)
                if life_result["success"]:
                    msg = ""
                    msg +="\n" + "=" * 10
                    msg +="生涯数据:"
                    msg +="=" * 10
                    msg +=life_result["data"]
                    yield event.plain_result(f"{msg}")
            
            else:
                yield event.plain_result(f"\n❌ {result['message']}")
    @filter.command("class_stats", alias={'职业'})
    async def cmd_classcx(self, event: AstrMessageEvent, player_name: str):
        '''查询职业数据'''
        if player_name:
            logger.info(f"\n查询玩家: {player_name}")
            
            # 查询所有数据
            result = self.fkapi.query_all_stats(player_name)
            
            if result["success"]:
                # 显示生涯数据
                life_result = self.fkapi.query_class_stats(player_name)
                if life_result["success"]:
                    msg = ""
                    msg +="\n" + "=" * 10
                    msg +="职业数据:"
                    msg +="=" * 10
                    msg +=life_result["data"]
                    yield event.plain_result(f"{msg}")
            
            else:
                yield event.plain_result(f"\n❌ {result['message']}")

    @filter.command("vehicle_stats", alias={'载具'})
    async def cmd_vehiclecx(self, event: AstrMessageEvent, player_name: str):
        '''查询载具数据'''
        if player_name:
            logger.info(f"\n查询玩家: {player_name}")
            
            # 查询所有数据
            result = self.fkapi.query_all_stats(player_name)
            
            if result["success"]:
                # 显示生涯数据
                life_result = self.fkapi.query_vehicle_stats(player_name)
                if life_result["success"]:
                    msg = ""
                    msg +="\n" + "=" * 10
                    msg +="载具数据:"
                    msg +="=" * 10
                    msg +=life_result["data"]
                    yield event.plain_result(f"{msg}")
            
            else:
                yield event.plain_result(f"\n❌ {result['message']}")
    @filter.command("bo_updata", alias={'方块行动更新'})
    async def cmd_bo_updata(self, event: AstrMessageEvent):
        """更新方块行动数据"""
        if self.is_admin_or_authorized(event):
            await self.get_data()
            yield event.plain_result("\n✅ 数据更新完成")
        else:
            yield event.plain_result("\n❌ 无权限")

    def is_admin_or_authorized(self, event: AstrMessageEvent) -> bool:
        """检查用户权限"""
        if event.is_admin():
            return True
        return str(event.get_sender_id()) in self.config.get("authorized_users", [])
    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
