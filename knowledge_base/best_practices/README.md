# AbaqusGPT Best Practices | 最佳实践指南

This directory contains best practice guides for Abaqus finite element analysis.
本目录包含 Abaqus 有限元分析的最佳实践指南。

## 📚 Guide Index | 指南索引

| Guide | 指南 | Description | 描述 |
|-------|------|-------------|------|
| [Meshing Guide](meshing.md) | 网格划分指南 | Element selection, mesh density, quality metrics |
| [Contact Guide](contact.md) | 接触分析指南 | Contact pairs, algorithms, stabilization |
| [Convergence Guide](convergence.md) | 收敛控制指南 | Newton-Raphson, step controls, stabilization |
| [Material Guide](materials.md) | 材料模型指南 | Material selection, parameter fitting |
| [Output Guide](output.md) | 输出设置指南 | Field output, history output, ODB management |

## 🎯 Quick Reference | 快速参考

### Common Workflow | 常见工作流

```
1. Pre-processing | 前处理
   ├── Geometry import/cleanup
   ├── Material definition
   ├── Mesh generation (see meshing.md)
   └── Boundary conditions

2. Analysis Setup | 分析设置
   ├── Step definition
   ├── Contact pairs (see contact.md)
   ├── Output requests
   └── Job parameters

3. Solving | 求解
   ├── Initial checks
   ├── Monitor convergence (see convergence.md)
   └── Handle warnings/errors

4. Post-processing | 后处理
   ├── Result validation
   ├── Visualization
   └── Report generation
```

## 🔗 Related Resources | 相关资源

- [Element Library](../abaqusgpt/knowledge/element_library.py) - Element type reference
- [Error Codes](../abaqusgpt/knowledge/error_codes.py) - Error diagnosis database
- [Shared References](../abaqusgpt/skills/shared_references/) - Cross-skill knowledge base

---

*Last updated: 2025-01*
