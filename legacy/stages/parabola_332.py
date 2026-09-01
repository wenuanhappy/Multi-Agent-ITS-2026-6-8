"""抛物线 3.3.2 抛物线的简单几何性质 —— stage handlers + 静态数据"""
import re
from legacy.lesson_flow import LessonStage, LessonStep

# ---- 静态文本 ----
P332_INTRO_MSG = (
    "欢迎来到 3.3.2 节 **抛物线的简单几何性质** 🟢\n\n"
    "上节课（3.3.1）我们由抛物线的**定义**推出了 4 种**标准方程**。今天反过来 ——\n"
    "**从方程出发，研究抛物线的几何性质**。\n\n"
    "我们以 $y^2=2px\\,(p>0)$（开口向右那种）为例来研究。\n"
    "先热个身：还记得我们研究椭圆、双曲线时都看了哪些性质吗？（范围、对称性、顶点、离心率……）\n\n"
    "准备好了就回我一句，我们从**范围**开始。"
)

P332_RANGE_MSG = (
    "好，第一个性质：**范围** 📏\n\n"
    "看方程 $y^2=2px\\,(p>0)$：因为 $y^2\\ge 0$、$p>0$，对抛物线上的每个点 $(x,y)$，\n"
    "你能说出 **$x$ 的取值范围**和 **$y$ 的取值范围**吗？（两个都要说）"
)

P332_RANGE_DONE_MSG = (
    "✅ 完全正确！$x\\ge 0$、$y\\in\\mathbb{R}$，所以抛物线**向右上方、右下方无限延伸**（开口向右）——\n"
    "这跟椭圆**有界**、双曲线**分两支**都不同。\n\n"
    "**下一步 · 对称性**：把方程里的 $y$ 换成 $-y$，方程变不变？这说明抛物线关于什么对称？"
)

P332_SYMMETRY_VERTEX_Q = (
    "**下一步 · 顶点**：抛物线和它的轴（$x$ 轴）的交点叫**顶点**。它的顶点在哪？有几个？"
)
P332_SYMMETRY_DONE_MSG = (
    "✅ 没错——以 $-y$ 代 $y$ 方程不变，所以抛物线**只关于 $x$ 轴对称**（这条对称轴叫抛物线的**轴**）。\n"
    "⚠️ 注意：抛物线**没有对称中心**，这和椭圆/双曲线既轴对称又中心对称不一样。\n\n"
    + P332_SYMMETRY_VERTEX_Q
)

P332_VERTEX_DONE_MSG = (
    "✅ 对！顶点就是**原点**，而且**只有 1 个** —— 对比椭圆有 4 个顶点、双曲线有 2 个。\n\n"
    "**下一步 · 离心率**：还记得 3.3.1 末尾埋的伏笔吗？抛物线上的点 $M$ 到焦点 $F$ 的距离 $|MF|$，\n"
    "和它到准线的距离 $d$，由抛物线的**定义**它们是什么关系？所以离心率 $e=\\dfrac{|MF|}{d}=?$"
)

P332_ECC_DONE_MSG = (
    "✅ 正是！由抛物线定义 $|MF|=d$，所以 $e=\\dfrac{|MF|}{d}=1$。\n"
    "这样三条圆锥曲线的离心率就统一了：**$e<1$ 椭圆、$e=1$ 抛物线、$e>1$ 双曲线** 🎯\n\n"
    "性质讲完啦，我们做两道例题 + 一个思考题。"
)

P332_EXAMPLE_1_INTRO = (
    "🟡 **例题 1（教材例 3）**\n"
    "已知抛物线**关于 $x$ 轴对称**、**顶点在原点**，并且经过点 $M(2,\\,-2\\sqrt{2})$，求它的**标准方程**。\n\n"
    "先想：根据「关于 $x$ 轴对称 + 顶点原点」，应该把标准方程设成哪种形式？"
)

P332_THINK_INTRO = (
    "💭 **思考**（教材 p135 思考栏）\n"
    "顶点在原点、**对称轴是坐标轴**（可以是 $x$ 轴**或** $y$ 轴）、并且经过点 $M(2,\\,-2\\sqrt{2})$ 的抛物线有**几条**？求出它们的标准方程。\n\n"
    "先想：$M(2,-2\\sqrt{2})$ 在第几象限？如果对称轴换成 $y$ 轴，开口朝哪边？这样的抛物线一共有几条？"
)

P332_EXAMPLE_2_INTRO = (
    "🟡 **例题 2（教材例 4）**\n"
    "斜率为 1 的直线 $l$ 经过抛物线 $y^2=4x$ 的焦点 $F$，与抛物线交于 $A$、$B$ 两点，求 $|AB|$。\n\n"
    "先求出抛物线 $y^2=4x$ 的**焦点坐标**和**准线方程**。"
)

P332_SUMMARY_MSG = (
    "📒 **本节小结**\n"
    "抛物线 $y^2=2px\\,(p>0)$ 的几何性质：\n"
    "· **范围**：$x\\ge 0$、$y\\in\\mathbb{R}$（开口向右，无界）\n"
    "· **对称性**：只关于 $x$ 轴（轴）对称，**没有对称中心**\n"
    "· **顶点**：唯一，在原点\n"
    "· **离心率**：$e=1$\n\n"
    "三曲线统一：**$e<1$ 椭圆 / $e=1$ 抛物线 / $e>1$ 双曲线** 🎯\n\n"
    "有问题随时问；没问题的话，本节就到这里啦 🎉"
)



