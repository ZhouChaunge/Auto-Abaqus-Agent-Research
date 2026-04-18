---
name: domain-expert
version: 1.0.0
description: Domain-specific knowledge and Q&A for various engineering fields
description_cn: 各工程领域的专业知识问答
triggers:
  - "ask"
  - "question"
  - "what"
  - "how"
  - "why"
  - "问"
  - "怎么"
  - "为什么"
priority: P1
dependencies: []
author: AbaqusGPT Team
tags:
  - qa
  - knowledge
  - domain
---

# Domain Expert | 领域专家

## Overview | 概述

Provide domain-specific expertise for various engineering fields, answering questions about Abaqus modeling, analysis techniques, and best practices.

为各工程领域提供专业知识，回答关于 Abaqus 建模、分析技术和最佳实践的问题。

## Capabilities | 能力

1. **Multi-Domain Knowledge | 多领域知识**
   - Structural, thermal, dynamic, contact, etc.
   - 结构、热、动力学、接触等

2. **Context-Aware Answers | 上下文感知回答**
   - Consider your current model and analysis
   - 考虑您当前的模型和分析

3. **Code Examples | 代码示例**
   - Provide .inp snippets and Python scripts
   - 提供 .inp 代码片段和 Python 脚本

## Usage | 用法

### CLI

```bash
# Ask a question
abaqusgpt ask "如何处理接触不收敛？"

# Specify domain
abaqusgpt ask "什么是沙漏模式？" --domain structural
```

### Python API

```python
from abaqusgpt.skills.domain_expert import DomainExpertSkill

skill = DomainExpertSkill()
result = skill.execute({
    "question": "如何选择合适的接触算法？",
    "domain": "contact"
})
```

## Input Context | 输入上下文

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `question` | `str` | Yes | User's question |
| `domain` | `str` | No | Specific domain to focus on |
| `context` | `dict` | No | Additional context (current model, etc.) |

## Output | 输出

```python
{
    "status": "success",
    "answer": "...",
    "references": [...],
    "code_examples": [...],
    "follow_up_questions": [...]
}
```

## Supported Domains | 支持的领域

| Domain | Description | 描述 |
|--------|-------------|------|
| `structural` | Static and strength | 静力与强度 |
| `thermal` | Heat transfer | 传热 |
| `dynamic` | Dynamic and vibration | 动力学与振动 |
| `contact` | Contact mechanics | 接触力学 |
| `fatigue` | Fatigue analysis | 疲劳分析 |
| `cfd` | Coupled fluid | 流固耦合 |
| `material` | Material modeling | 材料建模 |

## Knowledge Sources | 知识来源

- Abaqus Documentation
- `knowledge_base/` directory
- Domain-specific guidelines in `shared-references/`

## References | 参考资料

- `shared-references/domain-guidelines.md`
- `knowledge_base/abaqus_docs/`
