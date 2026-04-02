# 项目状态快照

**更新时间**：2026-04-02

## 当前阶段

Phase 1 完成，Phase 2 启动中（框架已搭好，数据待接入）

## 最近完成（2026-04-02）

- **数据库架构切换**：dev 环境从 Docker MySQL 迁移到远程 SQL 查询服务
  - 内网部署 FastAPI SQL 服务（10.189.26.145:9033），经堡垒机反向代理到公网
  - `config.py` dev 模式改为 remote，通过 HTTP 查询 Doris 真实数据
  - `db/connection.py` 支持 remote/direct 双模式，对上层透明
  - 不再依赖本地 Docker MySQL

## 历史完成

- 思考时间轴 + 结构化结果展示（ThinkingTimeline / ResultTable）
- 对话日志（conv_logger）、Decimal 序列化修复
- 侧边栏导航布局、路由 `/`, `/chat`, `/models/yield-curve`

## 下一步

- Phase 2：模型展示页面（YieldCurve 接入真实数据）
- 可选：聊天界面手动测试验证（需要后端 LLM API 密钥）

## 关键约束

- LLM: DeepSeek-V3，东财 API 代理（LLM_API_KEY 环境变量）
- 开发 DB: 远程 SQL 服务（REMOTE_SQL_TOKEN 环境变量），经堡垒机代理查 Doris
- 后端端口: 8000，前端端口: 5173
