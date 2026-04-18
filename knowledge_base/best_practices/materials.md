# Material Modeling Best Practices | 材料建模最佳实践

## 📋 Overview | 概述

Proper material definition is critical for accurate simulation results. This guide covers material model selection, parameter fitting, and common pitfalls.

正确的材料定义对于准确的仿真结果至关重要。本指南涵盖材料模型选择、参数拟合和常见陷阱。

---

## 1️⃣ Material Model Selection | 材料模型选择

### Decision Tree | 决策树

```
Start | 开始
  │
  ├── Is material metallic? | 是金属材料吗？
  │   ├── Yes → Linear elastic or Elastoplastic
  │   │         弹性或弹塑性
  │   └── No ─┬── Is it rubber-like? | 像橡胶吗？
  │           │   ├── Yes → Hyperelastic
  │           │   │         超弹性
  │           │   └── No ─┬── Is it foam? | 是泡沫吗？
  │           │           │   ├── Yes → Hyperfoam or Crushable Foam
  │           │           │   │         超弹性泡沫或可压溃泡沫
  │           │           │   └── No → Composite or General
  │           │           │           复合材料或通用
```

### Common Materials | 常见材料

| Material | 材料 | Model | 模型 | Key Parameters | 关键参数 |
|----------|------|-------|------|----------------|---------|
| Steel | 钢 | Elastic + Plastic | E, ν, σ_y, hardening |
| Aluminum | 铝 | Elastic + Plastic | E, ν, σ_y, hardening |
| Rubber | 橡胶 | Hyperelastic (Mooney-Rivlin) | C_10, C_01, D_1 |
| Foam | 泡沫 | Hyperfoam | μ_i, α_i, β_i |
| Concrete | 混凝土 | CDP or Brittle Cracking | f_c, f_t, damage |
| Composites | 复合材料 | Lamina | E_1, E_2, ν_12, G_12, G_13, G_23 |

---

## 2️⃣ Linear Elastic Materials | 线弹性材料

### Basic Definition | 基本定义

```python
*MATERIAL, NAME=Steel
*ELASTIC
210000., 0.3
#   ↑      ↑
#   E      ν (Poisson's ratio)
```

### Important Checks | 重要检查

```
✓ Young's modulus E > 0
✓ Poisson's ratio -1 < ν < 0.5
✓ For incompressible: use ν ≤ 0.495 with hybrid elements
✓ Units must be consistent (e.g., MPa-mm-ton-s)
```

---

## 3️⃣ Elastoplastic Materials | 弹塑性材料

### Isotropic Hardening | 各向同性硬化

```python
*MATERIAL, NAME=Steel_Plastic
*ELASTIC
210000., 0.3
*PLASTIC
250., 0.         # σ_y at ε_p = 0
350., 0.1        # σ at ε_p = 0.1
400., 0.2        # σ at ε_p = 0.2
450., 0.3        # σ at ε_p = 0.3
```

### Best Practices | 最佳实践

```
1. True stress-strain data | 真应力-真应变数据:
   σ_true = σ_eng × (1 + ε_eng)
   ε_true = ln(1 + ε_eng)

2. Plastic strain | 塑性应变:
   ε_plastic = ε_true - σ_true / E

3. Data density | 数据密度:
   - At least 10 data points
   - More points near yield
   - Ensure monotonically increasing

4. Maximum strain | 最大应变:
   - Include data beyond expected analysis range
   - Abaqus extrapolates linearly beyond last point
```

### Kinematic Hardening | 随动硬化

```python
*PLASTIC, HARDENING=KINEMATIC
250., 0.
350., 0.05

# For cyclic loading | 循环加载时:
*PLASTIC, HARDENING=COMBINED
# Use combined with:
*CYCLIC HARDENING, PARAMETERS=HALF CYCLE
```

---

## 4️⃣ Hyperelastic Materials | 超弹性材料

### Model Selection | 模型选择

| Model | 模型 | Best For | 适用场景 | Strain Range | 应变范围 |
|-------|------|----------|---------|--------------|---------|
| Neo-Hookean | 简单变形 | < 30% |
| Mooney-Rivlin | General rubber | < 200% |
| Ogden | Large strain rubber | < 700% |
| Arruda-Boyce | Biological tissue | < 300% |
| Polynomial | Complex behavior | Depends on order |

