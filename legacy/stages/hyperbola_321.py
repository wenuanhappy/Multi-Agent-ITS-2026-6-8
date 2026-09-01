"""双曲线 3.2.1 双曲线及其标准方程 —— stage handlers + 静态数据"""
import re
from typing import Any, Dict, List, Optional
from legacy.lesson_flow import LessonStage, LessonStep

# ---- 静态文本 ----

H321_INTRO_MSG = (
    "你好！上节课我们一起探索了**椭圆** —— 平面内到两个定点距离的『**和**』为定值的点的轨迹。\n\n"
    "本节我们类比椭圆的研究方法，研究**双曲线**：\n"
    "（教材开场：双曲线也具有广泛应用，如发电厂冷却塔的外形、通过声音时差测定信号源等。）\n\n"
    "在动手前，先回顾一下：**椭圆的定义**是什么？请用自己的话说一遍。"
)

H321_PROBE_DIFFERENCE_MSG = (
    "很好！椭圆是「到两个定点 $F_1, F_2$ 的**距离之和**为常数」的轨迹。\n\n"
    "现在我们来做一个**自然的变奏**：把『和』换成『**差**』。\n\n"
    "**先猜一下**：平面内到两个定点 $F_1, F_2$ 的**距离之差**为常数的点的轨迹，会是什么形状？\n"
    "（不知道也没关系，待会儿动手画一画就清楚了。）"
)

H321_EXPLORE_LOCUS_MSG = (
    "我们用**教材 p118 探究**来动手验证（先看图 3.2-1 椭圆铺垫）。\n\n"
    "右边画布**上方**有直线 $l$，上面有定点 $A, B$ 和**可拖动**的动点 $P$"
    "（约束：$P$ 只能在 $A, B$ **之间**滑动）。\n"
    "**下方平面**有定点 $F_1, F_2$（这里 $|F_1F_2| < |AB|$）。\n\n"
    "系统会自动以 $F_1$ 为圆心、$|PA|$ 为半径作圆，以 $F_2$ 为圆心、$|PB|$ 为半径作圆。"
    "**两圆的交点 $M$（橙）、$M'$（绿）就是轨迹点**。\n\n"
    "**任务**：在直线上拖动 $P$ 滑遍 $AB$，观察 $M, M'$ 累积出什么轨迹？"
    "（这是上节课刚学的图形，回忆一下。）"
)

# v3.39 EXPLORE_LOCUS 拆 2 phase：先椭圆铺垫，再切换到双曲线模型
H321_EXPLORE_HYP_PHASE_MSG = (
    "✅ 没错，$P$ 在 $AB$ 内滑动时，$M$ 满足 $|MF_1|+|MF_2|=|AB|$（常数），轨迹是**椭圆**。\n\n"
    "🔑 **关键观察**：这里我们用的是 $|F_1F_2|<|AB|$ 的几何条件。\n\n"
    "现在我们**调整参数**（**教材图 3.2-2**）：把 $|F_1F_2|$ 拉大、把 $|AB|$ 缩小，"
    "让 $|F_1F_2| > |AB|$，并且**放开 $P$ 的约束**——$P$ 可以在直线 $l$ 上**自由滑动**"
    "（包括 $A, B$ **之外**的位置）。\n\n"
    "**任务**：拖动 $P$，特别是把它拖到 $B$ 右边、$A$ 左边，看 $M, M'$ 累积出什么？\n"
    "拖完后告诉我：**$M, M'$ 的轨迹是几条曲线？**"
)

H321_AWAIT_SHAPE_NAME_MSG = (
    "漂亮！你画出了一条由**两支**组成的、关于原点对称的曲线。\n\n"
    "**你觉得这是什么图形？** 试着说出它的名字。"
)

H321_AWAIT_DEFINITION_MSG = (
    "完全正确！这就是**双曲线** 🌀\n\n"
    "现在请你**类比椭圆**，用自己的话归纳出双曲线的定义。\n"
    "（提示：椭圆是「距离之**和**为常数」，那双曲线呢？）"
)

# v3.38 拆 AWAIT_DEFINITION 为 2 phase：先追问"绝对值"，再追问约束 2a<2c
H321_AWAIT_DEF_ABS_NUDGE_MSG = (
    "✅ 你抓住了「**差**」这个核心 —— 这是从椭圆的「和」类比过来的关键变化。\n\n"
    "但还有一个**细节**值得想想 🤔\n\n"
    "你刚才拖动 $P$ 时（或回忆教材图 3.2-2）：动点 $M$ 在**右支**上时 $|MF_1|>|MF_2|$，"
    "在**左支**上时 $|MF_2|>|MF_1|$。\n\n"
    "**追问**：如果定义里只写「$|MF_1|-|MF_2|=$ 常数」（**不加绝对值**），"
    "那 $|MF_2|>|MF_1|$ 的那一支会满足这个定义吗？\n\n"
    "再重说一遍定义，看看要不要补点什么？"
)

H321_AWAIT_DEF_CONSTRAINT_MSG = (
    "✅ 完全正确！必须是 $\\bigl||MF_1|-|MF_2|\\bigr|$（**差的绝对值**），才能把**两支**都囊括进来。\n\n"
    "现在还剩最后一个**约束**要想清楚 —— 这个「常数 $2a$」要和**焦距 $|F_1F_2|=2c$** 满足什么关系？\n\n"
    "🤔 **试着想**：\n"
    "- 如果 $2a = 2c$ 会怎样？\n"
    "- 如果 $2a > 2c$ 会怎样？\n"
    "- 那 $2a$ 应该满足 $2a \\;?\\; 2c$？"
)

H321_REFLECT_COORD_MSG = (
    "✅ 完全正确！必须 $0 < 2a < 2c$（即 $a < c$）才能保证轨迹是双曲线。\n"
    "（边界情形：$2a = 2c$ 时退化为射线/线段，$2a > 2c$ 时无轨迹 —— 课末总结再回看。）\n\n"
    "至此我们得到了完整的**双曲线定义**（教材 p119）：\n\n"
    "> 一般地，平面内与两个定点 $F_1, F_2$ 的**距离的差的绝对值**等于**非零常数**"
    "（小于 $|F_1F_2|$）的点的轨迹叫做**双曲线**(hyperbola)。\n"
    "> - $F_1, F_2$ 叫做双曲线的**焦点**\n"
    "> - $|F_1F_2|$ 叫做双曲线的**焦距**（记作 $2c$）\n"
    "> - 距离差的绝对值记作 $2a$（$a < c$，与椭圆 $a > c$ 相反！）\n\n"
    "🟣 **思考 1**：类比椭圆，怎样建立坐标系，使得双曲线的方程最简单？"
)

H321_DERIVE_INTRO_MSG = (
    "完美！我们选 $F_1F_2$ 所在直线为 $x$ 轴，$F_1F_2$ 的中垂线为 $y$ 轴，"
    "原点 $O$ 在 $F_1F_2$ 中点。\n\n"
    "设 $M(x, y)$ 是双曲线上任意一点，$|F_1F_2|=2c$，则 $F_1(-c,0), F_2(c,0)$，"
    "且 $\\bigl||MF_1|-|MF_2|\\bigr|=2a\\,(0<2a<2c)$。\n\n"
    "**第一步**：用距离公式，写出 $|MF_1|$ 和 $|MF_2|$。"
)

H321_INTRODUCE_B_DEFINE_MSG = (
    "✅ 推导完成。我们得到：\n"
    "$$\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$$\n\n"
    "由 $c>a>0$，所以 $c^2-a^2>0$。**类比椭圆**，令 $b^2=c^2-a^2$（$b>0$）。\n\n"
    "✋ **重要对比**：椭圆里令 $b^2=a^2-c^2$，双曲线里换成了 $b^2=c^2-a^2$ —— **方向刚好相反**！\n\n"
    "代入得到**双曲线的标准方程**（教材 p119）：\n"
    "$$\\boxed{\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1\\,(a>0,\\,b>0)}$$\n\n"
    "参数关系：$\\boxed{c^2=a^2+b^2}$（椭圆是 $a^2=b^2+c^2$，也是反的）\n\n"
    "**练一下**：你能写出焦点坐标 $F_1, F_2$ 吗？"
)

H321_INTRODUCE_B_YAXIS_MSG = (
    "正确，焦点在 $x$ 轴时 $F_1(-c, 0), F_2(c, 0)$。\n\n"
    "🟣 **思考 2**（教材 p120）：类比焦点在 $y$ 轴的椭圆，**焦点在 $y$ 轴的双曲线**的标准方程是什么？\n"
    "（提示：把 $x$ 与 $y$ 互换试试。）"
)

# ── H321_EXAMPLE 题目 hard-coded（教材原题，禁止改任何数值）──
H321_EXAMPLE_1_INTRO = (
    "🟡 **例 1**（教材 p120 例 1）\n\n"
    "已知双曲线的两个焦点分别为 $F_1(-5, 0), F_2(5, 0)$，双曲线上一点 $P$ 到 $F_1, F_2$ 的"
    "**距离的差的绝对值等于 6**，求双曲线的标准方程。\n\n"
    "**第一步**：根据焦点位置，双曲线的标准方程应该是**什么形式**？"
)

