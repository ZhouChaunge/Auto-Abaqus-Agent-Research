# Error Patterns | 错误模式

Comprehensive database of Abaqus error patterns and solutions.
Abaqus 错误模式和解决方案的完整数据库。

---

## Convergence Errors | 收敛错误

### TOO MANY ATTEMPTS MADE FOR THIS INCREMENT
**严重程度**: 🔴 Critical

**Description | 描述:**
The solver failed to find equilibrium after the maximum number of attempts.
求解器在达到最大尝试次数后仍无法找到平衡状态。

**Common Causes | 常见原因:**
1. Time increment too large | 时间步太大
2. Improper contact settings | 接触设置不当
3. Material instability | 材料参数导致失稳
4. Abrupt boundary condition changes | 边界条件突变
5. Poor mesh quality | 网格质量差

**Solutions | 解决方案:**
```
*STEP, INC=10000
*STATIC
0.01, 1.0, 1E-10, 0.1
```
- Reduce initial increment | 减小初始增量步
- Increase maximum increments | 增加最大增量数
- Add stabilization | 添加稳定化
```
*STATIC, STABILIZE=0.0002, ALLSDTOL=0.05
```

**Reference | 参考:** Abaqus Analysis User's Guide 7.2.1

---

### NEGATIVE EIGENVALUE
**严重程度**: 🟡 Warning

**Description | 描述:**
The stiffness matrix has negative eigenvalues, indicating potential instability.
刚度矩阵存在负特征值，表明可能存在失稳。

**Common Causes | 常见原因:**
1. Structural buckling | 结构屈曲
2. Material softening | 材料软化
3. Contact separation | 接触分离
4. Improper element type | 不当的单元类型

**Solutions | 解决方案:**
1. Enable geometric nonlinearity | 启用几何非线性
```
*STEP, NLGEOM=YES
```
2. Use Riks method for buckling | 使用 Riks 方法
```
*STATIC, RIKS
```
3. Add initial imperfection | 添加初始缺陷

**Reference | 参考:** Abaqus Analysis User's Guide 6.2.4

---

### TIME INCREMENT REQUIRED IS LESS THAN THE MINIMUM
**严重程度**: 🔴 Critical

**Description | 描述:**
The solver needs a smaller time increment than allowed.
求解器需要的时间增量小于允许的最小值。

**Solutions | 解决方案:**
1. Reduce minimum increment limit | 减小最小增量步限制
```
*STATIC
0.01, 1.0, 1E-15, 0.1
```
2. Use automatic time stepping | 使用自动时间步
3. Add stabilization | 添加稳定化

---

## Element Errors | 单元错误

### EXCESSIVE DISTORTION
**严重程度**: 🔴 Critical

**Description | 描述:**
Element deformation exceeds allowable limits.
单元变形超出允许范围。

**Common Causes | 常见原因:**
1. Excessive element deformation | 单元变形过大
2. Coarse mesh | 网格太粗
3. Inappropriate material model | 材料模型不适合
4. Strain concentration | 应变集中

**Solutions | 解决方案:**
1. Refine mesh | 加密网格
2. Enable NLGEOM | 启用几何非线性
3. Use appropriate elements | 使用合适的单元类型 (C3D8R)
4. Consider ALE adaptive meshing | 考虑自适应网格

```
*ADAPTIVE MESH, ELSET=CRITICAL
```

---

### ELEMENT HAS NEGATIVE JACOBIAN
**严重程度**: 🔴 Critical

**Description | 描述:**
Element has inverted or severely distorted shape.
单元翻转或严重扭曲。

**Solutions | 解决方案:**
1. Remesh with better quality | 重新划分网格
2. Use quadratic elements | 使用二次单元
3. Enable hourglass control | 启用沙漏控制
4. Reduce increment size | 减小增量步

---

## Contact Errors | 接触错误

### CONTACT OVERCLOSURE
**严重程度**: 🟡 Warning

**Description | 描述:**
Initial geometric penetration detected between contact surfaces.
检测到接触面之间存在初始几何穿透。

**Solutions | 解决方案:**
1. Adjust overclosure handling | 调整穿透处理
```
*CONTACT CONTROLS, AUTOMATIC OVERCLOSURE
*CONTACT PAIR, ADJUST=0.01
```
2. Fix geometry | 修正几何
3. Redefine contact surfaces | 重新定义接触面

---

### SEVERE DISCONTINUITY ITERATION
**严重程度**: 🟡 Warning

**Description | 描述:**
Contact status frequently changing (open-close-open).
接触状态频繁变化。

**Solutions | 解决方案:**
1. Reduce increment size | 减小增量步
2. Add contact stabilization | 添加接触稳定化
```
*CONTACT STABILIZATION
```
3. Smooth load curves | 平滑载荷曲线
4. Adjust friction model | 调整摩擦模型

---

## Material Errors | 材料错误

### PLASTICITY ALGORITHM DID NOT CONVERGE
**严重程度**: 🔴 Critical

**Description | 描述:**
Plasticity return mapping algorithm failed to converge.
塑性返回映射算法无法收敛。

**Solutions | 解决方案:**
1. Reduce increment size | 减小增量步
2. Smooth hardening curve | 平滑硬化曲线
3. Check material parameters | 检查材料参数
4. Increase data point density | 增加数据点密度

---

### HYPERELASTIC MATERIAL HAS BECOME UNSTABLE
**严重程度**: 🔴 Critical

**Description | 描述:**
Hyperelastic material model lost stability (Drucker condition violated).
超弹性材料模型失稳。

**Solutions | 解决方案:**
1. Check material parameters | 检查材料参数
2. Re-fit from experimental data | 重新拟合实验数据
3. Try different hyperelastic model | 尝试不同的超弹性模型
4. Limit strain range | 限制应变范围

---

## Singularity Errors | 奇异性错误

### ZERO PIVOT
**严重程度**: 🔴 Critical

**Description | 描述:**
Zero pivot detected in stiffness matrix, indicating rigid body motion or disconnection.
刚度矩阵存在零主元，表明有刚体运动或断开。

**Common Causes | 常见原因:**
1. Unconstrained rigid body motion | 刚体运动未约束
2. Disconnected nodes/elements | 节点或单元未连接
3. Zero stiffness | 刚度为零
4. Complete contact separation | 接触完全分离

**Solutions | 解决方案:**
1. Check boundary conditions | 检查边界条件
2. Verify model connectivity | 验证模型连接性
3. Check material parameters | 检查材料参数
4. Add soft springs | 添加软弹簧

```
*SPRING, ELSET=SOFT_SPRINGS
1, 1, 1.0
```

---

## Quick Diagnosis Checklist | 快速诊断清单

| Symptom | First Check | 首先检查 |
|---------|-------------|----------|
| "Too many attempts" | Increment size, contact | 增量大小，接触设置 |
| "Negative eigenvalue" | NLGEOM, constraints | 几何非线性，约束 |
| "Excessive distortion" | Mesh quality, elements | 网格质量，单元类型 |
| "Zero pivot" | BCs, connectivity | 边界条件，连接性 |
| "Contact overclosure" | Initial geometry | 初始几何 |

---

## References | 参考资料

- Abaqus Analysis User's Guide, Chapter 7: Analysis Procedures
- Abaqus Analysis User's Guide, Chapter 35: Contact
- Abaqus Theory Manual, Section 2.2: Convergence Criteria
