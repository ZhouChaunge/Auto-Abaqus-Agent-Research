# Convergence Best Practices | 收敛控制最佳实践

## 📋 Overview | 概述

Achieving convergence in nonlinear analysis is often the most challenging aspect. This guide covers Newton-Raphson controls, step parameters, and stabilization techniques.

在非线性分析中实现收敛通常是最具挑战性的部分。本指南涵盖 Newton-Raphson 控制、步参数和稳定化技术。

---

## 1️⃣ Understanding Convergence | 理解收敛

### Newton-Raphson Iterations | Newton-Raphson 迭代

```
Abaqus checks two criteria each iteration:
Abaqus 每次迭代检查两个准则：

1. Force Residual | 力残差:
   ||R|| / ||P|| < tolerance (default 0.5%)
   残差力 / 施加力 < 容差

2. Displacement Correction | 位移修正:
   ||Δu|| / ||Δu_max|| < tolerance (default 1%)
   位移增量 / 最大位移 < 容差
```

### Iteration Output | 迭代输出解读

```
ATTEMPT  ITERATION   RESIDUAL     CORRECTION    STATUS
   1         1       1.00E+00     1.00E+00     
   1         2       5.23E-01     3.41E-01     
   1         3       1.12E-02     8.90E-03     
   1         4       3.45E-05     2.10E-05     CONVERGED ✓

Key indicators | 关键指标:
- Residual should decrease monotonically | 残差应单调下降
- Typical convergence: 3-5 iterations | 典型收敛：3-5次迭代
- >10 iterations: consider adjustments | >10次迭代：考虑调整
```

---

## 2️⃣ Step Controls | 步控制

### Time Incrementation | 时间增量

```python
# Typical setup | 典型设置:
*STEP, NLGEOM=YES
*STATIC
0.1, 1.0, 1e-8, 0.2
#  ↑    ↑    ↑    ↑
#  |    |    |    └── Maximum increment (Δt_max)
#  |    |    └── Minimum increment (Δt_min)
#  |    └── Total time (T)
#  └── Initial increment (Δt_0)

# Conservative setup | 保守设置:
*STATIC
0.01, 1.0, 1e-10, 0.1
```

### Automatic Stabilization | 自动稳定化

```python
# For unstable problems | 用于不稳定问题:
*STATIC, STABILIZE=0.0002, ALLSDTOL=0.05

# Parameters | 参数:
# STABILIZE: damping factor (default 0.0002)
# ALLSDTOL: max fraction of strain energy (default 0.05)

# Check in .sta file:
# DISSIPATED ENERGY FRACTION should be < 5%
```

---

## 3️⃣ Common Convergence Issues | 常见收敛问题

### Issue: Too Many Iterations | 迭代次数过多

```python
# Symptoms | 症状:
- 10+ iterations per increment
- Slow residual reduction
- "SEVERE DISCONTINUITIES" warnings

# Solutions | 解决方案:
1. Reduce initial increment:
   *STATIC
   0.01, 1.0, 1e-10, 0.1

2. Enable line search:
   *STEP, NLGEOM=YES, LINE SEARCH=YES

3. Add solution controls:
   *CONTROLS, PARAMETERS=LINE SEARCH
   5, 1.0, 0.0001, 0.25, 0.1
```

### Issue: Divergence | 发散

```python
# Symptoms | 症状:
- Residual increases each iteration
- "NUMERICAL SINGULARITY" error
- Very large displacements

# Solutions | 解决方案:
1. Check boundary conditions for rigid body motion
2. Verify material parameters (E > 0, 0 < ν < 0.5)
3. Check mesh quality (no distorted elements)
4. Use stabilization:
   *STATIC, STABILIZE=0.001

5. Apply loads gradually:
   *AMPLITUDE, NAME=RAMP
   0., 0., 1., 1.
   *CLOAD, AMPLITUDE=RAMP
   ...
```

### Issue: Cutbacks | 步长回退

```python
# Symptoms | 症状:
- "ATTEMPT 2", "ATTEMPT 3" in .sta
- Very small increments
- "TIME INCREMENT REQUIRED IS LESS THAN MINIMUM"

# Solutions | 解决方案:
1. Reduce minimum increment:
   *STATIC
   0.1, 1.0, 1e-15, 0.2

2. Increase max iterations:
   *CONTROLS, PARAMETERS=TIME INCREMENTATION
   8, 10, , , , , , 5, , , ,

3. Check for sudden changes:
   - Contact chattering
   - Material bifurcation
   - Geometric instability
```

