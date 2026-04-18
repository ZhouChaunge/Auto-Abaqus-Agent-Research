# Mesh Guidelines | 网格规范

Best practices for mesh quality in Abaqus simulations.
Abaqus 仿真中网格质量的最佳实践。

---

## Quality Metrics | 质量指标

### Aspect Ratio | 长宽比

The ratio of the longest edge to the shortest edge.
最长边与最短边的比值。

| Rating | Value | Recommendation |
|--------|-------|----------------|
| ✅ Good | < 3 | Ideal for most analyses |
| ⚠️ Warning | 3 - 10 | Acceptable for non-critical regions |
| ❌ Bad | > 10 | Remesh required |

**Impact | 影响:**
- High aspect ratio degrades accuracy | 高长宽比降低精度
- Affects stress gradients | 影响应力梯度计算

---

### Skewness | 畸变度

Deviation from ideal element shape (0 = perfect, 1 = degenerate).
与理想单元形状的偏差。

| Rating | Value | Recommendation |
|--------|-------|----------------|
| ✅ Good | < 0.5 | Ideal |
| ⚠️ Warning | 0.5 - 0.85 | Acceptable |
| ❌ Bad | > 0.85 | Remesh required |

---

### Jacobian Ratio | 雅可比比

Ratio of minimum to maximum Jacobian determinant.
雅可比行列式的最小值与最大值之比。

| Rating | Value | Recommendation |
|--------|-------|----------------|
| ✅ Good | > 0.5 | Ideal |
| ⚠️ Warning | 0.1 - 0.5 | Acceptable |
| ❌ Bad | < 0.1 | Remesh required |

**Note | 注意:** Negative Jacobian = inverted element = analysis will fail.

---

### Minimum Angle | 最小角度

**Quadrilateral Elements | 四边形单元:**
| Rating | Value | Recommendation |
|--------|-------|----------------|
| ✅ Good | > 45° | Ideal |
| ⚠️ Warning | 30° - 45° | Acceptable |
| ❌ Bad | < 30° | Remesh required |

**Triangular Elements | 三角形单元:**
| Rating | Value | Recommendation |
|--------|-------|----------------|
| ✅ Good | > 30° | Ideal |
| ⚠️ Warning | 15° - 30° | Acceptable |
| ❌ Bad | < 15° | Remesh required |

---

## Mesh Density Guidelines | 网格密度指南

### General Rules | 一般规则

1. **Minimum Elements Through Thickness | 厚度方向最少单元数**
   - C3D8R: ≥ 2 elements
   - C3D8I: ≥ 1 element (can handle bending)
   - C3D20R: ≥ 1 element

2. **Stress Concentration Areas | 应力集中区域**
   - Refine mesh at holes, notches, fillets | 在孔、缺口、圆角处加密
   - Gradual transition from fine to coarse | 从细到粗渐变过渡
   - Size ratio between adjacent elements ≤ 1.5 | 相邻单元尺寸比 ≤ 1.5

3. **Contact Regions | 接触区域**
   - Slave surface should be finer | 从面应更细
   - Similar element sizes on both surfaces | 两面单元尺寸相近
   - Minimum 3-4 elements across contact zone | 接触区域至少3-4个单元

---

## Element Selection by Analysis | 按分析类型选择单元

### Static Analysis | 静力分析

```
Preferred: C3D20R, C3D10M
Alternative: C3D8R (with hourglass control)
```

**Key Points | 要点:**
- Quadratic elements preferred for accuracy | 二次单元精度更高
- Use C3D8R for large models | 大模型使用C3D8R

---

### Large Deformation | 大变形分析

```
Preferred: C3D8R
Alternative: C3D10M
```

**Key Points | 要点:**
- Reduced integration essential | 减缩积分必须
- Enable NLGEOM | 启用几何非线性
- Hourglass control required | 需要沙漏控制

```
*STEP, NLGEOM=YES
*SECTION CONTROLS, HOURGLASS=ENHANCED
```

---

### Contact Analysis | 接触分析

```
Preferred: C3D8R, C3D10M
Avoid: C3D20, C3D10 (face nodes cause issues)
```

**Key Points | 要点:**
- Use modified elements (C3D10M) for tet meshes | 四面体用改进单元
- Surface mesh should be smooth | 表面网格应光滑

---

### Dynamic/Explicit | 动力学/显式分析

```
Preferred: C3D8R, S4R
```

**Key Points | 要点:**
- Reduced integration for efficiency | 减缩积分提高效率
- Control element size for stable time step | 控制单元尺寸以稳定时间步
- Avoid overly small elements | 避免过小的单元

**Stable Time Increment | 稳定时间增量:**
```
Δt ≈ L_min / c_d
```
Where L_min = smallest element dimension, c_d = dilatational wave speed

---

## Mesh Transition | 网格过渡

### Best Practices | 最佳实践

1. **Gradual Refinement | 渐进细化**
   - Use partition to control mesh density | 使用分区控制网格密度
   - Avoid abrupt size changes | 避免尺寸突变

2. **Tied Contacts | 绑定接触**
   - Use *TIE to connect different mesh densities | 使用 *TIE 连接不同密度网格
   ```
   *TIE, NAME=MESH_TRANSITION
   fine_surface, coarse_surface
   ```

3. **Bias Meshing | 偏置网格**
   - Gradually transition from fine to coarse | 从细到粗渐变
   - Use bias ratio ≤ 5 | 偏置比 ≤ 5

---

## Common Mesh Problems | 常见网格问题

### Problem: Shear Locking | 剪切锁死
**Symptoms | 症状:** Overly stiff response in bending
**Solution | 解决:** Use reduced integration (C3D8R) or incompatible modes (C3D8I)

### Problem: Hourglass Modes | 沙漏模式
**Symptoms | 症状:** Zero-energy deformation modes, checkerboard patterns
**Solution | 解决:** Enhanced hourglass control
```
*SECTION CONTROLS, HOURGLASS=ENHANCED
```

### Problem: Volumetric Locking | 体积锁死
**Symptoms | 症状:** Overly stiff response for incompressible materials
**Solution | 解决:** Use hybrid elements (C3D8H) or reduced integration

---

## Mesh Quality Check Commands | 网格质量检查命令

### Abaqus/CAE

```python
# Python script to check mesh quality
from abaqus import *
from abaqusConstants import *

# Get mesh quality metrics
mesh = mdb.models['Model-1'].parts['Part-1'].getMeshStats()
print(f"Elements: {mesh.numElements}")
print(f"Nodes: {mesh.numNodes}")
```

### Verify Keywords | 验证关键字

```
*PREPRINT, MODEL=NO, HISTORY=NO, CONTACT=NO, ECHO=YES
```

---

## References | 参考资料

- Abaqus Analysis User's Guide, Chapter 28: Elements
- "A First Course in Finite Elements" - Fish & Belytschko
- "The Finite Element Method" - Zienkiewicz & Taylor
