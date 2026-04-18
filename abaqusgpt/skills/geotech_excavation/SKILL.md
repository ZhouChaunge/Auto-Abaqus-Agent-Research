---
name: geotech-excavation
version: 1.0.0
description: Excavation, tunneling, and staged construction simulation in Abaqus
description_cn: 开挖、隧道与分步施工模拟（Abaqus）
triggers:
  - "excavation"
  - "开挖"
  - "基坑"
  - "tunnel"
  - "隧道"
  - "施工"
  - "construction"
  - "model change"
  - "单元生死"
  - "填土"
  - "embankment"
  - "路堤"
  - "盾构"
  - "TBM"
  - "边坡"
  - "slope"
  - "支护"
  - "分步"
  - "staged"
priority: P0
dependencies:
  - "geotech-boundary"
  - "geotech-constitutive"
author: AbaqusGPT Team
tags:
  - geotechnical
  - excavation
  - tunnel
  - staged-construction
---

# Geotech Excavation | 岩土开挖与施工模拟

## Overview | 概述

Expert guidance on simulating excavation, tunneling, embankment construction, and other staged construction processes in Abaqus using MODEL CHANGE and multi-step techniques.

使用 MODEL CHANGE 和多步分析技术模拟开挖、隧道掘进、路堤填筑和其他分步施工过程的专家指导。

## Capabilities | 能力

### 1. MODEL CHANGE 单元生死 | Element Activation/Deactivation

#### 开挖（移除单元）
```
*STEP, NAME=Excavation-1
*STATIC
*MODEL CHANGE, REMOVE
EXCAVATION_LAYER_1
*END STEP
```

#### 填筑（添加单元）
```
*STEP, NAME=Fill-1
*STATIC
*MODEL CHANGE, ADD
FILL_LAYER_1
*DLOAD
FILL_LAYER_1, GRAV, 9.81, 0., -1., 0.
*END STEP
```

#### 重要注意事项
- 被移除的单元：应力释放，等效节点力自动卸载
- 被添加的单元：初始无应力状态，需手动施加自重
- 不能在同一步中同时 ADD 和 REMOVE（分开步骤）
- 被移除单元的节点如被其他活跃单元共享，仍保持活跃

### 2. 基坑开挖 | Foundation Pit Excavation

#### 典型分析步序列
```
Step 1: GEOSTATIC    → 地应力平衡
Step 2: 安装围护结构   → MODEL CHANGE ADD (墙/桩)
Step 3: 第一层开挖    → MODEL CHANGE REMOVE + 安装支撑
Step 4: 第二层开挖    → MODEL CHANGE REMOVE + 安装支撑
Step 5: ...          → 逐层开挖
Step N: 底板施工      → MODEL CHANGE ADD + 拆撑
```

#### 围护结构建模
```
** 地下连续墙 - 实体单元
*ELEMENT, TYPE=CPE4, ELSET=DIAPHRAGM_WALL
...
*MATERIAL, NAME=CONCRETE
*ELASTIC
30000000., 0.2

** 钢支撑 - 梁/桁架单元
*ELEMENT, TYPE=B21, ELSET=STRUT
...
*BEAM SECTION, ELSET=STRUT, MATERIAL=STEEL, SECTION=PIPE
0.3, 0.016

** 也可用弹簧简化
*SPRING, ELSET=STRUT_SPRING
1
*SPRING, ELSET=STRUT_SPRING
500000.
```

#### 开挖面卸载（应力释放系数法）
```
** Step 3a: 应力释放 40%
*STEP
*STATIC
*MODEL CHANGE, REMOVE
EXCAVATION_1
*BOUNDARY
EXCAVATION_FACE, 1, 2    ** 临时约束开挖面
*END STEP

** Step 3b: 安装支撑 + 释放剩余 60%
*STEP
*STATIC
*MODEL CHANGE, ADD
SUPPORT_1
** 移除开挖面临时约束
*BOUNDARY, OP=NEW
...
*END STEP
```

### 3. 隧道开挖 | Tunnel Excavation

#### 全断面法
```
Step 1: Geostatic
Step 2: 开挖（移除核心土）
Step 3: 安装衬砌
```

#### 台阶法
```
Step 1: Geostatic
Step 2: 上台阶开挖 + 初期支护
Step 3: 下台阶开挖 + 初期支护
Step 4: 二衬施工
```

