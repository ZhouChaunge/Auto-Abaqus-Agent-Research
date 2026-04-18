# Copilot Code Review — AbaqusGPT 项目指令

## 项目概述

AbaqusGPT 是一个 AI 驱动的 Abaqus 有限元分析助手，包含：
- **Python 后端**（FastAPI + LiteLLM 多模型网关 + Agent 编排）
- **React 前端**（Vite + TypeScript + Tailwind CSS）
- **Docker Compose** 基础设施（backend, frontend, redis, postgres, chromadb）

## 通用审查规则

### 安全性（最高优先级）
- 🔴 **绝不允许** API key、密码、token 等硬编码到代码中。所有敏感值必须通过环境变量加载。
- 🔴 检查 LLM prompt injection 风险：用户输入拼接到 system prompt 前必须转义或沙箱化。
- 🔴 文件上传接口必须校验文件扩展名（仅允许 .msg, .sta, .dat, .inp, .odb）和大小限制。
- 🔴 Docker 配置不得以 root 运行生产容器。
- 检查 CORS 配置是否过于宽泛（生产环境不应使用 `*`）。

### 错误处理
- Agent 和 Workflow 步骤必须有明确的错误处理和重试边界，不允许静默吞掉异常。
- 解析器（InpParser, MsgParser, StaParser）遇到格式错误时应返回有意义的错误信息，而非崩溃。
- LLM 调用必须有超时和重试机制，并处理 rate limit / token limit 等常见错误。

### 类型安全
- Python 代码必须有类型标注（函数签名、返回值）。Pydantic model 用于 API 输入输出。
- TypeScript 严格模式，不允许 `any` 类型，除非有注释说明原因。

### 异步正确性
- FastAPI 路由使用 `async def` 时，不得在其中调用阻塞的同步 I/O（如 `open()`、`time.sleep()`）。
- 数据库和 Redis 操作应使用异步客户端。

### 代码质量
- 不允许引入未使用的 import 或变量。
- 每个 PR 应保持单一职责，不混入无关重构。
- 保持向后兼容：API 接口变更需说明迁移方案。

### 双语支持
- 用户可见的文本（UI、错误提示、日志输出）应同时支持中英文或至少使用中文。
- SKILL.md 文件中的 `description` 和 `description_cn` 需保持同步。

### Abaqus 领域规则
- 涉及 Abaqus 关键字（*STEP, *MATERIAL, *BOUNDARY 等）的解析和生成代码，需确保关键字格式遵循 Abaqus 官方语法。
- 单元类型引用必须对照 `element_library.py` 中的合法类型。
- 收敛诊断逻辑变更须确保不遗漏常见错误模式（参考 `error_codes.py`）。