H321_EXAMPLE_2_INTRO = (
    "🟡 **例 2**（教材 p120 例 2）\n\n"
    "已知 $A, B$ 两地相距 $800\\,\\mathrm{m}$，在 $A$ 地听到炮弹爆炸声响**比 $B$ 地晚 2 s**，"
    "声速 $340\\,\\mathrm{m/s}$，求炮弹爆炸点的轨迹方程。\n\n"
    "**第一步**：根据声响时间差和声速，爆炸点 $P$ 到 $A, B$ 两地的**距离差** "
    "$|PA|-|PB|$ 是多少？（注意 $A$ 是『晚听到』，$P$ 离 $A$ 更远还是更近？）"
)

H321_EXPLORATION_INTRO = (
    "🔍 **探究**（教材 p121）—— 与 3.1.1 例 3 对比\n\n"
    "点 $A, B$ 的坐标分别为 $(-5, 0), (5, 0)$，直线 $AM, BM$ 相交于点 $M$，"
    "且它们的**斜率之积是 $\\dfrac{4}{9}$**，求点 $M$ 的轨迹方程。\n\n"
    "⚠️ 对比 3.1.1 例 3：那里斜率积是 $-\\dfrac{4}{9}$（得椭圆），这里是 $+\\dfrac{4}{9}$"
    "（猜猜会得到什么图形？）\n\n"
    "**第一步**：直线 $AM$ 的斜率 $k_{AM}$ 与直线 $BM$ 的斜率 $k_{BM}$ "
    "用 $(x, y)$ 怎么表示？"
)

H321_SUMMARY_MSG = (
    "🎓 **3.2.1 总结**：椭圆 vs 双曲线对照\n\n"
    "| 概念 | 椭圆 (3.1.1) | 双曲线 (3.2.1) |\n"
    "|---|---|---|\n"
    "| 定义 | 距离之**和** $=2a$ | 距离之**差的绝对值** $=2a$ |\n"
    "| 常数约束 | $2a>|F_1F_2|$（$a>c$）| $2a<|F_1F_2|$（$a<c$）|\n"
    "| 标准方程 | $\\frac{x^2}{a^2}+\\frac{y^2}{b^2}=1$ | $\\frac{x^2}{a^2}-\\frac{y^2}{b^2}=1$ |\n"
    "| $b$ 的定义 | $b^2=a^2-c^2$ | $b^2=c^2-a^2$ |\n"
    "| 参数关系 | $a^2=b^2+c^2$ | $c^2=a^2+b^2$ |\n"
    "| 图形 | 一条封闭曲线 | **两支**对称曲线 |\n\n"
    "**下一节（3.2.2）双曲线的简单几何性质**：范围、对称性、顶点（实轴/虚轴）、**渐近线**（双曲线特有！）、"
    "**离心率 $e>1$**（与椭圆 $0<e<1$ 互补）。\n\n"
    "如果都明白了，回个『没问题』/『结束』我们就到这里。"
)


# ---- Skip function ----

def _looks_like_skip_to_example_321(text: str):
    """识别学生「直接跳到例 N / 探究」意图。
    返回 1 / 2 / 'exploration' / None。"""
    t = text.replace(" ", "")
    has_skip_intent = any(kw in t for kw in ["直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第", "看探究", "进入探究", "跳到探究"])
    has_exploration_kw = any(kw in t for kw in ["探究"])
    if has_exploration_kw and any(kw in t for kw in ["看", "跳到", "进入", "直接"]):
        return "exploration"
    if not has_skip_intent:
        return None
    if "例1" in t or "例一" in t or "第一题" in t or "第1题" in t:
        return 1
    if "例2" in t or "例二" in t or "第二题" in t or "第2题" in t:
        return 2
    return None


# ---- Stage Goals ----