---

## 4️⃣ Advanced Controls | 高级控制

### Solution Controls | 求解控制

```python
*CONTROLS, PARAMETERS=TIME INCREMENTATION
# Defaults and typical modifications:
I_0=4    # Initial equilibrium iterations before cutback → 8
I_R=8    # Max equilibrium iterations → 10
I_P=9    # Iterations for re-estimation → 9
I_C=16   # Max iterations for cutback → 20
I_L=5    # Max attempts per increment → 10
```

### Field Equations | 场方程

```python
*CONTROLS, PARAMETERS=FIELD
# Adjust convergence tolerances:
R_n^α = 0.005   # Force residual tolerance → 0.01 (relaxed)
C_n^α = 0.01    # Displacement correction tolerance → 0.02

*CONTROLS, PARAMETERS=FIELD, FIELD=DISPLACEMENT
0.01, 0.02, , , , ,
```

### Line Search | 线搜索

```python
*CONTROLS, PARAMETERS=LINE SEARCH
# For highly nonlinear problems:
N_LS=5      # Max line search iterations → 10
η_LS=1.0    # Lower bound → 0.5
γ_LS=0.0001 # Min scale factor → 0.001
```

---

## 5️⃣ Stabilization Strategies | 稳定化策略

### When to Use | 何时使用

```
✅ Use stabilization when | 使用稳定化的情况:
- Buckling/post-buckling analysis | 屈曲/后屈曲分析
- Material softening | 材料软化
- Contact problems with chattering | 接触振荡问题
- Geometric instabilities | 几何不稳定

❌ Avoid or be careful when | 避免或谨慎的情况:
- Static stress analysis | 静态应力分析
- When physical damping exists | 存在物理阻尼时
- Energy balance is critical | 能量平衡关键时
```

### Stabilization Types | 稳定化类型

```python
# 1. Automatic stabilization | 自动稳定化:
*STATIC, STABILIZE=0.0002

# 2. Contact-specific | 接触专用:
*CONTACT CONTROLS, STABILIZE=0.001

# 3. Manual damping | 手动阻尼:
*DAMPING, ALPHA=0.1
*DASHPOT, ...

# 4. Viscous regularization | 粘性正则化:
*VISCOELASTIC, TIME=RELAXATION TEST DATA
```

---

## 6️⃣ Monitoring Convergence | 监控收敛

### Key Files to Check | 检查关键文件

```
1. .sta file | 状态文件:
   - INCREMENT, ATTEMPTS, ITERATIONS
   - TOTAL TIME, STEP TIME
   - WARNINGS and ERRORS

2. .msg file | 消息文件:
   - Detailed iteration history
   - Element-level warnings
   - Contact status

3. .dat file | 数据文件:
   - Energy summaries
   - Reaction forces
   - Diagnostic output
```

### Energy Checks | 能量检查

```
Monitor in .dat or History Output:
监控在 .dat 或历史输出中：

ALLSE - Strain energy | 应变能
ALLKE - Kinetic energy | 动能
ALLWK - Work done | 外力做功
ALLSD - Stabilization dissipation | 稳定化耗散

Rule | 规则:
ALLSD / ALLSE < 5% (typically < 2%)
稳定化耗散 / 应变能 < 5%
```

---

## 7️⃣ Checklist | 检查清单

Before submitting analysis:

提交分析前请检查：

- [ ] Appropriate step type selected (Static, Dynamic, etc.)
      选择了合适的步类型
- [ ] Time incrementation parameters reasonable
      时间增量参数合理
- [ ] Boundary conditions properly constrain rigid body motion
      边界条件正确约束刚体运动
- [ ] Material parameters physically reasonable
      材料参数物理合理
- [ ] Mesh quality acceptable
      网格质量可接受
- [ ] Output requests include energy for monitoring
      输出请求包含能量用于监控

---

*See also: [Error Codes](../../abaqusgpt/knowledge/error_codes.py), [Contact Guide](contact.md)*
