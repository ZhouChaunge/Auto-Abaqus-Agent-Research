# Contact Analysis Best Practices | 接触分析最佳实践

## 📋 Overview | 概述

Contact modeling is one of the most challenging aspects of FEA. This guide covers contact pair setup, algorithm selection, and troubleshooting.

接触建模是有限元分析中最具挑战性的部分之一。本指南涵盖接触对设置、算法选择和故障排除。

---

## 1️⃣ Contact Surface Definition | 接触面定义

### Master/Slave Selection | 主从面选择

```
Rules | 规则:
1. STIFFER surface → Master | 较硬的面 → 主面
2. COARSER mesh → Master | 较粗的网格 → 主面
3. LARGER surface → Master | 较大的面 → 主面

Example | 示例:
- Steel plate (stiffer) → Master
- Rubber seal (softer) → Slave
- Tool surface (coarser) → Master
- Workpiece (finer) → Slave
```

### Surface Types | 面类型

| Type | 类型 | Use Case | 应用场景 | Pros | 优点 | Cons | 缺点 |
|------|------|----------|---------|------|------|------|------|
| Element-based | 基于单元 | Most general | Most flexible | More setup |
| Node-based | 基于节点 | Point contact | Simple | Less accurate |
| Analytical | 解析面 | Rigid tools | Efficient | Limited shapes |

---

## 2️⃣ Contact Algorithms | 接触算法

### Abaqus/Standard Algorithms

| Algorithm | 算法 | Best For | 适用场景 | Characteristics | 特点 |
|-----------|------|----------|---------|-----------------|------|
| **Penalty** | 罚函数 | General contact | Fast, slight penetration |
| **Augmented Lagrange** | 增广拉格朗日 | Accurate normal contact | Better constraint, slower |
| **Direct** | 直接 | Legacy, simple | Exact enforcement |
| **Kinematic** | 运动学 | Tied contact | Perfect bonding |

### Recommendation | 推荐

```python
# Default choice | 默认选择:
*SURFACE INTERACTION, NAME=IntProp-1
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD

# For better accuracy | 更好的精度:
*SURFACE BEHAVIOR, PENALTY, PRESSURE-OVERCLOSURE=EXPONENTIAL
*CONTACT CONTROLS, STABILIZE=0.0002
```

---

## 3️⃣ Friction Models | 摩擦模型

### Basic Coulomb Friction | 基本库仑摩擦

```
*FRICTION
0.3                    # μ = 0.3

Common coefficients | 常见系数:
- Steel/Steel (dry): 0.5-0.8
- Steel/Steel (lubricated): 0.1-0.2
- Rubber/Metal: 0.5-1.0
- Aluminum/Steel: 0.45-0.6
```

### Penalty vs Lagrange | 罚函数 vs 拉格朗日

```python
# Penalty (default, fast) | 罚函数（默认，快速）:
*FRICTION, SLIP TOLERANCE=0.005, ELASTIC SLIP=0.0001
0.3

# Lagrange (exact, slower) | 拉格朗日（精确，较慢）:
*FRICTION, LAGRANGE
0.3
```

---

## 4️⃣ Common Problems & Solutions | 常见问题与解决

### Problem: Contact Chattering | 接触振荡

```python
# Symptoms | 症状:
- Oscillating contact status
- Convergence difficulties
- EXCESSIVE CONTACT ADJUSTMENTS warning

# Solutions | 解决方案:
1. Add contact stabilization:
   *CONTACT CONTROLS, STABILIZE=0.0002

2. Use damping:
   *CONTACT DAMPING, DEFINITION=CRITICAL DAMPING FRACTION
   0.05

3. Increase time increments or use automatic
```

### Problem: Initial Penetration | 初始穿透

```python
# Solutions | 解决方案:

# Option 1: Adjust geometry | 调整几何
# Fix CAD model to remove overlap

# Option 2: Allow interference | 允许过盈
*CONTACT INTERFERENCE, SHRINK
*CONTACT PAIR, ADJUST=0.001

# Option 3: Use clearance | 使用间隙
*CLEARANCE, CLEARANCE=0.001
```

### Problem: Over-closure | 过度闭合

```python
# Symptoms | 症状:
- "SLAVE NODE IS IN INITIAL CONTACT"
- Unrealistic stress at contact

# Solutions | 解决方案:
1. Define initial clearance:
   *CLEARANCE, SLAVE=SlaveSurf, MASTER=MasterSurf, CLEARANCE=0.001

2. Use interference fit step:
   *CONTACT INTERFERENCE, SHRINK

3. Fix geometry in CAD
```

---

## 5️⃣ General Contact vs Contact Pairs | 通用接触 vs 接触对

### General Contact (Recommended for complex models) | 通用接触

```python
*CONTACT
*CONTACT INCLUSIONS, ALL EXTERIOR
*CONTACT PROPERTY ASSIGNMENT
,  , IntProp-1
*SURFACE INTERACTION, NAME=IntProp-1
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.2
```

**Pros | 优点:**
- Automatic detection
- Easy setup for many surfaces
- Self-contact included

### Contact Pairs (More control) | 接触对

```python
*CONTACT PAIR, INTERACTION=IntProp-1, TYPE=SURFACE TO SURFACE
SlaveSurf, MasterSurf
```

**Pros | 优点:**
- Fine-grained control
- Better for specific interactions
- Clearer debugging

---

## 6️⃣ Performance Tips | 性能优化

```
1. Use appropriate contact formulation | 使用合适的接触公式:
   - Surface-to-surface (default, robust)
   - Node-to-surface (faster, less accurate)

2. Limit contact pairs | 限制接触对:
   - Only define necessary interactions
   - Remove unused contact definitions

3. Smooth contact transitions | 平滑接触过渡:
   - Use ADJUST to avoid large initial corrections
   - Consider initial soft contact step

4. Monitor contact output | 监控接触输出:
   - Request CSTRESS, CDISP for debugging
   - Check contact pressure distribution
```

---

## 7️⃣ Checklist | 检查清单

Before running contact analysis:

运行接触分析前请检查：

- [ ] Master/slave assignment correct
      主从面分配正确
- [ ] Mesh compatibility (slave finer or equal)
      网格兼容性（从面更细或相等）
- [ ] Friction coefficient reasonable
      摩擦系数合理
- [ ] Initial gap/penetration handled
      初始间隙/穿透已处理
- [ ] Contact output requested
      已请求接触输出
- [ ] Stabilization considered if needed
      如需要已考虑稳定化

---

*See also: [Convergence Guide](convergence.md), [Error Codes](../../abaqusgpt/knowledge/error_codes.py)*