H321_STAGE_GOALS = {
    LessonStage.H321_INTRO: (
        "📒 双曲线开场阶段。学生听完开场词后回忆椭圆定义。\n"
        "学生答出椭圆相关关键词（定点 / 距离 / 和 / 焦点 / 常数）≥1 个即推进 RECALL_ELLIPSE。\n"
        "**严禁**：剧透双曲线答案。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_RECALL_ELLIPSE: (
        "📒 等学生答出椭圆定义。检测关键词：距离之和 / 常数 / 焦点 / 椭圆。\n"
        "命中 ≥1 个即推进到 PROBE_DIFFERENCE。\n"
        "**严禁**：剧透双曲线"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_PROBE_DIFFERENCE: (
        "🔵 开放预测：学生预测「差等于常数」会画出什么形状。\n"
        "三种应答类型：\n"
        "  · 学生说『不知道』→ 安慰他『没关系，动手画就清楚了』\n"
        "  · 学生猜了形状（双曲线 / 两条曲线 / 鞍形 等）→ 肯定『不错的猜想』，但**不评判对错**\n"
        "  · 学生答非所问 → 温和拉回画布探究\n"
        "无论哪种应答，系统都会推进到 EXPLORE_LOCUS。\n"
        "**严禁**：在此 stage 直接确认或否定『双曲线』答案。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_EXPLORE_LOCUS: (
        "🔵 教材 p118 双圆模型探究。v3.39 拆 2 phase：\n"
        "  · phase=ellipse_recap：发椭圆模型 viz（$|F_1F_2|<|AB|$，$P$ 限 $AB$ 内）。\n"
        "      学生答出『椭圆』→ 切到 hyperbola_explore phase + 发双曲线模型 viz。\n"
        "      此 phase **严禁**提『双曲线』『两条』，学生说时拉回观察椭圆铺垫。\n"
        "  · phase=hyperbola_explore：切到双曲线模型 viz（$|F_1F_2|>|AB|$，$P$ 自由）。\n"
        "      学生答出『两条/双曲线/两支』→ 推进 AWAIT_SHAPE_NAME 或 AWAIT_DEFINITION。\n"
        "**严禁**：在 ellipse_recap 中剧透双曲线。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_AWAIT_SHAPE_NAME: (
        "👀 学生画完两支曲线，等他说出名字『双曲线』。\n"
        "学生说出『双曲线 / hyperbola』即推进。\n"
        "答不上来时提示：『这个图形有两支，在数学里以「双」字开头…』\n"
        "**严禁**：直接告诉答案。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_AWAIT_DEFINITION: (
        "🧩 学生用自己的话归纳双曲线定义。v3.38 拆 2 phase：\n"
        "  · phase=await_abs：等学生答出含「**绝对值**」的定义。\n"
        "      - 学生答『差等于常数』但缺绝对值 → 苏格拉底追问（让他想两支对称性）\n"
        "      - 学生答含绝对值 → 推进 await_constraint\n"
        "  · phase=await_constraint：等学生答出 $2a < 2c$ 的不等约束。\n"
        "      - 学生答出 → 推进 REFLECT_COORD\n"
        "      - 学生提到边界情形（=会射线/>无轨迹）→ 引导回不等关系\n"
        "**严禁**：直接给完整定义文本（约束 $2a<2c$ 由 REFLECT_COORD 入口显示）。\n"
        "**严禁**：剧透定义里的『非零常数』『小于 $|F_1F_2|$』——让学生自己说出。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_REFLECT_COORD: (
        "🟣 思考1：怎样建立坐标系？\n"
        "期望答案：$F_1F_2$ 所在直线为 $x$ 轴，$F_1F_2$ 中垂线为 $y$ 轴。\n"
        "学生答出『焦点连线作 $x$ 轴』即可推进。\n"
        "学生只说『有对称性 / 对称轴』→ 苏格拉底追问『$x$ 轴具体放哪』。\n"
        "**严禁**：提前给标准方程。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_DERIVE_AND_RESULT: (
        "🧩 推导阶段。终点 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$。**全程不引入 $b$**。\n"
        "本阶段 3 phase 由 _H321_DERIVE_PHASE_GOALS 替换。\n"
        "**严禁**：替学生跳步、提及 $b$、提及离心率/渐近线（属 3.2.2）。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_INTRODUCE_B: (
        "🧩 引入 $b$ + 思考 2 阶段。\n"
        "本阶段 2 phase 由 _H321_INTRODUCE_B_PHASE_GOALS 替换。\n"
        "**关键对比**：椭圆 $b^2=a^2-c^2$，双曲线 $b^2=c^2-a^2$（反向）。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
    ),
    LessonStage.H321_EXAMPLE_1: (
        "🟡 例 1（教材 p120 例 1）：焦点 $(\\pm 5, 0)$，距离差绝对值=6 → $\\dfrac{x^2}{9}-\\dfrac{y^2}{16}=1$。\n"
        "3 phase：ask_form（焦点位置 → 标准方程形式）→ ask_ab（$a=3, b^2=16$）→ ask_equation。\n"
        "phase_goal 由 example_canonicals_321.EXAMPLE_1_PHASE_GOAL 控制。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
        "\n\n**铁律：不得捏造、改写或补充教材原题数值、题干文字、标准答案。**"
        "如果不确定，先原样复述题目，等学生给出答案后逐步核对。"
    ),
    LessonStage.H321_EXAMPLE_2: (
        "🟡 例 2（教材 p120 例 2）：声学应用，A 晚 2 s → 右支 $x \\ge 340$。\n"
        "3 phase：ask_setup（$2a=680$）→ ask_ab（$a=340, b^2=44400$）→ ask_equation_with_branch（方程+右支）。\n"
        "**题目原文（铁律：不得改『晚』为『早』，不得改任何数值）**：A、B 两地相距 800 m，A 地听到炮弹声响比 B 地**晚** 2 s，声速 340 m/s。\n"
        "答案：$\\dfrac{x^2}{115600}-\\dfrac{y^2}{44400}=1\\,(x\\ge 340)$。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
        "\n\n**铁律：不得捏造、改写或补充教材原题数值、题干文字、标准答案。**"
        "如果不确定，先原样复述题目，等学生给出答案后逐步核对。"
    ),
    LessonStage.H321_EXPLORATION: (
        "🔍 探究（教材 p121）：A(-5,0), B(5,0), 斜率积 $\\dfrac{4}{9}$ → $\\dfrac{x^2}{25}-\\dfrac{y^2}{100/9}=1\\,(x\\ne\\pm 5)$。\n"
        "3 phase：ask_slopes（$k_{AM}=\\dfrac{y}{x+5}, k_{BM}=\\dfrac{y}{x-5}$）→ ask_simplify（化简）→ ask_constraint（$x\\ne\\pm 5$）。\n"
        "**结构对比**：3.1.1 例 3 是斜率积 $-\\dfrac{4}{9}$（椭圆），本探究是 $+\\dfrac{4}{9}$（双曲线）。\n"
        "**题目原文（铁律：不得修改）**：点 A、B 坐标分别为 $(-5,0), (5,0)$，直线 AM、BM 相交于点 M，斜率之积是 $\\dfrac{4}{9}$。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
        "\n\n**铁律：不得捏造、改写或补充教材原题数值、题干文字、标准答案。**"
        "如果不确定，先原样复述题目，等学生给出答案后逐步核对。"
    ),
    LessonStage.H321_SUMMARY: (
        "📒 3.2.1 总结阶段。回顾双曲线全部内容，与椭圆对比。预告 3.2.2（实轴/虚轴/渐近线/离心率）。\n"
        "学生说『没问题』/『结束』时附加 [LESSON_END] 标记。"
        "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。"
        "\n\n**铁律：不得捏造、改写或补充教材原题数值、题干文字、标准答案。**"
        "如果不确定，先原样复述题目，等学生给出答案后逐步核对。"
    ),
}


# ---- Course Config ----

H321_COURSE_CONFIG = {
    "hyperbola_321": {
        "name_cn": "3.2.1 双曲线及其标准方程",
        "scope": "hyperbola",
        "first_stage": LessonStage.H321_INTRO,
        "start_stage": LessonStage.H321_RECALL_ELLIPSE,
        "kg_nodes_basic": [
            "foundation_distance_formula", "foundation_locus",
            "hyperbola_definition", "hyperbola_parameter_triangle",
        ],
        "kg_nodes_equation": [
            "hyperbola_standard_equation_x", "hyperbola_standard_equation_y",
        ],
        "kg_nodes_examples": {
            LessonStage.H321_EXAMPLE_1: ["hyperbola_321_example_1"],
            LessonStage.H321_EXAMPLE_2: ["hyperbola_321_example_2"],
            LessonStage.H321_EXPLORATION: ["hyperbola_321_exploration"],
        },
        # 3.2.1 不涉及离心率（属于 3.2.2），保持空集
        "kg_nodes_eccentricity": [],
        "eccentricity_stages": set(),
        "summary_kg_nodes": [
            "hyperbola_definition", "hyperbola_standard_equation_x",
            "hyperbola_parameter_triangle",
        ],
    },
}


# ---- Mandatory VIZ ----

H321_MANDATORY_VIZ = {
    # ---- v3.37 新增：双曲线 3.2.1 课，13 stage 的入口强制 viz ----
    # INTRO/RECALL_ELLIPSE/PROBE_DIFFERENCE 不出画布，让学生先思考
    # v3.39: EXPLORE_LOCUS 拆 2 phase
    #   · phase=ellipse_recap：入口发椭圆模型 viz（教材图 3.2-1，|F1F2|<|AB|，P 限 AB 内）
    #   · phase=hyperbola_explore：切到双曲线模型（教材图 3.2-2，|F1F2|>|AB|，P 自由）
    #     (双曲线模型 viz 由 _handle_h321_explore_locus 主动发，不在 mandatory_viz 表里)
    LessonStage.H321_EXPLORE_LOCUS: {"action": "init_h321_two_circles_ellipse", "config": {"F1": [-1.5, 0], "F2": [1.5, 0], "A": [-3, 4], "B": [3, 4], "line_y": 4}},
    LessonStage.H321_DERIVE_AND_RESULT: {"action": "show_h321_derivation_steps"},
    LessonStage.H321_INTRODUCE_B: {"action": "show_h321_abc_triangle_setup"},
    # 例题/探究入口：setup 版（不剧透）
    LessonStage.H321_EXAMPLE_1:    {"action": "show_h321_example_1_setup"},
    LessonStage.H321_EXAMPLE_2:    {"action": "show_h321_example_2_setup"},
    LessonStage.H321_EXPLORATION:  {"action": "show_h321_exploration_setup"},
}


# ---- Stage Dispatch Registry ----

H321_STAGE_DISPATCH = {
    LessonStage.H321_INTRO: ("_handle_h321_intro", {}),
    LessonStage.H321_RECALL_ELLIPSE: ("_handle_h321_recall_ellipse", {}),
    LessonStage.H321_PROBE_DIFFERENCE: ("_handle_h321_probe_difference", {}),
    LessonStage.H321_EXPLORE_LOCUS: ("_handle_h321_explore_locus", {}),
    LessonStage.H321_AWAIT_SHAPE_NAME: ("_handle_h321_await_shape_name", {}),
    LessonStage.H321_AWAIT_DEFINITION: ("_handle_h321_await_definition", {}),
    LessonStage.H321_REFLECT_COORD: ("_handle_h321_reflect_coord", {}),
    LessonStage.H321_DERIVE_AND_RESULT: ("_handle_h321_derive_and_result", {}),
    LessonStage.H321_INTRODUCE_B: ("_handle_h321_introduce_b", {}),
    LessonStage.H321_EXAMPLE_1: ("_handle_h321_example_1", {}),
    LessonStage.H321_EXAMPLE_2: ("_handle_h321_example_2", {}),
    LessonStage.H321_EXPLORATION: ("_handle_h321_exploration", {}),
    LessonStage.H321_SUMMARY: ("_handle_h321_summary", {}),
}


class Hyperbola321Mixin:
    """双曲线 3.2.1 课 stage handlers"""

    def _jump_to_h321_example(self, target_key) -> LessonStep:
        """从任何 stage 跳到例 1 / 例 2 / 探究。"""
        stage_map = {
            1: (LessonStage.H321_EXAMPLE_1, H321_EXAMPLE_1_INTRO),
            2: (LessonStage.H321_EXAMPLE_2, H321_EXAMPLE_2_INTRO),
            "exploration": (LessonStage.H321_EXPLORATION, H321_EXPLORATION_INTRO),
        }
        if target_key not in stage_map:
            return LessonStep(stage=self.stage.value, message="抱歉，没找到对应的例题/探究。")
        target_stage, intro = stage_map[target_key]
        self.stage = target_stage
        viz = H321_MANDATORY_VIZ.get(target_stage)
        label = "探究" if target_key == "exploration" else f"例 {target_key}"
        return LessonStep(
            stage=self.stage.value,
            message=f"好的，切到{label}（教材 3.2.1 节原题）：\n\n" + intro,
            canvas_action=viz,
        )

    def _advance_h321_example(self, example_key, ack: str = "") -> LessonStep:
        """例题/探究通关 → 发 solved viz + awaiting_next。学生确认后才切下一题。"""
        solved_name = "exploration" if example_key == "exploration" else f"example_{example_key}"
        solved_action = {"action": f"show_h321_{solved_name}_solved"}
        actions: List[Dict[str, Any]] = [solved_action]
        # 例 2 / 探究 通关后还有 explore 交互（拖点感受恒等式）
        if example_key in (2, "exploration"):
            actions.append({"action": f"show_h321_{solved_name}_explore"})

        self._h321_example_done_awaiting_next = example_key
        label = "探究" if example_key == "exploration" else f"例 {example_key}"
        head = ack + "\n\n" if ack else ""
        if example_key == "exploration":
            tail = f"🎉 {label} 完成！\n\n本节内容（例 1 / 例 2 / 探究）全部做完。准备好了回个「好」/「继续」我们看本课总结 📒。"
        elif example_key == 2:
            tail = f"🎉 {label} 完成！右边是完整答案图，拖动 P 看 |PA|-|PB|=680 恒成立。回个「好」/「继续」我们看下一题（探究）。"
        else:
            tail = f"🎉 {label} 完成！右边是完整答案图。回个「好」/「继续」我们看下一题。"

        return LessonStep(
            stage=self.stage.value,
            message=head + tail,
            canvas_action=actions if len(actions) > 1 else actions[0],
        )

    def _continue_to_next_h321_example(self, completed_key) -> LessonStep:
        """学生确认后真正切到下一例 / 探究 / SUMMARY。"""
        if completed_key == 1:
            self.stage = LessonStage.H321_EXAMPLE_2
            next_msg = H321_EXAMPLE_2_INTRO
            viz = H321_MANDATORY_VIZ.get(LessonStage.H321_EXAMPLE_2)
        elif completed_key == 2:
            self.stage = LessonStage.H321_EXPLORATION
            next_msg = H321_EXPLORATION_INTRO
            viz = H321_MANDATORY_VIZ.get(LessonStage.H321_EXPLORATION)
        else:  # exploration → SUMMARY
            self.stage = LessonStage.H321_SUMMARY
            next_msg = H321_SUMMARY_MSG
            viz = {"action": "show_h321_summary"}
        return LessonStep(stage=self.stage.value, message=next_msg, canvas_action=viz)

    # ---- 例题/探究通用 handler（仿 _handle_e312_example）----

    def _handle_h321_example_generic(self, text: str, example_key) -> LessonStep:
        """v3.45 重构：例 1 / 例 2 / 探究 共用 handler。

        架构（仿 311 example handler）：
          · 诊断器**扫描所有 canonical goal**，命中 → 累积 implied_flags 到 subflags
          · done_fn(subflags) 满足 → 整道题完成，advance_h321_example 收尾
          · 部分命中 → ack 已答 + 用 phases 提问还没答的部分（教学节奏）

        三层判断：
          Layer 1: example_diagnostician_321（全 goal 扫描）—— 解决"跳级答题"问题
          Layer 2: 路径 2 协议（LLM 输出 JSON）—— 兜底处理诊断器没识别的写法
          Layer 3: deterministic 提示
        """
        from .example_canonicals_321 import EXAMPLE_CONFIGS_321
        from .example_diagnostician_321 import diagnose_example_321

        if not hasattr(self, "_h321_example_phase_idx"):
            self._h321_example_phase_idx = {1: 0, 2: 0, "exploration": 0}
            self._h321_example_subflags = {1: set(), 2: set(), "exploration": set()}

        # awaiting_next 检查 —— 例题通关后等学生确认才切下一题
        awaiting_key = getattr(self, "_h321_example_done_awaiting_next", None)
        if awaiting_key is not None:
            if _looks_like_ready_to_continue(text):
                delattr(self, "_h321_example_done_awaiting_next")
                return self._continue_to_next_h321_example(awaiting_key)
            label = "探究" if awaiting_key == "exploration" else f"例 {awaiting_key}"
            return LessonStep(
                stage=self.stage.value,
                message=f"{label} 已经完成 🎉 看完右边的图后回个「好」/「继续」就切到下一题；想再看图随便拖。",
            )

        # 跨 stage 跳级（跳到其它例题/探究）
        skip = _looks_like_skip_to_example_321(text)
        if skip and skip != example_key:
            return self._jump_to_h321_example(skip)

        config = EXAMPLE_CONFIGS_321[example_key]
        phases = config["phases"]
        idx = self._h321_example_phase_idx[example_key]
        current_phase = phases[idx] if idx < len(phases) else phases[-1]

        # Layer 1: 诊断器扫描所有 goal（v3.45 不再传 phase 参数）
        dx = diagnose_example_321(text, example_key)

        # Layer 2: 协议兜底（诊断器不命中时）
        if dx is None:
            protocol = self._llm_h321_example_protocol(text, example_key, current_phase)
            if protocol is not None:
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = protocol.get("ack_text", "请继续。")[:300]
                skip_n = protocol.get("skip_to_example")

                # (a) skip_request → 跳例
                if diag == "skip_request" and skip_n in (1, 2, "exploration"):
                    return self._jump_to_h321_example(skip_n)

                # (b) correct + advance → 模拟诊断器命中（查 implies_map）
                if diag == "correct" and protocol.get("advance") is True:
                    from .example_diagnostician_321 import ExampleDiagnosis321
                    goal_name = protocol.get("hit_goal") or "equation"  # 默认推进力最强的 goal
                    flags = set(config["implies"].get(goal_name, set()))
                    if not flags:
                        flags = {f"{goal_name}_done"}
                    dx = ExampleDiagnosis321(
                        hit_goal=goal_name, hit_goals=[goal_name],
                        implied_flags=flags,
                        label="完全正确（协议）", via="protocol"
                    )
                    # fall through 到正常推进逻辑

                # (c) partial / wrong / off_topic → ack 但不推进
                elif diag in ("partial", "wrong", "off_topic"):
                    return LessonStep(stage=self.stage.value, message=ack_text)

        # Layer 3: 仍 None → deterministic 提示
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？或者把你的答案写完整些（比如方程请写成 x²/a² - y²/b² = 1 这样的形式）。",
            )

        # ── v3.45 命中：累积 subflags，按 done_fn 判定收尾或继续教学节奏 ──
        self._h321_example_subflags[example_key] |= dx.implied_flags
        subflags = self._h321_example_subflags[example_key]

        # 整道题完成？（done_fn 满足 → 直接收尾，跳过剩余 phase）
        done_fn = config["done_fn"]
        if done_fn(subflags):
            # 推 phase_idx 到末尾标记"全部完成"
            self._h321_example_phase_idx[example_key] = len(phases)
            return self._advance_h321_example(example_key, ack="✅ 完全正确！")

        # 部分命中：找出下一个还没 done 的 phase 来问（按教学节奏顺序）
        next_phase = None
        next_missing = set()
        for ph in phases:
            required = self._H321_PHASE_REQUIRED_FLAGS.get((example_key, ph), set())
            missing = required - subflags
            if missing:
                next_phase = ph
                next_missing = missing
                break
        if next_phase is None:
            # 所有 phase 都 done 但 done_fn 没满足（理论上不会，保险）
            return self._advance_h321_example(example_key, ack="✅ 完全正确！")

        # 推 phase_idx 到 next_phase 的位置
        self._h321_example_phase_idx[example_key] = phases.index(next_phase)

        # v3.45.1/v3.45.2 missing-aware prompt：只对"多-flag phase 内部部分命中"才用
        # （single-flag phase 没"部分命中"概念，直接用默认 phase prompt 即可）
        next_prompt = None
        next_required = self._H321_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
        if len(next_missing) == 1 and len(next_required) >= 2:
            single_missing = next(iter(next_missing))
            next_prompt = self._H321_PHASE_PROMPT_BY_MISSING.get(
                (example_key, next_phase, single_missing)
            )
        if next_prompt is None:
            # 没注册 missing-aware 文案 / 多个 missing / 单-flag phase → fallback 到默认 phase prompt
            next_prompt = self._h321_example_phase_prompt(example_key, next_phase)

        # ack 已答内容（基于 hit_goals + dx 信息）
        ack = "✅ " + (", ".join(dx.hit_goals[:3]) if dx.hit_goals else "答对了") + " 收到。"
        return LessonStep(stage=self.stage.value, message=ack + "\n\n" + next_prompt)

    # v3.45 phase → required flags 映射（用于"找下一个未答完的 phase"教学节奏）
    _H321_PHASE_REQUIRED_FLAGS = {
        (1, "ask_form"):     {"form_done"},
        (1, "ask_ab"):       {"a_done", "b_done"},
        (1, "ask_equation"): {"equation_done"},
        (2, "ask_setup"):    {"setup_done"},
        (2, "ask_ab"):       {"a_done", "b_done"},
        (2, "ask_equation_with_branch"): {"equation_done", "branch_done"},
        # v3.45.2 探究 ask_slopes 拆 2 个 sub-flag（修分两次答 k_AM/k_BM 死循环）
        ("exploration", "ask_slopes"):    {"slope_am_done", "slope_bm_done"},
        ("exploration", "ask_simplify"):  {"equation_done"},
        ("exploration", "ask_constraint"):{"constraint_done"},
    }

    # v3.45.1 missing-aware prompt：当 phase 部分命中时，按"缺哪个 flag"给精准提示，
    # 避免学生反复看到同一份 phase prompt（如已答分支还被追问完整方程+分支）
    _H321_PHASE_PROMPT_BY_MISSING = {
        # ───── 例 1 ─────
        (1, "ask_ab", "a_done"):
            "还差 $a$：由 $|MF_1|-|MF_2|=\\pm 6$ 推出 $2a=?$ 故 $a=?$",
        (1, "ask_ab", "b_done"):
            "还差 $b$（或 $b^2$）：由 $b^2=c^2-a^2$ 推出 $b^2=?$ 故 $b=?$",
        # ───── 例 2 ─────
        (2, "ask_ab", "a_done"):
            "还差 $a$：由 $2a=680$ 推出 $a=?$",
        (2, "ask_ab", "b_done"):
            "还差 $b^2$：由 $b^2=c^2-a^2=400^2-340^2$ 算出 $b^2=?$",
        (2, "ask_equation_with_branch", "equation_done"):
            "✅ 分支约束你已经答对了。\n\n还差**轨迹方程**：以 $a^2=115600,\\ b^2=44400$ 代入 "
            "$\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$ 形式写出方程。",
        (2, "ask_equation_with_branch", "branch_done"):
            "✅ 方程对了。\n\n还差**分支约束**：$|PA|-|PB|>0$ 意味着 $P$ 离 $A$ 远还是近？$x$ 的范围是？",
        # ───── 探究 ─────
        ("exploration", "ask_slopes", "slope_am_done"):
            "✅ $k_{BM}$ 对了。还差 $k_{AM}$ —— $A(-5, 0)$ 到 $M(x, y)$ 的斜率怎么写？",
        ("exploration", "ask_slopes", "slope_bm_done"):
            "✅ $k_{AM}$ 对了。还差 $k_{BM}$ —— $B(5, 0)$ 到 $M(x, y)$ 的斜率怎么写？",
        ("exploration", "ask_simplify", "equation_done"):
            "✅ 约束对了。\n\n还差**化简方程**：把 $k_{AM}\\cdot k_{BM}=\\dfrac{4}{9}$ 代入展开并化简，"
            "得到的方程是？",
        ("exploration", "ask_constraint", "constraint_done"):
            "✅ 方程对了。\n\n还差**约束**：$k_{AM}, k_{BM}$ 的分母不为零意味着 $x\\ne ?$",
    }

    def _h321_example_phase_prompt(self, example_key, phase: str) -> str:
        """例题/探究 每 phase 的提问文案（hard-coded，不让 LLM 编）。"""
        prompts = {
            (1, "ask_ab"):       "**很好，下一步**：由 $|MF_1|-|MF_2|=\\pm 6$ 得 $2a=?$ 故 $a=?$；又 $c=?$（由焦点距离）；所以 $b^2=c^2-a^2=?$",
            (1, "ask_equation"): "**最后**：把 $a^2, b^2$ 代回标准方程，**双曲线的标准方程**是？",
            (2, "ask_ab"):       "**好**，下一步建立坐标系（A、B 在 $x$ 轴上，原点为 AB 中点）。由 $2a=680$ 得 $a=?$；由 $|AB|=800$ 得 $c=?$；所以 $b^2=?$",
            (2, "ask_equation_with_branch"): "**最后**：写出 P 的轨迹方程，并**注明分支约束**（提示：$|PA|-|PB|>0$ 意味着 P 在哪一支？$x$ 的范围是？）",
            ("exploration", "ask_simplify"):   "**很好**，下一步把 $k_{AM}\\cdot k_{BM}=\\dfrac{4}{9}$ 代入并化简（提示：乘开后再整理成标准形式），得到的方程是？",
            ("exploration", "ask_constraint"): "**最后**：要不要排除某些点？（提示：$k_{AM}, k_{BM}$ 的分母不为零）",
        }
        return prompts.get((example_key, phase), "请继续。")

    # ---- 13 个 stage handler ----

    def _handle_h321_intro(self, text: str) -> LessonStep:
        """1. 开场。学生回应任意内容后推进 RECALL_ELLIPSE。"""
        # 跳例
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)
        # 学生已经答出椭圆相关 → 直接进 PROBE_DIFFERENCE
        if _looks_like_ellipse_def_recall_321(text):
            self.stage = LessonStage.H321_PROBE_DIFFERENCE
            return LessonStep(stage=self.stage.value, message=H321_PROBE_DIFFERENCE_MSG)
        # 否则推进到 RECALL_ELLIPSE 让学生答
        # v3.43: deterministic 返回，不走 _llm_respond 自由 ack（防 LLM 推偏 stage）
        self.stage = LessonStage.H321_RECALL_ELLIPSE
        return LessonStep(
            stage=self.stage.value,
            message="想想：椭圆是「距离之**和**」的轨迹，请用你自己的话回忆一下定义。",
        )

    def _handle_h321_recall_ellipse(self, text: str) -> LessonStep:
        """2. 回忆椭圆定义。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)
        if _looks_like_ellipse_def_recall_321(text):
            self.stage = LessonStage.H321_PROBE_DIFFERENCE
            return LessonStep(stage=self.stage.value, message=H321_PROBE_DIFFERENCE_MSG)
        # v3.43 deterministic
        return LessonStep(
            stage=self.stage.value,
            message="提示：椭圆是「到两个焦点的距离之**和**为定值」的轨迹。再说一遍试试。",
        )

    def _handle_h321_probe_difference(self, text: str) -> LessonStep:
        """3. 学生预测后推进 EXPLORE_LOCUS（无论答什么）。
        v3.39 进入 EXPLORE_LOCUS 时主动初始化 _h321_explore_phase = 'ellipse_recap'。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)
        self.stage = LessonStage.H321_EXPLORE_LOCUS
        # v3.39: 显式初始化 explore phase（不靠 lazy init，让 state 在 stage 切换时就明确）
        self._h321_explore_phase = "ellipse_recap"
        viz = H321_MANDATORY_VIZ.get(LessonStage.H321_EXPLORE_LOCUS)
        # 三类应答的 ack 选择
        if any(kw in text for kw in ["不知道", "不清楚", "没想法"]):
            ack = "没关系，动手画一画就清楚了。\n\n"
        elif any(kw in text for kw in ["双曲线", "两条", "两支", "曲线", "形状"]):
            ack = "不错的猜想！我们去画布验证一下。\n\n"
        else:
            ack = "好，我们去画布上看看。\n\n"
        return LessonStep(
            stage=self.stage.value,
            message=ack + H321_EXPLORE_LOCUS_MSG,
            canvas_action=viz,
            expect_event="trail_completed",
        )

    def _handle_h321_explore_locus(self, text: str) -> LessonStep:
        """4. 教材 p118 双圆模型探究。v3.39 拆 2 phase：

        · phase=ellipse_recap（入口）：发椭圆模型 viz（|F1F2|<|AB|，P 限 AB 内）。
            - 学生答"椭圆"等 → 切到 hyperbola_explore phase，发双曲线模型 viz
            - 学生答错（说"两条" / "双曲线"）→ 提示"先看图回忆椭圆"
        · phase=hyperbola_explore：切到双曲线模型 viz（|F1F2|>|AB|，P 在直线 l 上自由）。
            - 学生答"两条/两支/双曲线" → 推进 AWAIT_SHAPE_NAME / AWAIT_DEFINITION

        deterministic 路径（不调 _llm_respond，杜绝 [VIZ:] 注入）。
        """
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)

        if not hasattr(self, "_h321_explore_phase"):
            self._h321_explore_phase = "ellipse_recap"
        phase = self._h321_explore_phase

        # ===== Phase 1: 椭圆铺垫 =====
        if phase == "ellipse_recap":
            # 学生答出"椭圆" → 切到 hyperbola_explore phase
            t = text.replace(" ", "")
            saw_ellipse = ("椭圆" in t) or ("ellipse" in t.lower())
            if saw_ellipse:
                self._h321_explore_phase = "hyperbola_explore"
                viz_hyp = {
                    "action": "init_h321_two_circles_hyperbola",
                    "config": {"F1": [-3, 0], "F2": [3, 0], "A": [-1, 4], "B": [1, 4], "line_y": 4},
                }
                return LessonStep(
                    stage=self.stage.value,
                    message=H321_EXPLORE_HYP_PHASE_MSG,
                    canvas_action=viz_hyp,
                )
            # 学生提前说"双曲线" / "两条" → 拉回观察椭圆铺垫
            if _looks_like_hyperbola_name(text) or any(kw in t for kw in [
                "两条", "两支", "两个", "2条", "2支",
            ]):
                return LessonStep(
                    stage=self.stage.value,
                    message="先别急 🙂 现在画布上的 $|F_1F_2|<|AB|$，$P$ 在 $A, B$ 内滑动时，"
                            "$M$ 满足的条件是 $|MF_1|+|MF_2|=|AB|$ —— 这是哪种图形？"
                            "（提示：是我们上节课学过的）",
                )
            # 不知道
            if any(kw in text for kw in ["不知道", "不会", "看不出", "没看到"]):
                return LessonStep(
                    stage=self.stage.value,
                    message="提示：观察右边画布上 $M, M'$ 累积出来的形状——是封闭曲线吗？"
                            "想想 $|MF_1|+|MF_2|=|AB|$ 是什么图形的定义？",
                )
            # 其它
            return LessonStep(
                stage=self.stage.value,
                message="试着先在直线 $l$ 上拖动 $P$（限制在 $A, B$ 之间）"
                        "把 $M, M'$ 的轨迹画完整，再告诉我它是什么图形？",
            )

        # ===== Phase 2: 双曲线探究 =====
        if phase == "hyperbola_explore":
            # 学生直接说"双曲线" → 跳过 SHAPE_NAME，直接进 AWAIT_DEFINITION
            if _looks_like_hyperbola_name(text):
                self.trail_completed = True
                delattr(self, "_h321_explore_phase")
                self.stage = LessonStage.H321_AWAIT_DEFINITION
                return LessonStep(stage=self.stage.value, message=H321_AWAIT_DEFINITION_MSG)
            # 学生答"两条 / 两支" → 推进 AWAIT_SHAPE_NAME
            t = text.replace(" ", "")
            saw_two = any(kw in t for kw in [
                "两条", "两支", "两个", "两根", "2条", "2支", "2个",
                "分开", "分两边", "分支", "对称的两", "两段",
            ])
            if saw_two:
                self.trail_completed = True
                delattr(self, "_h321_explore_phase")
                self.stage = LessonStage.H321_AWAIT_SHAPE_NAME
                return LessonStep(stage=self.stage.value, message=H321_AWAIT_SHAPE_NAME_MSG)
            # 不知道
            if any(kw in text for kw in ["不知道", "不会", "看不出", "没看到"]):
                return LessonStep(
                    stage=self.stage.value,
                    message="试着把 $P$ 拖到 $B$ **右边**远一点的地方（比如 $P.x=5$），"
                            "再拖到 $A$ **左边**远一点（$P.x=-5$），观察 $M, M'$ 画出几条曲线？",
                )
            # 其它
            return LessonStep(
                stage=self.stage.value,
                message="再回画布上拖一下 $P$（特别是 $A, B$ **之外**），数数 $M, M'$ 累积出几条曲线？",
            )

        return LessonStep(stage=self.stage.value, message="（探究阶段已完成。）")

    def _handle_h321_await_shape_name(self, text: str) -> LessonStep:
        """5. 等学生说"双曲线"。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)
        if _looks_like_hyperbola_name(text):
            self.stage = LessonStage.H321_AWAIT_DEFINITION
            return LessonStep(stage=self.stage.value, message=H321_AWAIT_DEFINITION_MSG)
        # v3.43 deterministic
        return LessonStep(
            stage=self.stage.value,
            message="提示：这个图形有**两支**，在数学里以「双」字开头。",
        )

    def _handle_h321_await_definition(self, text: str) -> LessonStep:
        """6. 学生归纳定义。v3.38 拆 2 phase：

        · phase=await_abs：要求学生定义含「**绝对值**」。
            - 学生答"差是定值"但缺绝对值 → 苏格拉底追问（H321_AWAIT_DEF_ABS_NUDGE_MSG）
            - 学生补上绝对值 → 推进到 await_constraint phase
        · phase=await_constraint：要求学生答出 2a < 2c。
            - 学生答出 → 推进到 H321_REFLECT_COORD
            - 学生答边界情形（=会射线/>无轨迹）→ 温和追问"那 2a 该满足什么不等关系？"

        deterministic 路径为主（不让 LLM 自由 ack）。
        """
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)

        if not hasattr(self, "_h321_await_def_phase"):
            self._h321_await_def_phase = "await_abs"
        phase = self._h321_await_def_phase

        # ===== Phase 1: 追问绝对值 =====
        if phase == "await_abs":
            if _looks_like_hyperbola_def_with_abs(text):
                self._h321_await_def_phase = "await_constraint"
                return LessonStep(stage=self.stage.value, message=H321_AWAIT_DEF_CONSTRAINT_MSG)
            # 学生答了"差 + 距离"但缺绝对值 → 苏格拉底追问
            if _looks_like_hyperbola_def_diff_only(text):
                return LessonStep(stage=self.stage.value, message=H321_AWAIT_DEF_ABS_NUDGE_MSG)
            # 完全不沾边 → 协议兜底（off_topic / partial）
            protocol = self._llm_h321_protocol(
                text,
                "AWAIT_DEFINITION phase=await_abs：让学生类比椭圆「距离之和」答出「距离之差的绝对值为常数」。"
                "若学生答了「差+常数」但缺「绝对值」，给提示让学生注意两支的对称性。"
            )
            if protocol is not None:
                ack = (protocol.get("ack_text") or "")[:200]
                if ack:
                    return LessonStep(stage=self.stage.value, message=ack)
            return LessonStep(
                stage=self.stage.value,
                message="提示：椭圆是「距离之**和**为定值」，双曲线类比是「距离之**？？**为定值」。"
                        "试着把椭圆定义里的『和』换掉。",
            )

        # ===== Phase 2: 追问约束 2a < 2c =====
        if phase == "await_constraint":
            if _looks_like_constraint_2a_lt_2c(text):
                # 退栈、推进 stage
                delattr(self, "_h321_await_def_phase")
                self.stage = LessonStage.H321_REFLECT_COORD
                return LessonStep(stage=self.stage.value, message=H321_REFLECT_COORD_MSG)
            # 学生提到边界情形 → 温和引导回不等关系
            if _looks_like_constraint_boundary_insight(text):
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 你想到了**边界情形**！\n\n"
                            "把这些综合起来：$2a$ 和 $2c$ 应该满足什么**不等关系**？"
                            "（写成 $2a \\;?\\; 2c$ 的形式）",
                )
            # 协议兜底
            protocol = self._llm_h321_protocol(
                text,
                "AWAIT_DEFINITION phase=await_constraint：让学生答出 2a<2c 的不等约束。"
                "学生提到边界情形（=会射线/>无轨迹）时，温和引导回不等关系。"
            )
            if protocol is not None:
                ack = (protocol.get("ack_text") or "")[:200]
                if ack:
                    return LessonStep(stage=self.stage.value, message=ack)
            return LessonStep(
                stage=self.stage.value,
                message="提示：动手想想——若 $2a = 2c$，两圆交点的轨迹会变成什么？"
                        "若 $2a > 2c$ 呢？由此推出 $2a$ 和 $2c$ 的**不等关系**。",
            )

        return LessonStep(stage=self.stage.value, message="（定义阶段已完成。）")

    def _handle_h321_reflect_coord(self, text: str) -> LessonStep:
        """7. 思考 1：建系。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)
        if _looks_like_coord_choice(text):
            self.stage = LessonStage.H321_DERIVE_AND_RESULT
            if not hasattr(self, "_h321_derive_phase"):
                self._h321_derive_phase = "collect_radii"
            viz = H321_MANDATORY_VIZ.get(LessonStage.H321_DERIVE_AND_RESULT)
            return LessonStep(
                stage=self.stage.value,
                message=H321_DERIVE_INTRO_MSG,
                canvas_action=viz,
            )
        # v3.43 deterministic
        return LessonStep(
            stage=self.stage.value,
            message="提示：类比椭圆，把 $F_1F_2$ 所在的直线作 $x$ 轴，$F_1F_2$ 的中垂线作 $y$ 轴。",
        )

    def _handle_h321_derive_and_result(self, text: str) -> LessonStep:
        """8. 推导阶段。3 phase 状态机 + 路径 2 协议。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)

        if not hasattr(self, "_h321_derive_phase"):
            self._h321_derive_phase = "collect_radii"

        phase = self._h321_derive_phase

        # 关键词识别学生是否已写出最终方程
        t_norm = text.replace(" ", "").lower()
        final_eq_patterns = [
            "x²/a²-y²/(c²-a²)=1", "x^2/a^2-y^2/(c^2-a^2)=1",
            "x²/a²-y²/c²-a²=1",
        ]
        wrote_final_eq = any(p in t_norm for p in final_eq_patterns)

        # 距离公式关键词
        has_mf1 = any(p in t_norm for p in ["(x+c)²+y²", "(x+c)^2+y^2"])
        has_mf2 = any(p in t_norm for p in ["(x-c)²+y²", "(x-c)^2+y^2"])

        if phase == "collect_radii":
            # v3.42: 跨轮累积命中状态（修死循环 —— 学生分两次答 MF1/MF2 也能识别）
            if not hasattr(self, "_h321_derive_radii_hits"):
                self._h321_derive_radii_hits = {"mf1": False, "mf2": False}
            hits = self._h321_derive_radii_hits
            if has_mf1:
                hits["mf1"] = True
            if has_mf2:
                hits["mf2"] = True

            # 两个都命中 → 推进 challenge phase
            if hits["mf1"] and hits["mf2"]:
                self._h321_derive_phase = "challenge"
                delattr(self, "_h321_derive_radii_hits")
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 两个距离公式都写对了。\n\n**第二步**：你能直接由 $\\bigl||MF_1|-|MF_2|\\bigr|=2a$ 推出最终方程吗？\n试试看（提示：终点形如 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{?}=1$）。",
                )
            # 本轮命中了某个新公式 → 提示写剩下那个
            if has_mf1 or has_mf2:
                missing = "$|MF_2|$" if hits["mf1"] and not hits["mf2"] else "$|MF_1|$"
                return LessonStep(
                    stage=self.stage.value,
                    message=f"✅ 一个对了。再写另一个距离公式 {missing}。",
                )
            # 本轮没命中任何公式 → v3.44 方案 B 协议兜底（角色 3，socratic_text 2-4 句）
            protocol = self._llm_h321_derive_action_protocol(
                text,
                context_note=(
                    "phase=collect_radii。学生应该写出 $|MF_1|=\\sqrt{(x+c)^2+y^2}$ 和 $|MF_2|=\\sqrt{(x-c)^2+y^2}$。"
                    "若学生答非所问，给苏格拉底提示让他回到距离公式上来。"
                )
            )
            if protocol is not None:
                socratic = (protocol.get("socratic_text") or "")[:500]
                if self._h321_proto_b_advance(protocol):
                    # 协议确认推进 → 切 challenge phase
                    self._h321_derive_phase = "challenge"
                    if hasattr(self, "_h321_derive_radii_hits"):
                        delattr(self, "_h321_derive_radii_hits")
                    challenge_prompt = ("\n\n**第二步**：你能直接由 $\\bigl||MF_1|-|MF_2|\\bigr|=2a$ "
                                        "推出最终方程吗？试试看（提示：终点形如 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{?}=1$）。")
                    return LessonStep(
                        stage=self.stage.value,
                        message=(socratic or "✅ 好的，进入下一步。") + challenge_prompt,
                    )
                if socratic:
                    return LessonStep(stage=self.stage.value, message=socratic)
            # v3.44 deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message="提示：用距离公式 $|MF_1|=\\sqrt{(x-(-c))^2+(y-0)^2}$ "
                        "和 $|MF_2|=\\sqrt{(x-c)^2+y^2}$ 写出两个焦半径。",
            )

        if phase == "challenge":
            if wrote_final_eq:
                self._h321_derive_phase = "done"
                self.stage = LessonStage.H321_INTRODUCE_B
                self._h321_introduce_b_phase = "define_b"
                viz = H321_MANDATORY_VIZ.get(LessonStage.H321_INTRODUCE_B)
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 漂亮！你直接推出来了。\n\n" + H321_INTRODUCE_B_DEFINE_MSG,
                    canvas_action=viz,
                )
            # 学生说不会 → 转入引导路径
            if any(kw in text for kw in ["不会", "不知道", "卡住", "求引导", "提示", "帮我"]):
                self._h321_derive_phase = "guided_simplify"
                return LessonStep(
                    stage=self.stage.value,
                    message="没关系，我们一步步来。\n\n**步骤 1**：由定义 $\\bigl||MF_1|-|MF_2|\\bigr|=2a$，写出含正负号的方程：$\\sqrt{(x+c)^2+y^2}-\\sqrt{(x-c)^2+y^2}=\\pm 2a$。\n移项让一个根号单独留在一边，你能写出来吗？",
                )
            # v3.44 方案 B 协议（角色 3）—— 关键修复：响应 advance=true 推进 stage
            protocol = self._llm_h321_derive_action_protocol(
                text,
                context_note=(
                    "phase=challenge。学生应直接写出最终方程 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$。"
                    "若学生答出此式（或等价形式如 $x^2/a^2-y^2/(c^2-a^2)=1$），diagnosis=完全正确, advance=true。"
                    "若学生答非所问、推不动，给苏格拉底引导让他尝试推或承认不会。"
                )
            )
            if protocol is not None:
                socratic = (protocol.get("socratic_text") or "")[:500]
                if self._h321_proto_b_advance(protocol):
                    # 学生写出最终方程 → 切到 INTRODUCE_B stage
                    self._h321_derive_phase = "done"
                    self.stage = LessonStage.H321_INTRODUCE_B
                    self._h321_introduce_b_phase = "define_b"
                    viz = H321_MANDATORY_VIZ.get(LessonStage.H321_INTRODUCE_B)
                    return LessonStep(
                        stage=self.stage.value,
                        message=(socratic or "✅ 漂亮！你直接推出来了。") + "\n\n" + H321_INTRODUCE_B_DEFINE_MSG,
                        canvas_action=viz,
                    )
                if socratic:
                    return LessonStep(stage=self.stage.value, message=socratic)
            # v3.44 deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message="试试看：终点是 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$（**不要引入字母 b**）。\n\n"
                        "卡住可以说『不会』我会一步一步帮你。",
            )

        if phase == "guided_simplify":
            if wrote_final_eq:
                self._h321_derive_phase = "done"
                self.stage = LessonStage.H321_INTRODUCE_B
                self._h321_introduce_b_phase = "define_b"
                viz = H321_MANDATORY_VIZ.get(LessonStage.H321_INTRODUCE_B)
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 推导完成！\n\n" + H321_INTRODUCE_B_DEFINE_MSG,
                    canvas_action=viz,
                )
            # v3.44 方案 B 协议（角色 3）—— 苏格拉底逐步引导 + 响应 advance
            protocol = self._llm_h321_derive_action_protocol(
                text,
                context_note=(
                    "phase=guided_simplify。你正在**逐步引导**学生从距离公式推到最终方程：\n"
                    "  (1) 移项 → $\\sqrt{(x+c)^2+y^2}=\\sqrt{(x-c)^2+y^2}\\pm 2a$\n"
                    "  (2) 第一次平方 + 整理 → $cx-a^2=\\pm a\\sqrt{(x-c)^2+y^2}$\n"
                    "  (3) 第二次平方 + 整理 → $(c^2-a^2)x^2-a^2y^2=a^2(c^2-a^2)$\n"
                    "  (4) 两边除以 $a^2(c^2-a^2)$ → $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$\n"
                    "诊断学生当前在哪一步、有什么错；用 socratic_text 给下一步提示（不要替学生写完）。"
                    "学生写出最终方程时 advance=true。"
                )
            )
            if protocol is not None:
                socratic = (protocol.get("socratic_text") or "")[:500]
                if self._h321_proto_b_advance(protocol):
                    self._h321_derive_phase = "done"
                    self.stage = LessonStage.H321_INTRODUCE_B
                    self._h321_introduce_b_phase = "define_b"
                    viz = H321_MANDATORY_VIZ.get(LessonStage.H321_INTRODUCE_B)
                    return LessonStep(
                        stage=self.stage.value,
                        message=(socratic or "✅ 推导完成！") + "\n\n" + H321_INTRODUCE_B_DEFINE_MSG,
                        canvas_action=viz,
                    )
                if socratic:
                    return LessonStep(stage=self.stage.value, message=socratic)
            # v3.44 deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message="提示：把一个根号留在等号一边，两次平方就能消掉根号。最后两边除以 $a^2(c^2-a^2)$ 即可。\n\n"
                        "目标式：$\\dfrac{x^2}{a^2}-\\dfrac{y^2}{c^2-a^2}=1$。",
            )

        return LessonStep(stage=self.stage.value, message="（推导阶段已完成。）")

    def _handle_h321_introduce_b(self, text: str) -> LessonStep:
        """9. 引入 b + y 轴形式。2 phase。"""
        skip = _looks_like_skip_to_example_321(text)
        if skip:
            return self._jump_to_h321_example(skip)

        if not hasattr(self, "_h321_introduce_b_phase"):
            self._h321_introduce_b_phase = "define_b"

        phase = self._h321_introduce_b_phase

        if phase == "define_b":
            # 学生答出焦点坐标 → 推进 yaxis_form
            if _looks_like_hyperbola_focus_coords_x(text):
                self._h321_introduce_b_phase = "yaxis_form"
                return LessonStep(
                    stage=self.stage.value,
                    message=H321_INTRODUCE_B_YAXIS_MSG,
                )
            # 学生说"已经写出 b²=c²-a²" → 推进
            if _looks_like_b_squared_c_minus_a(text):
                # 给提示去写焦点
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 对，$b^2=c^2-a^2$。\n\n那么焦点 $F_1, F_2$ 的坐标是？（提示：在 $x$ 轴上，到原点距离为 $c$）",
                )
            # v3.44 方案 B 协议（角色 3）
            protocol = self._llm_h321_introduce_b_action_protocol(
                text,
                context_note=(
                    "phase=define_b。学生应答出焦点坐标 $F_1(-c, 0), F_2(c, 0)$。"
                    "强调对比：双曲线 $b^2=c^2-a^2$ vs 椭圆 $b^2=a^2-c^2$。"
                    "**严禁**讨论 y 轴形式（下一 phase）或离心率/渐近线（属 3.2.2）。"
                )
            )
            if protocol is not None:
                socratic = (protocol.get("socratic_text") or "")[:500]
                if self._h321_proto_b_advance(protocol):
                    self._h321_introduce_b_phase = "yaxis_form"
                    return LessonStep(
                        stage=self.stage.value,
                        message=(socratic or "✅ 焦点对了。") + "\n\n" + H321_INTRODUCE_B_YAXIS_MSG,
                    )
                if socratic:
                    return LessonStep(stage=self.stage.value, message=socratic)
            # v3.44 deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message="提示：焦点在 $x$ 轴上，到原点距离 $c$，所以 $F_1, F_2$ 坐标是？",
            )

        if phase == "yaxis_form":
            if _looks_like_yaxis_hyperbola_eq(text):
                self.stage = LessonStage.H321_EXAMPLE_1
                viz = H321_MANDATORY_VIZ.get(LessonStage.H321_EXAMPLE_1)
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 完全正确！焦点在 $y$ 轴时方程是 $\\dfrac{y^2}{a^2}-\\dfrac{x^2}{b^2}=1$。\n\n"
                            "至此双曲线的两种标准方程都掌握了。下面我们用 3 道题（例 1、例 2、探究）巩固。\n\n"
                            + H321_EXAMPLE_1_INTRO,
                    canvas_action=viz,
                )
            # v3.44 方案 B 协议（角色 3）
            protocol = self._llm_h321_introduce_b_action_protocol(
                text,
                context_note=(
                    "phase=yaxis_form。学生应类比椭圆 y 轴形式，写出双曲线 y 轴方程 "
                    "$\\dfrac{y^2}{a^2}-\\dfrac{x^2}{b^2}=1$（提示：把 x 与 y 互换）。"
                    "**严禁**讨论离心率/渐近线（属 3.2.2 下一节）。"
                )
            )
            if protocol is not None:
                socratic = (protocol.get("socratic_text") or "")[:500]
                if self._h321_proto_b_advance(protocol):
                    # 推进到 EXAMPLE_1
                    self.stage = LessonStage.H321_EXAMPLE_1
                    if hasattr(self, "_h321_introduce_b_phase"):
                        delattr(self, "_h321_introduce_b_phase")
                    viz = H321_MANDATORY_VIZ.get(LessonStage.H321_EXAMPLE_1)
                    return LessonStep(
                        stage=self.stage.value,
                        message=(socratic or "✅ 完全正确！焦点在 $y$ 轴时方程是 $\\dfrac{y^2}{a^2}-\\dfrac{x^2}{b^2}=1$。")
                                + "\n\n至此双曲线的两种标准方程都掌握了。下面我们用 3 道题（例 1、例 2、探究）巩固。\n\n"
                                + H321_EXAMPLE_1_INTRO,
                        canvas_action=viz,
                    )
                if socratic:
                    return LessonStep(stage=self.stage.value, message=socratic)
            # v3.44 deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message="提示：把 $x$ 与 $y$ 在 $\\dfrac{x^2}{a^2}-\\dfrac{y^2}{b^2}=1$ 里互换试试。",
            )

        return LessonStep(stage=self.stage.value, message="（引入 $b$ 阶段已完成。）")

    def _handle_h321_example_1(self, text: str) -> LessonStep:
        """10. 🟡 例 1。"""
        return self._handle_h321_example_generic(text, 1)

    def _handle_h321_example_2(self, text: str) -> LessonStep:
        """11. 🟡 例 2。"""
        return self._handle_h321_example_generic(text, 2)

    def _handle_h321_exploration(self, text: str) -> LessonStep:
        """12. 🔍 探究（结构仿 311 例 3，路径 2 协议独立实现）。"""
        return self._handle_h321_example_generic(text, "exploration")

    def _handle_h321_summary(self, text: str) -> LessonStep:
        """13. 总结。v3.43 改 deterministic：杜绝 LLM 自由 ack。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "👏 恭喜完成 3.2.1 课程！\n\n"
                    "下次见 —— 我们将进入 3.2.2「双曲线的简单几何性质」，"
                    "看实轴/虚轴/渐近线/离心率（$e>1$，与椭圆 $0<e<1$ 互补）。\n\n"
                    "[LESSON_END]"
                ),
            )
        # 非结课轮次：保留协议兜底（学生可能继续问问题），但兜底失败用 deterministic
        protocol = self._llm_h321_protocol(text, "SUMMARY：学生在总结阶段闲聊或提问。简短回答后引导结课。")
        if protocol is not None:
            ack = (protocol.get("ack_text") or "")[:200]
            if ack:
                return LessonStep(stage=self.stage.value, message=ack)
        return LessonStep(
            stage=self.stage.value,
            message="还有什么问题想问？或者输入「结束」结课。",
        )