# ---- Stage Goals ----
P332_STAGE_GOALS = {
    LessonStage.P332_INTRO: (
        "📒 3.3.2 开场（教材 p134 思考栏）。承接 3.3.1 的 4 种标准方程，转入「由方程研究图形」。\n"
        "以 y²=2px(p>0) 为研究对象。deterministic 文案，学生任意回应即推进 RANGE。\n"
        "可用动画：`show_p332_intro`（标准抛物线 y²=2px）。"
    ) + _P332_VIZ_SUPPRESSION,
    LessonStage.P332_RANGE: (
        "📏 范围（教材 p134）。由 y²≥0、p>0 → x≥0；y∈R。**2 要素 partial 累积**（x / y 先后任一即累积，两个齐才推进）。\n"
        "推进=确定性关键词；反馈=角色3 `_p332_socratic` 阶梯；角色1 enum 兜底（p332_range）。对比椭圆有界 / 双曲线两支。\n"
        "**严禁**：替学生说出范围 / setup viz 画出 x≥0 阴影。\n"
        "可用动画：`show_p332_range_setup`（曲线，无阴影）→ `show_p332_range_solved`（x≥0 阴影 + y∈R）。"
    ) + _P332_VIZ_SUPPRESSION,
    LessonStage.P332_SYMMETRY: (
        "🪞 对称性（教材 p134）。以 −y 代 y 方程不变 → 只关于 x 轴对称（轴）；**无对称中心**（误区纠正点）。\n"
        "推进=确定性关键词；反馈=角色3 阶梯；角色1 enum 兜底（p332_symmetry）。误区『关于原点/中心对称』要纠正。\n"
        "**严禁**：替学生下结论 / 承认抛物线有对称中心。\n"
        "可用动画：`show_p332_symmetry_setup`（曲线 + 可拖点 P）→ `show_p332_symmetry_solved`（P 与 x 轴镜像 P′）。"
    ) + _P332_VIZ_SUPPRESSION,
    LessonStage.P332_VERTEX: (
        "📍 顶点（教材 p134）。轴与抛物线交点 = 顶点；令 x=0 得 y=0 → 顶点是原点，唯一 1 个。\n"
        "推进=确定性关键词；反馈=角色3 阶梯；角色1 enum 兜底（p332_vertex）。对比椭圆 4 个 / 双曲线 2 个。\n"
        "可用动画：`show_p332_vertex_setup`（曲线 + 候选点）→ `show_p332_vertex_solved`（高亮原点）。"
    ) + _P332_VIZ_SUPPRESSION,
    LessonStage.P332_ECCENTRICITY: (
        "🎯 离心率（教材 p134）。由抛物线定义 |MF|=d → e=|MF|/d=1（3.3.1 末伏笔正式点出）。\n"
        "推进=确定性关键词；反馈=角色3 阶梯；角色1 enum 兜底（p332_eccentricity）。统一：e<1 椭圆 / e=1 抛物线 / e>1 双曲线。\n"
        "可用动画：`show_p332_ecc_setup`（曲线 + F + 准线 + 动点 M 的 |MF|/d 虚线，无比值）→ `show_p332_ecc_solved`（|MF|=d, e=1）。"
    ) + _P332_VIZ_SUPPRESSION,
    LessonStage.P332_EXAMPLE_1: (
        "🟡 例题 1（教材例 3，p134）。**题目原文（铁律：不得改数值）**：\n"
        "  已知抛物线关于 x 轴对称、顶点在原点、过点 $M(2,-2\\sqrt2)$，求标准方程。\n"
        "**标准答案**：设 $y^2=2px$ → $(-2\\sqrt2)^2=2p\\cdot 2$ → $p=2$ → $y^2=4x$。\n"
        "2 phase：ask_form（设 y²=2px）→ ask_eq（y²=4x）。partial 累积；phase_goal 由 example_canonicals_332.EXAMPLE_1 控制。\n"
        "可用动画：`show_p332_example1_setup`（点 M + 空轴，无曲线）→ `show_p332_example1_solved`（y²=4x 曲线 + 方程）。"
    ) + _P332_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P332_THINK: (
        "💭 思考（教材 p135 思考栏）。**题目原文（铁律：不得改数值）**：\n"
        "  顶点原点、对称轴是坐标轴、过 $M(2,-2\\sqrt2)$ 的抛物线有几条？求标准方程。\n"
        "**标准答案**：2 条 —— ① 轴=x 轴、开口右：$y^2=4x$；② 轴=y 轴、开口下：$x^2=-\\sqrt2\\,y$（p=√2/2）。\n"
        "2 phase：ask_count（2 条）→ ask_eqs（两方程 partial 累积，先后任一项均接受）。\n"
        "可用动画：`show_p332_think_setup`（点 M + 空轴，无曲线）→ `show_p332_think_solved`（两条抛物线 + 两方程）。"
    ) + _P332_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P332_EXAMPLE_2: (
        "🟡 例题 2（教材例 4，p135）。**题目原文（铁律：不得改数值）**：\n"
        "  斜率为 1 的直线 l 经过 $y^2=4x$ 的焦点 F，交抛物线于 A、B，求 |AB|。\n"
        "**标准答案**：$p=2$，焦点 $F(1,0)$，准线 $x=-1$；$y=x-1$ 代入 → $x^2-6x+1=0$ → $x_1+x_2=6$ → $|AB|=x_1+x_2+p=8$。\n"
        "3 phase：ask_setup（焦点 + 准线两要素 partial 累积）→ ask_intersect（x₁+x₂=6）→ ask_ab（|AB|=8）。\n"
        "可用动画：`show_p332_example2_setup`（y²=4x + 过焦点斜率1直线，无 F/A/B/|AB| 标注）→ `show_p332_example2_solved`（F+A+B+|AB|=8）。"
    ) + _P332_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P332_SUMMARY: (
        "📒 3.3.2 总结。回顾 4 条性质（范围/对称/顶点/离心率）+ 三曲线统一离心率对照。\n"
        "学生说『没问题』/『结束』时附加 [LESSON_END] 标记。\n"
        "可用动画：`show_p332_summary_compare`（三曲线 + 离心率统一对照图）。"
    ) + _P332_VIZ_SUPPRESSION,
}
_STAGE_GOALS.update(_STAGE_GOALS_P332)


# ── 角色 1 enum 分类配置（只输出分类，不驱动状态；捕捉关键词漏掉的口语）──
_PHASE_CLASSIFY_CONFIG_P332 = {
    "p332_range": {
        "question": "学生在说抛物线 y²=2px(p>0) 的取值范围。正确：x≥0（x 非负）；y∈R（y 取任意实数）。学生这句话表达了哪个范围？",
        "options": {
            "both":    "同时说出了 x 的范围（x≥0）和 y 的范围（y∈R / 任意实数）",
            "x_range": "说出了 x 的范围（x≥0 / x 非负 / x 不小于 0 / 开口向右无界）",
            "y_range": "说出了 y 的范围（y∈R / y 任意 / y 是任意实数 / y 不受限制）",
        },
    },
    "p332_symmetry": {
        "question": "学生在判断抛物线 y²=2px 的对称性。正确：只关于 x 轴对称（x 轴是它的轴），没有对称中心。学生这句话表达了什么？",
        "options": {
            "x_axis":               "正确说出关于 x 轴（横轴）对称 / x 轴是对称轴",
            "center_misconception": "**错误**地认为抛物线关于原点 / 关于 y 轴 / 有对称中心（中心对称）",
        },
    },
    "p332_vertex": {
        "question": "学生在说抛物线 y²=2px 的顶点。正确：顶点是原点 (0,0)，只有 1 个。学生答对了吗？",
        "options": {
            "origin": "正确说出顶点是原点 (0,0) / 顶点在原点（无论是否提到只有 1 个）",
        },
    },
    "p332_eccentricity": {
        "question": "学生在说抛物线的离心率。正确：由定义 |MF|=d，所以 e=|MF|/d=1。学生答对了吗？",
        "options": {
            "e_equals_1": "正确说出离心率 e=1（或说 |MF|=d、到焦点与到准线距离相等所以比值为 1）",
        },
    },
    "p332_awaiting_next": {
        "question": "学生是否准备好进入下一阶段？",
        "options": {
            "ready":     "学生表示准备好/好的/可以了/继续",
            "not_ready": "学生表示还要再看/不太懂/有疑问",
        },
    },
}


