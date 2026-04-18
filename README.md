<div align="center">

# AbaqusGPT

**AI-Powered Assistant for Abaqus Finite Element Analysis**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)

[Features](#features) | [Quick Start](#quick-start) | [Documentation](#documentation) | [Contributing](#contributing)

</div>

---

## Features

| Module | Description |
|--------|-------------|
| **Convergence Doctor** | Automatically diagnose `.msg`/`.sta` files and identify root causes |
| **Model Generator** | Natural language to `.inp` files or Python scripts |
| **Mesh Advisor** | Mesh quality assessment + optimization suggestions |
| **Result Interpreter** | Help understand simulation outputs and check reasonability |
| **Domain Q&A** | Multi-domain knowledge base (Geotechnical, Structural, Mechanical, Thermal...) |

### Multi-Platform Access

```
+----------------------------------------------------------+
|                    Access Methods                         |
+--------------+--------------+-------------+--------------+
|   Web UI     |   REST API   |    CLI      |   Jupyter    |
|   (React)    |   (FastAPI)  |  (Terminal) |  (Notebook)  |
+--------------+--------------+-------------+--------------+
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start full stack (frontend + backend)
docker-compose up -d

# Access:
# - Web UI:  http://localhost:3000
# - API:     http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/ZhouChaunge/AbaqusGPT.git
cd AbaqusGPT

# Install backend
pip install -e ".[dev]"

# Install frontend
cd frontend && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn server.main:app --reload

# Start frontend (new terminal)
cd frontend && npm run dev
```

### Option 3: CLI Only

```bash
pip install abaqusgpt

# Diagnose convergence issues
abaqusgpt diagnose Job-1.msg

# Generate inp file
abaqusgpt generate "Steel plate 20x10x5mm, fixed bottom, 10MPa pressure on top"

# Check mesh quality
abaqusgpt mesh-check model.inp

# Domain-specific Q&A
abaqusgpt ask "What is the difference between C3D8R and C3D8?" --domain geotechnical
```

---

## Architecture

```
+-------------------------------------------------------------+
|                    Frontend (React + Tailwind)               |
+-----------------------------+-------------------------------+
                              | HTTP / WebSocket
+-----------------------------v-------------------------------+
|                    Backend (FastAPI)                         |
|  +---------+  +---------+  +---------+  +-----------------+ |
|  | REST API|  |WebSocket|  |  Auth   |  |   Rate Limit    | |
|  +---------+  +---------+  +---------+  +-----------------+ |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    Agents Layer                              |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |Converge  | |   Inp    | |  Mesh    | |   Material     |  |
|  | Doctor   | |Generator | | Advisor  | |    Helper      |  |
|  +----------+ +----------+ +----------+ +----------------+  |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    Knowledge Base                            |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |Geotechni-| |Structural| |Mechanical| |    Thermal     |  |
|  |   cal    | |          | |          | |                |  |
|  +----------+ +----------+ +----------+ +----------------+  |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |  Impact  | |Composite | | Biomech  | | Electromagnetic|  |
|  +----------+ +----------+ +----------+ +----------------+  |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    LLM Providers                             |
|  +---------+ +---------+ +---------+ +---------+ +-------+ |
|  | OpenAI  | | Claude  | | Ollama  | |DeepSeek | |  15+  | |
|  |GPT-4/4o | | 3.5/4   | | (Local) | |   V3    | | more  | |
|  +---------+ +---------+ +---------+ +---------+ +-------+ |
+-------------------------------------------------------------+
```

---

## Project Structure

```
AbaqusGPT/
|-- frontend/                # React frontend
|   |-- src/
|   |   |-- components/      # UI components
|   |   |-- pages/           # Page views
|   |   +-- services/        # API calls
|   +-- package.json
|
|-- server/                  # FastAPI backend
|   |-- main.py              # Entry point
|   |-- api/v1/              # API routes
|   |   |-- diagnose.py      # Diagnosis endpoint
|   |   |-- generate.py      # Generation endpoint
|   |   |-- mesh.py          # Mesh endpoint
|   |   +-- chat.py          # Chat endpoint
|   +-- core/                # Core configs
|
|-- abaqusgpt/               # Core engine (CLI + shared logic)
|   |-- cli.py               # CLI entry point
|   |-- agents/              # AI agents
|   |   |-- converge_doctor.py
|   |   |-- inp_generator.py
|   |   |-- mesh_advisor.py
|   |   +-- domain_expert.py
|   |-- knowledge/           # Domain knowledge
|   |   +-- domains/
|   |-- llm/                 # LLM client
|   |   +-- client.py
|   +-- parsers/             # File parsers
|       |-- inp_parser.py
|       |-- msg_parser.py
|       +-- sta_parser.py
|
|-- knowledge_base/          # Knowledge files
|-- tests/                   # Test suite
|-- docker-compose.yml       # Docker deployment
|-- pyproject.toml           # Python config
+-- .env.example             # Environment template
```

---

## Domain Knowledge

AbaqusGPT includes specialized knowledge across **8 engineering domains**:

| Domain | Coverage |
|--------|----------|
| **Geotechnical** | Mohr-Coulomb, Drucker-Prager, CAM-Clay; Soil-structure interaction; Seepage |
| **Structural** | Concrete Damaged Plasticity (CDP); Rebar modeling; Seismic analysis |
| **Mechanical** | Contact analysis; Gear/bearing modeling; Fatigue; Manufacturing |
| **Thermal** | Heat transfer; Thermal-stress coupling; Phase change; Welding |
| **Impact** | Explicit solver; Collision; Penetration; Blast; Material failure |
| **Composite** | Laminate modeling; Hashin failure; Delamination; Progressive damage |
| **Biomechanical** | Soft tissue hyperelasticity; Bone modeling; Implant analysis |
| **Electromagnetic** | EM-thermal-structural coupling; Induction heating |

---

## API Reference

### Convergence Diagnosis

```http
POST /api/v1/diagnose
Content-Type: multipart/form-data

file: <.msg or .sta file>
verbose: true
```

### Model Generation

```http
POST /api/v1/generate
Content-Type: application/json

{
  "description": "Steel plate with fixed bottom and pressure load",
  "output_format": "inp"
}
```

### Chat / Q&A

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "How to set up initial stress in tunnel excavation?",
  "domain": "geotechnical"
}
```

---

## Supported LLM Providers

AbaqusGPT supports **15+ LLM providers** via LiteLLM:

| Provider | Models | Config |
|----------|--------|--------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5 | `OPENAI_API_KEY` |
| Anthropic | Claude 3.5/4 | `ANTHROPIC_API_KEY` |
| DeepSeek | DeepSeek-V3, Coder | `DEEPSEEK_API_KEY` |
| Zhipu AI | GLM-4, GLM-4V | `ZHIPU_API_KEY` |
| Qwen | qwen-max, qwen-plus | `DASHSCOPE_API_KEY` |
| Moonshot | Kimi (8k/32k/128k) | `MOONSHOT_API_KEY` |
| Ollama | Local models | `OLLAMA_BASE_URL` |
| ... | 15+ Chinese providers | See `.env.example` |

---

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required: Choose at least one LLM provider
OPENAI_API_KEY=sk-...
# or
DEEPSEEK_API_KEY=sk-...

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./abaqusgpt.db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=abaqusgpt

# Run specific test
pytest tests/test_parsers.py -v
```

