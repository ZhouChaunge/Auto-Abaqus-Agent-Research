# AI PR Review 设置指南

本项目支持多种 AI 代码审查工具，参考 StructureClaw 的配置。

## 推荐方案：GitHub Apps（零代码）

### 1. Gemini Code Assist (Google) ⭐ 推荐

**安装步骤：**
1. 访问 [GitHub Marketplace - Gemini Code Assist](https://github.com/marketplace/gemini-code-assist)
2. 点击 "Install it for free"
3. 选择仓库 `ZhouChaunge/AbaqusGPT`
4. 完成授权

**功能：**
- PR 自动代码审查
- 安全漏洞检测
- 代码风格建议
- 支持中英文

**配置文件：** `.gemini/config.yaml` (已创建)

---

### 2. GitHub Copilot for PRs

**安装步骤：**
1. 确保你有 GitHub Copilot 订阅
2. 访问仓库 Settings → Copilot
3. 启用 "Copilot for pull requests"

**功能：**
- PR 摘要自动生成
- 代码审查建议
- 文档更新建议

---

### 3. CodeRabbit (可选)

**安装步骤：**
1. 访问 [CodeRabbit.ai](https://coderabbit.ai)
2. 用 GitHub 登录
3. 选择仓库安装

**配置文件示例：**
```yaml
# .coderabbit.yaml
language: "zh-CN"
reviews:
  auto_review:
    enabled: true
  path_filters:
    - "!**/*.md"
    - "!**/*.txt"
chat:
  auto_reply: true
```

---

## 使用方式

安装后，每次创建 PR 时：
1. AI 会自动审查代码变更
2. 在 PR 评论区给出建议
3. 可以 @ 机器人进行对话

## 参考

- [StructureClaw 仓库](https://github.com/structureclaw/structureclaw) - 使用 Gemini + Copilot
- [Gemini Code Assist 文档](https://cloud.google.com/gemini/docs/code-assist)