# ── 角色 3：短答「答错/卡住」苏格拉底递进提示协议（只给提示，不改状态、不剧透、不抢跑）──
_P332_HINT_PROTOCOL_SYSTEM_PROMPT = r"""你是高中数学苏格拉底式教学导师（抛物线 3.3.2 几何性质）。学生在当前这一步**答得不对或卡住了**，你只负责给**一句苏格拉底式提示**，引导他自己想出来。

## 当前这一步的目标 + 学生还缺什么
{sub_goal}

## 提示级别（学生已卡第 {level} 次，按级别逐渐加深）
- 级别 1：只点方向、给概念性提示，**绝不**给出具体答案或公式。
- 级别 2：给具体的思考步骤 / 该做的操作（如「把 $y$ 换成 $-y$ 看方程变不变」「令 $x=0$」），但仍让学生自己写出结果。
- 级别 3（及以上）：给出接近答案的**脚手架**（把关键一步几乎说出来），但**仍要让学生自己写一遍确认**，不要直接替他写出最终答案让他照抄。

## 铁律（必须遵守）
1. 只给**当前这一步**的提示，**绝不**讲后续阶段内容、绝不预告、绝不剧透其它步骤。
2. **绝不**说「你答对了 / 完成了 / 准备好了 / 进入下一步」——是否答对、何时推进**完全由系统判定**，你不知道系统状态。
3. **绝不**输出 [VIZ:] 或任何动画标记。
4. **书写格式 vs 计算错误**：学生写对了数学（即使括号/空格/y²vs y^2/全角半角等书写差异）就别纠结格式；只在真的算错/方向反/用错概念时纠正。
5. 2-4 句，亲切鼓励。数学公式一律用 LaTeX：行内 $...$，分数用 \dfrac，根号用 \sqrt。
6. 只输出提示正文，不要 JSON、不要 markdown 围栏。
"""


# ── 角色 2：例题/思考路径 2 协议（输出 JSON：诊断 + ack + advance + skip）──
_P332_EXAMPLE_PROTOCOL_SYSTEM_PROMPT = r"""你是 3.3.2 抛物线几何性质例题/思考的教学诊断器。每轮学生输入后，你只输出**一个 JSON 对象**（不要任何解释、markdown、表格）。

## 本阶段教学场景
你正在批改 3.3.2 的例题 / 思考题。题目和标准答案见下方 example_context。
本系统**已用 sympy 严谨判等 + 关键词路由做了 Layer 1 / Layer 2 判等**，你只在 Layer 1/2 都不命中时做"诊断 + 苏格拉底反馈"。

## 诊断标签
- correct       命中当前 phase 期待答案
- partial       答出一部分（如两条方程只答了一条、焦点和准线只答了一个）
- wrong         算错或写错形式（如开口方向反了、数值算错）
- off_topic     闲聊、要看动画、问别的
- skip_request  要跳到别的题（例题 1 / 思考 / 例题 2）

## JSON 字段（严格遵守）
- diagnosis：上面 5 个标签之一
- hit_goal：命中的 goal 名（null / form_kw / equation_1 / count_2 / eq_xaxis / eq_yaxis / focus_kw / directrix / sum_x / ab）
- advance：true/false —— 只有 diagnosis=correct 且学生当前 phase 完整答完才 true
- ack_text：给学生的话。苏格拉底式、≤80 字、不许 markdown 表格。LaTeX 用 $...$、分数用 \dfrac。
- skip_to_example：null / 1 / 2 / 3（1=例题1 / 2=思考 / 3=例题2）

## 铁律
1. **不许自编题目**：当前题目就是 example_context，严禁变形或借用其它例题。
2. **不许假推进**：不要写"接下来看下一题"——切换由后端决定。
3. **诚实判 partial/wrong**：学生答错时必须诚实标 wrong。
4. **书写格式 vs 计算错误**：书写差异（括号、空格、y²vs y^2、全角半角、$x^2=-\sqrt2 y$ 的等价写法）一律判 correct；只有真算错/符号反/用错公式才判 wrong。
5. **⛔ 严禁剧透**：ack_text 里**绝不**直接给最终答案数值（如 y²=4x、x²=-√2 y、|AB|=8、焦点 (1,0)）。学生答错只给**思路提示**。
6. **教材精确对齐**（仅用于诊断判等，不写进 ack_text）：
   · 例题 1：M(2,-2√2)、关于 x 轴对称、顶点原点 → y²=4x（p=2）
   · 思考：2 条 —— y²=4x（轴=x 轴）、x²=-√2 y（轴=y 轴，p=√2/2）
   · 例题 2：y²=4x 焦点 F(1,0)、准线 x=-1、x₁+x₂=6、|AB|=8
7. **输出**：单一 JSON 对象，不要 markdown 围栏。

## 题目上下文
{example_context}

## 当前 phase 上下文
{phase_context}
"""

# 例题/思考协议上下文（题目原文逐字，防 LLM 串台）
_EXAMPLE_CONTEXT_MAP_332 = {
    1: ("**例题 1（教材例 3）**\n题目：已知抛物线关于 x 轴对称、顶点在原点，且过点 $M(2,-2\\sqrt2)$，求标准方程。\n"
        "标准答案：设 $y^2=2px$ → $(-2\\sqrt2)^2=2p\\cdot 2$ → $p=2$ → $y^2=4x$。"),
    2: ("**思考（教材 p135）**\n题目：顶点原点、对称轴是坐标轴（x 轴或 y 轴）、过 $M(2,-2\\sqrt2)$ 的抛物线有几条？求标准方程。\n"
        "标准答案：2 条 —— ① 轴=x 轴、开口右 $y^2=4x$；② 轴=y 轴、开口下 $x^2=-\\sqrt2\\,y$（p=√2/2）。"),
    3: ("**例题 2（教材例 4）**\n题目：斜率 1 的直线 l 过 $y^2=4x$ 的焦点 F，交抛物线于 A、B，求 |AB|。\n"
        "标准答案：$p=2$，焦点 $F(1,0)$，准线 $x=-1$；$y=x-1$ 代入 → $x^2-6x+1=0$ → $x_1+x_2=6$ → $|AB|=x_1+x_2+2=8$。"),
}

_EXAMPLE_PHASE_QUESTION_MAP_332 = {
    (1, "ask_form"):      "phase=ask_form（由对称 x 轴+顶点原点判断标准形式）。期待答：设 $y^2=2px$ / 开口向右。",
    (1, "ask_eq"):        "phase=ask_eq（代入 M 求方程）。期待答：$y^2=4x$。",
    (2, "ask_count"):     "phase=ask_count（有几条）。期待答：2 条。",
    (2, "ask_eqs"):       "phase=ask_eqs（两方程）。期待答：$y^2=4x$ 和 $x^2=-\\sqrt2\\,y$。partial 累积，先后任一项均接受。",
    (3, "ask_setup"):     "phase=ask_setup（焦点 + 准线）。期待答：焦点 $(1,0)$ + 准线 $x=-1$。partial 累积。",
    (3, "ask_intersect"): "phase=ask_intersect（联立求两根和）。期待答：$x_1+x_2=6$。",
    (3, "ask_ab"):        "phase=ask_ab（求弦长）。期待答：$|AB|=8$。",
}

