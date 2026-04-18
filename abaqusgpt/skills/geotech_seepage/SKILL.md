---
name: geotech-seepage
version: 1.0.0
description: Seepage, consolidation, and coupled pore fluid-stress analysis in Abaqus
description_cn: 渗流、固结与流固耦合分析（Abaqus）
triggers:
  - "seepage"
  - "渗流"
  - "consolidation"
  - "固结"
  - "pore pressure"
  - "孔隙水压"
  - "孔压"
  - "渗透"
  - "permeability"
  - "coupled"
  - "耦合"
  - "排水"
  - "drainage"
  - "降水"
  - "dewatering"
priority: P1
dependencies:
  - "geotech-constitutive"
author: AbaqusGPT Team
tags:
  - geotechnical
  - seepage
  - consolidation
  - coupled-analysis
---

# Geotech Seepage | 岩土渗流与固结

## Overview | 概述

Expert guidance on seepage analysis, Terzaghi/Biot consolidation, and fully coupled pore fluid-stress analysis in Abaqus. Covers steady-state/transient seepage, dewatering, dam seepage, and consolidation settlement prediction.

渗流分析、太沙基/Biot 固结和全耦合孔隙流体-应力分析指导。覆盖稳态/瞬态渗流、降水、大坝渗流和固结沉降预测。

## Capabilities | 能力

### 1. 单元选择 | Element Selection

#### 耦合孔压单元（必须使用）
| 单元类型 | 维度 | 用途 |
|---------|------|------|
| CPE4P / CPE4PH | 2D 平面应变 | 常规固结 |
| CPE8P / CPE8PH | 2D 平面应变高阶 | 精确分析 |
| C3D8P / C3D8PH | 3D 六面体 | 常规 3D |
| C3D20P / C3D20PH | 3D 高阶 | 精确 3D |
| CAX4P | 轴对称 | 桩基、竖井 |

- **P 后缀**：孔隙水压自由度
- **H 后缀**：混合公式（适用于不可压缩/近不可压缩材料）

#### 纯渗流分析单元
| 单元类型 | 维度 | 用途 |
|---------|------|------|
| DC2D4 | 2D | 稳态/瞬态热传导（类比渗流） |
| FC3D8 | 3D | 流体单元 |

### 2. 材料渗透性 | Material Permeability

#### 各向同性渗透
```
*PERMEABILITY, SPECIFIC=1.0
1.0e-5,    0.8
1.0e-4,    1.0
1.0e-3,    1.2
```
- 参数：渗透系数 k (m/s), 孔隙比 e
- SPECIFIC=1.0 表示流体密度比重

#### 各向异性渗透
```
*PERMEABILITY, TYPE=ANISO
1.0e-5, 1.0e-5, 1.0e-6
```
- kx, ky, kz（通常 kh >> kv）

#### 渗透系数参考值
| 土体类型 | k (m/s) | 特征 |
|---------|---------|------|
| 砾石 | 1e-2 ~ 1e-1 | 自由排水 |
| 粗砂 | 1e-4 ~ 1e-2 | 排水良好 |
| 细砂 | 1e-6 ~ 1e-4 | 半透水 |
| 粉土 | 1e-8 ~ 1e-6 | 弱透水 |
| 黏土 | 1e-11 ~ 1e-8 | 不透水 |

#### 孔隙比-渗透系数关系
```
*PERMEABILITY, SPECIFIC=1.0
1.0e-9, 0.6
5.0e-9, 0.8
2.0e-8, 1.0
1.0e-7, 1.2
```
- Abaqus 自动根据当前孔隙比插值渗透系数

### 3. 固结分析 | Consolidation Analysis

#### 基本设置
```
*STEP, NAME=Consolidation
*SOILS, CONSOLIDATION, END=PERIOD
0.01, 3.15e7, 1e-6, 3.15e6
```
- 初始增量、总时间（秒）、最小增量、最大增量
- END=PERIOD：按时间段控制
- END=SS：达到稳态后结束

#### 初始时间增量估算
$$\Delta t \geq \frac{\gamma_w}{6 E k} (\Delta h)^2$$
- Δh：最小单元尺寸
- E：弹性模量
- k：渗透系数
- γ_w：水的重度

#### 排水边界
```
** 排水面：孔压=0
*BOUNDARY
TOP_SURFACE, 8, 8, 0.
** 不排水面：不施加孔压约束（自然不排水）
```

#### 单面排水 vs 双面排水
- 单面排水：仅顶面设 u_p=0
- 双面排水：顶底面均设 u_p=0
- 固结时间比：t_单面 = 4 × t_双面

### 4. 稳态渗流 | Steady-State Seepage

#### 纯渗流分析
```
*STEP, NAME=SteadySeepage
*SOILS, STEADY STATE
1., 1., 1e-5, 1.
*BOUNDARY
UPSTREAM, 8, 8, 100.    ** 上游水头
DOWNSTREAM, 8, 8, 0.    ** 下游水头
*END STEP
```

#### 大坝渗流（自由面问题）
```
*SOILS, STEADY STATE
*BOUNDARY
UPSTREAM_FACE, 8, 8, 50.
*FLOW, TYPE=SEEPAGE
DAM_DOWNSTREAM, S, 1.0e-5
```
- SEEPAGE 允许自由面在下游面渗出

### 5. 瞬态渗流 | Transient Seepage

```
*STEP, NAME=TransientSeepage
*SOILS, CONSOLIDATION
0.01, 100., 1e-6, 10.
*BOUNDARY
WATER_LEVEL, 8, 8, 80.    ** 水位变化
*END STEP
```

### 6. 降水/抽水模拟 | Dewatering

#### 点井降水
```
*BOUNDARY
WELL_NODES, 8, 8, -20.    ** 强制孔压到目标值
```

#### 井点降水（流量控制）
```
*CFLOW
WELL_NODE, 8, -0.001      ** 流量 (m³/s)
```

### 7. 不排水分析 | Undrained Analysis

#### 有效应力法（耦合单元）
- 使用 CPE4P 等耦合单元
- 不设置排水边界
- Abaqus 自动跟踪超孔压

#### 总应力法（简化）
- 使用普通单元
- 不排水强度参数：c_u, φ_u = 0
- 不跟踪孔压

## Common Issues | 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 固结步开始就发散 | 初始增量太大 | 用公式估算 Δt_min |
| 孔压出现负值 | 抽水/降水设置不当 | 检查边界值和初始条件 |
| 渗流面不收敛 | 自由面位置振荡 | 减小增量，增加稳定化 |
| 固结不完成 | 时间不够 | t_90 ≈ T_v × H²/c_v |
| 饱和度异常 | 部分饱和参数缺失 | 检查 *SORPTION 和 *PERMEABILITY |

## Output Requests | 输出请求

```
*OUTPUT, FIELD
*NODE OUTPUT
POR,     ** 孔隙水压力
U,       ** 位移
*ELEMENT OUTPUT
S,       ** 有效应力
E,       ** 应变
VOIDR,   ** 孔隙比
SAT,     ** 饱和度
FLVEL,   ** 渗流速度
```

## Usage | 用法

### CLI
```bash
abaqusgpt ask "一维固结分析怎么设置" --domain geotechnical
abaqusgpt ask "大坝渗流分析步骤" --domain geotechnical
```

### Python API
```python
from abaqusgpt.skills.geotech_seepage import GeotechSeepageSkill

skill = GeotechSeepageSkill()
result = skill.execute({
    "query_type": "consolidation_setup",
    "drainage": "double",
    "soil_permeability": 1e-9
})
```
