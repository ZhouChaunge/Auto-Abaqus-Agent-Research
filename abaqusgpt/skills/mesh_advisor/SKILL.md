---
name: mesh-advisor
version: 1.0.0
description: Provide mesh quality advice and element selection guidance
description_cn: 提供网格质量建议和单元选择指导
triggers:
  - "mesh"
  - "element"
  - "网格"
  - "单元"
  - "划分"
priority: P1
dependencies: []
author: AbaqusGPT Team
tags:
  - mesh
  - element
  - preprocessing
---

# Mesh Advisor | 网格顾问

## Overview | 概述

Provide expert guidance on mesh quality, element type selection, and mesh refinement strategies for Abaqus simulations.

为 Abaqus 仿真提供网格质量、单元类型选择和网格细化策略的专家指导。

## Capabilities | 能力

1. **Element Type Selection | 单元类型选择**
   - 20+ element types with detailed guidance
   - 20+ 种单元类型的详细指导

2. **Mesh Quality Assessment | 网格质量评估**
   - Aspect ratio, skewness, Jacobian checks
   - 长宽比、畸变度、雅可比检查

3. **Refinement Strategies | 细化策略**
   - Local vs global refinement advice
   - 局部与全局细化建议

## Usage | 用法

### CLI

```bash
# Get element recommendation
abaqusgpt mesh recommend --analysis-type static --geometry shell

# Analyze mesh quality
abaqusgpt mesh quality path/to/model.inp
```

### Python API

```python
from abaqusgpt.skills.mesh_advisor import MeshAdvisorSkill

skill = MeshAdvisorSkill()
result = skill.execute({
    "query_type": "element_recommendation",
    "analysis_type": "static",
    "geometry_type": "shell"
})
```

## Input Context | 输入上下文

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `query_type` | `str` | Yes | "element_recommendation" or "quality_check" |
| `analysis_type` | `str` | No | Analysis type (static, dynamic, thermal, etc.) |
| `geometry_type` | `str` | No | Geometry type (solid, shell, beam, etc.) |
| `inp_path` | `str` | No | Path to .inp file for quality check |

## Output | 输出

```python
{
    "status": "success",
    "recommendations": [
        {
            "element": "C3D8R",
            "suitability": "high",
            "reason": "适合大变形静力分析"
        }
    ],
    "warnings": [...],
    "alternatives": [...]
}
```

## Supported Elements | 支持的单元

### 3D Solids | 三维实体
- C3D8, C3D8R, C3D8I
- C3D20, C3D20R
- C3D10, C3D10M, C3D4

### Shells | 壳单元
- S4, S4R, S8R
- SC8R (continuum shell)

### Beams | 梁单元
- B31, B32

### Connectors | 连接单元
- CONN3D2

### Special | 特殊单元
- MASS, ROTARYI

## References | 参考资料

- `shared-references/element-catalog.md`
- `shared-references/mesh-guidelines.md`
