# AbaqusGPT 🔧

> 全栈 AI 驱动的 Abaqus 有限元分析助手 — 支持 Web、API、CLI 多端访问，覆盖岩土、结构、机械等多领域专业知识库。

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)

---

## 🎯 项目简介

AbaqusGPT 是一个**全栈智能助手平台**，专为 Abaqus 有限元分析打造：

| 功能模块 | 说明 |
|---------|------|
| 🔴 **收敛诊断** | 自动分析 `.msg`/`.sta` 文件，定位问题根源 |
| 🧱 **模型生成** | 自然语言描述 → `.inp` 文件或 Python 脚本 |
| 🔲 **网格优化** | 网格质量评估 + 优化建议 |
| 📊 **结果解读** | 帮助理解仿真输出，检查合理性 |
| 📚 **专业问答** | 多领域知识库支持（岩土/结构/机械/热分析...） |

### 多端访问

```
┌─────────────────────────────────────────────────────────────┐
│                        用户访问方式                          │
├─────────────┬─────────────┬─────────────┬─────────────────┤
│   🌐 Web UI  │   🔌 REST API │   💻 CLI    │   📓 Jupyter   │
│  (React前端) │  (FastAPI)   │  (命令行)   │   (Notebook)   │
└─────────────┴─────────────┴─────────────┴─────────────────┘
```

---

## 🚀 快速开始

### 方式一：Docker 一键启动 (推荐)

```bash
# 启动完整服务 (前端 + 后端 + 数据库)
docker-compose up -d

# 访问
# - Web UI:  http://localhost:3000
# - API:     http://localhost:8000
# - API文档: http://localhost:8000/docs
```

### 方式二：本地开发安装

```bash
# 克隆项目
git clone https://github.com/ZhouChaunge/AbaqusGPT.git
cd AbaqusGPT

# 安装后端
pip install -e ".[dev]"

# 安装前端
cd frontend && npm install && cd ..

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入 API Key

# 启动后端
uvicorn server.main:app --reload

# 启动前端 (新终端)
cd frontend && npm run dev
```

### 方式三：仅使用 CLI

```bash
pip install abaqusgpt

# 诊断收敛问题
abaqusgpt diagnose Job-1.msg

# 生成 inp 文件
abaqusgpt generate "20x10x5mm钢板，底部固定，顶面10MPa压力"

# 网格检查
abaqusgpt mesh-check model.inp

# 专业问答
abaqusgpt ask "C3D8R和C3D8有什么区别？" --domain geotechnical
```

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                           前端 (Frontend)                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  React SPA  │  │   Tailwind  │  │   Shadcn   │  │  Zustand  │  │
│  │   Web App   │  │     CSS     │  │     UI     │  │   State   │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ HTTP/WebSocket
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          后端 (Backend)                              │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Server                          │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │   │
│  │  │  REST   │  │ WebSocket│  │  Auth   │  │   Rate Limit   │ │   │
│  │  │  API    │  │  实时流  │  │  JWT    │  │    限流保护    │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│  ┌─────────────────────────────┼─────────────────────────────────┐ │
│  │                    智能体层 (Agents)                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │
│  │  │ Converge │  │   Inp    │  │   Mesh   │  │   Material   │  │ │
│  │  │  Doctor  │  │Generator │  │ Advisor  │  │   Helper     │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │ │
│  │  │  Result  │  │ Domain   │  │   QA     │                    │ │
│  │  │Interpret │  │ Expert   │  │  Agent   │                    │ │
│  │  └──────────┘  └──────────┘  └──────────┘                    │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│  ┌─────────────────────────────┼─────────────────────────────────┐ │
│  │                   知识库层 (Knowledge)                         │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │
│  │  │ 🏗️ 岩土  │  │ 🏛️ 结构  │  │ ⚙️ 机械  │  │ 🔥 热分析   │  │ │
│  │  │Geotechni│  │Structural│  │Mechanical│  │  Thermal     │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │
│  │  │ 💥 冲击  │  │ 🔗 复合材│  │ 🩺 生物力│  │ ⚡ 电磁     │  │ │
│  │  │ Impact   │  │Composite │  │Biomech   │  │  EM          │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                │                                    │
│  ┌─────────────────────────────┼─────────────────────────────────┐ │
│  │                    基础设施层 (Infrastructure)                 │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │ │
│  │  │ ChromaDB │  │  Redis   │  │PostgreSQL│  │    Celery    │  │ │
│  │  │ 向量存储 │  │   缓存   │  │  数据库  │  │   任务队列   │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘  │ │
│  └───────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       LLM 后端 (LLM Backend)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │   OpenAI    │  │   Claude    │  │   Ollama    │  │  DeepSeek │  │
│  │  GPT-4/4o   │  │   3.5/4     │  │  本地部署   │  │   V3      │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📁 项目结构