# ---- H321-specific keyword detection helpers (module-level, used by handlers) ----

def _looks_like_hyperbola_name(text: str) -> bool:
    """识别学生说出『双曲线』。"""
    t = text.lower()
    return ("双曲线" in text) or ("hyperbola" in t)


def _looks_like_ellipse_def_recall_321(text: str) -> bool:
    """H321_RECALL_ELLIPSE：学生回忆椭圆定义。
    关键词命中 ≥1（距离 / 和 / 焦点 / 常数 / 椭圆）。"""
    kws = ["距离之和", "之和", "和等于", "焦点", "常数", "定值", "椭圆", "2a"]
    return any(kw in text for kw in kws)


def _looks_like_hyperbola_def_diff_only(text: str) -> bool:
    """v3.38 phase await_abs：学生答了"差 + 距离/焦点" 但缺"绝对值"。
    用于触发苏格拉底追问。"""
    t = text
    has_diff = "差" in t or "之差" in t
    has_anchor = any(kw in t for kw in ["焦点", "定点", "定值", "常数", "非零", "距离"])
    has_abs = ("绝对值" in t) or ("||" in t)
    # 含差 + 锚点，但不含绝对值
    return has_diff and has_anchor and not has_abs


def _looks_like_hyperbola_def_with_abs(text: str) -> bool:
    """v3.38 phase await_abs：学生定义里**明确**含"绝对值"+ 差 + 距离。"""
    t = text
    has_abs = ("绝对值" in t) or ("||" in t)
    has_diff = ("差" in t) or ("之差" in t)
    has_distance = "距离" in t
    return has_abs and has_diff and has_distance


