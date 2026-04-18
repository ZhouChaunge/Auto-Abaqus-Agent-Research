---
name: geotech-constitutive
version: 1.0.0
description: Geotechnical constitutive model selection and parameter calibration for Abaqus
description_cn: 岩土本构模型选择与参数标定（Abaqus）
triggers:
  - "constitutive"
  - "本构"
  - "material"
  - "材料"
  - "mohr-coulomb"
  - "drucker-prager"
  - "cam-clay"
  - "摩尔库仑"
  - "德鲁克普拉格"
  - "剑桥模型"
  - "损伤"
  - "蠕变"
  - "creep"
  - "黏弹"
  - "viscoelastic"
  - "超弹"
  - "hyperelastic"
priority: P0
dependencies: []
author: AbaqusGPT Team
tags:
  - geotechnical
  - constitutive
  - material
  - calibration
---

# Geotech Constitutive | 岩土本构模型

## Overview | 概述

Expert guidance on selecting, configuring, and calibrating constitutive models for geotechnical materials in Abaqus. Covers soils, rocks, soft clays, sands, and engineered fills.

岩土材料本构模型的选择、配置和参数标定专家指导。覆盖土、岩石、软黏土、砂土和工程填料。

## Capabilities | 能力

### 1. 弹塑性模型 | Elastoplastic Models

#### Mohr-Coulomb 模型
- **适用范围**：一般土体的稳定性分析、边坡、基坑
- **关键参数**：内摩擦角 φ、黏聚力 c、膨胀角 ψ
- **Abaqus 关键字**：
```
*MATERIAL, NAME=SOIL_MC
*ELASTIC
50000., 0.3
*MOHR COULOMB
30., 0.
*MOHR COULOMB HARDENING
0., 0.0
100., 0.05
200., 0.10
```
- **注意事项**：
  - Abaqus 中 Mohr-Coulomb 在尖角处可能导致收敛困难
  - 建议设置膨胀角 ψ < φ（非关联流动法则）
  - 对于含水土体需区分有效应力参数和总应力参数

#### Drucker-Prager 模型
- **适用范围**：岩石、混凝土、密实砂土
- **关键参数**：摩擦角 β、流动应力比 K、膨胀角
- **Abaqus 关键字**：
```
*MATERIAL, NAME=SOIL_DP
*ELASTIC
80000., 0.25
*DRUCKER PRAGER
35., 1.0, 10.
*DRUCKER PRAGER HARDENING
200., 0.0
500., 0.02
800., 0.05
```
- **与 Mohr-Coulomb 的转换关系**：
  - 平面应变：tan β = (√3 · sin φ) / (cos θ_T + sin θ_T · sin φ / √3)
  - K = (3 - sin φ) / (3 + sin φ)

#### Extended Drucker-Prager (Cap 模型)
- **适用范围**：考虑体积压缩硬化的土体（如填土、粉土）
- **关键参数**：d、β、R (cap eccentricity)、初始屈服面位置
- **Abaqus 关键字**：
```
*DRUCKER PRAGER
35., 1.0, 0.
*DRUCKER PRAGER HARDENING
100., 0.0
300., 0.01
*CAP PLASTICITY
0.01, 0.5, 0.0, 0.02
*CAP HARDENING
0.02, 50.
0.04, 100.
0.06, 200.
```

### 2. 临界状态模型 | Critical State Models

#### Modified Cam-Clay
- **适用范围**：正常固结或轻微超固结饱和黏土
- **关键参数**：
  - λ (压缩指数 Cc / 2.303)
  - κ (回弹指数 Cs / 2.303)
  - M (临界状态线斜率 = 6sinφ / (3-sinφ))
  - e₁ (参考孔隙比)
  - 初始屈服应力 p₀'
- **Abaqus 关键字**：
```
*MATERIAL, NAME=SOFT_CLAY
*ELASTIC
*POROUS ELASTIC, SHEAR=POISSON
0.026, 0.3
*CLAY PLASTICITY
1.0, 1.0
*CLAY HARDENING
200., 1.5
```
- **配套设置**：
```
*INITIAL CONDITIONS, TYPE=STRESS
SOIL_SET, -50., -100., -50., 0., 0., 0.
*INITIAL CONDITIONS, TYPE=RATIO
SOIL_SET, 0.8
```

#### Modified Drucker-Prager/Cap
- **适用范围**：需要同时考虑剪切破坏和体积压缩的粒状材料
- **与 Cam-Clay 的区别**：剪切屈服面使用 Drucker-Prager 而非 von Mises

### 3. 蠕变模型 | Creep Models

#### 时间硬化蠕变
- **适用范围**：软黏土的长期变形、软岩蠕变
- **Abaqus 关键字**：
```
*MATERIAL, NAME=CREEP_SOIL
*ELASTIC
30000., 0.35
*CREEP, LAW=TIME
1.e-10, 3.0, -0.5
```

