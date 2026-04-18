---
applyTo: "{Dockerfile*,docker-compose*.yml,nginx.conf,frontend/nginx.conf}"
---

# Docker 与基础设施审查指令

## Docker 安全
- 生产镜像不得以 root 用户运行，必须创建非特权用户。
- 不在 Dockerfile 或 docker-compose.yml 中硬编码密码、API key。
  敏感值通过 `${VARIABLE}` 引用环境变量或 `.env` 文件。
- 基础镜像使用 `-slim` 或 `-alpine` 变体，减少攻击面。
- 多阶段构建分离构建依赖和运行依赖。

## Docker Compose
- 所有服务必须定义 `healthcheck`。
- 服务间依赖使用 `depends_on` + `condition: service_healthy`。
- 生产环境不暴露内部服务端口（redis、postgres 不映射到宿主机）。
- 数据卷必须使用命名卷，不使用匿名卷。

## Nginx
- 反向代理配置必须包含正确的 `proxy_set_header`（Host, X-Real-IP 等）。
- SSE 端点需要 `proxy_buffering off` 和适当的超时设置。
- 静态文件应有缓存头。
- 禁止目录列表（`autoindex off`）。
