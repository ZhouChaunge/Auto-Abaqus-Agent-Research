# Output Settings Best Practices | 输出设置最佳实践

## 📋 Overview | 概述

Proper output configuration ensures you capture necessary data without excessive file sizes. This guide covers field output, history output, and file management.

正确的输出配置确保捕获必要数据而不产生过大文件。本指南涵盖场输出、历史输出和文件管理。

---

## 1️⃣ Field Output | 场输出

### Common Variables | 常见变量

| Variable | 变量 | Description | 描述 | When to Use | 何时使用 |
|----------|------|-------------|------|-------------|---------|
| S | Stress | 应力 | Stress analysis |
| E | Strain | 应变 | Deformation analysis |
| U | Displacement | 位移 | All analyses |
| RF | Reaction force | 反力 | Check BCs |
| CSTRESS | Contact stress | 接触应力 | Contact analysis |
| NT | Temperature | 温度 | Thermal analysis |
| PE | Plastic strain | 塑性应变 | Plasticity |
| PEEQ | Equiv. plastic strain | 等效塑性应变 | Plasticity |
| SDEG | Damage | 损伤变量 | Damage analysis |

### Efficient Setup | 高效设置

```python
# Minimal stress analysis | 最小应力分析:
*OUTPUT, FIELD, FREQUENCY=10
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, E

# Contact analysis | 接触分析:
*OUTPUT, FIELD, FREQUENCY=5
*NODE OUTPUT
U, RF
*ELEMENT OUTPUT
S, E, PE, PEEQ
*CONTACT OUTPUT
CSTRESS, CDISP, CFORCE

# Dynamic analysis | 动力学分析:
*OUTPUT, FIELD, FREQUENCY=20
*NODE OUTPUT
U, V, A, RF
*ELEMENT OUTPUT
S, E
```

### Output Frequency | 输出频率

```
Guidelines | 指南:

Static analysis | 静态分析:
- Use increment-based: FREQUENCY=1 to 10
- Critical steps: FREQUENCY=1

Dynamic analysis | 动力学分析:
- Use time-based: TIME INTERVAL=0.001
- Capture peaks: at least 10 points per cycle

Large models | 大型模型:
- Reduce frequency: FREQUENCY=10 or higher
- Use selective output sets
```

---

## 2️⃣ History Output | 历史输出

### Common Uses | 常见用途

```python
# Force-displacement curve | 力-位移曲线:
*OUTPUT, HISTORY, FREQUENCY=1
*NODE OUTPUT, NSET=LoadPoint
U1, RF1

# Energy monitoring | 能量监控:
*OUTPUT, HISTORY, FREQUENCY=1
*ENERGY OUTPUT
ALLSE, ALLKE, ALLWK, ALLPD, ALLSD

# Contact monitoring | 接触监控:
*OUTPUT, HISTORY
*CONTACT OUTPUT, CPSET=ContactPair
CAREA, CFN, CFS
```

### Energy Outputs | 能量输出

| Variable | 变量 | Description | 描述 | Use | 用途 |
|----------|------|-------------|------|-----|------|
| ALLWK | External work | 外力功 | Energy input |
| ALLSE | Strain energy | 应变能 | Stored energy |
| ALLKE | Kinetic energy | 动能 | Dynamic check |
| ALLPD | Plastic dissipation | 塑性耗散 | Inelastic work |
| ALLSD | Stabilization dissipation | 稳定化耗散 | Check < 5% of ALLSE |
| ALLIE | Internal energy | 内能 | Total internal |
| ETOTAL | Total energy | 总能量 | Conservation check |

---

## 3️⃣ Output Sets | 输出集

### Selective Output | 选择性输出

```python
# Define sets | 定义集合:
*NSET, NSET=CriticalNodes
1001, 1002, 1003, 1050

*ELSET, ELSET=StressRegion
1, 2, 3, 4, 5

# Output to specific sets | 输出到特定集:
*OUTPUT, FIELD
*NODE OUTPUT, NSET=CriticalNodes
U, RF
*ELEMENT OUTPUT, ELSET=StressRegion
S, E, PE
```