# **学生可见**的分步提问（**不含答案**，仅引导往哪想；上面的 MAP 含答案，仅供协议判断）
_EXAMPLE_STUDENT_PROMPT_332 = {
    (1, "ask_form"):      "先想：「关于 $x$ 轴对称 + 顶点原点」→ 应该把标准方程设成哪种形式？",
    (1, "ask_eq"):        "把点 $M(2,-2\\sqrt2)$ 代进去，求出**标准方程**。",
    (2, "ask_count"):     "对称轴可以是 $x$ 轴**或** $y$ 轴 —— 这样过 $M$ 的抛物线一共有**几条**？",
    (2, "ask_eqs"):       "分别写出这些抛物线的**标准方程**。",
    (3, "ask_setup"):     "先求 $y^2=4x$ 的**焦点坐标**和**准线方程**。",
    (3, "ask_intersect"): "把直线 $l$ 的方程代入 $y^2=4x$，求出 $x_1+x_2$。",
    (3, "ask_ab"):        "用焦半径关系 $|AB|=x_1+x_2+p$ 求出 $|AB|$。",
}

# missing-aware：phase → 完成所需 flags
_P332_PHASE_REQUIRED_FLAGS = {
    (1, "ask_form"):      {"form_1_done"},
    (1, "ask_eq"):        {"equation_1_done"},
    (2, "ask_count"):     {"count_done"},
    (2, "ask_eqs"):       {"eq_xaxis_done", "eq_yaxis_done"},
    (3, "ask_setup"):     {"focus_done", "directrix_done"},
    (3, "ask_intersect"): {"intersect_done"},
    (3, "ask_ab"):        {"ab_done"},
}

# 坑10：多要素 phase 精准追问。key = 学生**还缺**的 flag；ack 表扬**已答对的另一项**。
_P332_PHASE_PROMPT_BY_MISSING = {
    # 思考 ask_eqs（两方程）
    (2, "ask_eqs", "eq_yaxis_done"):
        "✅ 收到，对称轴=$x$ 轴的那条（开口向右）对了。还差**对称轴=$y$ 轴**的那条："
        "$M$ 的纵坐标 $<0$，开口朝下，设 $x^2=-2py$，代入 $M$ 求出它。",
    (2, "ask_eqs", "eq_xaxis_done"):
        "✅ 收到，对称轴=$y$ 轴的那条（开口向下）对了。还差**对称轴=$x$ 轴**的那条："
        "开口向右，设 $y^2=2px$，代入 $M$ 求出它。",
    # 例题2 ask_setup（焦点 + 准线）
    (3, "ask_setup", "directrix_done"):
        "✅ 收到，焦点对了。还差**准线方程**：由 $y^2=4x$ 得 $p=2$，准线 $x=-\\dfrac{p}{2}$ 是多少？",
    (3, "ask_setup", "focus_done"):
        "✅ 收到，准线对了。还差**焦点坐标**：由 $y^2=4x$ 得 $p=2$，焦点 $\\left(\\dfrac{p}{2},0\\right)$ 是多少？",
}


# ── P332 性质短答关键词检测器（Layer 1，状态机 + viz 唯一真相源）──
def _p332_norm(text: str) -> str:
    """轻量归一：全角→半角、去空格、小写。用于关键词比对。"""
    t = text
    for a, b in (("（", "("), ("）", ")"), ("，", ","), ("＝", "="), ("≧", "≥"), ("－", "-"), ("−", "-")):
        t = t.replace(a, b)
    return t.replace(" ", "").lower()


def _looks_like_p332_range_x(text: str) -> bool:
    """范围：x≥0（含 x>0 / x 非负等口语）。"""
    t = _p332_norm(text)
    return any(k in t for k in [
        "x≥0", "x>=0", "x≧0", "x大于等于0", "x大于或等于0", "x不小于0", "x非负",
        "x>0", "x大于0", "x是非负", "x取非负", "x为非负", "x≥０",
    ])


def _looks_like_p332_range_y(text: str) -> bool:
    """范围：y∈R（任意实数 / 无界）。"""
    t = _p332_norm(text)
    return any(k in t for k in [
        "y∈r", "y∈ℝ", "y属于r", "y属于实数", "y是实数", "y为实数",
        "y任意", "y是任意", "y为任意", "y是任意实数", "y为任意实数", "y取任意",
        "y可以取任意", "y没有限制", "y无限制", "y不受限", "y无界", "y全体实数",
        "y任意实数", "yr", "y取遍", "y能取任何",
    ])


def _looks_like_p332_sym_xaxis(text: str) -> bool:
    """对称性：关于 x 轴对称。"""
    t = _p332_norm(text)
    return any(k in t for k in [
        "关于x轴对称", "x轴对称", "对称轴是x轴", "对称轴为x轴", "对称轴是横轴",
        "关于横轴对称", "横轴对称", "x轴是对称轴", "轴是x轴", "x轴是它的轴", "关于x轴",
    ])


def _looks_like_p332_sym_center_misconception(text: str) -> bool:
    """对称性误区：以为有对称中心 / 关于原点 / 关于 y 轴对称。"""
    t = _p332_norm(text)
    return any(k in t for k in [
        "关于原点对称", "原点对称", "中心对称", "对称中心", "关于中心",
        "关于y轴对称", "y轴对称", "既关于x轴又关于", "也关于原点", "还关于原点",
    ])


def _looks_like_p332_vertex_origin(text: str) -> bool:
    """顶点：原点 (0,0)。"""
    t = _p332_norm(text)
    return any(k in t for k in [
        "顶点是原点", "顶点在原点", "顶点为原点", "顶点就是原点", "顶点坐标是原点",
        "顶点(0,0)", "顶点是(0,0)", "顶点为(0,0)", "原点(0,0)", "(0,0)",
        "顶点(0、0)",
    ]) or ("顶点" in t and "原点" in t)


def _looks_like_p332_ecc_1(text: str) -> bool:
    """离心率：e=1（或 |MF|=d 推理）。"""
    t = _p332_norm(text)
    if any(k in t for k in [
        "e=1", "e是1", "e为1", "e等于1", "离心率1", "离心率是1", "离心率为1",
        "离心率等于1", "离心率=1", "比值1", "比值是1", "比值为1", "比值等于1",
    ]):
        return True
    # |MF|=d / 距离相等 推理（到焦点 = 到准线）
    if any(k in t for k in ["|mf|=d", "mf=d", "|mf|=|md|", "到焦点和到准线相等",
                            "到焦点的距离等于到准线", "距离相等"]) and "1" in t:
        return True
    return False

