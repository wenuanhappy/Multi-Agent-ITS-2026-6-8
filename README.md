 # Multi-Agent ITS

基于 CrewAI 多智能体框架的苏格拉底式高中数学交互教学系统。

复旦大学硕士学位论文项目。

## 系统架构

采用 **Flow-Crew-Agent-Tool** 四层架构：

- **TutoringFlow**（CrewAI Flow）：FSM 状态机编排器，管理教学阶段推进、按需激活 Crew
- **TeachingCrew / FeynmanCrew / CorrectionCrew**：三个功能 Crew，分别负责主线教学、费曼反问、三段式纠错
- **TeacherAgent / PeerAgent / TAAgent**：CrewAI Agent，各自持有工具、独立推理
- **SymPyDiagnosisTool / AntiSpoilerTool / KGRetrievalTool / LLMClassifierTool**：四个 CrewAI Tool

异构 LLM 分工：Claude Sonnet 4 做文本生成，DeepSeek V3 做 Tool 路由（function calling）。

## 课程覆盖

| 章节 | 课程 | 说明 |
|------|------|------|
| 3.1.1 | 椭圆及其标准方程 | 13 stage |
| 3.1.2 | 椭圆的简单几何性质 | 9 stage |
| 3.2.1 | 双曲线及其标准方程 | 13 stage |
| 3.2.2 | 双曲线的简单几何性质 | 11 stage |
| 3.3.1 | 抛物线及其标准方程 | 12 stage |
| 3.3.2 | 抛物线的简单几何性质 | 9 stage |

## 环境配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Key

在项目根目录创建 `.env` 文件：

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
```

### 3. 启动服务

```bash
python run.py
```

服务启动后访问 `http://localhost:8300`。

## 目录结构

```
Multi-Agent-ITS/
├── run.py                  # 入口
├── config/settings.py      # 配置（LLM、端口、Anthropic SDK patch）
├── api/server.py           # FastAPI REST API
├── flow/
│   ├── state.py            # Pydantic 状态模型 + E312 阶段枚举
│   └── tutoring_flow.py    # CrewAI Flow FSM 编排器
├── agents/                 # CrewAI Agent 定义
│   ├── teacher.py
│   ├── peer.py
│   ├── ta.py
│   └── diagnostician.py
├── crews/                  # CrewAI Crew 组合
│   ├── teaching_crew.py
│   ├── feynman_crew.py
│   └── correction_crew.py
├── tools/                  # CrewAI Tool
│   ├── sympy_diagnosis.py
│   ├── anti_spoiler_scan.py
│   ├── llm_classify.py
│   └── kg_retrieval.py
├── core/                   # 共享核心模块
│   ├── llm_providers.py
│   ├── anti_spoiler.py
│   ├── feynman_loop.py
│   ├── math_normalizer.py
│   ├── diagnostic.py
│   └── ...
├── courses/                # 课程数据（例题标准答案、诊断协议）
├── knowledge_graph/        # 圆锥曲线知识图谱
├── legacy/                 # 完整课程引擎（6课通用状态机）
│   ├── lesson_flow.py
│   └── stages/
├── frontend/
│   ├── dispatcher.html     # 课程选择主页
│   ├── section.html        # 小节选择页
│   └── interactive.html    # JSXGraph 交互课堂
└── docs/
    └── architecture_for_thesis.md
```

## 消融实验模式

| 模式 | 激活组件 | 说明 |
|------|---------|------|
| off | Flow + 基础 LLM | 基线：纯 FSM 单 Agent |
| A | 同 off + UI 三头像 | UI 对照组 |
| B | + TeacherAgent + AntiSpoilerTool | + 约束层 Tool |
| C | + TeachingCrew + FeynmanCrew + CorrectionCrew | 完整多 Crew 协作 |
| D | 同 C + Agent 自主 Tool 调用 | + Agent 自主性 |
