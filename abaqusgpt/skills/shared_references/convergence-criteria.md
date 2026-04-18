# Convergence Criteria | 收敛标准

Understanding and tuning convergence criteria in Abaqus.
理解和调整 Abaqus 中的收敛标准。

---

## Newton-Raphson Method | 牛顿-拉夫森法

Abaqus uses Newton-Raphson iteration to solve nonlinear problems.
Abaqus 使用牛顿-拉夫森迭代求解非线性问题。

### Residual Force Criterion | 残差力准则

```
||R|| / ||P|| < R_n^α
```

Where:
- R = Residual force vector | 残差力向量
- P = Applied load vector | 施加载荷向量
- R_n^α = Force residual tolerance | 力残差容差

**Default:** R_n^α = 0.005 (0.5%)

---

### Displacement Correction Criterion | 位移修正准则

```
||Δu|| / ||u_max|| < C_n^α
```

Where:
- Δu = Displacement correction | 位移修正
- u_max = Maximum displacement | 最大位移
- C_n^α = Displacement tolerance | 位移容差

**Default:** C_n^α = 0.01 (1%)

---

## Adjusting Convergence Controls | 调整收敛控制

### Method 1: CONTROLS Keyword | CONTROLS 关键字

```
*CONTROLS, PARAMETERS=FIELD
0.01, 0.01, , , 0.02, , ,
*CONTROLS, PARAMETERS=TIME INCREMENTATION
8, 10, , , , , , 5, , ,
```

**Parameters Explained | 参数说明:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| I_0 | Max equilibrium iterations | 4 |
| I_R | Max severe discontinuity iterations | 8 |
| I_C | Max consecutive equilibrium iterations | 12 |
| I_L | Max iterations for linear increment | 50 |
| D_F | Max cutback factor | 0.25 |

---

### Method 2: Relaxing Tolerances | 放宽容差

**⚠️ Use with caution | 谨慎使用**

```
*CONTROLS, PARAMETERS=FIELD
0.05, 0.05, , , 0.1
```

This relaxes:
- Force residual: 0.5% → 5%
- Displacement correction: 1% → 5%
- Penetration: default → 10%

---

## Severe Discontinuity Iterations | 严重不连续迭代

### What They Are | 定义

Iterations where contact status changes (open↔closed) or friction status changes (stick↔slip).
接触状态变化（开↔闭）或摩擦状态变化（粘↔滑）时的迭代。

### Default Limits | 默认限制

- I_R = 8 severe discontinuity iterations per attempt
- More than I_R → new attempt with smaller increment

### Adjustments | 调整

```
*CONTROLS, PARAMETERS=TIME INCREMENTATION
, 12, , , , , , , , ,
```

Increases severe discontinuity iteration limit to 12.

---

## Automatic Stabilization | 自动稳定化

### When to Use | 何时使用

- Initial contact establishment | 初始接触建立
- Near-singular configurations | 接近奇异配置
- Local instabilities | 局部失稳

### Implementation | 实现

```
*STATIC, STABILIZE=2E-4, ALLSDTOL=0.05
```

**Parameters:**
- STABILIZE: Damping factor (fraction of strain energy)
- ALLSDTOL: Allowable ratio of dissipated energy

### Best Practices | 最佳实践

1. Start with small damping factor | 从小阻尼系数开始
2. Check ALLSD (stabilization energy) in output | 检查输出中的稳定化能量
3. ALLSD should be < 5% of ALLIE (internal energy) | ALLSD 应 < ALLIE 的 5%

---

## Contact Stabilization | 接触稳定化

### Dedicated Contact Damping | 专用接触阻尼

```
*CONTACT STABILIZATION, NAME=CONTACT_STAB
slave_surface
*CONTACT CONTROLS, STABILIZE
0.1, 0.1
```

**Advantages | 优点:**
- Only applies to contact regions | 仅作用于接触区域
- Reduces unwanted damping | 减少不必要的阻尼

---

## Line Search | 线搜索

### Purpose | 目的

Improves convergence for highly nonlinear problems by finding optimal step size.
通过寻找最优步长改善高度非线性问题的收敛性。

### Activation | 激活

```
*STEP, NLGEOM=YES, LINE SEARCH=YES
```

### Best Practices | 最佳实践

- Useful for strong nonlinearities | 对强非线性有用
- May slow down well-behaved problems | 可能减慢良态问题
- Recommended for hyperelastic materials | 推荐用于超弹性材料

---

## Time Increment Control | 时间增量控制

### Automatic Time Stepping | 自动时间步

```
*STATIC
initial_increment, total_time, min_increment, max_increment
```

**Example | 示例:**
```
*STATIC
0.1, 1.0, 1E-10, 0.5
```

- Initial: 10% of step time
- Minimum: 1E-10
- Maximum: 50% of step time

### Cutback Strategy | 回退策略

When convergence fails:
1. Cut increment by factor (default 0.25)
2. Retry with smaller increment
3. If still fails, cut again
4. If exceeds max attempts (default 5), abort

---

## Troubleshooting Convergence | 收敛故障排除

### Diagnostic Output | 诊断输出

```
*STEP
...
*OUTPUT, DIAGNOSTICS=YES
*END STEP
```

### Check List | 检查清单

| Issue | Indicator | Action |
|-------|-----------|--------|
| Force imbalance | Large residuals | Reduce increment, check loads |
| Large corrections | Δu > 10% of u | Enable line search |
| Contact changes | Many SDI | Add contact stabilization |
| Material issues | Plasticity failure | Reduce increment, check data |

---

## Recommended Settings by Problem Type | 按问题类型推荐设置

### Standard Nonlinear Static | 标准非线性静力

```
*STEP, NLGEOM=YES, INC=1000
*STATIC
0.1, 1.0, 1E-8, 0.5
```

### Severe Contact | 严重接触

```
*STEP, NLGEOM=YES, INC=10000
*STATIC, STABILIZE=1E-4, ALLSDTOL=0.05
0.01, 1.0, 1E-12, 0.1
```

### Near-Buckling | 接近屈曲

```
*STEP, NLGEOM=YES, INC=1000
*STATIC, RIKS
0.01, 1.0, 1E-10, 0.05, , , 2.0
```

---

## References | 参考资料

- Abaqus Analysis User's Guide, Section 7.2: Solving Nonlinear Problems
- Abaqus Theory Manual, Section 2.2: Iterative Solution Methods
- "Nonlinear Finite Elements for Continua and Structures" - Belytschko et al.
