---
applyTo: "frontend/**/*.{ts,tsx}"
---

# 前端审查指令

## TypeScript 规范
- 严格模式：不允许使用 `any` 类型，除非有注释说明不可避免的原因。
- API 请求和响应必须定义 TypeScript interface/type。
- 事件处理函数使用正确的 React 事件类型（`React.ChangeEvent<HTMLInputElement>` 等）。

## React 组件
- 优先使用函数组件 + Hooks。
- 避免在 `useEffect` 中遗漏依赖项（exhaustive-deps）。
- 组件 props 必须定义 interface，不使用 inline 类型。
- 状态管理使用 zustand store，避免 prop drilling 超过 2 层。

## API 调用
- 所有后端 API 调用路径必须以 `/api/v1/` 开头。
- SSE 流式响应使用 `EventSource` 或 `fetch` + `ReadableStream`，必须处理连接断开和错误。
- API 错误必须向用户显示有意义的中文提示，不展示原始 JSON 错误。

## 样式
- 使用 Tailwind CSS utility class，不添加自定义 CSS 文件除非有充分理由。
- 响应式设计：关键布局必须在移动端可用（`md:` 断点以上显示侧边栏等）。
- UI 组件优先使用 Radix UI 基础组件。

## 安全
- 不在前端代码中存储或暴露 API key。
- 用户上传文件前必须在前端做格式和大小预校验。
- 使用 `react-markdown` 渲染 LLM 输出时注意 XSS：禁用 `dangerouslySetInnerHTML`。
