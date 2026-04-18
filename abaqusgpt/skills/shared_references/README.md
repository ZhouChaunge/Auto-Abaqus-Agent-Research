# Shared References | 共享规范

This directory contains shared reference documents used across all skills.
此目录包含所有技能共享的参考文档。

## Contents | 目录

| File | Description | 描述 |
|------|-------------|------|
| [element-catalog.md](element-catalog.md) | Element type reference | 单元类型参考 |
| [error-patterns.md](error-patterns.md) | Error pattern database | 错误模式数据库 |
| [mesh-guidelines.md](mesh-guidelines.md) | Mesh quality guidelines | 网格质量指南 |
| [convergence-criteria.md](convergence-criteria.md) | Convergence criteria | 收敛标准 |

## Usage | 使用方法

These documents are automatically loaded by skills when needed. They can also be accessed directly through the knowledge base API.

这些文档在需要时由技能自动加载。也可以通过知识库 API 直接访问。

```python
from abaqusgpt.skills.shared_references import get_reference

# Get element catalog
element_info = get_reference("element-catalog", "C3D8R")

# Get error pattern
error_info = get_reference("error-patterns", "NEGATIVE EIGENVALUE")
```
