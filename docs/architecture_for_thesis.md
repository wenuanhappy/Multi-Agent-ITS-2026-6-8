# 论文架构图素材（供 TikZ 绘制）

## 一、Tool 分配表

### 1.1 Agent × Tool 持有关系

| Agent | 所属 Crew | 持有 Tool | Tool 用途 |
|-------|----------|----------|----------|
| TeacherAgent | TeachingCrew | AntiSpoilerTool | 生成回复后自检是否泄漏当前阶段禁词 |
| TeacherAgent | TeachingCrew | KGRetrievalTool | 生成回复前检索椭圆知识图谱获取上下文 |
| PeerAgent | FeynmanCrew | AntiSpoilerTool | 生成费曼提问前检查问题不含答案 |
| PeerAgent | FeynmanCrew | KGRetrievalTool | 基于知识图谱生成更精准的阶段相关提问 |
| TAAgent | CorrectionCrew | SymPyDiagnosisTool | 符号验证学生数学表达式，定位具体错误类型 |
| TAAgent | CorrectionCrew | KGRetrievalTool | 纠错时引用准确的椭圆知识点 |
| CanvasAgent | CanvasCrew *(未来)* | JSXGraphTool *(未来)* | 根据学生状态生成个性化几何动画与多模态资源（当前由FSM确定性控制） |

### 1.2 FSM 直接调用的 Tool

| Tool | 调用时机 | 用途 |
|------|---------|------|
| SymPyDiagnosisTool | 学生提交答案后、分发到 Crew 之前 | 前置诊断：判对错 → 决定走 TeachingCrew 还是 CorrectionCrew |
| AntiSpoilerTool | Agent 生成回复后 | 后置过滤：命中黑名单 → 重生或 fallback |
| LLMClassifierTool | 关键词匹配失败时 | 语义兜底：用 LLM 对学生口语化回答做枚举分类 |
| KGRetrievalTool | 构建 system prompt 时 | 注入阶段感知的知识上下文，防止超前泄漏 |

### 1.3 异构 LLM 分工

| LLM | 角色 | 用途 |
|-----|------|------|
| Claude Sonnet 4 | 文本生成 | 苏格拉底式教学对话、三段式纠错、费曼评判与总结 |
| DeepSeek V3 | Tool 路由 | Agent 决定调哪个 Tool、传什么参数（function calling） |

---

## 二、功能架构图（系统视角）

### TikZ 绘制要点

```
层级结构（自上而下）：

┌─────────────────────────────────────────────────────────┐
│                    学生（浏览器）                          │
│              文本输入 / JSXGraph 画布交互                   │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                FastAPI Server (REST API)                  │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│          TutoringFlow (CrewAI Flow · FSM 编排器)          │
│  Pydantic 状态管理 · 阶段分发 · 按需激活 Crew              │
│                                                          │
│  直接调用 Tool：                                          │
│  · SymPyDiagnosis (前置诊断)                              │
│  · LLMClassifier (语义兜底)                               │
│  · AntiSpoiler (后置过滤)                                 │
│  · KGRetrieval (上下文注入)                                │
└──┬──────────┬──────────┬──────────┬──────────────────┘
   ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌─────────────────┐
│Teaching│ │Feynman │ │Correct.│ │  CanvasCrew     │
│Crew    │ │Crew    │ │Crew    │ │  (未来扩展)      │
│        │ │        │ │        │ │                 │
│Teacher │ │Peer    │ │TA      │ │ CanvasAgent     │
│Agent   │ │Agent   │ │Agent   │ │ ┌─────────────┐ │
│┌──────┐│ │┌──────┐│ │┌──────┐│ │ │JSXGraphTool │ │
││Anti- ││ ││Anti- ││ ││SymPy ││ │ │(画布指令生成)│ │
││Spoil.││ ││Spoil.││ ││Diag. ││ │ └─────────────┘ │
││KG    ││ ││KG    ││ ││KG    ││ │                 │
││Retri.││ ││Retri.││ ││Retri.││ │ 当前：FSM确定性  │
│└──────┘│ │└──────┘│ │└──────┘│ │ 控制画布动作     │
│        │ │        │ │        │ │ 未来：Agent根据  │
│        │ │Teacher │ │        │ │ 学生需求生成个性 │
│        │ │(总结)  │ │        │ │ 化多模态资源     │
└────────┘ └────────┘ └────────┘ └─────────────────┘
 每轮触发   阶段切换    检测错误    阶段切换时(未来)
 Sequential Sequential Sequential  Sequential
```