### Benefits | 优势

```
✓ Reduced ODB file size | 减小 ODB 文件大小
✓ Faster post-processing | 更快后处理
✓ Focused on critical regions | 聚焦关键区域
✓ More frequent output possible | 可以更频繁输出
```

---

## 4️⃣ ODB File Management | ODB 文件管理

### File Size Control | 文件大小控制

```
Typical ODB sizes | 典型 ODB 大小:
- Small model (< 10k elements): 10-100 MB
- Medium model (10k-100k): 100 MB - 1 GB
- Large model (> 100k): 1 GB - 10+ GB

To reduce size | 减小大小:
1. Increase output frequency interval
2. Use output sets (don't output all)
3. Remove unneeded variables
4. Use compressed output
```

### Compression | 压缩

```python
# In job submission | 作业提交时:
*OUTPUT, FIELD, COMPRESS=YES

# Or in abaqus_v6.env:
odb_compress = ON
```

### Best Practices | 最佳实践

```
1. Start with minimal output | 从最小输出开始
   - Add variables as needed
   - Don't output everything "just in case"

2. Use restart files | 使用重启文件
   *RESTART, WRITE, FREQUENCY=10
   - Allows rerunning from checkpoint
   - Separate from ODB

3. Archive and clean | 归档和清理
   - Delete intermediate ODBs
   - Keep final results only
   - Document what's in each file
```

---

## 5️⃣ Special Outputs | 特殊输出

### Contact Debugging | 接触调试

```python
*OUTPUT, FIELD, FREQUENCY=1
*CONTACT OUTPUT
CSTRESS     # Contact stress | 接触应力
CDISP       # Contact displacement | 接触位移
CFORCE      # Contact force | 接触力
CSTATUS     # Open/closed/slip status | 状态
COPEN       # Contact opening | 接触开口
CSLIP       # Slip distance | 滑移距离
```

### Damage Analysis | 损伤分析

```python
*OUTPUT, FIELD
*ELEMENT OUTPUT
DMICRT      # Damage initiation criterion | 损伤起始准则
SDEG        # Scalar damage | 标量损伤
STATUS      # Element status | 单元状态
```

### Dynamic Analysis | 动力学分析

```python
*OUTPUT, FIELD, TIME INTERVAL=0.001
*NODE OUTPUT
U, V, A     # Displacement, Velocity, Acceleration

*OUTPUT, HISTORY, TIME INTERVAL=0.0001
*NODE OUTPUT, NSET=Sensor
U1, V1, A1
```

---

## 6️⃣ Troubleshooting | 故障排除

### Issue: ODB Too Large | ODB 文件过大

```
Solutions | 解决方案:
1. Check output frequency:
   - Static: FREQUENCY > 5
   - Dynamic: TIME INTERVAL > T/100

2. Remove unneeded variables:
   - Don't output S if only need U
   - Don't output LE if have E

3. Use output sets:
   - Only output critical regions

4. Enable compression:
   *OUTPUT, FIELD, COMPRESS=YES
```

### Issue: Missing Data | 缺少数据

```
Check | 检查:
1. Output request in correct step
2. Variable available for element type
3. FREQUENCY/TIME INTERVAL appropriate
4. Set definition correct
5. Preselect in ODB not filtering data
```

---

## 7️⃣ Checklist | 检查清单

Before submitting job:

提交作业前请检查：

- [ ] Output variables match analysis needs
      输出变量符合分析需求
- [ ] Output frequency appropriate for analysis type
      输出频率适合分析类型
- [ ] Critical regions have sufficient output
      关键区域有足够输出
- [ ] Energy output for solution monitoring
      能量输出用于求解监控
- [ ] Expected file size acceptable
      预期文件大小可接受
- [ ] Restart output enabled for long jobs
      长作业启用了重启输出

---

*See also: [Convergence Guide](convergence.md), [Contact Guide](contact.md)*