def _looks_like_constraint_2a_lt_2c(text: str) -> bool:
    """v3.38 phase await_constraint：学生答出 2a < 2c（或等价表达）。

    宽松识别：
      · "2a < 2c" / "a < c" / "2a小于2c" / "小于焦距" / "小于|F1F2|"
      · 描述性："常数比焦距小" / "比 2c 小"
    """
    t = text.replace(" ", "")
    # 标准数学符号
    if "2a<2c" in t or "a<c" in t:
        return True
    # 文字描述：含"小于" + 焦距/2c/|F1F2| 锚点
    has_lt = ("小于" in text) or ("少于" in text) or ("<" in t)
    has_anchor = any(kw in t for kw in ["焦距", "2c", "|f1f2|", "|F1F2|", "f1f2", "F1F2"])
    if has_lt and has_anchor:
        return True
    # "常数比焦距小" / "比 2c 小"
    if "比" in text and ("小" in text or "少" in text) and has_anchor:
        return True
    return False


def _looks_like_constraint_boundary_insight(text: str) -> bool:
    """v3.38 phase await_constraint：学生提到边界情形（=会变射线/线段，>无轨迹等）。
    用于温和追问"那 2a 该满足什么不等关系？"。"""
    t = text
    keywords = ["射线", "线段", "中垂线", "直线", "不存在", "无轨迹", "没有", "无解", "退化", "重合"]
    return any(kw in t for kw in keywords)


