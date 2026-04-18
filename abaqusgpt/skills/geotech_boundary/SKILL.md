---
name: geotech-boundary
version: 1.0.0
description: Geotechnical boundary conditions, initial conditions, and loading for Abaqus
description_cn: 岩土边界条件、初始条件与荷载设置（Abaqus）
triggers:
  - "boundary"
  - "边界"
  - "初始条件"
  - "initial conditions"
  - "geostatic"
  - "地应力"
  - "自重"
  - "gravity"
  - "荷载"
  - "load"
  - "水压"
  - "pore pressure"
  - "孔压"
  - "位移边界"
  - "约束"
priority: P0
dependencies: []
author: AbaqusGPT Team
tags:
  - geotechnical
  - boundary
  - initial-conditions
  - loading
---

# Geotech Boundary | 岩土边界条件

## Overview | 概述

Expert guidance on setting up boundary conditions, initial conditions, and loading sequences for geotechnical Abaqus simulations. Covers geostatic stress initialization, groundwater conditions, staged construction loading, and infinite boundaries.

岩土 Abaqus 仿真中的边界条件、初始条件和加载序列设置指导。覆盖地应力初始化、地下水条件、分步施工加载和无限边界。

## Capabilities | 能力

### 1. 初始地应力 | Initial Geostatic Stress

#### Geostatic 步骤法（推荐）
```
*STEP, NAME=Geostatic
*GEOSTATIC
*DLOAD
ALL_SOIL, GRAV, 9.81, 0., -1., 0.
*END STEP
```

#### 直接指定初始应力
```
*INITIAL CONDITIONS, TYPE=STRESS, GEOSTATIC
SOIL_SET, -100., 10., -30., 0., 0.8
```
- 参数含义：σ_v(底), z(底), σ_v(顶), z(顶), K₀_x, K₀_y（默认=K₀_x）
- 自动根据深度线性插值竖向应力
- 水平应力 = K₀ × σ_v'

#### K₀ 值参考
| 土体类型 | K₀ 范围 | 推荐值 |
|---------|---------|--------|
| 正常固结砂土 | 0.35-0.50 | 1 - sin φ |
| 正常固结黏土 | 0.50-0.70 | 1 - sin φ |
| 超固结黏土 | 0.50-2.50 | K₀_nc × OCR^(sin φ) |
| 软岩 | 0.30-0.50 | 0.40 |
| 硬岩 | 0.10-0.50 | 按实测 |

#### 地应力平衡检查
```
*STEP, NAME=VerifyGeostatic
*GEOSTATIC
*OUTPUT, FIELD
*ELEMENT OUTPUT
S, E, COORD
*NODE OUTPUT
U, RF
*END STEP
```
- **关键判据**：位移 < 1e-6 × 模型尺寸，说明平衡良好
- 若位移过大，检查 K₀ 与弹性参数是否匹配：K₀ = ν / (1-ν) 时完全弹性平衡

### 2. 地下水与孔隙水压 | Groundwater & Pore Pressure

#### 静水压力初始条件
```
*INITIAL CONDITIONS, TYPE=PORE PRESSURE
SOIL_SET, 0., 10., 100., 0.
```
- 参数：孔压(位置1), z(位置1), 孔压(位置2), z(位置2)
- 从水位线处孔压=0，向下线性增加

#### 孔压边界条件
```
*BOUNDARY
BOTTOM_NODES, 8, 8, 100.
SURFACE_NODES, 8, 8, 0.
```
- 自由度 8 = 孔隙水压力
- 排水面孔压=0，不排水面不施加约束

#### 降水/抽水
```
*BOUNDARY
WELL_NODES, 8, 8, -50.
```
- 负值表示抽水引起的孔压降低

### 3. 位移边界条件 | Displacement Boundaries

#### 标准岩土边界
```
*BOUNDARY
BOTTOM, 1, 3, 0.       ** 底面固定 (x,y,z)
LEFT, 1, 1, 0.          ** 左侧法向约束 (x)
RIGHT, 1, 1, 0.         ** 右侧法向约束 (x)
FRONT, 2, 2, 0.         ** 前面法向约束 (y) - 3D
BACK, 2, 2, 0.          ** 后面法向约束 (y) - 3D
** 顶面自由（地表）
```

