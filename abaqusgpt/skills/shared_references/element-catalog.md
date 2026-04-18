# Element Catalog | 单元目录

Comprehensive reference for Abaqus element types.
Abaqus 单元类型的完整参考。

---

## 3D Solid Elements | 三维实体单元

### C3D8 Family | C3D8 系列

#### C3D8 - 8-node Linear Brick (Full Integration)
**中文名称**: 8节点线性六面体（全积分）

| Property | Value |
|----------|-------|
| Nodes | 8 |
| Integration | Full (2×2×2 = 8 points) |
| DOF/Node | 3 (ux, uy, uz) |

**Recommended Use Cases | 推荐用途:**
- ✅ Accurate stress analysis | 精确应力分析
- ✅ Models without large deformation | 不涉及大变形的问题
- ✅ Problems requiring no hourglass control | 不需要沙漏控制的问题

**Warnings | 警告:**
- ⚠️ Prone to shear locking | 可能导致剪切锁死
- ⚠️ Lower accuracy in bending-dominated problems | 弯曲主导问题中精度较低
- ⚠️ Not recommended for coarse meshes | 网格较粗时不推荐

**Alternatives | 替代方案:** C3D8R, C3D8I, C3D20R

---

#### C3D8R - 8-node Linear Brick (Reduced Integration)
**中文名称**: 8节点线性六面体（减缩积分）

| Property | Value |
|----------|-------|
| Nodes | 8 |
| Integration | Reduced (1 point) |
| DOF/Node | 3 (ux, uy, uz) |

**Recommended Use Cases | 推荐用途:**
- ✅ Large deformation analysis | 大变形分析
- ✅ Contact problems | 接触问题
- ✅ Plasticity analysis | 塑性分析
- ✅ General structural analysis | 一般结构分析

**Warnings | 警告:**
- ⚠️ Requires hourglass control | 需要沙漏控制
- ⚠️ Minimum 2 elements through thickness | 厚度方向至少需要2层单元
- ⚠️ Not suitable for bending-dominated problems | 不适合弯曲主导问题

**Hourglass Control | 沙漏控制:**
```
*SECTION CONTROLS, NAME=HOURGLASS, HOURGLASS=ENHANCED
```

**Alternatives | 替代方案:** C3D8, C3D8I, C3D20R

---

#### C3D8I - 8-node Linear Brick (Incompatible Modes)
**中文名称**: 8节点线性六面体（非协调模式）

| Property | Value |
|----------|-------|
| Nodes | 8 |
| Integration | Full + Incompatible modes |
| DOF/Node | 3 (ux, uy, uz) |

**Recommended Use Cases | 推荐用途:**
- ✅ Bending problems | 弯曲问题
- ✅ Thin-walled structures | 薄壁结构
- ✅ When fewer elements are needed | 需要较少单元的情况

**Warnings | 警告:**
- ⚠️ Higher computational cost than C3D8R | 计算成本高于C3D8R
- ⚠️ May be unstable in large deformation | 大变形时可能不稳定
- ⚠️ Not suitable for contact analysis | 不适合接触分析

**Alternatives | 替代方案:** C3D8R, C3D20R

---

### C3D20 Family | C3D20 系列

#### C3D20R - 20-node Quadratic Brick (Reduced Integration)
**中文名称**: 20节点二次六面体（减缩积分）

| Property | Value |
|----------|-------|
| Nodes | 20 |
| Integration | Reduced (2×2×2 = 8 points) |
| DOF/Node | 3 (ux, uy, uz) |

**Recommended Use Cases | 推荐用途:**
- ✅ High-accuracy analysis | 高精度分析
- ✅ Bending problems | 弯曲问题
- ✅ Areas with large stress gradients | 应力梯度大的区域

**Best Practice | 最佳实践:**
- Preferred for static linear analysis | 静力线性分析首选
- One element through thickness may suffice | 厚度方向一层单元可能就够了

**Alternatives | 替代方案:** C3D10M, C3D8R

---

### Tetrahedral Elements | 四面体单元

#### C3D10 - 10-node Quadratic Tetrahedron
**中文名称**: 10节点二次四面体

