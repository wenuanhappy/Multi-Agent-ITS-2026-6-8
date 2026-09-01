# 架构对比文档：CrewAI 版 vs 原版

## 1. 系统概述

| 维度 | 原版架构 | CrewAI 重构版 |
|------|---------------------------------------|----------------------------|
| 框架 | 自研单体架构 | CrewAI 多智能体框架 |
| 核心文件 | `lesson_flow.py` (12,300行) | `flow/tutoring_flow.py` (814行) + 模块化组件 |
| Agent定义 | 内嵌在 `agent_persona.py` 的文本模板 | CrewAI Agent 类（role/goal/backstory） |
| 工具系统 | 直接函数调用 | CrewAI Tool 类（BaseTool + args_schema） |
| LLM调用 | MultiProvider.complete() 直接调用 | 通过 CrewAI Agent → Crew → Task 链路 |
| 编排方式 | if/elif 分支 + 状态变量 | CrewAI Flow 状态机 + 结构化 Pydantic 状态 |
| 端口 | 8200 | 8300 |

## 2. 架构映射

### 2.1 原版五 Agent → CrewAI 四 Agent + 三 Crew

| 原版 Agent | CrewAI Agent | 所属 Crew | 说明 |
|-----------|-------------|----------|------|
| 教师 Agent | `TeacherAgent` | TeachingCrew / FeynmanCrew | 苏格拉底式对话生成 |
| 约束 Agent（反剧透） | — | — | 重构为 `AntiSpoilerTool`，由教师 Agent 持有 |
| 诊断 Agent | `DiagnosticianAgent` | — | 重构为 `SymPyDiagnosisTool` + `LLMClassifierTool` |
| 助教 Agent | `TAAgent` | CorrectionCrew | 结构化数学纠错反馈 |
| 同伴 Agent | `PeerAgent` | FeynmanCrew | 费曼反问检验理解深度 |

**关键设计决策**：原版的"约束 Agent"和"诊断 Agent"在 CrewAI 版中被重构为 **Tool** 而非 Agent，因为它们的行为是确定性的（黑名单匹配、SymPy 符号验证），不需要 LLM 自主决策。这更符合 CrewAI 的设计理念：**Agent 负责需要推理的任务，Tool 负责确定性的能力**。

### 2.2 FSM 编排器 → CrewAI Flow

| 原版组件 | CrewAI 对应 |
|---------|------------|
| `LessonFlow` 类 | `TutoringFlow(Flow[LessonState])` |
| `LessonStage` 枚举 | `E312Stage` 枚举 |
| `self.stage` + 散落的 `self._e312_*` 属性 | `LessonState`（Pydantic BaseModel，结构化状态） |
| `_STAGE_DISPATCH` 字典 | `process_student_message()` 中的 handlers 字典 |
| `_llm_respond()` | `TeachingCrew.kickoff()` |
| `_maybe_enter_feynman_at_transition()` | `_try_enter_feynman()` |
| `_maybe_inject_ta_correction()` | `CorrectionCrew.generate_correction()` |
| `_resolve_phase_answer()` | 阶段 handler 中的关键词匹配 + `LLMClassifierTool` |

### 2.3 工具映射

| 原版函数 | CrewAI Tool |
|---------|------------|
| `anti_spoiler.scan_spoiler()` | `AntiSpoilerTool` |
| `derive_diagnostician.diagnose()` | `SymPyDiagnosisTool` |
| `llm_classifier.classify()` | `LLMClassifierTool` |
| `ConicKnowledgeGraph.retrieve()` | `KGRetrievalTool` |

## 3. 消融实验与 CrewAI 组件映射

原版通过 `MULTI_AGENT_MODE` 环境变量控制 off/A/B/C/D 五档消融。在 CrewAI 架构中，每档对应逐步激活不同层级的框架组件：

