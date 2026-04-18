---
name: geotech-interface
version: 1.0.0
description: Soil-structure interaction, contact, and interface modeling in Abaqus
description_cn: 土-结构相互作用、接触与界面建模（Abaqus）
triggers:
  - "interface"
  - "界面"
  - "contact"
  - "接触"
  - "土结构"
  - "soil-structure"
  - "摩擦"
  - "friction"
  - "桩土"
  - "pile"
  - "衬砌"
  - "lining"
  - "支护"
  - "retaining"
  - "锚杆"
  - "anchor"
priority: P1
dependencies: []
author: AbaqusGPT Team
tags:
  - geotechnical
  - contact
  - interface
  - soil-structure-interaction
---

# Geotech Interface | 岩土接触与界面

## Overview | 概述

Expert guidance on modeling soil-structure interaction, contact pairs, and interface behavior in geotechnical Abaqus simulations. Covers pile-soil, retaining wall-soil, tunnel lining-ground, and anchor-grout interfaces.

岩土 Abaqus 仿真中土-结构相互作用、接触对和界面行为的建模指导。覆盖桩-土、挡墙-土、隧道衬砌-围岩、锚杆-灌浆体界面。

## Capabilities | 能力

### 1. 接触算法选择 | Contact Algorithm Selection

#### Surface-to-Surface（推荐）
```
*CONTACT PAIR, INTERACTION=SOIL_STRUCT, TYPE=SURFACE TO SURFACE
STRUCTURE_SURFACE, SOIL_SURFACE
```
- **优点**：应力传递更平滑，减少穿透
- **主面选择**：刚度大的为主面（通常是结构面）

#### Node-to-Surface
```
*CONTACT PAIR, INTERACTION=SOIL_STRUCT, TYPE=NODE TO SURFACE
SOIL_SURFACE, STRUCTURE_SURFACE
```
- 适用于细网格对粗网格的情况

#### General Contact（3D 复杂模型）
```
*CONTACT
*CONTACT INCLUSIONS, ALL EXTERIOR
*CONTACT PROPERTY ASSIGNMENT
, , SOIL_STRUCT_PROP
```

### 2. 接触属性 | Contact Properties

#### 法向行为（硬接触）
```
*SURFACE INTERACTION, NAME=SOIL_STRUCT
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
```

#### 法向行为（软接触）
```
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=EXPONENTIAL
10., 0.001
```
- 适用于回填松散土的接触

#### 切向行为（库仑摩擦）
```
*FRICTION
0.4
```
- 摩擦系数参考值：
  | 界面类型 | μ 范围 | 推荐值 |
  |---------|--------|--------|
  | 混凝土-砂土 | 0.40-0.60 | tan(2φ/3) |
  | 混凝土-黏土 | 0.25-0.40 | tan(φ/2) |
  | 钢-砂土 | 0.30-0.50 | tan(φ/2) |
  | 钢-黏土 | 0.20-0.35 | tan(φ/3) |
  | 土工膜-土 | 0.15-0.30 | 按试验 |

#### 切向行为（有限滑移 + 弹性滑移）
```
*FRICTION, ELASTIC SLIP=0.001
0.4
```
- ELASTIC SLIP：接触面在滑动前允许的弹性位移

#### 黏聚力接触（Cohesive Contact）
```
*COHESIVE BEHAVIOR
1e6, 1e6, 1e6
*DAMAGE INITIATION, CRITERION=QUADS
100., 50., 50.
*DAMAGE EVOLUTION, TYPE=ENERGY
0.1, 0.05, 0.05
```
- 适用于灌浆-岩石界面、锚固段

### 3. 典型工程界面 | Typical Engineering Interfaces

#### 桩-土界面
```
** 桩侧摩擦
*SURFACE INTERACTION, NAME=PILE_SHAFT
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.4
** 桩端承压
*SURFACE INTERACTION, NAME=PILE_TIP
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.5
```
- 桩侧可用 Cohesive 模拟极限侧摩阻力
- 需分开定义桩侧和桩端接触

#### 挡墙-土界面
```
*SURFACE INTERACTION, NAME=WALL_SOIL
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.35
```
- 墙背需允许分离（拉力截断）

#### 隧道衬砌-围岩
```
*SURFACE INTERACTION, NAME=LINING_ROCK
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.40
*GAP
** 注浆层可用 gap 单元模拟
```

#### 锚杆建模
- **嵌入式（简化）**：
```
*EMBEDDED ELEMENT, HOST ELSET=SOIL
ANCHOR_ELEMENTS
```
- **完整接触**：锚杆-灌浆体-土三层接触
- **弹簧等效**：
```
*SPRING, ELSET=ANCHOR_SPRING
1
*SPRING, ELSET=ANCHOR_SPRING
200000.
```

#### 土工格栅/土工膜
```
*SURFACE INTERACTION, NAME=GEOGRID_SOIL
*SURFACE BEHAVIOR, PRESSURE-OVERCLOSURE=HARD
*FRICTION
0.35
```
- 格栅自身用 membrane 或 truss 单元
- 上下两面分别与土建立接触

### 4. 接触稳定化 | Contact Stabilization

#### 初始接触困难
```
*CONTACT CONTROLS, STABILIZE=0.001
```
- 在 Geostatic 步可使用稳定化，后续步逐渐移除

#### 接触调整（过穿透修复）
```
*CONTACT PAIR, ADJUST=0.001
```

### 5. Tie 约束 | Tie Constraints

#### 完全绑定（无相对滑移）
```
*TIE, NAME=SOIL_CONCRETE_TIE
CONCRETE_SURFACE, SOIL_SURFACE
```
- 适用于固结良好的界面（如灌注桩与周围土体良好黏结时的简化）
- 不需要接触分析，计算效率高

## Common Issues | 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 接触不收敛 | 初始间隙/穿透过大 | 使用 ADJUST，检查网格对齐 |
| 应力震荡 | 主从面选反了 | 刚性大的面做主面 |
| 接触面穿透 | 罚刚度不够 | 增大 penalty stiffness |
| 大变形下接触丢失 | 有限滑移不够 | 改用 FINITE SLIDING |
| 摩擦力不对 | 法向压力不正确 | 检查地应力平衡是否完成 |

## Usage | 用法

### CLI
```bash
abaqusgpt ask "桩土接触怎么设置" --domain geotechnical
abaqusgpt ask "挡墙接触面摩擦系数取多少" --domain geotechnical
```

### Python API
```python
from abaqusgpt.skills.geotech_interface import GeotechInterfaceSkill

skill = GeotechInterfaceSkill()
result = skill.execute({
    "query_type": "contact_setup",
    "interface_type": "pile_soil",
    "soil_type": "sand"
})
```
