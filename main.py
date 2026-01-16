from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register,StarTools
from astrbot.api import logger
import fklib
# import random
# from datetime import datetime
# from zoneinfo import ZoneInfo
@register("fkxdapi", "Guailoudou", "方块行动查询插件", "0.0.1")
class fkxdApi(Star):
    def __init__(self, context: Context,config: AstrBotConfig):
        super().__init__(context)
        logger.info("\n🔍 检查环境...")
        if not fklib.check_nodejs_installation():
            logger.info("错误，环境不可用")
            return
        logger.info("开始获取配置文件")
        self.config = config
        self.data_dir = StarTools.get_data_dir()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""
        logger.info("开始初始化")
        fklib.Config.API_KEY = self.config.API_KEY
        fklib.Config.BASE_URL = self.config.BASE_URL
        fklib.Config.DAEMON_ID = self.config.DAEMON_ID
        fklib.Config.INSTANCE_ID = self.config.INSTANCE_ID
        fklib.Config.FILE_PATH = self.config.FILE_PATH
        fklib.Config.NBT_DIR = self.data_dir
    async def get_data(self):
        # 下载文件
        logger.info("\n📥 第一步：下载 scoreboard.dat 文件...")
        download_result = fklib.download_scoreboard_file()
        
        if not download_result.get("success"):
            logger.info(f"\n❌ 下载失败: {download_result.get('error')}")
            return
        
        # 解析文件
        logger.info("\n🔧 第二步：解析NBT文件...")
        parse_result = fklib.parse_nbt_file()
        
        if not parse_result.get("success"):
            logger.info(f"\n❌ 解析失败: {parse_result.get('error')}")
            return
        
        # 创建分析器
        json_data = parse_result["data"]
        self.analyzer = fklib.ScoreboardAnalyzer(json_data)
        
        logger.info(f"\n✅ 数据加载完成!")
        logger.info(f"- 总玩家数: {len(self.analyzer.get_all_players())}")
        
        # 创建API
        self.fkapi = fklib.BlockOpsAPI(self.analyzer)
        
        # 创建报告生成器
        # self.report_gen = fklib.ReportGenerator()
    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("fkxd_cx", alias={'数据查询'})
    async def cmd_cx(self, event: AstrMessageEvent, player_name: str):
        '''查询'''
        if player_name:
            print(f"\n查询玩家: {player_name}")
            
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
                
                # 生成报告
                # gen_report = input(f"\n是否为 {player_name} 生成详细报告? (y/n): ").lower()
                # if gen_report == 'y':
                #     complete_stats = self.analyzer.get_complete_stats(player_name)
                #     if complete_stats:
                #         report_file = self.report_gen.generate_player_report(player_name, complete_stats)
                #         print(f"报告已保存: {report_file}")
            
            else:
                print(f"\n❌ {result['message']}")

        #yield event.plain_result(f"{user_name}，你今天的人品是{rp}，{message_str}")

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