```
AbaqusGPT/
├── frontend/                    # 🌐 React 前端
│   ├── src/
│   │   ├── components/          # UI 组件
│   │   ├── pages/               # 页面
│   │   ├── hooks/               # 自定义 Hooks
│   │   ├── stores/              # Zustand 状态管理
│   │   ├── services/            # API 调用
│   │   └── utils/               # 工具函数
│   ├── package.json
│   └── vite.config.ts
│
├── server/                      # 🔌 FastAPI 后端
│   ├── main.py                  # 入口
│   ├── api/                     # API 路由
│   │   ├── v1/
│   │   │   ├── diagnose.py      # 诊断接口
│   │   │   ├── generate.py      # 生成接口
│   │   │   ├── mesh.py          # 网格接口
│   │   │   ├── chat.py          # 对话接口
│   │   │   └── knowledge.py     # 知识库接口
│   │   └── deps.py              # 依赖注入
│   ├── core/                    # 核心配置
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/                  # 数据模型
│   └── schemas/                 # Pydantic Schemas
│
├── abaqusgpt/                   # 💻 核心引擎 (CLI + 共享逻辑)
│   ├── __init__.py
│   ├── cli.py                   # CLI 入口
│   ├── agents/                  # 智能体
│   │   ├── orchestrator.py      # 任务编排
│   │   ├── converge_doctor.py   # 收敛诊断
│   │   ├── inp_generator.py     # inp 生成
│   │   ├── mesh_advisor.py      # 网格顾问
│   │   ├── material_helper.py   # 材料助手
│   │   ├── result_interpreter.py# 结果解读
│   │   ├── domain_expert.py     # 领域专家
│   │   └── qa_agent.py          # 通用问答
│   ├── parsers/                 # 文件解析
│   │   ├── inp_parser.py
│   │   ├── msg_parser.py
│   │   ├── sta_parser.py
│   │   └── odb_reader.py
│   ├── knowledge/               # 知识库管理
│   │   ├── base.py              # 基类
│   │   ├── domains/             # 领域知识
│   │   │   ├── geotechnical.py  # 🏗️ 岩土工程
│   │   │   ├── structural.py    # 🏛️ 结构工程
│   │   │   ├── mechanical.py    # ⚙️ 机械工程
│   │   │   ├── thermal.py       # 🔥 热分析
│   │   │   ├── impact.py        # 💥 冲击动力学
│   │   │   ├── composite.py     # 🔗 复合材料
│   │   │   ├── biomechanics.py  # 🩺 生物力学
│   │   │   └── electromagnetic.py# ⚡ 电磁分析
│   │   ├── error_codes.py       # 错误代码库
│   │   ├── element_library.py   # 单元类型库
│   │   └── material_models.py   # 材料模型库
│   ├── llm/                     # LLM 接口
│   │   ├── client.py
│   │   ├── providers/
│   │   └── prompts/
│   └── utils/
│
├── knowledge_base/              # 📚 RAG 知识库数据
│   ├── domains/                 # 按领域分类
│   │   ├── geotechnical/        # 岩土
│   │   ├── structural/          # 结构
│   │   ├── mechanical/          # 机械
│   │   └── ...
│   ├── abaqus_docs/             # Abaqus 文档
│   ├── error_cases/             # 错误案例
│   └── templates/               # inp 模板
│
├── tests/                       # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docker/                      # Docker 配置
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml           # 一键部署
├── pyproject.toml               # Python 配置
├── .env.example                 # 环境变量模板
└── README.md
```

---

## 🧠 多领域知识库

AbaqusGPT 内置 **8 大工程领域** 的专业知识库：

| 领域 | 覆盖内容 |
|------|---------|
| 🏗️ **岩土工程** | Mohr-Coulomb、Drucker-Prager、CAM-Clay 模型；土-结构相互作用；渗流耦合 |
| 🏛️ **结构工程** | 混凝土损伤塑性 (CDP)、钢筋建模、地震分析、连续倒塌 |
| ⚙️ **机械工程** | 接触分析、齿轮/轴承建模、疲劳分析、制造工艺仿真 |
| 🔥 **热分析** | 传热、热应力耦合、相变、焊接仿真 |
| 💥 **冲击动力学** | Explicit 求解、碰撞、穿甲、爆炸、材料失效 |
| 🔗 **复合材料** | 层合板建模、Hashin 失效、分层、渐进损伤 |
| 🩺 **生物力学** | 软组织超弹性、骨骼建模、植入物分析 |
| ⚡ **电磁分析** | 电磁-热-结构耦合、感应加热 |

### 使用领域知识

```bash
# CLI 指定领域
abaqusgpt ask "隧道开挖如何设置初始地应力？" --domain geotechnical

# API 调用
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "混凝土CDP模型参数如何标定？", "domain": "structural"}'
```

---

## 🔌 API 参考

### 收敛诊断

```http
POST /api/v1/diagnose
Content-Type: multipart/form-data

file: <.msg or .sta file>
verbose: true
```

### 模型生成

```http
POST /api/v1/generate
Content-Type: application/json

{
  "description": "创建一个钢筋混凝土梁，长3m，截面300x500mm",
  "format": "inp",
  "domain": "structural"
}
```

### 对话接口 (流式)

```http
POST /api/v1/chat/stream
Content-Type: application/json

{
  "message": "如何解决接触分析中的穿透问题？",
  "domain": "mechanical",
  "history": []
}
```

完整 API 文档：http://localhost:8000/docs

---

## 📋 开发路线图

- [x] 项目骨架搭建
- [x] CLI 基础功能
- [ ] **v0.2** - FastAPI 后端 + REST API
- [ ] **v0.3** - React 前端 + 对话界面
- [ ] **v0.4** - 多领域知识库 (岩土/结构/机械)
- [ ] **v0.5** - RAG 增强 + 向量检索
- [ ] **v0.6** - 用户系统 + 历史记录
- [ ] **v1.0** - 生产就绪版本

---

## 🤝 贡献指南

欢迎贡献！特别欢迎以下类型的 PR：

- 🧠 **领域知识** — 添加新的工程领域或扩展现有知识库
- 🐛 **Bug 修复** — 修复解析器或智能体的问题
- 📚 **文档** — 改进使用说明或添加教程
- 🌐 **国际化** — 添加其他语言支持

详见 [CONTRIBUTING.md](docs/CONTRIBUTING.md)

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<p align="center">
  <b>AbaqusGPT</b> — 让有限元分析不再困难 🚀
</p>

<!-- copilot test -->
