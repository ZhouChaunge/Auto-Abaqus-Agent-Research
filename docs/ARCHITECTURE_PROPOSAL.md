# AbaqusGPT 架构改进建议

> 借鉴 ARIS (Auto Research In Sleep) 系统的成熟架构

## 一、当前架构

```
abaqusgpt/
├── agents/           # 独立的 Agent 模块
│   ├── converge_doctor.py
│   ├── domain_expert.py
│   ├── inp_generator.py
│   ├── mesh_advisor.py
│   └── qa_agent.py
├── knowledge/        # 知识库
│   ├── element_library.py
│   └── error_codes.py
├── parsers/          # 文件解析器
│   ├── inp_parser.py
│   ├── msg_parser.py
│   └── sta_parser.py
└── llm/              # LLM 客户端
    └── client.py
```

## 二、建议的架构改进

### 2.1 引入 Skill 系统

仿照 ARIS 的 skill 架构，每个功能模块有独立的 SKILL.md 描述文件：

```
abaqusgpt/
├── skills/
│   ├── shared-references/        # 共享规范
│   │   ├── element-catalog.md    # 单元库规范
│   │   ├── error-patterns.md     # 错误模式
│   │   ├── mesh-guidelines.md    # 网格规范
│   │   └── convergence-criteria.md
│   │
│   ├── converge-doctor/          # 收敛诊断 Skill
│   │   ├── SKILL.md              # 功能描述 + 工作流
│   │   └── templates/
│   │       └── diagnosis_report.md
│   │
│   ├── mesh-advisor/             # 网格建议 Skill
│   │   ├── SKILL.md
│   │   └── templates/
│   │       └── mesh_quality_report.md
│   │
│   ├── inp-generator/            # INP 生成 Skill
│   │   ├── SKILL.md
│   │   └── templates/
│   │       ├── static_analysis.inp
│   │       ├── dynamic_explicit.inp
│   │       └── thermal_analysis.inp
│   │
│   └── domain-expert/            # 领域专家 Skill
│       └── SKILL.md
```

### 2.2 Workflow 编排系统

定义完整的仿真工作流（类似 ARIS 的 research-pipeline）：

```
# Workflow 1: 建模到求解
inp-generator → mesh-advisor → run-analysis

# Workflow 2: 诊断修复循环
parse-results → converge-doctor → apply-fixes → re-run
                    ↑_______________|

# Workflow 3: 完整仿真生命周期
modeling → meshing → solving → diagnosis → optimization
```

### 2.3 状态持久化

仿照 ARIS 的 `REVIEW_STATE.json`，为长时间任务保存状态：

```json
// abaqusgpt-state.json
{
  "workflow": "convergence-debug",
  "stage": "iteration_3",
  "job_name": "beam_analysis",
  "last_increment": 45,
  "last_error": "CONVERGENCE_FAILED",
  "applied_fixes": [
    {"type": "time_increment", "old": 0.1, "new": 0.01},
    {"type": "contact_damping", "value": 0.0001}
  ],
  "pending_trials": [
    {"type": "stabilization", "value": 0.001}
  ],
  "timestamp": "2026-04-18T14:30:00"
}
```

### 2.4 可配置常量系统

每个 Skill 定义默认常量，可被覆盖：

```python
# skills/converge-doctor/config.py
class ConvergeDoctorConfig:
    MAX_ITERATIONS = 5          # 最大诊断迭代次数
    TIME_INCREMENT_FACTOR = 0.5 # 时间步减小系数
    CONTACT_DAMPING_DEFAULT = 0.0001
    STABILIZATION_DEFAULT = 0.001
    HUMAN_CHECKPOINT = True     # 修复前确认
```

### 2.5 人机检查点

```python
# 诊断完成后，等待用户确认修复方案
async def diagnose_and_fix(job_path: str, auto_proceed: bool = False):
    diagnosis = await converge_doctor.diagnose(job_path)
    
    if not auto_proceed:
        # 🚦 检查点：展示诊断结果，等待确认
        print("📋 诊断完成，建议修复方案：")
        for i, fix in enumerate(diagnosis.fixes):
            print(f"  {i+1}. {fix.description}")
        
        if not await user_confirms("是否应用这些修复？"):
            return diagnosis
    
    # 应用修复
    await apply_fixes(diagnosis.fixes)
```

## 三、输出目录结构

仿照 ARIS 的分阶段输出目录：

```
project/
├── CLAUDE.md                     # 项目配置（参考 ARIS）
├── MANIFEST.md                   # 输出追踪清单
│
├── modeling-stage/               # 建模阶段
│   ├── model_spec.md
│   └── inp_files/
│
├── meshing-stage/                # 网格阶段
│   ├── MESH_REPORT.md
│   └── mesh_quality/
│
├── analysis-stage/               # 分析阶段
│   ├── job.inp
│   ├── job.msg
│   ├── job.sta
│   └── job.odb
│
└── diagnosis-stage/              # 诊断阶段
    ├── DIAGNOSIS_REPORT.md
    ├── DIAGNOSIS_REPORT_20260418_143022.md  # 时间戳版本
    └── fix_history.json
```

## 四、SKILL.md 模板

```markdown
---
name: converge-doctor
description: "诊断 Abaqus 收敛问题并建议修复方案。触发词：'收敛问题', 'convergence', '不收敛', 'debug analysis'"
argument-hint: [job-path-or-error-message]
allowed-tools: Read, Write, Edit, Grep, Glob
---

# Converge Doctor: 收敛问题诊断专家

诊断目标: **$ARGUMENTS**

## Constants

- MAX_ITERATIONS = 5
- HUMAN_CHECKPOINT = true
- AUTO_FIX = false

## Workflow

### Phase 1: 解析日志文件

1. 读取 .msg 和 .sta 文件
2. 提取错误代码和增量信息
3. 识别收敛失败模式

### Phase 2: 诊断分析

1. 匹配错误代码到知识库
2. 分析失败增量的特征
3. 生成诊断报告

### Phase 3: 建议修复方案

基于诊断结果，按优先级建议：
1. 时间步控制调整
2. 接触参数优化
3. 材料模型检查
4. 边界条件验证

### Phase 4: 人机检查点

🚦 展示诊断报告和修复方案，等待用户确认。
```

## 五、实施路线图

### Phase 1: 基础架构（1-2 周）
- [ ] 创建 skills 目录结构
- [ ] 迁移现有 agents 到 skill 格式
- [ ] 编写 SKILL.md 模板

### Phase 2: 状态管理（1 周）
- [ ] 实现状态持久化
- [ ] 添加断点恢复机制
- [ ] 添加人机检查点

### Phase 3: Workflow 编排（1-2 周）
- [ ] 定义仿真工作流
- [ ] 实现 workflow 执行引擎
- [ ] 添加进度追踪

### Phase 4: 知识库增强（持续）
- [ ] 扩充单元库
- [ ] 完善错误码数据库
- [ ] 添加最佳实践指南

## 六、与 ARIS 的对比

| 维度 | ARIS | AbaqusGPT |
|------|------|-----------|
| 核心领域 | 学术研究自动化 | 有限元仿真辅助 |
| Workflow 示例 | idea→review→paper | model→mesh→solve→debug |
| 外部模型 | Codex MCP (GPT) | LiteLLM (多模型) |
| 输出格式 | LaTeX 论文 | INP 文件 + 诊断报告 |
| 检查点 | 审稿分数判断 | 收敛判断 + 用户确认 |
