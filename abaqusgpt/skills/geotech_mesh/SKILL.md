---
name: geotech-mesh
version: 1.0.0
description: Geotechnical-specific meshing strategies and element selection for Abaqus
description_cn: 岩土专用网格策略与单元选择（Abaqus）
triggers:
  - "geotech mesh"
  - "岩土网格"
  - "土体网格"
  - "地层网格"
  - "CPE"
  - "C3D"
  - "CAX"
  - "网格加密"
  - "映射网格"
  - "自由网格"
  - "单元类型"
  - "缩减积分"
  - "沙漏"
  - "hourglass"
  - "锁定"
  - "locking"
priority: P1
dependencies: []
author: AbaqusGPT Team
tags:
  - geotechnical
  - mesh
  - element-selection
---

# Geotech Mesh | 岩土网格策略

## Overview | 概述

Geotechnical-specific meshing strategies, element type selection, and mesh quality guidelines for Abaqus. Covers element formulation pitfalls (locking, hourglassing), mesh density recommendations for different problem types, and transition meshing techniques.

岩土专用网格策略、单元类型选择和网格质量准则。覆盖单元公式陷阱（锁定、沙漏）、不同问题类型的网格密度建议和过渡网格技术。

## Capabilities | 能力

### 1. 岩土常用单元 | Common Geotechnical Elements

#### 2D 平面应变
| 单元 | 节点 | 积分 | 孔压 | 适用场景 |
|------|------|------|------|---------|
| CPE4 | 4 | 全积分 | 否 | 不推荐（剪切锁定） |
| CPE4R | 4 | 缩减积分 | 否 | 排水分析（注意沙漏） |
| CPE4H | 4 | 全积分+混合 | 否 | 不可压缩材料 |
| **CPE4P** | 4 | 全积分 | **是** | **耦合固结（推荐）** |
| CPE4PH | 4 | 全积分+混合 | 是 | 不可压缩+固结 |
| CPE8 | 8 | 全积分 | 否 | 精确排水分析 |
| CPE8R | 8 | 缩减积分 | 否 | 高精度排水 |
| **CPE8P** | 8 | 全积分 | **是** | **高精度固结** |
| CPE8RP | 8 | 缩减积分 | 是 | 大变形固结 |

#### 3D 实体
| 单元 | 节点 | 积分 | 孔压 | 适用场景 |
|------|------|------|------|---------|
| C3D8 | 8 | 全积分 | 否 | 不推荐（锁定严重） |
| **C3D8R** | 8 | 缩减积分 | 否 | **3D 排水分析** |
| C3D8RH | 8 | 缩减+混合 | 否 | 不可压缩 3D |
| **C3D8P** | 8 | 全积分 | **是** | **3D 固结** |
| C3D8PH | 8 | 全积分+混合 | 是 | 不可压缩+固结 3D |
| C3D20 | 20 | 全积分 | 否 | 高精度（计算贵） |
| **C3D20RP** | 20 | 缩减积分 | **是** | **精确 3D 固结** |

#### 轴对称
| 单元 | 适用场景 |
|------|---------|
| CAX4 / CAX4R | 桩基轴对称排水分析 |
| **CAX4P** | **桩基轴对称固结** |
| CAX8R / CAX8RP | 高精度轴对称 |

#### 特殊单元
| 单元 | 用途 |
|------|------|
| CIN3D8 / CINPE4 | 无限元（远场边界） |
| COH2D4 / COH3D8 | 内聚力单元（裂缝/节理） |
| SFM3D4 / SFM3D4R | 表面单元（荷载施加） |
| CONN2D2 / CONN3D2 | 连接单元（弹簧/阻尼器） |
| T2D2 / T3D2 | 桁架单元（锚杆/土钉） |
| B21 / B31 | 梁单元（支撑/桩简化） |

### 2. 单元选择决策树 | Element Selection Decision Tree

```
分析类型判断
├── 纯力学分析（排水）
│   ├── 2D 平面应变
│   │   ├── 线弹性/小变形 → CPE8R（推荐）
│   │   ├── 大变形/塑性 → CPE4R + hourglass 控制
│   │   └── 不可压缩（ν≈0.5）→ CPE4H / CPE8RH
│   ├── 3D
│   │   ├── 常规 → C3D8R（推荐）
│   │   ├── 应力集中区 → C3D20R
│   │   └── 不可压缩 → C3D8RH
│   └── 轴对称 → CAX4R / CAX8R
├── 耦合固结分析（孔压）
│   ├── 2D → CPE4P（常规）/ CPE8RP（精确）
│   ├── 3D → C3D8P（常规）/ C3D20RP（精确）
│   └── 轴对称 → CAX4P / CAX8RP
└── 动力分析
    ├── 2D → CPE4R（显式）
    └── 3D → C3D8R（显式）
```

