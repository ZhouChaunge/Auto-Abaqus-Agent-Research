---
name: inp-generator
version: 1.0.0
description: Generate Abaqus .inp files from natural language or templates
description_cn: 从自然语言或模板生成 Abaqus .inp 文件
triggers:
  - "generate"
  - "inp"
  - "create model"
  - "生成"
  - "建模"
priority: P1
dependencies: []
author: AbaqusGPT Team
tags:
  - generation
  - inp
  - modeling
---

# INP Generator | INP 生成器

## Overview | 概述

Generate Abaqus input (.inp) files from natural language descriptions, templates, or structured specifications.

从自然语言描述、模板或结构化规范生成 Abaqus 输入文件 (.inp)。

## Capabilities | 能力

1. **Natural Language to INP | 自然语言转 INP**
   - Describe your model in plain language
   - 用自然语言描述您的模型

2. **Template-Based Generation | 基于模板生成**
   - Use predefined templates for common analyses
   - 使用预定义模板进行常见分析

3. **Parametric Models | 参数化模型**
   - Generate model variants with parameter sweeps
   - 通过参数扫描生成模型变体

## Usage | 用法

### CLI

```bash
# Generate from description
abaqusgpt generate "一个受均布载荷的悬臂梁，长度1m，截面0.1x0.1m"

# Generate from template
abaqusgpt generate --template cantilever --length 1.0 --load 1000
```

### Python API

```python
from abaqusgpt.skills.inp_generator import InpGeneratorSkill

skill = InpGeneratorSkill()
result = skill.execute({
    "description": "悬臂梁，固定端约束，自由端施加集中力",
    "output_path": "my_model.inp"
})
```

## Input Context | 输入上下文

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `description` | `str` | No | Natural language description |
| `template` | `str` | No | Template name |
| `parameters` | `dict` | No | Parameters for template |
| `output_path` | `str` | No | Output file path |

## Output | 输出

```python
{
    "status": "success",
    "inp_content": "...",
    "output_path": "my_model.inp",
    "validation": {
        "syntax_ok": True,
        "warnings": []
    }
}
```

## Available Templates | 可用模板

| Template | Description | 描述 |
|----------|-------------|------|
| `cantilever` | Cantilever beam | 悬臂梁 |
| `plate_hole` | Plate with hole | 带孔平板 |
| `contact_3d` | 3D contact | 三维接触 |
| `thermal` | Thermal analysis | 热分析 |

## Validation | 验证

Generated .inp files are validated for:
- Keyword syntax correctness
- Required sections completeness
- Parameter consistency

生成的 .inp 文件会验证：
- 关键字语法正确性
- 必需部分完整性
- 参数一致性

## References | 参考资料

- `shared-references/inp-keywords.md`
- Abaqus Keywords Reference Manual