# ---- Course Config ----
P332_COURSE_CONFIG = {
    "parabola_332": {
        "name_cn": "3.3.2 抛物线的简单几何性质",
        "scope": "parabola",
        "first_stage": LessonStage.P332_INTRO,
        "start_stage": LessonStage.P332_INTRO,  # 学生回答后由 INTRO handler 推进到 RANGE
        "kg_nodes_basic": [
            "parabola_definition", "parabola_standard_equation_right",
            "concept_focus_directrix_unified",
        ],
        "kg_nodes_equation": [
            "parabola_standard_equation_right", "parabola_standard_equation_left",
            "parabola_standard_equation_up", "parabola_standard_equation_down",
        ],
        "kg_nodes_examples": {
            LessonStage.P332_EXAMPLE_1: ["parabola_332_example_1"],
            LessonStage.P332_THINK: ["parabola_332_think"],
            LessonStage.P332_EXAMPLE_2: ["parabola_332_example_2"],
        },
        # 3.3.2 正式点出离心率 e=1
        "kg_nodes_eccentricity": ["concept_focus_directrix_unified"],
        "eccentricity_stages": {LessonStage.P332_ECCENTRICITY},
        "summary_kg_nodes": [
            "parabola_definition", "parabola_standard_equation_right",
            "concept_focus_directrix_unified",
        ],
    },
}

# ---- Mandatory VIZ ----
P332_MANDATORY_VIZ = {
    LessonStage.P332_INTRO: {"action": "show_p332_intro"},
    LessonStage.P332_RANGE: {"action": "show_p332_range_setup"},              # 不剧透：曲线无 x≥0 阴影
    LessonStage.P332_SYMMETRY: {"action": "show_p332_symmetry_setup"},        # 不剧透：曲线 + 可拖点，无镜像
    LessonStage.P332_VERTEX: {"action": "show_p332_vertex_setup"},            # 不剧透：候选点，不高亮原点
    LessonStage.P332_ECCENTRICITY: {"action": "show_p332_ecc_setup"},         # 不剧透：F/准线/M 虚线，无比值
    LessonStage.P332_EXAMPLE_1: {"action": "show_p332_example1_setup"},       # 不剧透：点 M + 空轴，无曲线
    LessonStage.P332_THINK: {"action": "show_p332_think_setup"},              # 不剧透：点 M + 空轴，无曲线
    LessonStage.P332_EXAMPLE_2: {"action": "show_p332_example2_setup"},       # 不剧透：曲线 + 题给直线，无 F/A/B/|AB|
    LessonStage.P332_SUMMARY: {"action": "show_p332_summary_compare"},        # solved 版：三曲线统一对比
}

# ---- Skip function ----
def _looks_like_skip_to_example_332(text: str):
    """识别 3.3.2 跳级到 例题1(1) / 思考(2) / 例题2(3) 的意图。返回 1/2/3 或 None。"""
    t = text.replace(" ", "")
    has_skip_intent = any(kw in t for kw in [
        "直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第",
        "看思考", "进入思考", "做题", "看题", "看练习",
    ])
    if has_skip_intent:
        if "例题1" in t or "例1" in t or "例题一" in t or "第一题" in t or "第1题" in t:
            return 1
        if "思考" in t:
            return 2
        if "例题2" in t or "例2" in t or "例题二" in t or "第二题" in t or "第2题" in t:
            return 3
    # 隐式指代
    if "思考" in t and ("几条" in t or "坐标轴" in t):
        return 2
    if any(kw in t for kw in ["焦点弦", "求ab", "求|ab|", "ab的长", "ab长", "弦长"]):
        return 3
    return None



# ---- Stage Dispatch Registry ----
P332_STAGE_DISPATCH = {
    LessonStage.P332_INTRO: ("_handle_p332_intro", {}),
    LessonStage.P332_RANGE: ("_handle_p332_range", {}),
    LessonStage.P332_SYMMETRY: ("_handle_p332_symmetry", {}),
    LessonStage.P332_VERTEX: ("_handle_p332_vertex", {}),
    LessonStage.P332_ECCENTRICITY: ("_handle_p332_eccentricity", {}),
    LessonStage.P332_EXAMPLE_1: ("_handle_p332_example_1", {}),
    LessonStage.P332_THINK: ("_handle_p332_think", {}),
    LessonStage.P332_EXAMPLE_2: ("_handle_p332_example_2", {}),
    LessonStage.P332_SUMMARY: ("_handle_p332_summary", {}),
}