| Property | Value |
|----------|-------|
| Nodes | 10 |
| Integration | Full (4 points) |
| DOF/Node | 3 (ux, uy, uz) |

**Recommended Use Cases | 推荐用途:**
- ✅ Complex geometry auto-meshing | 复杂几何自动网格
- ✅ High accuracy requirements | 高精度需求
- ✅ General structural analysis | 一般结构分析

**Warnings | 警告:**
- ⚠️ Requires more elements than hex | 比六面体需要更多单元
- ⚠️ Refine at stress concentrations | 应力集中处需加密

**Alternatives | 替代方案:** C3D10M, C3D4

---

#### C3D10M - 10-node Modified Quadratic Tetrahedron
**中文名称**: 10节点改进二次四面体

**Recommended Use Cases | 推荐用途:**
- ✅ Contact analysis | 接触分析
- ✅ Large deformation | 大变形
- ✅ Complex geometry | 复杂几何

**Best Practice | 最佳实践:**
- Preferred over C3D10 for contact | 接触分析时优于C3D10
- Works well with Abaqus/Explicit | 与 Abaqus/Explicit 配合良好

---

## Shell Elements | 壳单元

### S4R - 4-node Shell (Reduced Integration)
**中文名称**: 4节点壳（减缩积分）

| Property | Value |
|----------|-------|
| Nodes | 4 |
| Integration | Reduced (1 in-plane + Simpson through thickness) |
| DOF/Node | 6 (ux, uy, uz, rx, ry, rz) |

**Recommended Use Cases | 推荐用途:**
- ✅ General shell analysis | 一般壳分析
- ✅ Large deformation | 大变形
- ✅ Contact problems | 接触问题

**Keywords | 关键字:**
```
*SHELL SECTION, MATERIAL=xxx
thickness
```

---

### SC8R - 8-node Continuum Shell
**中文名称**: 8节点连续体壳

**Recommended Use Cases | 推荐用途:**
- ✅ 3D-like behavior with shell efficiency | 三维行为但壳单元效率
- ✅ Composite laminates | 复合材料层合板
- ✅ Through-thickness stress output | 厚度方向应力输出

---

## Beam Elements | 梁单元

### B31 - 2-node Linear Beam
**中文名称**: 2节点线性梁

**Recommended Use Cases | 推荐用途:**
- ✅ Frame structures | 框架结构
- ✅ Reinforcement | 钢筋

### B32 - 3-node Quadratic Beam
**中文名称**: 3节点二次梁

**Recommended Use Cases | 推荐用途:**
- ✅ Curved beams | 曲梁
- ✅ Higher accuracy needed | 需要更高精度

---

## Connector Elements | 连接单元

### CONN3D2 - 3D Connector
**中文名称**: 三维连接器

**Recommended Use Cases | 推荐用途:**
- ✅ Springs and dampers | 弹簧和阻尼器
- ✅ Bolts and fasteners | 螺栓和紧固件
- ✅ Joints and hinges | 铰接和转动副

---

## Special Elements | 特殊单元

### MASS - Point Mass
**中文名称**: 质点

**Usage | 用法:**
```
*ELEMENT, TYPE=MASS
*MASS
mass_value
```

### ROTARYI - Rotary Inertia
**中文名称**: 转动惯量

**Usage | 用法:**
```
*ELEMENT, TYPE=ROTARYI
*ROTARY INERTIA
I11, I22, I33
```

---

## Quick Selection Guide | 快速选择指南

| Analysis Type | Recommended Elements |
|--------------|---------------------|
| Static (General) | C3D8R, C3D20R, C3D10M |
| Large Deformation | C3D8R, C3D10M |
| Contact | C3D8R, C3D10M, S4R |
| Bending | C3D8I, C3D20R, S4R |
| Explicit/Impact | C3D8R, S4R |
| Thermal | DC3D8, DC3D20 |

---

## References | 参考资料

- Abaqus Analysis User's Guide, Chapter 28: Elements
- Abaqus Theory Manual, Section 3.2: Solid Elements
