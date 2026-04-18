# Meshing Best Practices | 网格划分最佳实践

## 📋 Overview | 概述

Proper meshing is fundamental to accurate FEA results. This guide covers element selection, mesh density, and quality metrics.

网格质量是有限元分析精度的基础。本指南涵盖单元选择、网格密度和质量指标。

---

## 1️⃣ Element Selection | 单元选择

### Solid Elements | 实体单元

| Application | 应用场景 | Recommended | 推荐 | Avoid | 避免 |
|-------------|---------|-------------|------|-------|------|
| General stress analysis | 一般应力分析 | C3D8R, C3D10 | C3D4 |
| Contact problems | 接触问题 | C3D8R, C3D10M | C3D20R |
| Large deformation | 大变形 | C3D8R | C3D20 |
| Stress concentration | 应力集中 | C3D20R, C3D10 | C3D8 |
| Bending dominated | 弯曲主导 | C3D8I, C3D20R | C3D4 |

### Shell Elements | 壳单元

| Application | 应用场景 | Recommended | 推荐 | Notes | 备注 |
|-------------|---------|-------------|------|-------|------|
| General thin shell | 一般薄壳 | S4R | Most versatile |
| Precision stress | 精确应力 | S8R | Higher cost |
| Composite | 复合材料 | SC8R | Thickness direction |
| Transition zones | 过渡区域 | S3 | Only for transitions |

### Beam Elements | 梁单元

| Application | 应用场景 | Recommended | 推荐 |
|-------------|---------|-------------|------|
| General frame | 一般框架 | B31 |
| Curved beams | 曲梁 | B32 |
| Open sections | 开口截面 | B31OS |
| Pipes | 管道 | PIPE31 |

---

## 2️⃣ Mesh Density Guidelines | 网格密度指南

### Stress Concentration Regions | 应力集中区域

```
Minimum 3-5 elements across:
- Fillet radii | 圆角半径
- Hole edges | 孔边
- Notch roots | 缺口根部
- Contact edges | 接触边缘
```

### Gradual Transition | 渐变过渡

```
✅ Good Practice | 好的做法:
   - Element size ratio < 1.5 between adjacent elements
   - Use bias or growth rate controls
   - 相邻单元尺寸比 < 1.5
   - 使用偏置或增长率控制

❌ Bad Practice | 坏的做法:
   - Abrupt size changes > 2:1
   - Sharp density jumps at interfaces
   - 突变尺寸变化 > 2:1
   - 界面处密度急剧跳变
```

### Contact Regions | 接触区域

```
Rules | 规则:
1. Slave surface should have finer mesh
   从面应有更细的网格
   
2. Element size ratio master:slave ≈ 2:1 or 1:1
   主从面单元尺寸比约为 2:1 或 1:1
   
3. Avoid point contact with coarse mesh
   避免粗网格的点接触
```

---

## 3️⃣ Mesh Quality Metrics | 网格质量指标

### Hex/Quad Elements | 六面体/四边形单元

| Metric | 指标 | Acceptable | 可接受 | Warning | 警告 | Critical | 严重 |
|--------|------|------------|-------|---------|------|----------|------|
| Aspect Ratio | 长宽比 | < 5 | 5-10 | > 10 |
| Jacobian | 雅可比 | > 0.5 | 0.2-0.5 | < 0.2 |
| Warpage (°) | 翘曲 | < 15° | 15-30° | > 30° |
| Skew (°) | 扭曲 | < 45° | 45-60° | > 60° |

### Tet/Tri Elements | 四面体/三角形单元

| Metric | 指标 | Acceptable | 可接受 | Warning | 警告 | Critical | 严重 |
|--------|------|------------|-------|---------|------|----------|------|
| Aspect Ratio | 长宽比 | < 3 | 3-5 | > 5 |
| Min Angle (°) | 最小角 | > 20° | 10-20° | < 10° |
| Max Angle (°) | 最大角 | < 120° | 120-140° | > 140° |

---

## 4️⃣ Common Issues & Solutions | 常见问题与解决

### Issue: Hourglass Modes | 沙漏模式

```python
# Symptoms | 症状:
- Zero-energy deformation patterns
- Wavy displacement fields
- ARTIFICIAL STRAIN ENERGY warning

# Solutions | 解决方案:
1. Use full integration: C3D8 instead of C3D8R
2. Add hourglass control: *SECTION CONTROLS, HOURGLASS=ENHANCED
3. Refine mesh in affected regions
4. Check boundary conditions
```

### Issue: Shear Locking | 剪切锁定

```python
# Symptoms | 症状:
- Overly stiff bending response
- Artificial restraint in thin structures

# Solutions | 解决方案:
1. Use incompatible mode elements: C3D8I
2. Use reduced integration: C3D8R
3. Use shell elements for thin structures
4. Increase mesh density through thickness
```

### Issue: Volumetric Locking | 体积锁定

```python
# Symptoms | 症状:
- Overly stiff response in nearly incompressible materials
- Checkerboard pressure patterns

# Solutions | 解决方案:
1. Use hybrid elements: C3D8H, C3D10MH
2. Use reduced integration: C3D8R
3. Avoid full integration with ν → 0.5
```

---

## 5️⃣ Checklist | 检查清单

Before submitting a job, verify:

提交作业前请检查：

- [ ] Element types appropriate for analysis
      单元类型适合分析类型
- [ ] Mesh density adequate in critical regions
      关键区域网格密度足够
- [ ] Quality metrics within acceptable limits
      质量指标在可接受范围内
- [ ] Gradual mesh transitions
      网格平滑过渡
- [ ] No orphan/free nodes
      无孤立/自由节点
- [ ] Proper element connectivity
      单元连接正确

---

*See also: [Element Library](../../abaqusgpt/knowledge/element_library.py)*