def _looks_like_b_squared_c_minus_a(text: str) -> bool:
    """H321_INTRODUCE_B define_b phase：学生写出 b²=c²-a² 或确认这个关系。"""
    t = text.replace(" ", "").lower()
    patterns = [
        "b²=c²-a²", "b^2=c^2-a^2", "b2=c2-a2",
        "b²=c2-a²", "b^2=c^2−a^2",
    ]
    return any(p in t for p in patterns)


def _looks_like_yaxis_hyperbola_eq(text: str) -> bool:
    """H321_INTRODUCE_B yaxis_form phase：学生写出 y²/a² - x²/b² = 1。"""
    t = text.replace(" ", "").lower()
    patterns = [
        "y²/a²-x²/b²=1", "y^2/a^2-x^2/b^2=1", "y2/a2-x2/b2=1",
    ]
    return any(p in t for p in patterns)


def _looks_like_hyperbola_focus_coords_x(text: str) -> bool:
    """H321_INTRODUCE_B define_b phase 后半：学生答出焦点坐标 F₁(-c,0), F₂(c,0)。"""
    t = text.replace(" ", "")
    # 必须出现 (-c, 0) 和 (c, 0) 两种形式
    has_neg_c = "(-c,0)" in t or "(−c,0)" in t
    has_pos_c = "(c,0)" in t
    has_pm = "(±c,0)" in t
    return (has_neg_c and has_pos_c) or has_pm