#### 盾构 TBM 模拟
```
** 分环推进
*STEP, NAME=Ring-1
*STATIC
*MODEL CHANGE, REMOVE
TUNNEL_RING_1
*MODEL CHANGE, ADD         ** 分开步骤
LINING_RING_1
** 盾尾注浆压力
*DSLOAD
LINING_RING_1_OUTER, P, 200.
*END STEP
```

#### 收敛-约束法（隧道特有）
- 应力释放比 λ 控制开挖面空间效应
```
** 预收敛步：释放 λ 比例的地层应力
** 衬砌安装步：安装衬砌，释放 (1-λ) 的剩余应力
```
- λ 的取值取决于围岩等级和开挖方法（通常 0.3-0.7）

#### 地层损失法（简化）
```
** 在隧道周围施加收缩位移模拟地层损失
*BOUNDARY
TUNNEL_BOUNDARY, 1, 1, -0.005   ** 径向收缩
```
- 地层损失率：软土 1-3%，硬土/岩石 0.5-1%

### 4. 路堤/填土 | Embankment Construction

#### 分层填筑
```
*STEP, NAME=Fill-Layer-1
*SOILS, CONSOLIDATION
1., 86400., 0.1, 43200.
*MODEL CHANGE, ADD
FILL_1
*DLOAD
FILL_1, GRAV, 9.81, 0., -1., 0.
*END STEP

*STEP, NAME=Consolidation-1
*SOILS, CONSOLIDATION
1., 2592000., 0.1, 864000.
** 等待固结 30 天
*END STEP

*STEP, NAME=Fill-Layer-2
*SOILS, CONSOLIDATION
1., 86400., 0.1, 43200.
*MODEL CHANGE, ADD
FILL_2
*DLOAD
FILL_2, GRAV, 9.81, 0., -1., 0.
*END STEP
```

#### 预压法
```
** 填筑预压荷载
*STEP, NAME=Preload
*MODEL CHANGE, ADD
PRELOAD_FILL
*DLOAD
PRELOAD_FILL, GRAV, 9.81, 0., -1., 0.
*END STEP

** 固结等待
*STEP, NAME=Consolidation
*SOILS, CONSOLIDATION
1., 15768000., 0.1, 2592000.
*END STEP

** 卸载（移除预压填土）
*STEP, NAME=Remove-Preload
*MODEL CHANGE, REMOVE
PRELOAD_FILL
*END STEP
```

### 5. 边坡分析 | Slope Analysis

#### 强度折减法 (SRM)
- 逐步降低 c 和 tan(φ) 直到不收敛
- 安全系数 FoS = 原始参数 / 折减后参数
```
** 在 Python 脚本中循环调用，逐步降低材料参数
** 判据：当不再收敛时的折减系数即为 FoS
```

#### 边坡开挖
```
Step 1: Geostatic
Step 2: 分级开挖（多步 MODEL CHANGE REMOVE）
Step 3: 支护安装
```

### 6. 地基处理 | Ground Improvement

#### 桩基模拟
```
** 桩体 - 嵌入式
*EMBEDDED ELEMENT, HOST ELSET=SOIL
PILE_ELEMENTS

** 或使用完整接触建模（见 geotech-interface skill）
```

#### 水泥土搅拌桩
- 改变被加固区域的材料参数
```
*SOLID SECTION, ELSET=IMPROVED_SOIL, MATERIAL=CEMENT_SOIL
*MATERIAL, NAME=CEMENT_SOIL
*ELASTIC
500000., 0.25
*MOHR COULOMB
35., 5.
```

## Common Issues | 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 开挖后应力突变 | 一次移除太多 | 分多步逐层开挖 |
| 移除单元后不平衡 | 卸载路径不连续 | 使用应力释放系数法 |
| 添加单元后大位移 | 新单元无初始应力 | 添加后加 GEOSTATIC 子步 |
| 隧道开挖不收敛 | 围岩太弱 | 减小一次开挖长度，增加支护 |
| 路堤填筑沉降异常 | 孔压没有消散 | 检查排水边界和渗透系数 |
| 边坡 SRM 过早发散 | 增量太大 | 减小折减步长 |

## Usage | 用法

### CLI
```bash
abaqusgpt ask "三层基坑开挖分析步怎么设" --domain geotechnical
abaqusgpt ask "盾构隧道模拟方法" --domain geotechnical
```

### Python API
```python
from abaqusgpt.skills.geotech_excavation import GeotechExcavationSkill

skill = GeotechExcavationSkill()
result = skill.execute({
    "query_type": "excavation_setup",
    "problem_type": "foundation_pit",
    "depth": 15.0,
    "layers": 4,
    "support_type": "diaphragm_wall_with_struts"
})
```
