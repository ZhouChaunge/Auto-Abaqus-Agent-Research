---
applyTo: "**/*.py"
---

# Python 后端审查指令

## FastAPI 路由
- 所有路由函数必须使用 `async def`，除非有充分理由使用同步。
- 使用 Pydantic model 定义请求体和响应体，不使用裸 dict。
- 路由中避免直接调用阻塞 I/O（`open()`, `time.sleep()`, `requests.get()`），
  应使用 `aiofiles`, `asyncio.sleep()`, `httpx.AsyncClient`。
- 文件上传端点必须校验 `ALLOWED_EXTENSIONS`（.msg, .sta, .dat, .inp, .odb）和 `MAX_UPLOAD_SIZE`。

## LLM 调用
- 所有 LLM 调用必须通过 `abaqusgpt/llm/client.py` 的统一接口。
- 不允许直接 `import openai` 或 `import anthropic`，必须经过 LiteLLM 抽象层。
- LLM 调用必须设置 `timeout` 参数，并处理 `litellm.exceptions` 中的常见错误。
- system prompt 中引用用户输入时，必须明确标记为用户内容区域，防止 prompt injection。

## Agent 和 Workflow
- Agent 类必须接受 `model` 参数，不硬编码模型名。
- WorkflowStep 的 `execute()` 方法必须在 try/except 中运行，失败时更新 step 状态为 FAILED。
- Workflow 重试逻辑上限为 3 次（`max_retries=3`），超过后必须向用户报告错误。

## 解析器
- InpParser, MsgParser, StaParser 遇到无法识别的行或格式时，应记录警告并跳过，不应崩溃。
- 解析结果必须有类型标注（返回 Pydantic model 或 TypedDict）。

## 类型标注
- 函数签名必须有参数类型和返回值类型。
- 使用 `from __future__ import annotations` 启用延迟注解。
- 优先使用 `list[str]` 而非 `List[str]`（Python 3.10+）。

## 导入规范
- 标准库、第三方库、项目内部导入之间空一行分隔。
- 不允许 `from module import *`。