### 3. 常见单元问题 | Common Element Issues

#### 剪切锁定 (Shear Locking)
- **症状**：位移偏小、刚度偏大
- **原因**：全积分线性单元（CPE4, C3D8）在弯曲/剪切时假剪切应变
- **解决**：
  - 使用缩减积分（CPE4R, C3D8R）
  - 使用二次单元（CPE8, C3D20）
  - 使用不兼容模式（CPE4I, C3D8I）

#### 体积锁定 (Volumetric Locking)
- **症状**：接近不可压缩时（ν→0.5）应力振荡
- **原因**：体积约束过多
- **解决**：
  - 使用混合公式（H 后缀：CPE4H, C3D8PH）
  - 使用缩减积分

#### 沙漏效应 (Hourglassing)
- **症状**：单元出现锯齿状变形
- **原因**：缩减积分单元的零能量模式
- **解决**：
```
*SECTION CONTROLS, NAME=HOURGLASS_CTRL, HOURGLASS=ENHANCED
*SOLID SECTION, ELSET=SOIL, MATERIAL=SOIL, CONTROLS=HOURGLASS_CTRL
```
- 检查：沙漏能量 < 总内能的 5%

### 4. 网格密度指南 | Mesh Density Guidelines

| 问题类型 | 关键区域 | 推荐尺寸 |
|---------|---------|---------|
| 基坑开挖 | 墙体周围 | 0.5~1.0m |
| 基坑开挖 | 远场 | 3~5m |
| 隧道 | 洞周 1D 范围 | 0.2~0.5m |
| 隧道 | 远场 | 2~5m |
| 桩基 | 桩周 3D 范围 | 0.1~0.3D (D=桩径) |
| 浅基础 | 基底 2B 范围 | 0.2~0.5m |
| 边坡 | 潜在滑面 | 0.5~1.0m |
| 渗流 | 水头梯度大处 | 细化 |

### 5. 过渡网格技术 | Mesh Transition

#### Tie 约束过渡
```
*TIE, NAME=MESH_TRANSITION
FINE_SURFACE, COARSE_SURFACE
```
- 粗细网格不需要节点对齐
- 简单有效，推荐使用

#### 梯度网格（Bias/Seeding）
- 在 CAE 中使用 Edge Seed 控制网格密度渐变
- 渐变比不超过 1:3（相邻单元尺寸比）

#### 多实例（Instance）网格
- 不同区域建不同 Part → 不同网格密度
- 用 Tie 连接

### 6. 网格质量检查 | Mesh Quality Check

| 指标 | 可接受范围 | 理想值 |
|------|-----------|--------|
| 长宽比 (Aspect Ratio) | < 5:1 | < 3:1 |
| 内角 (Quad) | 45°~135° | 90° |
| 雅可比 (Jacobian) | > 0.2 | > 0.5 |
| 翘曲 (Warpage) | < 15° | < 5° |

## Common Issues | 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 固结分析收敛差 | 网格太粗或 Δt 不匹配 | Δt ≥ γ_w/(6Ek) × Δh² |
| 应力结果锯齿状 | 缩减积分沙漏 | 加 ENHANCED hourglass 控制 |
| 不排水分析位移异常 | 体积锁定 | 用混合公式（H 后缀） |
| 应力集中处不准 | 网格太粗 | 局部加密 |
| 接触面穿透 | 从面网格太粗 | 从面网格 ≤ 主面的 2 倍 |

## Usage | 用法

### CLI
```bash
abaqusgpt ask "基坑开挖用什么单元" --domain geotechnical
abaqusgpt mesh recommend --analysis-type consolidation --geometry solid
```

### Python API
```python
from abaqusgpt.skills.geotech_mesh import GeotechMeshSkill

skill = GeotechMeshSkill()
result = skill.execute({
    "query_type": "element_recommendation",
    "analysis_type": "coupled_consolidation",
    "problem_type": "tunnel",
    "dimensions": "3D"
})
```