### Parameter Fitting | 参数拟合

```python
# From test data | 从试验数据:
*HYPERELASTIC, TEST DATA INPUT, MOONEY-RIVLIN
*UNIAXIAL TEST DATA
# stress, strain pairs from uniaxial test

*BIAXIAL TEST DATA
# stress, strain pairs from biaxial test

*PLANAR TEST DATA
# stress, strain pairs from planar test

# Or specify coefficients directly | 或直接指定系数:
*HYPERELASTIC, MOONEY-RIVLIN
C_10, C_01, D_1
```

### Stability Checks | 稳定性检查

```
Drucker Stability | Drucker 稳定性:
- Strain energy must be positive definite
- Check Abaqus material evaluation output
- Test with simple element model first

Common issues | 常见问题:
- C_01 < 0 may cause instability
- Initial modulus μ = 2(C_10 + C_01) should be positive
- Bulk modulus K = 2/D_1 should be >> μ for incompressibility
```

---

## 5️⃣ Damage and Failure | 损伤与失效

### Ductile Damage | 延性损伤

```python
*MATERIAL, NAME=Steel_Damage
*ELASTIC
210000., 0.3
*PLASTIC
250., 0.
400., 0.2

*DAMAGE INITIATION, CRITERION=DUCTILE
0.3, -0.33, 0.     # ε_D^pl, η, ε̇
0.2, 0.0, 0.
0.15, 0.33, 0.

*DAMAGE EVOLUTION, TYPE=DISPLACEMENT
0.1                 # u_f^pl = characteristic length × fracture strain
```

### Brittle Failure | 脆性失效

```python
*MATERIAL, NAME=Glass
*ELASTIC
70000., 0.2
*BRITTLE CRACKING
5., 0.           # σ_t, u_n (crack opening)
0., 0.05

*BRITTLE SHEAR
1., 0.
0., 0.05
```

---

## 6️⃣ Temperature Effects | 温度效应

### Temperature-dependent Properties | 温度相关属性

```python
*MATERIAL, NAME=Steel_Thermal
*ELASTIC
210000., 0.3, 20.    # At 20°C
190000., 0.32, 200.  # At 200°C
150000., 0.35, 500.  # At 500°C

*EXPANSION
1.2e-5, 20.          # α at 20°C
1.3e-5, 200.
1.4e-5, 500.

*CONDUCTIVITY
50., 20.             # k at 20°C
45., 200.
40., 500.

*SPECIFIC HEAT
450., 20.            # c_p at 20°C
500., 200.
550., 500.
```

---

## 7️⃣ Unit Systems | 单位系统

### Consistent Unit Systems | 一致单位系统

| System | 系统 | Length | Mass | Time | Force | Stress | Energy |
|--------|------|--------|------|------|-------|--------|--------|
| SI (m) | m | kg | s | N | Pa | J |
| SI (mm) | mm | tonne | s | N | MPa | mJ |
| US (inch) | in | lbf·s²/in | s | lbf | psi | lbf·in |

### Common Mistakes | 常见错误

```
❌ Mixing MPa with kg (should use tonne)
❌ Using g instead of kg with Pa
❌ Forgetting to convert density

✓ Always document your unit system
✓ Check dimensions: [Force] = [Mass][Length]/[Time]²
```

---

## 8️⃣ Checklist | 检查清单

Before using material definition:

使用材料定义前请检查：

- [ ] Material model appropriate for loading type
      材料模型适合加载类型
- [ ] Parameters from reliable test data
      参数来自可靠试验数据
- [ ] Consistent unit system
      一致的单位系统
- [ ] Stability requirements satisfied
      稳定性要求满足
- [ ] Temperature dependence if relevant
      如相关已考虑温度依赖性
- [ ] Damage/failure criteria if applicable
      如适用已定义损伤/失效准则

---

*See also: [Element Library](../../abaqusgpt/knowledge/element_library.py), [Error Codes](../../abaqusgpt/knowledge/error_codes.py)*
