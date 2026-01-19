# 方块行动查询插件

## 介绍
一个基于MCSM_API的，通过获取`scoreboard.dat`文件，查询方块行动整合包玩家数据的定制插件

## 指令
|触发指令|触发别名|参数|描述|示例|
|-------|-------|----|----|------|
|life_stats|生涯|id|获取玩家生涯信息|/生涯 Guailoudou|
|class_stats|职业|id|获取玩家职业信息|/职业 Guailoudou|
|vehicle_stats|载具|id|获取玩家载具信息|/载具 Guailoudou|
|bo_updata|方块行动更新|无|从服务器更新数据|/方块行动更新|

## 安装方法
1. 先手动给里面的`.js`文件给移动到`/Artbot`路径下
2. 从链接`https://github.com/Guailoudou/astrbot_plugin_fkxdapi`安装插件
3. 填写配置文件信息

## 配置文件
|字段|描述|示例|
|------|------|----|
|API_KEY|MCSM的访问API_KEY|-|
|BASE_URL|MCSM的面板API地址|http://abc.com:43333/api/|
|DAEMON_ID|MCSM的节点ID|-|
|INSTANCE_ID|MCSM的实例ID|-|
|FILE_PATH|dat文件保存路径|/Block Ops/data/scoreboard.dat|
|authorized_users|管理员列表，填QQ号|-|