| 消融模式 | 激活的 CrewAI 组件 | 论文描述 |
|---------|------------------|---------|
| **off** | 仅 Flow 编排 + 基础 LLM 调用 | 基线：纯 FSM + 单 Agent |
| **A** | 同 off（前端 UI 区分三 Agent 头像） | UI 对照组 |
| **B** | Flow + TeacherAgent + **AntiSpoilerTool** | + 约束层 Tool |
| **C** | Flow + **TeachingCrew + FeynmanCrew + CorrectionCrew**（完整） | + 完整多 Crew 协作 |
| **D** | 同 C + **LLM 自主提议 Tool**（D-1 推进仲裁 / D-2 同伴触发） | + Agent 自主性 |

**论文建议表述**：「消融实验通过逐步激活 CrewAI 框架的不同层级组件（Tool → Crew → Agent 自主性）来评估各模块对教学效果的贡献。」

## 4. 目录结构

```
Multi-Agent-ITS/
├── config/settings.py          # 配置（LLM、端口、模式）
├── core/                       # 复用模块（纯逻辑，框架无关）
│   ├── anti_spoiler.py         # 反剧透黑名单
│   ├── feynman_loop.py         # 费曼循环状态机
│   ├── math_normalizer.py      # 数学输入归一化
│   ├── llm_classifier.py       # LLM 语义分类器
│   ├── llm_providers.py        # Claude + DeepSeek 双通道
│   ├── agent_persona.py        # Agent 人设文本
│   ├── example_diagnostician.py # 通用 SymPy 判等
│   ├── diagnostic.py           # 学生状态追踪
│   └── interaction_logger.py   # JSONL 日志
├── courses/                    # 课程配置
│   ├── example_canonicals_312.py    # 3.1.2 标准答案
│   └── example_diagnostician_312.py # 3.1.2 诊断器
├── agents/                     # CrewAI Agent 定义
│   ├── teacher.py              # 苏格拉底教师
│   ├── peer.py                 # 好奇同学
│   ├── ta.py                   # 数学助教
│   └── diagnostician.py        # 诊断分类器
├── tools/                      # CrewAI Tool 定义
│   ├── sympy_diagnosis.py      # SymPy 符号验证
│   ├── anti_spoiler_scan.py    # 反剧透扫描
│   ├── llm_classify.py         # 语义分类
│   └── kg_retrieval.py         # 知识图谱检索
├── crews/                      # CrewAI Crew 定义
│   ├── teaching_crew.py        # 主教学 Crew
│   ├── feynman_crew.py         # 费曼反问 Crew
│   └── correction_crew.py      # 纠错 Crew
├── flow/                       # CrewAI Flow（FSM 编排器）
│   ├── state.py                # LessonState 状态模型
│   └── tutoring_flow.py        # TutoringFlow 主编排
├── api/server.py               # FastAPI 服务端
├── frontend/interactive.html   # 教学前端（JSXGraph + KaTeX）
└── run.py                      # 入口
```

## 5. 技术优势

### 5.1 相比原版的改进

1. **状态管理规范化**：原版 12,300 行单体中散落的 `self._e312_*` 属性 → 统一的 `LessonState` Pydantic 模型，类型安全、可序列化
2. **关注点分离**：原版所有逻辑耦合在一个类 → Agent/Tool/Crew/Flow 四层分离
3. **可测试性**：每个 Crew 可独立测试（给定输入 → 验证输出），无需启动整个 FSM
4. **可扩展性**：新增课程只需添加 courses/ 下的配置 + flow/stages/ 下的 handler
5. **框架标准化**：基于 CrewAI 成熟框架，降低维护成本，便于社区协作

### 5.2 保持不变的核心

1. **教学逻辑完全等价**：9 个阶段的推进条件、关键词匹配、相位累积逻辑 1:1 还原
2. **学生体验一致**：前端 UI、交互方式、Agent 对话风格完全相同
3. **实验数据兼容**：C 模式下的行为等价于原版 C 模式，已有实验数据可直接使用