#### 幂律蠕变
```
*CREEP, LAW=STRAIN
A, n, m
```

### 4. 损伤与软化模型 | Damage & Softening

#### 应变软化 Mohr-Coulomb
- **适用范围**：渐进破坏分析、边坡滑坡
- 通过 *MOHR COULOMB HARDENING 定义峰后软化
```
*MOHR COULOMB HARDENING
100., 0.0
120., 0.02
50., 0.05
30., 0.10
```
- **注意**：应变软化会导致网格依赖性，建议使用非局部正则化

#### 岩石损伤模型
- 可结合 *DAMAGE INITIATION 和 *DAMAGE EVOLUTION
- 对于脆性岩石可使用 Extended Drucker-Prager + 拉伸截断

### 5. 特殊材料模型 | Special Material Models

#### 膨胀土
- 使用 *MOISTURE SWELLING 定义湿胀变形
- 配合渗流分析
```
*MOISTURE SWELLING
0.0, 0.0
0.5, 0.03
1.0, 0.08
```

#### 冻土
- 使用温度相关的材料参数
```
*ELASTIC
*ELASTIC, TYPE=ISOTROPIC
30000., 0.3, -20.
15000., 0.35, -5.
5000.,  0.4,  0.
```

## Parameter Calibration Guide | 参数标定指南

### 从试验数据获取参数

| 试验类型 | 可标定的参数 |
|---------|-------------|
| 三轴压缩试验 (CU/CD) | φ, c, E, ν, M (Cam-Clay) |
| 固结试验 (oedometer) | λ, κ, Cc, Cs, cv, 预固结压力 |
| 直剪试验 | φ, c (大应变) |
| 无侧限压缩 | qu, Eu |
| 共振柱试验 | Gmax, D (动力参数) |

### Mohr-Coulomb 参数标定流程
1. 至少 3 组不同围压的三轴试验
2. 绘制 Mohr 圆 → 包络线 → φ 和 c
3. 弹性模量取 50% 强度对应的割线模量 E₅₀
4. 泊松比 ν：砂土 0.25-0.35，黏土 0.30-0.45

### Cam-Clay 参数标定流程
1. 固结试验 → e-ln(p') 曲线 → λ 和 κ
2. 三轴试验 → 临界状态线 → M
3. 初始屈服面 → 预固结压力 → p₀'

## Common Issues | 常见问题

### 收敛问题
| 问题 | 原因 | 解决方案 |
|------|------|---------|
| Mohr-Coulomb 不收敛 | 屈服面尖角处不光滑 | 改用 Drucker-Prager 或增大步数 |
| Cam-Clay 初始步不平衡 | 初始应力与 OCR 不匹配 | 检查 *INITIAL CONDITIONS 和 *GEOSTATIC |
| 大变形下收敛困难 | 材料参数在大应变下不合理 | 检查硬化曲线斜率，确保单调递增 |
| Cap 模型发散 | 初始帽面位置不合理 | 调整 *CAP HARDENING 初始值 |

### 模型选择决策树
```
土体类型判断
├── 黏土
│   ├── 正常固结/轻超固结 → Cam-Clay
│   ├── 强超固结 → Mohr-Coulomb / Drucker-Prager
│   └── 软黏土长期变形 → Cam-Clay + 蠕变
├── 砂土
│   ├── 静力分析 → Mohr-Coulomb / Drucker-Prager
│   ├── 动力/液化 → Drucker-Prager + 孔压模型
│   └── 填土压实 → Cap 模型
├── 岩石
│   ├── 脆性岩石 → Drucker-Prager + 拉伸截断
│   ├── 软岩 → Drucker-Prager + 蠕变
│   └── 节理岩体 → 等效连续体 + 弱化参数
└── 特殊土
    ├── 膨胀土 → Cam-Clay + *MOISTURE SWELLING
    └── 冻土 → 温度相关参数
```

## Usage | 用法

### CLI
```bash
# Get model recommendation
abaqusgpt ask "粉质黏土基坑开挖用什么本构模型" --domain geotechnical

# Parameter calibration help
abaqusgpt ask "如何从三轴试验标定Mohr-Coulomb参数" --domain geotechnical
```

### Python API
```python
from abaqusgpt.skills.geotech_constitutive import GeotechConstitutiveSkill

skill = GeotechConstitutiveSkill()
result = skill.execute({
    "query_type": "model_selection",
    "soil_type": "soft_clay",
    "analysis_type": "consolidation",
    "available_tests": ["triaxial_cu", "oedometer"]
})
```

## References | 参考文献

- Abaqus Analysis User's Manual: Section 23 (Geostatic stress state)
- Abaqus Theory Manual: Chapter 4.4 (Plasticity models)
- Potts, D.M. & Zdravkovic, L. (2001) Finite Element Analysis in Geotechnical Engineering
- Wood, D.M. (2004) Geotechnical Modelling