class Parabola332Mixin:
    """抛物线 3.3.2 课 stage handlers（作为 LessonFlow 的 mixin 使用）"""

    def _handle_p332_example_generic(self, text: str, example_key) -> LessonStep:
        """例题1 / 思考 / 例题2 共用。三层判断 + partial 累积 + awaiting_next。"""
        from .example_canonicals_332 import EXAMPLE_CONFIGS_332
        from .example_diagnostician_332 import diagnose_example_332, ExampleDiagnosis332

        if not hasattr(self, "_p332_example_phase_idx"):
            self._p332_example_phase_idx = {1: 0, 2: 0, 3: 0}
            self._p332_example_subflags = {1: set(), 2: set(), 3: set()}

        # awaiting_next 检查
        awaiting_key = getattr(self, "_p332_example_done_awaiting_next", None)
        if awaiting_key is not None:
            if _looks_like_ready_to_continue(text):
                self._p332_example_done_awaiting_next = None
                return self._continue_to_next_p332_example(awaiting_key)
            label = {1: "例题 1", 2: "思考", 3: "例题 2"}[awaiting_key]
            return LessonStep(
                stage=self.stage.value,
                message=f"{label} 已经完成 🎉 看完右边的图后回个『好』/『继续』就切到下一个；想再看图随便拖。",
            )

        # 跨题跳级
        skip = _looks_like_skip_to_example_332(text)
        if skip and skip != example_key:
            return self._jump_to_p332_example(skip)

        config = EXAMPLE_CONFIGS_332[example_key]
        phases = config["phases"]
        idx = self._p332_example_phase_idx[example_key]
        current_phase = phases[idx] if idx < len(phases) else phases[-1]

        # Layer 1: 诊断器扫描所有 goal
        dx = diagnose_example_332(text, example_key)

        # Layer 2: 协议兜底
        if dx is None:
            protocol = self._llm_p332_example_protocol(text, example_key, current_phase)
            if protocol is not None:
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = (protocol.get("ack_text") or "请继续。")[:300]
                skip_n = protocol.get("skip_to_example")

                if diag == "skip_request" and skip_n in (1, 2, 3):
                    return self._jump_to_p332_example(skip_n)

                if diag == "correct" and protocol.get("advance") is True:
                    goal_name = protocol.get("hit_goal")
                    flags = set(config["implies"].get(goal_name, set())) if goal_name else set()
                    if not flags:
                        flags = set(_P332_PHASE_REQUIRED_FLAGS.get((example_key, current_phase), set()))
                    if not flags and goal_name:
                        flags = {f"{goal_name}_done"}
                    dx = ExampleDiagnosis332(
                        hit_goal=goal_name or "", hit_goals=[goal_name] if goal_name else [],
                        implied_flags=flags, label="完全正确（协议）", via="protocol",
                    )
                    # fall through
                elif diag in ("partial", "wrong", "off_topic"):
                    return LessonStep(stage=self.stage.value, message=ack_text)

        # Layer 3: 仍 None → deterministic 提示
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？把你的答案写完整些（坐标写成 (a, b)，方程写成 y²=2px 这样）。",
            )

        # 命中：累积 + 判定收尾或继续节奏
        self._p332_example_subflags[example_key] |= dx.implied_flags
        subflags = self._p332_example_subflags[example_key]

        if config["done_fn"](subflags):
            self._p332_example_phase_idx[example_key] = len(phases)
            return self._advance_p332_example(example_key, ack="✅ 完全正确！")

        # 部分命中：找下一未答完 phase
        next_phase = None
        next_missing: set = set()
        for ph in phases:
            required = _P332_PHASE_REQUIRED_FLAGS.get((example_key, ph), set())
            missing = required - subflags
            if missing:
                next_phase = ph
                next_missing = missing
                break
        if next_phase is None:
            return self._advance_p332_example(example_key, ack="✅ 完全正确！")

        self._p332_example_phase_idx[example_key] = phases.index(next_phase)

        # missing-aware prompt（多-flag phase 内部部分命中 → 精准追问，坑10）
        next_prompt = None
        next_required = _P332_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
        if len(next_missing) == 1 and len(next_required) >= 2:
            single_missing = next(iter(next_missing))
            next_prompt = _P332_PHASE_PROMPT_BY_MISSING.get((example_key, next_phase, single_missing))
        if next_prompt is None:
            next_prompt = _EXAMPLE_STUDENT_PROMPT_332.get((example_key, next_phase), "请继续。")

        # 干净 ack（不暴露内部 goal 名，坑9）
        prefix = "" if next_prompt.startswith("✅") else "✅ 收到。\n\n"
        return LessonStep(stage=self.stage.value, message=prefix + next_prompt)



    def _p332_clear_stuck(self, *keys) -> None:
        """推进过某设问后清零其 stuck 计数。"""
        if hasattr(self, "_p332_stuck"):
            for k in keys:
                self._p332_stuck.pop(k, None)

    # ---- 角色 2：例题/思考路径 2 协议 ----

    def _jump_to_p332_example(self, target_key) -> LessonStep:
        """从任何性质 stage 跳到 例题1(1) / 思考(2) / 例题2(3)。"""
        stage_map = {
            1: (LessonStage.P332_EXAMPLE_1, P332_EXAMPLE_1_INTRO, "show_p332_example1_setup", "例题 1（教材例 3）"),
            2: (LessonStage.P332_THINK,     P332_THINK_INTRO,     "show_p332_think_setup",    "思考"),
            3: (LessonStage.P332_EXAMPLE_2, P332_EXAMPLE_2_INTRO, "show_p332_example2_setup", "例题 2（教材例 4）"),
        }
        if target_key not in stage_map:
            return LessonStep(stage=self.stage.value, message="抱歉，没找到对应的题目。")
        target_stage, intro, viz, label = stage_map[target_key]
        self.stage = target_stage
        if not hasattr(self, "_p332_example_subflags"):
            self._p332_example_subflags = {1: set(), 2: set(), 3: set()}
            self._p332_example_phase_idx = {1: 0, 2: 0, 3: 0}
        self._p332_example_subflags[target_key] = set()
        self._p332_example_phase_idx[target_key] = 0
        self._p332_example_done_awaiting_next = None
        return LessonStep(
            stage=self.stage.value,
            message=f"好的，切到{label}：\n\n" + intro,
            canvas_action={"action": viz},
        )


    def _advance_p332_example(self, example_key, ack: str = "") -> LessonStep:
        """例题/思考通关 → 发 solved viz + awaiting_next。学生确认后才切下一题。"""
        solved_map = {1: "show_p332_example1_solved", 2: "show_p332_think_solved", 3: "show_p332_example2_solved"}
        self._p332_example_done_awaiting_next = example_key
        head = ack + "\n\n" if ack else ""
        tail_map = {
            1: "🎉 例题 1 完成！右边是解答图。回个『好』/『继续』，我们看教材的**思考**题。",
            2: "🎉 思考完成！右边画出了两条抛物线。回个『好』/『继续』，我们做**例题 2**。",
            3: "🎉 例题 2 完成！本节例题 + 思考全部做完。回个『好』/『继续』我们看小结 📒。",
        }
        return LessonStep(
            stage=self.stage.value,
            message=head + tail_map[example_key],
            canvas_action={"action": solved_map[example_key]},
        )


    def _continue_to_next_p332_example(self, completed_key) -> LessonStep:
        """学生确认后真正切到下一题 / SUMMARY。"""
        if completed_key == 1:
            self.stage = LessonStage.P332_THINK
            return LessonStep(stage=self.stage.value, message=P332_THINK_INTRO,
                              canvas_action={"action": "show_p332_think_setup"})
        if completed_key == 2:
            self.stage = LessonStage.P332_EXAMPLE_2
            return LessonStep(stage=self.stage.value, message=P332_EXAMPLE_2_INTRO,
                              canvas_action={"action": "show_p332_example2_setup"})
        # 3 → SUMMARY
        self.stage = LessonStage.P332_SUMMARY
        return LessonStep(stage=self.stage.value, message=P332_SUMMARY_MSG,
                          canvas_action={"action": "show_p332_summary_compare"})

    # ---- 例题/思考通用 handler（仿 _handle_p331_example_generic）----

    def _handle_p332_example_generic(self, text: str, example_key) -> LessonStep:
        """例题1 / 思考 / 例题2 共用。三层判断 + partial 累积 + awaiting_next。"""
        from .example_canonicals_332 import EXAMPLE_CONFIGS_332
        from .example_diagnostician_332 import diagnose_example_332, ExampleDiagnosis332

        if not hasattr(self, "_p332_example_phase_idx"):
            self._p332_example_phase_idx = {1: 0, 2: 0, 3: 0}
            self._p332_example_subflags = {1: set(), 2: set(), 3: set()}

        # awaiting_next 检查
        awaiting_key = getattr(self, "_p332_example_done_awaiting_next", None)
        if awaiting_key is not None:
            if _looks_like_ready_to_continue(text):
                self._p332_example_done_awaiting_next = None
                return self._continue_to_next_p332_example(awaiting_key)
            label = {1: "例题 1", 2: "思考", 3: "例题 2"}[awaiting_key]
            return LessonStep(
                stage=self.stage.value,
                message=f"{label} 已经完成 🎉 看完右边的图后回个『好』/『继续』就切到下一个；想再看图随便拖。",
            )

        # 跨题跳级
        skip = _looks_like_skip_to_example_332(text)
        if skip and skip != example_key:
            return self._jump_to_p332_example(skip)

        config = EXAMPLE_CONFIGS_332[example_key]
        phases = config["phases"]
        idx = self._p332_example_phase_idx[example_key]
        current_phase = phases[idx] if idx < len(phases) else phases[-1]

        # Layer 1: 诊断器扫描所有 goal
        dx = diagnose_example_332(text, example_key)

        # Layer 2: 协议兜底
        if dx is None:
            protocol = self._llm_p332_example_protocol(text, example_key, current_phase)
            if protocol is not None:
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = (protocol.get("ack_text") or "请继续。")[:300]
                skip_n = protocol.get("skip_to_example")

                if diag == "skip_request" and skip_n in (1, 2, 3):
                    return self._jump_to_p332_example(skip_n)

                if diag == "correct" and protocol.get("advance") is True:
                    goal_name = protocol.get("hit_goal")
                    flags = set(config["implies"].get(goal_name, set())) if goal_name else set()
                    if not flags:
                        flags = set(_P332_PHASE_REQUIRED_FLAGS.get((example_key, current_phase), set()))
                    if not flags and goal_name:
                        flags = {f"{goal_name}_done"}
                    dx = ExampleDiagnosis332(
                        hit_goal=goal_name or "", hit_goals=[goal_name] if goal_name else [],
                        implied_flags=flags, label="完全正确（协议）", via="protocol",
                    )
                    # fall through
                elif diag in ("partial", "wrong", "off_topic"):
                    return LessonStep(stage=self.stage.value, message=ack_text)

        # Layer 3: 仍 None → deterministic 提示
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？把你的答案写完整些（坐标写成 (a, b)，方程写成 y²=2px 这样）。",
            )

        # 命中：累积 + 判定收尾或继续节奏
        self._p332_example_subflags[example_key] |= dx.implied_flags
        subflags = self._p332_example_subflags[example_key]

        if config["done_fn"](subflags):
            self._p332_example_phase_idx[example_key] = len(phases)
            return self._advance_p332_example(example_key, ack="✅ 完全正确！")

        # 部分命中：找下一未答完 phase
        next_phase = None
        next_missing: set = set()
        for ph in phases:
            required = _P332_PHASE_REQUIRED_FLAGS.get((example_key, ph), set())
            missing = required - subflags
            if missing:
                next_phase = ph
                next_missing = missing
                break
        if next_phase is None:
            return self._advance_p332_example(example_key, ack="✅ 完全正确！")

        self._p332_example_phase_idx[example_key] = phases.index(next_phase)

        # missing-aware prompt（多-flag phase 内部部分命中 → 精准追问，坑10）
        next_prompt = None
        next_required = _P332_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
        if len(next_missing) == 1 and len(next_required) >= 2:
            single_missing = next(iter(next_missing))
            next_prompt = _P332_PHASE_PROMPT_BY_MISSING.get((example_key, next_phase, single_missing))
        if next_prompt is None:
            next_prompt = _EXAMPLE_STUDENT_PROMPT_332.get((example_key, next_phase), "请继续。")

        # 干净 ack（不暴露内部 goal 名，坑9）
        prefix = "" if next_prompt.startswith("✅") else "✅ 收到。\n\n"
        return LessonStep(stage=self.stage.value, message=prefix + next_prompt)


    def _handle_p332_example_1(self, text: str) -> LessonStep:
        return self._handle_p332_example_generic(text, 1)


    def _handle_p332_think(self, text: str) -> LessonStep:
        return self._handle_p332_example_generic(text, 2)


    def _handle_p332_example_2(self, text: str) -> LessonStep:
        return self._handle_p332_example_generic(text, 3)

    # ---- 性质短答 + 开场/总结 handler ----

    def _handle_p332_intro(self, text: str) -> LessonStep:
        """1. 开场：学生任意回应即推进 RANGE（确定性）。"""
        skip = _looks_like_skip_to_example_332(text)
        if skip:
            return self._jump_to_p332_example(skip)
        self.stage = LessonStage.P332_RANGE
        return LessonStep(stage=self.stage.value, message=P332_RANGE_MSG,
                          canvas_action={"action": "show_p332_range_setup"})


    def _handle_p332_range(self, text: str) -> LessonStep:
        """2. 范围：2 要素（x≥0 / y∈R）partial 累积。推进=确定性；反馈=角色3 阶梯。"""
        skip = _looks_like_skip_to_example_332(text)
        if skip:
            return self._jump_to_p332_example(skip)
        if not hasattr(self, "_p332_range_done"):
            self._p332_range_done = set()
        done = self._p332_range_done
        # Layer 1 关键词
        if _looks_like_p332_range_x(text):
            done.add("x")
        if _looks_like_p332_range_y(text):
            done.add("y")
        # Layer 2 角色 1 enum 兜底（只分类不驱动状态）
        if not {"x", "y"}.issubset(done):
            hit = self._resolve_phase_answer(text, "p332_range", lambda _t: None)[0]
            if hit == "x_range":
                done.add("x")
            elif hit == "y_range":
                done.add("y")
            elif hit == "both":
                done.update({"x", "y"})
        self._p332_range_done = done
        # 两要素齐 → 推进 SYMMETRY（确定性转场）
        if {"x", "y"}.issubset(done):
            self._p332_clear_stuck("range_x", "range_y", "range_both")
            self._p332_range_done = set()
            self.stage = LessonStage.P332_SYMMETRY
            return LessonStep(stage=self.stage.value, message=P332_RANGE_DONE_MSG,
                              canvas_action=[{"action": "show_p332_range_solved"},
                                             {"action": "show_p332_symmetry_setup"}])
        # 只答 x → 表扬 x、追问 y（坑10）
        if "x" in done:
            sub = ("学生已答对 x 的范围（x≥0），还差 **y 的范围**：方程 y²=2px 里 y² 可取任意非负值，"
                   "所以 y 取遍全体实数 y∈R。引导他想 y 有没有限制，不要直接给出。")
            fb = "✅ $x$ 的范围对了（$x\\ge 0$）。那 **$y$ 的范围**呢？方程里 $y$ 受不受限制？"
            return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "range_y", sub, fb))
        # 只答 y → 表扬 y、追问 x（坑10）
        if "y" in done:
            sub = ("学生已答对 y 的范围（y∈R），还差 **x 的范围**：由 y²=2px≥0、p>0 得 x≥0。"
                   "引导他从 y²≥0 推 x，不要直接给出。")
            fb = "✅ $y\\in\\mathbb{R}$ 对了。那 **$x$ 的范围**呢？由 $y^2=2px\\ge 0$、$p>0$ 能推出 $x$ 满足什么？"
            return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "range_x", sub, fb))
        # 都没答 → 角色3 提示
        sub = ("学生在想抛物线 y²=2px(p>0) 的范围（x、y 各自取值）。正确：由 y²≥0、p>0 得 x≥0；y 取遍全体实数。"
               "引导他往这两点想，不要直接给出。")
        fb = ("提示：抛物线 $y^2=2px\\,(p>0)$。因为 $y^2\\ge 0$，由方程能推出 $x$ 的范围；"
              "而 $y$ 有没有限制？（$x$、$y$ 两个都要说）")
        return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "range_both", sub, fb))


    def _handle_p332_symmetry(self, text: str) -> LessonStep:
        """3. 对称性：仅 x 轴；纠正「有对称中心」误区。推进=确定性；反馈=角色3。"""
        skip = _looks_like_skip_to_example_332(text)
        if skip:
            return self._jump_to_p332_example(skip)
        has_xaxis = _looks_like_p332_sym_xaxis(text)
        misconception = _looks_like_p332_sym_center_misconception(text)
        # Layer 2 enum 兜底
        if not has_xaxis:
            hit = self._resolve_phase_answer(text, "p332_symmetry", lambda _t: None)[0]
            if hit == "x_axis":
                has_xaxis = True
            elif hit == "center_misconception":
                misconception = True
        # 答对 x 轴 → 推进（若兼有对称中心误区，转场里温和纠正）
        if has_xaxis:
            self._p332_clear_stuck("sym")
            self.stage = LessonStage.P332_VERTEX
            if misconception:
                msg = ("✅ 关于 $x$ 轴对称这点对了。不过纠正一下：抛物线**没有对称中心**，"
                       "它只关于 $x$ 轴（轴）对称——这和椭圆/双曲线不同。\n\n" + P332_SYMMETRY_VERTEX_Q)
            else:
                msg = P332_SYMMETRY_DONE_MSG
            return LessonStep(stage=self.stage.value, message=msg,
                              canvas_action=[{"action": "show_p332_symmetry_solved"},
                                             {"action": "show_p332_vertex_setup"}])
        # 误区：以为有对称中心 → 角色3 纠正（不推进）
        if misconception:
            sub = ("学生以为抛物线像椭圆/双曲线那样有对称中心或关于 y 轴对称。纠正：以 -x 代 x 方程会变（开口反向），"
                   "故抛物线**不**关于 y 轴、也**没有**对称中心；只有以 -y 代 y 不变，故只关于 x 轴对称。温和纠正并引导重答。")
            fb = ("🤔 抛物线其实**没有**对称中心哦。试试：把方程里的 $x$ 换成 $-x$，方程变不变？"
                  "再把 $y$ 换成 $-y$ 呢？由此抛物线只关于哪条线对称？")
            return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "sym", sub, fb))
        # 没答到 → 角色3 提示
        sub = ("学生在判断抛物线 y²=2px 的对称性。正确：以 -y 代 y 方程不变 → 关于 x 轴对称；"
               "以 -x 代 x 方程改变 → 不关于 y 轴、无对称中心。引导他用代换法想，不要直接给出。")
        fb = "提示：把方程 $y^2=2px$ 里的 $y$ 换成 $-y$，方程变不变？变不变说明它关于哪条线对称？"
        return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "sym", sub, fb))


    def _handle_p332_vertex(self, text: str) -> LessonStep:
        """4. 顶点：唯一=原点。推进=确定性；反馈=角色3。"""
        skip = _looks_like_skip_to_example_332(text)
        if skip:
            return self._jump_to_p332_example(skip)
        has_origin = _looks_like_p332_vertex_origin(text)
        if not has_origin:
            hit = self._resolve_phase_answer(text, "p332_vertex", lambda _t: None)[0]
            if hit == "origin":
                has_origin = True
        if has_origin:
            self._p332_clear_stuck("vertex")
            self.stage = LessonStage.P332_ECCENTRICITY
            return LessonStep(stage=self.stage.value, message=P332_VERTEX_DONE_MSG,
                              canvas_action=[{"action": "show_p332_vertex_solved"},
                                             {"action": "show_p332_ecc_setup"}])
        sub = ("学生在找抛物线 y²=2px 的顶点。正确：顶点 = 抛物线与轴(x轴)的交点；令 x=0 得 y=0，"
               "故顶点是原点 (0,0)，只有 1 个。引导他令 x=0 想，不要直接给出。")
        fb = "提示：顶点是抛物线与它的轴（$x$ 轴）的交点。在 $y^2=2px$ 中令 $x=0$ 得什么点？这样的顶点有几个？"
        return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "vertex", sub, fb))


    def _handle_p332_eccentricity(self, text: str) -> LessonStep:
        """5. 离心率：e=1。推进=确定性；反馈=角色3。答对后进入例题 1。"""
        skip = _looks_like_skip_to_example_332(text)
        if skip:
            return self._jump_to_p332_example(skip)
        has_e1 = _looks_like_p332_ecc_1(text)
        if not has_e1:
            hit = self._resolve_phase_answer(text, "p332_eccentricity", lambda _t: None)[0]
            if hit == "e_equals_1":
                has_e1 = True
        if has_e1:
            self._p332_clear_stuck("ecc")
            self.stage = LessonStage.P332_EXAMPLE_1
            if not hasattr(self, "_p332_example_phase_idx"):
                self._p332_example_phase_idx = {1: 0, 2: 0, 3: 0}
                self._p332_example_subflags = {1: set(), 2: set(), 3: set()}
            return LessonStep(stage=self.stage.value,
                              message=P332_ECC_DONE_MSG + "\n\n" + P332_EXAMPLE_1_INTRO,
                              canvas_action=[{"action": "show_p332_ecc_solved"},
                                             {"action": "show_p332_example1_setup"}])
        sub = ("学生在求抛物线的离心率。正确：由抛物线定义，动点到焦点距离 |MF| = 到准线距离 d，"
               "所以 e=|MF|/d=1。引导他回忆定义里 |MF| 和 d 的关系，不要直接报 1。")
        fb = ("提示：离心率 $e=\\dfrac{|MF|}{d}$。回忆抛物线的**定义**——点到焦点的距离 $|MF|$ "
              "和到准线的距离 $d$ 是什么关系？所以 $e=?$")
        return LessonStep(stage=self.stage.value, message=self._p332_socratic(text, "ecc", sub, fb))


    def _handle_p332_summary(self, text: str) -> LessonStep:
        """9. 总结。deterministic 结课。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "👏 恭喜完成 3.3.2 课程！\n\n"
                    "你已掌握抛物线的 4 条几何性质（范围、对称性、顶点、离心率），"
                    "以及三曲线离心率的统一（$e<1$ 椭圆 / $e=1$ 抛物线 / $e>1$ 双曲线）。\n\n"
                    "[LESSON_END]"
                ),
            )
        return LessonStep(
            stage=self.stage.value,
            message="还有什么问题想问？或者输入「结束」结课。",
        )

    # ================================================================