def _looks_like_ready_to_continue(text: str) -> bool:
    """v3.28/v3.31/v3.55：学生表示「准备好进入下一节」的意图（用于 stage 间过渡）

    v3.55（2026-05-28 pilot 前增补）：扩展宽松确认词识别清单。
    pilot 体验测试发现学生会答 "ok/OK/Ok/没问题/对的" 等，原识别漏掉这些 → stage 卡死。
    本次修补 ABCD 4 档共用，不影响任一档对照基线。
    """
    from legacy.lesson_flow import _looks_like_understood
    if _looks_like_understood(text):
        return True
    t_low = text.strip().lower()
    if any(kw in text for kw in [
        "准备好", "好了", "可以了", "走起", "来吧", "开始", "继续吧",
        "没问题", "没毛病", "可以的", "明白了", "懂了",
    ]):
        return True
    # 单字/短词宽松确认（v3.55 加 ok/k/嗯嗯/对的/搞定）
    return t_low in (
        "好", "可以", "嗯", "行", "中", "成", "y", "yes",
        "ok", "okay", "k", "嗯嗯", "对", "对的", "搞定", "懂", "明白", "没事", "yep",
    )


def _looks_like_lesson_end(text: str) -> bool:
    """学生主动结课"""
    return any(kw in text for kw in ["结束", "没了", "没问题", "谢谢", "再见", "下课"])


def _looks_like_coord_choice(text: str) -> bool:
    """Imported from lesson_flow for use in handlers — re-exported here for convenience."""
    from legacy.lesson_flow import _looks_like_coord_choice as _lf_coord_choice
    return _lf_coord_choice(text)
