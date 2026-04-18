---
name: converge-doctor
version: 1.0.0
description: Diagnose and fix Abaqus convergence issues
description_cn: 诊断并修复 Abaqus 收敛问题
triggers:
  - "diagnose"
  - "convergence"
  - "收敛"
  - "不收敛"
  - "报错"
  - "error"
priority: P0
dependencies: []
author: AbaqusGPT Team
tags:
  - diagnosis
  - convergence
  - solver
---

# Converge Doctor | 收敛医生

## Overview | 概述

Diagnose Abaqus convergence issues from `.msg` and `.sta` files, providing root cause analysis and actionable fix recommendations.

从 `.msg` 和 `.sta` 文件诊断 Abaqus 收敛问题，提供根本原因分析和可操作的修复建议。

## Capabilities | 能力

1. **Error Pattern Matching | 错误模式匹配**
   - Match against 15+ known error patterns
   - 匹配 15+ 种已知错误模式

2. **Root Cause Analysis | 根本原因分析**
   - LLM-powered deep analysis
   - 基于 LLM 的深度分析

3. **Fix Recommendations | 修复建议**
   - Specific Abaqus keywords/parameters
   - 具体的 Abaqus 关键字/参数

## Usage | 用法

### CLI

```bash
# Diagnose a .msg file
abaqusgpt diagnose path/to/job.msg

# Verbose mode with all details
abaqusgpt diagnose path/to/job.msg --verbose
```

### Python API

```python
from abaqusgpt.skills.converge_doctor import ConvergeDoctorSkill

skill = ConvergeDoctorSkill()
result = skill.execute({
    "file_path": "path/to/job.msg",
    "verbose": True
})
```

## Input Context | 输入上下文

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `file_path` | `str` | Yes | Path to .msg or .sta file |
| `verbose` | `bool` | No | Show detailed output (default: False) |

## Output | 输出

```python
{
    "status": "success",
    "errors_found": [...],
    "known_patterns": [...],
    "diagnosis": "...",
    "recommendations": [...],
    "report_path": "diagnosis-stage/DIAGNOSIS_REPORT.md"
}
```

## Error Patterns Covered | 覆盖的错误模式

- TOO MANY ATTEMPTS MADE FOR THIS INCREMENT
- NEGATIVE EIGENVALUE
- EXCESSIVE DISTORTION
- ZERO PIVOT
- CONTACT OVERCLOSURE
- SEVERE DISCONTINUITY ITERATION
- ELEMENT HAS NEGATIVE JACOBIAN
- PLASTICITY ALGORITHM DID NOT CONVERGE
- TIME INCREMENT REQUIRED IS LESS THAN THE MINIMUM
- HYPERELASTIC MATERIAL HAS BECOME UNSTABLE

## References | 参考资料

- [Abaqus Analysis User's Guide - Convergence](https://help.3ds.com/2024/English/DSSIMULIA_Established/SIMACAEANLRefMap/simaanl-c-convergence.htm)
- `shared-references/error-patterns.md`