---

## Documentation

- [AI PR Review Setup](docs/AI_PR_REVIEW_SETUP.md) - Configure automated code review
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

---

## Contributing

Contributions are welcome! We especially appreciate:

- **Bug fixes** - Fix issues in parsers or agents
- **Documentation** - Improve usage guides or add tutorials
- **Domain knowledge** - Add new engineering domains or expand existing ones
- **Internationalization** - Add language support

Please read our contributing guidelines before submitting PRs.

---

## License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**AbaqusGPT** - Making Finite Element Analysis Easier

[Report Bug](https://github.com/ZhouChaunge/AbaqusGPT/issues) | [Request Feature](https://github.com/ZhouChaunge/AbaqusGPT/issues)

</div>
<![CDATA[<div align="center">

# AbaqusGPT

**AI-Powered Assistant for Abaqus Finite Element Analysis**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)

[Features](#features) | [Quick Start](#quick-start) | [Documentation](#documentation) | [Contributing](#contributing)

</div>

---

## Features

| Module | Description |
|--------|-------------|
| **Convergence Doctor** | Automatically diagnose `.msg`/`.sta` files and identify root causes |
| **Model Generator** | Natural language to `.inp` files or Python scripts |
| **Mesh Advisor** | Mesh quality assessment + optimization suggestions |
| **Result Interpreter** | Help understand simulation outputs and check reasonability |
| **Domain Q&A** | Multi-domain knowledge base (Geotechnical, Structural, Mechanical, Thermal...) |

### Multi-Platform Access

```
+----------------------------------------------------------+
|                    Access Methods                         |
+--------------+--------------+-------------+--------------+
|   Web UI     |   REST API   |    CLI      |   Jupyter    |
|   (React)    |   (FastAPI)  |  (Terminal) |  (Notebook)  |
+--------------+--------------+-------------+--------------+
```

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Start full stack (frontend + backend)
docker-compose up -d

# Access:
# - Web UI:  http://localhost:3000
# - API:     http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/ZhouChaunge/AbaqusGPT.git
cd AbaqusGPT

# Install backend
pip install -e ".[dev]"

# Install frontend
cd frontend && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn server.main:app --reload

# Start frontend (new terminal)
cd frontend && npm run dev
```

### Option 3: CLI Only

```bash
pip install abaqusgpt

# Diagnose convergence issues
abaqusgpt diagnose Job-1.msg

# Generate inp file
abaqusgpt generate "Steel plate 20x10x5mm, fixed bottom, 10MPa pressure on top"

# Check mesh quality
abaqusgpt mesh-check model.inp

# Domain-specific Q&A
abaqusgpt ask "What is the difference between C3D8R and C3D8?" --domain geotechnical
```

---

## Architecture

```
+-------------------------------------------------------------+
|                    Frontend (React + Tailwind)               |
+-----------------------------+-------------------------------+
                              | HTTP / WebSocket
+-----------------------------v-------------------------------+
|                    Backend (FastAPI)                         |
|  +---------+  +---------+  +---------+  +-----------------+ |
|  | REST API|  |WebSocket|  |  Auth   |  |   Rate Limit    | |
|  +---------+  +---------+  +---------+  +-----------------+ |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    Agents Layer                              |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |Converge  | |   Inp    | |  Mesh    | |   Material     |  |
|  | Doctor   | |Generator | | Advisor  | |    Helper      |  |
|  +----------+ +----------+ +----------+ +----------------+  |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    Knowledge Base                            |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |Geotechni-| |Structural| |Mechanical| |    Thermal     |  |
|  |   cal    | |          | |          | |                |  |
|  +----------+ +----------+ +----------+ +----------------+  |
|  +----------+ +----------+ +----------+ +----------------+  |
|  |  Impact  | |Composite | | Biomech  | | Electromagnetic|  |
|  +----------+ +----------+ +----------+ +----------------+  |
+-----------------------------+-------------------------------+
                              |
+-----------------------------v-------------------------------+
|                    LLM Providers                             |
|  +---------+ +---------+ +---------+ +---------+ +-------+ |
|  | OpenAI  | | Claude  | | Ollama  | |DeepSeek | |  15+  | |
|  |GPT-4/4o | | 3.5/4   | | (Local) | |   V3    | | more  | |
|  +---------+ +---------+ +---------+ +---------+ +-------+ |
+-------------------------------------------------------------+
```

---

## Project Structure

```
AbaqusGPT/
|-- frontend/                # React frontend
|   |-- src/
|   |   |-- components/      # UI components
|   |   |-- pages/           # Page views
|   |   +-- services/        # API calls
|   +-- package.json
|
|-- server/                  # FastAPI backend
|   |-- main.py              # Entry point
|   |-- api/v1/              # API routes
|   |   |-- diagnose.py      # Diagnosis endpoint
|   |   |-- generate.py      # Generation endpoint
|   |   |-- mesh.py          # Mesh endpoint
|   |   +-- chat.py          # Chat endpoint
|   +-- core/                # Core configs
|
|-- abaqusgpt/               # Core engine (CLI + shared logic)
|   |-- cli.py               # CLI entry point
|   |-- agents/              # AI agents
|   |   |-- converge_doctor.py
|   |   |-- inp_generator.py
|   |   |-- mesh_advisor.py
|   |   +-- domain_expert.py
|   |-- knowledge/           # Domain knowledge
|   |   +-- domains/
|   |-- llm/                 # LLM client
|   |   +-- client.py
|   +-- parsers/             # File parsers
|       |-- inp_parser.py
|       |-- msg_parser.py
|       +-- sta_parser.py
|
|-- knowledge_base/          # Knowledge files
|-- tests/                   # Test suite
|-- docker-compose.yml       # Docker deployment
|-- pyproject.toml           # Python config
+-- .env.example             # Environment template
```

---

## Domain Knowledge

AbaqusGPT includes specialized knowledge across **8 engineering domains**:

| Domain | Coverage |
|--------|----------|
| **Geotechnical** | Mohr-Coulomb, Drucker-Prager, CAM-Clay; Soil-structure interaction; Seepage |
| **Structural** | Concrete Damaged Plasticity (CDP); Rebar modeling; Seismic analysis |
| **Mechanical** | Contact analysis; Gear/bearing modeling; Fatigue; Manufacturing |
| **Thermal** | Heat transfer; Thermal-stress coupling; Phase change; Welding |
| **Impact** | Explicit solver; Collision; Penetration; Blast; Material failure |
| **Composite** | Laminate modeling; Hashin failure; Delamination; Progressive damage |
| **Biomechanical** | Soft tissue hyperelasticity; Bone modeling; Implant analysis |
| **Electromagnetic** | EM-thermal-structural coupling; Induction heating |

---

## API Reference

### Convergence Diagnosis

```http
POST /api/v1/diagnose
Content-Type: multipart/form-data

file: <.msg or .sta file>
verbose: true
```

### Model Generation

```http
POST /api/v1/generate
Content-Type: application/json

{
  "description": "Steel plate with fixed bottom and pressure load",
  "output_format": "inp"
}
```

### Chat / Q&A

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "How to set up initial stress in tunnel excavation?",
  "domain": "geotechnical"
}
```

---

## Supported LLM Providers

AbaqusGPT supports **15+ LLM providers** via LiteLLM:

| Provider | Models | Config |
|----------|--------|--------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5 | `OPENAI_API_KEY` |
| Anthropic | Claude 3.5/4 | `ANTHROPIC_API_KEY` |
| DeepSeek | DeepSeek-V3, Coder | `DEEPSEEK_API_KEY` |
| Zhipu AI | GLM-4, GLM-4V | `ZHIPU_API_KEY` |
| Qwen | qwen-max, qwen-plus | `DASHSCOPE_API_KEY` |
| Moonshot | Kimi (8k/32k/128k) | `MOONSHOT_API_KEY` |
| Ollama | Local models | `OLLAMA_BASE_URL` |
| ... | 15+ Chinese providers | See `.env.example` |

---

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required: Choose at least one LLM provider
OPENAI_API_KEY=sk-...
# or
DEEPSEEK_API_KEY=sk-...

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./abaqusgpt.db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=abaqusgpt

# Run specific test
pytest tests/test_parsers.py -v
```

---

## Documentation

- [AI PR Review Setup](docs/AI_PR_REVIEW_SETUP.md) - Configure automated code review
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

---

## Contributing

Contributions are welcome! We especially appreciate:

- **Bug fixes** - Fix issues in parsers or agents
- **Documentation** - Improve usage guides or add tutorials
- **Domain knowledge** - Add new engineering domains or expand existing ones
- **Internationalization** - Add language support

Please read our contributing guidelines before submitting PRs.

---

## License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**AbaqusGPT** - Making Finite Element Analysis Easier

[Report Bug](https://github.com/ZhouChaunge/AbaqusGPT/issues) | [Request Feature](https://github.com/ZhouChaunge/AbaqusGPT/issues)

</div>
]]><![CDATA[<div align="center">

# 🔧 AbaqusGPT

**AI-Powered Assistant for Abaqus Finite Element Analysis**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## ✨ Features

| Module | Description |
|--------|-------------|
| 🔴 **Convergence Doctor** | Automatically diagnose `.msg`/`.sta` files and identify root causes |
| 🧱 **Model Generator** | Natural language → `.inp` files or Python scripts |
| 🔲 **Mesh Advisor** | Mesh quality assessment + optimization suggestions |
| 📊 **Result Interpreter** | Help understand simulation outputs and check reasonability |
| 📚 **Domain Q&A** | Multi-domain knowledge base (Geotechnical, Structural, Mechanical, Thermal...) |

### Multi-Platform Access

```
┌──────────────────────────────────────────────────────────┐
│                    Access Methods                         │
├──────────────┬──────────────┬─────────────┬──────────────┤
│   🌐 Web UI  │  🔌 REST API │   💻 CLI    │  📓 Jupyter  │
│   (React)    │   (FastAPI)  │  (Terminal) │  (Notebook)  │
└──────────────┴──────────────┴─────────────┴──────────────┘
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Start full stack (frontend + backend)
docker-compose up -d

# Access:
# - Web UI:  http://localhost:3000
# - API:     http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Clone repository
git clone https://github.com/ZhouChaunge/AbaqusGPT.git
cd AbaqusGPT

# Install backend
pip install -e ".[dev]"

# Install frontend
cd frontend && npm install && cd ..

# Configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start backend
uvicorn server.main:app --reload

# Start frontend (new terminal)
cd frontend && npm run dev
```

### Option 3: CLI Only

```bash
pip install abaqusgpt

# Diagnose convergence issues
abaqusgpt diagnose Job-1.msg

# Generate inp file
abaqusgpt generate "Steel plate 20x10x5mm, fixed bottom, 10MPa pressure on top"

# Check mesh quality
abaqusgpt mesh-check model.inp

# Domain-specific Q&A
abaqusgpt ask "What's the difference between C3D8R and C3D8?" --domain geotechnical
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Tailwind)               │
└─────────────────────────────┬───────────────────────────────┘
                              │ HTTP / WebSocket
┌─────────────────────────────┴───────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │ REST API│  │WebSocket│  │  Auth   │  │   Rate Limit    │ │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────────┘ │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Agents Layer                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │Converge  │ │   Inp    │ │  Mesh    │ │   Material     │  │
│  │ Doctor   │ │Generator │ │ Advisor  │ │    Helper      │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    Knowledge Base                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │Geotechni-│ │Structural│ │Mechanical│ │    Thermal     │  │
│  │   cal    │ │          │ │          │ │                │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐  │
│  │  Impact  │ │Composite │ │ Biomech  │ │ Electromagnetic│  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                    LLM Providers                             │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────┐ │
│  │ OpenAI  │ │ Claude  │ │ Ollama  │ │DeepSeek │ │  15+  │ │
│  │GPT-4/4o │ │ 3.5/4   │ │ (Local) │ │   V3    │ │ more  │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └───────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
AbaqusGPT/
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # UI components
│   │   ├── pages/           # Page views
│   │   └── services/        # API calls
│   └── package.json
│
├── server/                  # FastAPI backend
│   ├── main.py              # Entry point
│   ├── api/v1/              # API routes
│   │   ├── diagnose.py      # Diagnosis endpoint
│   │   ├── generate.py      # Generation endpoint
│   │   ├── mesh.py          # Mesh endpoint
│   │   └── chat.py          # Chat endpoint
│   └── core/                # Core configs
│
├── abaqusgpt/               # Core engine (CLI + shared logic)
│   ├── cli.py               # CLI entry point
│   ├── agents/              # AI agents
│   │   ├── converge_doctor.py
│   │   ├── inp_generator.py
│   │   ├── mesh_advisor.py
│   │   └── domain_expert.py
│   ├── knowledge/           # Domain knowledge
│   │   └── domains/
│   ├── llm/                 # LLM client
│   │   └── client.py
│   └── parsers/             # File parsers
│       ├── inp_parser.py
│       ├── msg_parser.py
│       └── sta_parser.py
│
├── knowledge_base/          # Knowledge files
├── tests/                   # Test suite
├── docker-compose.yml       # Docker deployment
├── pyproject.toml           # Python config
└── .env.example             # Environment template
```

---

## 🧠 Domain Knowledge

AbaqusGPT includes specialized knowledge across **8 engineering domains**:

| Domain | Coverage |
|--------|----------|
| 🏗️ **Geotechnical** | Mohr-Coulomb, Drucker-Prager, CAM-Clay; Soil-structure interaction; Seepage |
| 🏛️ **Structural** | Concrete Damaged Plasticity (CDP); Rebar modeling; Seismic analysis |
| ⚙️ **Mechanical** | Contact analysis; Gear/bearing modeling; Fatigue; Manufacturing |
| 🔥 **Thermal** | Heat transfer; Thermal-stress coupling; Phase change; Welding |
| 💥 **Impact** | Explicit solver; Collision; Penetration; Blast; Material failure |
| 🔗 **Composite** | Laminate modeling; Hashin failure; Delamination; Progressive damage |
| 🩺 **Biomechanical** | Soft tissue hyperelasticity; Bone modeling; Implant analysis |
| ⚡ **Electromagnetic** | EM-thermal-structural coupling; Induction heating |

---

## 🔌 API Reference

### Convergence Diagnosis

```http
POST /api/v1/diagnose
Content-Type: multipart/form-data

file: <.msg or .sta file>
verbose: true
```

### Model Generation

```http
POST /api/v1/generate
Content-Type: application/json

{
  "description": "Steel plate with fixed bottom and pressure load",
  "output_format": "inp"
}
```

### Chat / Q&A

```http
POST /api/v1/chat
Content-Type: application/json

{
  "message": "How to set up initial stress in tunnel excavation?",
  "domain": "geotechnical"
}
```

---

## 🤖 Supported LLM Providers

AbaqusGPT supports **15+ LLM providers** via LiteLLM:

| Provider | Models | Config |
|----------|--------|--------|
| OpenAI | GPT-4, GPT-4o, GPT-3.5 | `OPENAI_API_KEY` |
| Anthropic | Claude 3.5/4 | `ANTHROPIC_API_KEY` |
| DeepSeek | DeepSeek-V3, Coder | `DEEPSEEK_API_KEY` |
| Zhipu AI | GLM-4, GLM-4V | `ZHIPU_API_KEY` |
| Qwen | qwen-max, qwen-plus | `DASHSCOPE_API_KEY` |
| Moonshot | Kimi (8k/32k/128k) | `MOONSHOT_API_KEY` |
| Ollama | Local models | `OLLAMA_BASE_URL` |
| ... | 15+ Chinese providers | See `.env.example` |

---

## 🛠️ Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Required: Choose at least one LLM provider
OPENAI_API_KEY=sk-...
# or
DEEPSEEK_API_KEY=sk-...

# Optional: Database (defaults to SQLite)
DATABASE_URL=sqlite:///./abaqusgpt.db

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=abaqusgpt

# Run specific test
pytest tests/test_parsers.py -v
```

---

## 📖 Documentation

- [AI PR Review Setup](docs/AI_PR_REVIEW_SETUP.md) - Configure automated code review
- [API Documentation](http://localhost:8000/docs) - Interactive API docs (when running)

---

## 🤝 Contributing

Contributions are welcome! We especially appreciate:

- 🐛 **Bug fixes** - Fix issues in parsers or agents
- 📚 **Documentation** - Improve usage guides or add tutorials
- 🧠 **Domain knowledge** - Add new engineering domains or expand existing ones
- 🌍 **Internationalization** - Add language support

Please read our contributing guidelines before submitting PRs.

---

## 📄 License

MIT License - see [LICENSE](LICENSE)

---

<div align="center">

**AbaqusGPT** — Making Finite Element Analysis Easier 🚀

[Report Bug](https://github.com/ZhouChaunge/AbaqusGPT/issues) • [Request Feature](https://github.com/ZhouChaunge/AbaqusGPT/issues)

</div>
]]>