#### 对称边界
```
*BOUNDARY
SYMM_PLANE, YSYMM       ** y=0 对称面：u2=ur1=ur3=0
```

#### 无限元边界（远场）
- 使用 CIN3D8 (3D) 或 CINPE4 (平面应变) 无限元
- 在模型边界外围一圈无限元
```
*ELEMENT, TYPE=CIN3D8, ELSET=INFINITE
...
```
- 无限元极点朝外，最内侧节点与有限元共节点

### 4. 荷载类型 | Load Types

#### 自重（重力）
```
*DLOAD
ALL_ELEMENTS, GRAV, 9.81, 0., -1., 0.
```
- 方向向量 (0, -1, 0) 表示 y 轴负方向（根据建模方向调整）

#### 均布面荷载
```
*DSLOAD
SURFACE_TOP, P, 100.    ** 均布压力 100 kPa
```

#### 线荷载（2D 平面应变）
```
*CLOAD
NODE_SET, 2, -50.       ** 竖向集中力
```

#### 分步施工加载
```
*STEP, NAME=Layer1
*STATIC
*MODEL CHANGE, ADD
FILL_LAYER1
*DLOAD
FILL_LAYER1, GRAV, 9.81, 0., -1., 0.
*END STEP

*STEP, NAME=Layer2
*STATIC
*MODEL CHANGE, ADD
FILL_LAYER2
*DLOAD
FILL_LAYER2, GRAV, 9.81, 0., -1., 0.
*END STEP
```

#### 地震荷载
```
*STEP, NAME=Earthquake
*DYNAMIC, IMPLICIT
0.01, 10., 1e-6, 0.05
*BOUNDARY, TYPE=ACCELERATION
BASE_NODES, 1, 1, 1.0
*AMPLITUDE, NAME=EQ_MOTION, INPUT=earthquake.txt
*BOUNDARY, AMPLITUDE=EQ_MOTION
BASE_NODES, 1, 1, 1.0
*END STEP
```

### 5. 分析步设置 | Step Configuration

#### 岩土典型分析步序列
```
Step 1: GEOSTATIC（地应力平衡）
Step 2: 开挖/施工（MODEL CHANGE）
Step 3: 固结（SOILS, CONSOLIDATION）
Step 4: 长期运营/地震（视需求）
```

#### 固结分析步
```
*STEP, NAME=Consolidation
*SOILS, CONSOLIDATION, END=PERIOD
0.001, 100., 1e-8, 10.
*END STEP
```
- 初始时间增量、总时间、最小增量、最大增量

#### 大变形设置
```
*STEP, NLGEOM=YES
```
- 深基坑、边坡大滑动必须开启

## Common Issues | 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 地应力不平衡 | K₀ 与弹性参数不匹配 | K₀ = ν/(1-ν) 或使用 *GEOSTATIC |
| 孔压初始不对 | 水位线设置错误 | 检查 z 坐标方向和参考水位 |
| 无限元不起作用 | 极点方向反了 | 检查节点编号顺序 |
| 分步施工应力跳变 | 新加单元无初始应力 | 在 MODEL CHANGE 后加 *GEOSTATIC 子步 |
| 固结步发散 | 初始增量太大 | 减小初始增量至 0.001 或更小 |

## Boundary Size Guidelines | 边界尺寸指南

| 问题类型 | 水平范围 | 竖向深度 |
|---------|---------|---------|
| 浅基础 | ≥ 5B (B=基础宽) | ≥ 3B |
| 深基坑 | ≥ 3~5 倍开挖深度 | ≥ 2 倍开挖深度 |
| 隧道 | ≥ 3~5D (D=洞径) | 洞底下 ≥ 3D |
| 边坡 | 坡脚外 ≥ 2H (H=坡高) | ≥ 1.5H |
| 桩基 | ≥ 20D (D=桩径) | 桩底下 ≥ 5D |

## Usage | 用法

### CLI
```bash
abaqusgpt ask "深基坑开挖边界条件怎么设置" --domain geotechnical
abaqusgpt ask "如何做地应力平衡" --domain geotechnical
```

### Python API
```python
from abaqusgpt.skills.geotech_boundary import GeotechBoundarySkill

skill = GeotechBoundarySkill()
result = skill.execute({
    "query_type": "boundary_setup",
    "problem_type": "excavation",
    "dimensions": "3D"
})
```