### 关键标注

- Flow → Crew 的箭头标注「按需激活」
- Tool 在 Agent 内部，箭头标注「Agent 自主调用，DeepSeek 做路由」
- FSM 直接调 Tool 的箭头标注「确定性调用」
- 双 LLM 标注：Claude（文本生成）/ DeepSeek（Tool 路由）
- CanvasCrew 用虚线框标注「未来扩展：个性化多模态资源生成」

---

## 三、对话交互架构图（学生视角）

### TikZ 绘制要点

```
纵轴：时间线（一节课的流程）
横轴：左侧=学生看到的对话，右侧=幕后 FSM 编排

学生看到的对话                    幕后编排
─────────────                   ─────────
                                
【阶段内：教师主导】               FSM 分发 → TeachingCrew
🧑‍🏫 老师：x的范围是什么？          关键词匹配 → 命中
🙋 学生：-a≤x≤a                  → 推进到下一 phase
🧑‍🏫 老师：✅正确！y呢？            AntiSpoiler 后过滤 ✓
                                
【答错时：助教介入】               FSM → SymPy 诊断 → 错误
🙋 学生：-b≤x≤b（变量错位）        → CorrectionCrew
🧑‍💻 助教：变量错位了...            TA 用 KG 获取椭圆上下文
      从方程推导y²/b²≤1...        生成三段式纠错
                                
【阶段切换：同学费曼反问】          FSM → 触发条件命中
🧑‍🎓 同学：为什么y²/b²≥0          → FeynmanCrew
       能推出x的范围？             Peer 用 KG 检索知识
🙋 学生：因为方程两项加起来=1       Peer 判定 → 满意/追问
🧑‍🎓 同学：嗯我明白了！谢谢！        → Teacher 总结
🧑‍🏫 老师：解释得好！继续...         恢复目标阶段 SYMMETRY
                                
【画布交互】                      前端 JSXGraph
📐 右侧画布同步展示：              POST /event → FSM
   abc线段·范围矩形·顶点点选      on_canvas_event 处理
   离心率滑块·例题图形
```

### 关键标注

- 三种气泡颜色：教师(蓝) / 同学(紫) / 助教(金)
- 学生只看到自然的角色切换，不感知 FSM
- 教师占主导(~80%对话)，同学和助教按需出现
- 画布与对话同步联动
- 最多3轮费曼追问，学生说"不知道"直接退出到教师

---

## 四、消融实验与 CrewAI 组件映射

| 消融模式 | 激活的 CrewAI 组件 | 论文描述 |
|---------|------------------|---------|
| off | 仅 Flow 编排 + 基础 LLM 调用 | 基线：纯 FSM + 单 Agent |
| A | 同 off（前端 UI 区分三 Agent 头像） | UI 对照组 |
| B | Flow + TeacherAgent + AntiSpoilerTool | + 约束层 Tool |
| C | Flow + TeachingCrew + FeynmanCrew + CorrectionCrew | + 完整多 Crew 协作 |
| D | 同 C + LLM 自主提议 Tool（推进仲裁/同伴触发） | + Agent 自主性 |

### 未来扩展方向

| 方向 | 对应组件 | 说明 |
|------|---------|------|
| 个性化多模态资源 | CanvasCrew + JSXGraphTool | Agent 根据学生学习状态自主生成网页动画、视频等多模态资源（戴老师建议） |
| Agent 自进化 | 全部 Crew | 课堂组织和学习流程根据数据反馈自动优化 |
