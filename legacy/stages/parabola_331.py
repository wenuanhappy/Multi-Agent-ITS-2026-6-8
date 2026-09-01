"""抛物线 3.3.1 抛物线及其标准方程 —— stage handlers + 静态数据"""
import re
from legacy.lesson_flow import LessonStage, LessonStep

# ---- 静态文本 + 关键词 ----
P331_OPENS_RIGHT_KEYWORDS = ["开口向右", "向右", "右开", "y²=2px", "y^2=2px", "x正", "x轴正"]
P331_OPENS_LEFT_KEYWORDS  = ["开口向左", "向左", "左开", "y²=-2px", "y^2=-2px", "x负", "x轴负"]
P331_OPENS_UP_KEYWORDS    = ["开口向上", "向上", "上开", "x²=2py", "x^2=2py", "y正", "y轴正"]
P331_OPENS_DOWN_KEYWORDS  = ["开口向下", "向下", "下开", "x²=-2py", "x^2=-2py", "y负", "y轴负"]


P331_INTRO_MSG = (
    "你好！今天我们一起学习 **3.3.1 抛物线及其标准方程**。\n\n"
    "**承接 3.2.2 离心率 e 的发现**：我们已经知道椭圆 $0<e<1$、双曲线 $e>1$。\n"
    "其中离心率 $e$ 描述的是：动点到**焦点**的距离 与 到**定直线**的距离之比 $k$。\n\n"
    "$$\n"
    "\\dfrac{|MF|}{d(M,l)}=k\n"
    "$$\n\n"
    "**一个自然的问题**：\n"
    "  · 当 $0<k<1$ 时是椭圆 ✓\n"
    "  · 当 $k>1$ 时是双曲线 ✓\n"
    "  · **当 $k=1$ 时**（动点到焦点的距离 = 到定直线的距离），轨迹会是什么形状？\n\n"
    "今天我们就来研究这个问题。先回忆一下 —— **椭圆和双曲线的定义分别是什么？**"
)

P331_RECALL_CONIC_MSG = (
    "👍 好的。回忆一下：\n"
    "  · **椭圆**：到两个定点的**距离之和**等于常数（且常数 > 焦距）\n"
    "  · **双曲线**：到两个定点的**距离之差的绝对值**等于常数（且常数 < 焦距）\n\n"
    "这两条都基于**两个**定点。如果只用 **1 个** 定点 + **1 条** 定直线（且直线不过该点），"
    "**让动点到定点的距离 = 到定直线的距离**，会画出什么形状？**先大胆猜一下**，不一定要答对。"
)

P331_PROBE_EQUAL_MSG = (
    "✅ 椭圆「距离之和」、双曲线「距离之差的绝对值」都记得很准！\n\n"
    "现在轮到 **$k=1$** 的情形：动点到**定点 $F$** 的距离 **等于** 它到**定直线 $l$** 的距离。\n\n"
    "**你猜这条轨迹会是什么形状？** 大胆猜一下，不一定要答对～"
)

# EXPLORE_LOCUS 入口（学生预测后发，附带 locus viz）
P331_EXPLORE_LOCUS_MSG = (
    "🎨 来动手画画看！\n\n"
    "右侧画布上已经放好了一个**定点 $F$** 和一条**定直线 $l$**（$l$ 不经过 $F$）。\n"
    "$H$ 是 $l$ 上的任意一点（可上下拖动）；过 $H$ 作 $MH\\perp l$；线段 $FH$ 的**垂直平分线**交 $MH$ 于点 $M$。\n\n"
    "**请拖动 $H$**，让 $M$ 随之运动 —— **观察 $|MF|$ 和 $|MH|$ 之间满足什么关系？** 看出关系后在下面告诉我。"
)

P331_AWAIT_SHAPE_NAME_MSG = (
    "🎯 漂亮！你画出了一条**开放的曲线**，并且整个过程中始终有 **$|MF|=|MH|$**。\n\n"
    "**你觉得这是什么图形？** 试着说出它的名字。"
)

P331_AWAIT_DEFINITION_MSG = (
    "✅ 没错，这就是 **抛物线 (parabola)**！\n\n"
    "回忆刚才作图过程：动点 $M$ 到**定点 $F$** 的距离始终等于它到**定直线 $l$** 的距离，"
    "并且 $l$ 不经过 $F$（否则轨迹退化）。\n\n"
    "**请你用自己的话归纳出抛物线的定义** —— 想清楚两个核心要素：到什么相等？还有什么限制条件？"
)

P331_AWAIT_DEF_EQUAL_NUDGE_MSG = (
    "👍 已经抓到关键之一。还差一个限制条件 —— 想一想：**定直线 $l$ 对定点 $F$ 有什么要求**？"
    "如果 $l$ 经过 $F$ 会怎么样？"
)

P331_AWAIT_DEF_LINE_NUDGE_MSG = (
    "👍 已经抓到关键之一。还差核心的**距离关系** —— $M$ 到 $F$ 的距离 与 $M$ 到 $l$ 的距离，是什么关系？"
)

P331_REFLECT_COORD_MSG = (
    "🟣 **思考 1**（教材 p130-131）。\n\n"
    "我们要给抛物线建立坐标系来求方程。回忆椭圆和双曲线建系时利用了**两个焦点的对称性**："
    "通常取焦点连线为 $x$ 轴、焦点连线中点为原点。\n\n"
    "抛物线只有**一个**焦点 $F$ 和**一条**准线 $l$，但仍有一个天然的**对称要素**——"
    "**过焦点 $F$ 且垂直于准线 $l$** 的那条直线。\n\n"
    "**你认为应该怎么建立坐标系，可能使所求抛物线的方程形式最简单？** 提示词："
    "**焦点 / 准线 / 垂线 / 中点 / 原点**。"
)

# 推导 4 子阶段提示
# 建系 build 完成 → 进入 locate_focus 子阶段（右侧画出抛物线，引导求焦点/准线）
P331_LOCATE_FOCUS_MSG = (
    "✅ 很好！按照你刚才说的建系：取过焦点 $F$ 且垂直于准线 $l$ 的直线为 $x$ 轴，垂足为 $K$，"
    "**$KF$ 的中点为原点 $O$**。右侧已经画出这条抛物线 📈\n"
    "设 $|KF|=p$（$p>0$）—— $p$ 是焦点到准线的距离。\n\n"
    "**先由你来定位**：$F$ 在 $x$ 轴正半轴、$K$ 在负半轴，$O$ 是 $KF$ 中点、$|KF|=p$。\n"
    "那么 **焦点 $F$ 的坐标是？准线 $l$ 的方程是？**（用 $p$ 表示）"
)

# locate_focus 完成 → 进入 DERIVE（推导标准方程）
P331_DERIVE_START_MSG = (
    "✅ 完全正确！焦点 $F\\left(\\dfrac{p}{2}, 0\\right)$，准线 $l: x=-\\dfrac{p}{2}$。\n"
    "**建系阶段完成** —— 接下来推导**标准方程**。\n\n"
    "设 $M(x, y)$ 是抛物线上任意一点，**先把 $|MF|$ 写出来**（用 $x, y, p$ 表示）。"
)

# ── P331_EXAMPLE 题目 hard-coded（教材原题，禁止改任何数值）──
P331_EXAMPLE_1_INTRO = (
    "📘 **例 1**（教材 p132，原题不得修改任何数值）\n\n"
    "(1) 已知抛物线的标准方程是 $y^2=6x$，求它的**焦点坐标**和**准线方程**；\n"
    "(2) 已知抛物线的焦点是 $F(0,-2)$，求它的**标准方程**。\n\n"
    "我们一步步来。先看 **(1)**：抛物线 $y^2=6x$，**焦点坐标是什么？**"
)

P331_EXAMPLE_2_INTRO = (
    "📘 **例 2**（教材 p132，卫星天线应用题，原题不得修改）\n\n"
    "一种卫星接收天线如图所示，其曲面与轴截面的交线为抛物线。在轴截面内的卫星波束呈近似平行状态射入"
    "形为抛物线的接收天线，经反射聚集到**焦点**处。\n\n"
    "已知接收天线的**口径（直径）为 $4.8\\ \\mathrm{m}$，深度为 $1\\ \\mathrm{m}$**。"
    "试建立适当的坐标系，求**抛物线的标准方程**和**焦点坐标**。\n\n"
    "**先建系**：右侧画布有截面示意 + 口径 / 深度标注。你觉得**怎么建系最方便**？开口边缘的点坐标是？"
)

P331_SUMMARY_MSG = (
    "🎓 **3.3.1 总结**：抛物线 & 三种圆锥曲线的统一对比\n\n"
    "**抛物线定义**：到一个定点 $F$（焦点）的距离 等于 到一条定直线 $l$（准线）的距离的点的轨迹（$l$ 不过 $F$）。\n\n"
    "**4 种标准方程对照**（设 $|KF|=p>0$）：\n\n"
    "| 开口方向 | 标准方程 | 焦点坐标 | 准线方程 |\n"
    "|---|---|---|---|\n"
    "| 右 | $y^2=2px$ | $\\left(\\dfrac{p}{2}, 0\\right)$ | $x=-\\dfrac{p}{2}$ |\n"
    "| 左 | $y^2=-2px$ | $\\left(-\\dfrac{p}{2}, 0\\right)$ | $x=\\dfrac{p}{2}$ |\n"
    "| 上 | $x^2=2py$ | $\\left(0, \\dfrac{p}{2}\\right)$ | $y=-\\dfrac{p}{2}$ |\n"
    "| 下 | $x^2=-2py$ | $\\left(0, -\\dfrac{p}{2}\\right)$ | $y=\\dfrac{p}{2}$ |\n\n"
    "**三种圆锥曲线在焦点-准线统一定义下**（$e=\\dfrac{|MF|}{d(M,l)}$）：\n"
    "  · $0<e<1$ → **椭圆**\n"
    "  · $e=1$  → **抛物线**\n"
    "  · $e>1$  → **双曲线**\n\n"
    "下一节 **3.3.2 抛物线的简单几何性质** 我们会研究范围、对称性、顶点、焦准距等性质。\n\n"
    "如果都明白了，回个『没问题』/『结束』我们就到这里。"
)


# ── ECCENTRICITY 6 个 phase 的子目标 ──
_E312_ECC_PHASE_GOALS = {
    "explore_c": (
        "🔵 **离心率探究 phase 1**：固定 $a$，改变 $c$。学生应该在沙盒动画里拖滑块，"
        "观察并回答「$c$ 越大椭圆越扁/越圆」。\n"
        "学生答出『$c$ 大变扁』或『$c$ 接近 $a$ 时椭圆压扁』即推进。\n"
        "**严禁**：直接给离心率定义，让学生先体感。\n\n"
        "可用动画：`show_e312_explore_c`（沙盒，$c$ 滑块）。"
    ) + _E312_VIZ_SUPPRESSION,
    "explore_a": (
        "🔵 **离心率探究 phase 2**：固定 $c$，改变 $a$。学生答出「$a$ 越大椭圆越圆」即推进。\n"
        "可用动画：`show_e312_explore_a`（沙盒，$a$ 滑块）。"
    ) + _E312_VIZ_SUPPRESSION,
    "induce_ratio": (
        "🧩 **诱导比值** phase：学生已发现 $c$ 大变扁、$a$ 大变圆 → 引导他想到要看 $c$ 和 $a$ "
        "的**比值** $c/a$。\n"
        "学生答出『比值 / c 比 a / c/a』即推进。\n"
        "**严禁**：直接说『叫做离心率』——让学生先发现量再命名。"
    ) + _E312_VIZ_SUPPRESSION,
    "define": (
        "📖 **定义 phase**：宣布命名 $e=c/a$ 叫离心率。让学生写出定义式 $e=c/a$。\n"
        "学生输入命中 $e=c/a$（sympy 等价）即推进。"
    ) + _E312_VIZ_SUPPRESSION,
    "geometry": (
        "🎚️ **几何意义 phase**：触发主板 e-slider（show_summary_viz）。\n"
        "学生拖 slider，需总结：「$e$ 越接近 1 越扁，越接近 0 越圆」。\n"
        "命中关键词「越扁 / 越圆 / 接近 1 / 接近 0」即推进。\n\n"
        "可用动画：主板 e-slider（show_summary_viz，已存在）。"
    ) + _E312_VIZ_SUPPRESSION,
    "range": (
        "📐 **范围 phase**：引导学生回答 $0<e<1$；同时追问 **a=b 时 e=?**\n"
        "学生答出 $0<e<1$ 即基本推进；再追问 a=b → c=0 → e=0，圆是椭圆的极限。\n"
        "学生答出『圆 / e=0 / 椭圆变圆』即完成。\n"
        "**严禁**：跳到双曲线 e>1。"
    ) + _E312_VIZ_SUPPRESSION,
}




# ---- Stage Goals ----
P331_STAGE_GOALS = {
    LessonStage.P331_INTRO: (
        "📒 3.3.1 开场（教材 p130 引言段）。承接 3.2.2 离心率 e：椭圆 e<1、双曲线 e>1，"
        "**当 k=1 时（动点到焦点的距离等于到定直线的距离），轨迹会是什么形状？**\n"
        "deterministic 文案 + 不剧透。学生看完直接推进 RECALL_CONIC。\n\n"
        "可用动画：`show_p331_intro`（k 滑轨：k<1 椭圆，k>1 双曲线，k=1 未知曲线占位）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_RECALL_CONIC: (
        "🔍 回忆椭圆「距离之和=常数」+ 双曲线「距离之差的绝对值=常数」。\n"
        "学生答出『和』/『差』等核心关键词 ≥2 个即推进 PROBE_EQUAL。\n"
        "**严禁**：直接说『抛物线是距离相等』（这是定义阶段的内容）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_PROBE_EQUAL: (
        "💡 思维实验：「距离相等」（k=1）的动点轨迹是什么？让学生大胆猜。\n"
        "学生说『开口曲线 / U 形 / 抛物线 / 不知道』等任意预测都可推进。\n"
        "**严禁**：替学生下结论 / 直接告知『是抛物线』。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_EXPLORE_LOCUS: (
        "🎨 探究 1（教材 p130 图 3.3-1）。右画布有定点 F、定直线 l、l 上动点 H、过 H 的垂线 m、"
        "FH 中垂线交 m 于 M。学生**拖动 H** 画 trail，观察 |MF|=|MH| 关系。\n"
        "前端事件 `p331_trail_completed` 触发推进；学生发文本则用关键词「|MF|=|MH|/距离相等/等距」推进。\n"
        "**严禁**：左侧文案预告轨迹形状 / 提前画抛物线（setup viz 必须空轨迹）。\n\n"
        "可用动画：`show_p331_locus_setup`（F/l/H/m/M，无轨迹）→ `show_p331_locus_solved`（trail 后含完整抛物线）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_AWAIT_SHAPE_NAME: (
        "🎯 等学生说出『**抛物线**』。命中 parabola 关键词即推进 AWAIT_DEFINITION。\n"
        "学生卡 ≥1 turn 时温和提示『形状像不像物理课讲过的抛物运动？』（不直接给名）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_AWAIT_DEFINITION: (
        "📝 归纳定义（教材 p130 定义段）。期待两个核心要素同时答出：\n"
        "  ① **距离相等**：到定点 F 的距离 = 到定直线 l 的距离\n"
        "  ② **l 不过 F**：定直线不经过定点（防退化为直线）\n"
        "学生只答 ① 时温和补问「这条定直线对焦点 F 有什么限制？」；只答 ② 时反过来引「距离关系是什么？」。\n"
        "**严禁**：直接补完整定义 / 提到焦点 / 准线术语（在下一 stage 才正式命名）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_REFLECT_COORD: (
        "🟣 思考 1（教材 p130-131）。让学生类比椭圆 / 双曲线，提出『取过 F 且垂直 l 的直线为 x 轴，KF 中点为原点』。\n"
        "学生答出关键意思（焦点、准线、垂线、中点）≥2 个即推进 DERIVE。\n"
        "**setup viz 是空白板**：handler 在学生答对后才发 solved viz 画轴、F(p/2,0)、l:x=-p/2 标注（首次引入 p）。\n\n"
        "可用动画：`show_p331_coord_setup`（空板，只显示文字提示）→ `show_p331_coord_solved`（含 x/y 轴 + F + l 标注 + |KF|=p）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_DERIVE_AND_RESULT: (
        "⭐ 推导阶段（教材 p131 推导段）。**4 子阶段苏格拉底链**：\n"
        "  ① write_distance: 写出 |MF|=√((x-p/2)²+y²)、d=|x+p/2|\n"
        "  ② setup_equation: 由定义 |MF|=d 建立方程\n"
        "  ③ square_both_sides: 两边平方\n"
        "  ④ final_form: 化简得到 **y²=2px (p>0)**\n"
        "走 _P331_DERIVE_PROTOCOL_SYSTEM_PROMPT 协议输出 socratic_text。\n"
        "**严禁**：提前提到『4 种开口方向』（属于下一 stage）/ 焦点准线性质 / 准线特殊性。\n\n"
        "可用动画：`show_p331_derive_setup`（F/l/M/距离虚线，无曲线无方程）→ `show_p331_derive_solved`（含曲线 + y²=2px 公式）。"
    ) + _P331_VIZ_SUPPRESSION,
    LessonStage.P331_FOUR_FORMS: (
        "🔍 探究 2（教材 p131 探究 2 + 教材 p131 表格）。4 种标准方程对照填表：\n"
        "  · 开口向右 y²=2px / 焦点 (p/2,0) / 准线 x=-p/2（已由推导得出）\n"
        "  · 开口向左 y²=-2px / 焦点 (-p/2,0) / 准线 x=p/2\n"
        "  · 开口向上 x²=2py / 焦点 (0,p/2) / 准线 y=-p/2\n"
        "  · 开口向下 x²=-2py / 焦点 (0,-p/2) / 准线 y=p/2\n"
        "**主路径前端点击**（`p331_form_clicked` 事件，参数 direction ∈ {right,left,up,down}）；"
        "学生用文字答时走角色 1 enum 兜底（_PHASE_CLASSIFY_CONFIG_P331）。\n"
        "**partial 累积**：4 个独立 sub-flag (opens_*_done)，全到才推进 EXAMPLE_1。\n"
        "**严禁**：替学生填表 / 一次给完 4 种方程。\n\n"
        "可用动画：`show_p331_four_forms_setup`（4 行空表 + 4 小图）→ `show_p331_four_forms_solved`（完整对照表）。"
    ) + _P331_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P331_EXAMPLE_1: (
        "🟡 例 1（教材 p132）。**题目原文（铁律：不得修改任何数值）**：\n"
        "  (1) 已知抛物线的标准方程是 $y^2=6x$，求它的焦点坐标和准线方程；\n"
        "  (2) 已知抛物线的焦点是 $F(0,-2)$，求它的标准方程。\n"
        "**标准答案**：\n"
        "  (1) $p=3$，焦点 $\\left(\\dfrac{3}{2},0\\right)$，准线 $x=-\\dfrac{3}{2}$。\n"
        "  (2) 焦点在 y 轴负半轴，设 $x^2=-2py$，由 $p/2=2$ 得 $p=4$，标准方程 $x^2=-8y$。\n"
        "4 phase 苏格拉底逐项问：ask_focus_1 → ask_directrix_1 → ask_form_2 → ask_eq_2。\n"
        "phase_goal 由 example_canonicals_p331.EXAMPLE_1_PHASE_GOAL 控制。partial 累积：先答任一项后再答另一项均累积。\n\n"
        "可用动画：`show_p331_example_1_setup`（题目文字 + 空坐标系）、`show_p331_example_1_solved`（含焦点 / 准线 / 曲线）。"
    ) + _P331_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P331_EXAMPLE_2: (
        "🟡 例 2（教材 p132 卫星天线应用题）。**题目原文（铁律：不得修改任何数值）**：\n"
        "  一种卫星接收天线如图，其曲面与轴截面的交线为抛物线。已知接收天线的口径（直径）为 **4.8 m**，深度为 **1 m**。"
        "试建立适当的坐标系，求抛物线的标准方程和焦点坐标。\n"
        "**标准答案**：取顶点为原点、焦点在 x 轴正半轴，设 $y^2=2px$。开口边缘点 $A(1, 2.4)$ 代入：$2.4^2=2p\\cdot 1$，"
        "解得 $p=2.88$。标准方程 $y^2=5.76x$，焦点 $(1.44, 0)$。\n"
        "3 phase：ask_setup（点 A 坐标 / 代入式）→ ask_p（p=2.88）→ ask_conclude（方程 + 焦点）。\n"
        "**ask_conclude partial 累积**：拆 equation_done + focus_done 两维度（学生可先答方程再答焦点，反之亦可）。\n\n"
        "可用动画：`show_p331_example_2_setup`（截面图 + 4.8m / 1m 标注，无求出曲线）、`show_p331_example_2_solved`（含曲线 + p=2.88 + 焦点 (1.44,0)）。"
    ) + _P331_VIZ_SUPPRESSION + _EXAMPLE_NO_FABRICATE_RULE,
    LessonStage.P331_SUMMARY: (
        "📒 3.3.1 总结阶段。回顾抛物线定义（距离相等）、4 种标准方程、与椭圆 / 双曲线的统一对比"
        "（焦点-准线统一定义：e<1 椭圆，e=1 抛物线，e>1 双曲线）。预告 3.3.2 几何性质。\n"
        "学生说『没问题』/『结束』时附加 [LESSON_END] 标记。\n\n"
        "可用动画：`show_p331_summary_compare`（三曲线 + 离心率统一对照图）。"
    ) + _P331_VIZ_SUPPRESSION,
}

_STAGE_GOALS.update(_STAGE_GOALS_P331)


# ════════════════════════════ 抛物线 3.3.2 几何性质（P332）════════════════════════════
# 结构仿 H322 性质章节奏；性质短答仿 P331（确定性推进 + 角色1 enum 兜底 + 角色3 苏格拉底阶梯反馈）；
# 例题/思考仿 P331 例题三层防御（角色2 路径2 协议 + sympy + partial 累积 + awaiting_next）。
# 设计见 docs/3.3.2_design_phase1.md。

_P332_VIZ_SUPPRESSION = (
    "\n\n**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
    "学生明确要求看动画时温和回应「好的，我们看一个动画」，由系统自动配图。"
    "**严禁承诺画不出的图**。"
)

# ---- Course Config ----
P331_COURSE_CONFIG = {
    "parabola_331": {
        "name_cn": "3.3.1 抛物线及其标准方程",
        "scope": "parabola",
        "first_stage": LessonStage.P331_INTRO,
        "start_stage": LessonStage.P331_INTRO,  # 学生回答后由 INTRO handler 推进到 RECALL_CONIC
        "kg_nodes_basic": [
            "foundation_distance_formula", "foundation_locus",
            "parabola_definition", "concept_focus_directrix_unified",
        ],
        "kg_nodes_equation": [
            "parabola_standard_equation_right", "parabola_standard_equation_left",
            "parabola_standard_equation_up", "parabola_standard_equation_down",
        ],
        "kg_nodes_examples": {
            LessonStage.P331_EXAMPLE_1: ["parabola_331_example_1"],
            LessonStage.P331_EXAMPLE_2: ["parabola_331_example_2"],
        },
        # 3.3.1 不涉及离心率（属于 3.3.2），保持空集
        "kg_nodes_eccentricity": [],
        "eccentricity_stages": set(),
        "summary_kg_nodes": [
            "parabola_definition", "parabola_standard_equation_right",
            "concept_focus_directrix_unified",
        ],
    },
}

# ---- Mandatory VIZ ----
P331_MANDATORY_VIZ = {
    LessonStage.P331_INTRO: {"action": "show_p331_intro"},
    LessonStage.P331_EXPLORE_LOCUS: {"action": "show_p331_locus_setup"},      # 不剧透：F/l/H/m/M 无轨迹
    LessonStage.P331_REFLECT_COORD: {"action": "show_p331_coord_setup"},      # 不剧透：空板只显文字提示
    LessonStage.P331_DERIVE_AND_RESULT: {"action": "show_p331_derive_setup"}, # 不剧透：F/l/M/距离虚线，无曲线无方程
    LessonStage.P331_FOUR_FORMS: {"action": "show_p331_form_left"},    # 一次一图：从开口向左开始（不剧透）
    LessonStage.P331_EXAMPLE_1: {"action": "show_p331_example_1_setup"},      # 不剧透：题目 + 空坐标系
    LessonStage.P331_EXAMPLE_2: {"action": "show_p331_example_2_setup"},      # 不剧透：截面图 + 标注，无求出曲线
    LessonStage.P331_SUMMARY: {"action": "show_p331_summary_compare"},        # solved 版：含三曲线统一对比
}

# ---- Skip function ----
def _looks_like_skip_to_example_331(text: str):
    """识别 3.3.1 学生跳级到例 N（1 / 2）的意图。
    支持显式"跳到例 N"、隐式"看天线 / 卫星 / 应用题"等指代例 2，"看 y²=6x / 双向题"指代例 1。
    返回 1 / 2 / None。
    """
    t = text.replace(" ", "")
    has_skip_intent = any(kw in t for kw in [
        "直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第", "看练习", "进入练习",
        "看应用", "看题", "做题",
    ])
    # 显式编号
    if has_skip_intent:
        if "例1" in t or "例一" in t or "第一题" in t or "第1题" in t:
            return 1
        if "例2" in t or "例二" in t or "第二题" in t or "第2题" in t:
            return 2
    # 隐式指代例 2（卫星天线应用题）
    e2_kws = ["卫星", "天线", "接收天线", "应用题", "口径", "深度"]
    if any(kw in text for kw in e2_kws):
        return 2


# ---- Stage Dispatch Registry ----
P331_STAGE_DISPATCH = {
    LessonStage.P331_INTRO: ("_handle_p331_intro", {}),
    LessonStage.P331_RECALL_CONIC: ("_handle_p331_recall_conic", {}),
    LessonStage.P331_PROBE_EQUAL: ("_handle_p331_probe_equal", {}),
    LessonStage.P331_EXPLORE_LOCUS: ("_handle_p331_explore_locus", {}),
    LessonStage.P331_AWAIT_SHAPE_NAME: ("_handle_p331_await_shape_name", {}),
    LessonStage.P331_AWAIT_DEFINITION: ("_handle_p331_await_definition", {}),
    LessonStage.P331_REFLECT_COORD: ("_handle_p331_reflect_coord", {}),
    LessonStage.P331_DERIVE_AND_RESULT: ("_handle_p331_derive_and_result", {}),
    LessonStage.P331_FOUR_FORMS: ("_handle_p331_four_forms", {}),
    LessonStage.P331_EXAMPLE_1: ("_handle_p331_example_1", {}),
    LessonStage.P331_EXAMPLE_2: ("_handle_p331_example_2", {}),
    LessonStage.P331_SUMMARY: ("_handle_p331_summary", {}),
}


class Parabola331Mixin:
    """抛物线 3.3.1 课 stage handlers（作为 LessonFlow 的 mixin 使用）"""

    def _handle_p331_example_generic(self, text: str, example_key) -> LessonStep:
        """v3.x: 例 1 / 例 2 共用 handler。三层判断 + partial 累积 + 教学节奏保留。

        Layer 1: example_diagnostician_p331（全 goal 扫描）
        Layer 2: 路径 2 协议（_llm_p331_example_protocol）
        Layer 3: deterministic 提示
        """
        from .example_canonicals_p331 import EXAMPLE_CONFIGS_P331
        from .example_diagnostician_p331 import diagnose_example_p331, ExampleDiagnosisP331

        if not hasattr(self, "_p331_example_phase_idx"):
            self._p331_example_phase_idx = {1: 0, 2: 0}
            self._p331_example_subflags = {1: set(), 2: set()}

        # awaiting_next 检查
        awaiting_key = getattr(self, "_p331_example_done_awaiting_next", None)
        if awaiting_key is not None:
            if _looks_like_ready_to_continue(text):
                delattr(self, "_p331_example_done_awaiting_next")
                return self._continue_to_next_p331_example(awaiting_key)
            return LessonStep(
                stage=self.stage.value,
                message=f"例 {awaiting_key} 已经完成 🎉 看完右边的图后回个『好』/『继续』就切到下一题；想再看图随便拖。",
            )

        # 跨例跳级
        skip = _looks_like_skip_to_example_331(text)
        if skip and skip != example_key:
            return self._jump_to_p331_example(skip)

        config = EXAMPLE_CONFIGS_P331[example_key]
        phases = config["phases"]
        idx = self._p331_example_phase_idx[example_key]
        current_phase = phases[idx] if idx < len(phases) else phases[-1]

        # Layer 1: 诊断器扫描所有 goal
        dx = diagnose_example_p331(text, example_key)

        # Layer 2: 协议兜底
        if dx is None:
            protocol = self._llm_p331_example_protocol(text, example_key, current_phase)
            if protocol is not None:
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = (protocol.get("ack_text") or "请继续。")[:300]
                skip_n = protocol.get("skip_to_example")

                # (a) skip_request → 跳例
                if diag == "skip_request" and skip_n in (1, 2):
                    return self._jump_to_p331_example(skip_n)

                # (b) correct + advance → 模拟诊断器命中
                if diag == "correct" and protocol.get("advance") is True:
                    goal_name = protocol.get("hit_goal") or "equation"
                    flags = set(config["implies"].get(goal_name, set()))
                    if not flags:
                        flags = {f"{goal_name}_done"}
                    dx = ExampleDiagnosisP331(
                        hit_goal=goal_name, hit_goals=[goal_name],
                        implied_flags=flags,
                        label="完全正确（协议）", via="protocol",
                    )
                    # fall through

                elif diag in ("partial", "wrong", "off_topic"):
                    return LessonStep(stage=self.stage.value, message=ack_text)

        # Layer 3: 仍 None → deterministic 提示
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？或者把你的答案写完整些（坐标可以写成 (a, b)，方程写成 y²=2px 这样）。",
            )

        # 命中：累积 + 判定收尾或继续节奏
        self._p331_example_subflags[example_key] |= dx.implied_flags
        subflags = self._p331_example_subflags[example_key]

        done_fn = config["done_fn"]
        if done_fn(subflags):
            self._p331_example_phase_idx[example_key] = len(phases)
            return self._advance_p331_example(example_key, ack="✅ 完全正确！")

        # 部分命中：找下一未答完 phase（按教学节奏）
        next_phase = None
        next_missing: set = set()
        for ph in phases:
            required = _P331_PHASE_REQUIRED_FLAGS.get((example_key, ph), set())
            missing = required - subflags
            if missing:
                next_phase = ph
                next_missing = missing
                break
        if next_phase is None:
            return self._advance_p331_example(example_key, ack="✅ 完全正确！")

        self._p331_example_phase_idx[example_key] = phases.index(next_phase)

        # missing-aware prompt（多-flag phase 内部部分命中时）
        next_prompt = None
        next_required = _P331_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
        if len(next_missing) == 1 and len(next_required) >= 2:
            single_missing = next(iter(next_missing))
            next_prompt = _P331_PHASE_PROMPT_BY_MISSING.get(
                (example_key, next_phase, single_missing)
            )
        if next_prompt is None:
            # 学生可见提问（不含答案）；找不到再退回通用语
            next_prompt = _EXAMPLE_STUDENT_PROMPT_P331.get(
                (example_key, next_phase),
                "请继续。",
            )

        # 干净 ack（不暴露内部 goal 名）
        ack_msg = "✅ 收到。"
        # 例 2：建系（ask_setup）答完进入后续 phase 时，才发坐标系图（setup 图无坐标轴，不剧透建系）
        canvas = None
        if (example_key == 2 and next_phase in ("ask_p", "ask_conclude")
                and not getattr(self, "_p331_ex2_coords_shown", False)):
            self._p331_ex2_coords_shown = True
            canvas = {"action": "show_p331_example_2_coords"}
        return LessonStep(stage=self.stage.value, message=ack_msg + "\n\n" + next_prompt,
                          canvas_action=canvas)

    # ---- 12 个 stage handler ----



    def _jump_to_p331_example(self, target_key) -> LessonStep:
        """从任何 stage 跳到例 1 / 例 2。"""
        stage_map = {
            1: (LessonStage.P331_EXAMPLE_1, P331_EXAMPLE_1_INTRO),
            2: (LessonStage.P331_EXAMPLE_2, P331_EXAMPLE_2_INTRO),
        }
        if target_key not in stage_map:
            return LessonStep(stage=self.stage.value, message="抱歉，没找到对应的例题。")
        target_stage, intro = stage_map[target_key]
        self.stage = target_stage
        viz = P331_MANDATORY_VIZ.get(target_stage)
        return LessonStep(
            stage=self.stage.value,
            message=f"好的，切到例 {target_key}（教材 3.3.1 节原题）：\n\n" + intro,
            canvas_action=viz,
        )


    def _advance_p331_example(self, example_key, ack: str = "") -> LessonStep:
        """例题通关 → 发 solved viz + awaiting_next。学生确认后才切下一题。"""
        solved_action = {"action": f"show_p331_example_{example_key}_solved"}
        actions: List[Dict[str, Any]] = [solved_action]
        # 例 2 通关后可追加 explore 互动（不强求）；当前不加
        self._p331_example_done_awaiting_next = example_key
        head = ack + "\n\n" if ack else ""
        if example_key == 2:
            tail = (
                "🎉 例 2 完成！右边是完整解答图。\n\n"
                "本节内容（例 1 + 例 2）全部做完。回个『好』/『继续』我们看本课总结 📒。"
            )
        else:
            tail = "🎉 例 1 完成！右边是完整解答图。回个『好』/『继续』我们看下一题。"
        return LessonStep(
            stage=self.stage.value,
            message=head + tail,
            canvas_action=actions if len(actions) > 1 else actions[0],
        )


    def _continue_to_next_p331_example(self, completed_key) -> LessonStep:
        """学生确认后真正切到下一例 / SUMMARY。"""
        if completed_key == 1:
            self.stage = LessonStage.P331_EXAMPLE_2
            next_msg = P331_EXAMPLE_2_INTRO
            viz = P331_MANDATORY_VIZ.get(LessonStage.P331_EXAMPLE_2)
        else:  # 2 → SUMMARY
            self.stage = LessonStage.P331_SUMMARY
            next_msg = P331_SUMMARY_MSG
            viz = {"action": "show_p331_summary_compare"}
        return LessonStep(stage=self.stage.value, message=next_msg, canvas_action=viz)

    # ---- 例题通用 handler（仿 _handle_h321_example_generic）----

    def _handle_p331_example_generic(self, text: str, example_key) -> LessonStep:
        """v3.x: 例 1 / 例 2 共用 handler。三层判断 + partial 累积 + 教学节奏保留。

        Layer 1: example_diagnostician_p331（全 goal 扫描）
        Layer 2: 路径 2 协议（_llm_p331_example_protocol）
        Layer 3: deterministic 提示
        """
        from .example_canonicals_p331 import EXAMPLE_CONFIGS_P331
        from .example_diagnostician_p331 import diagnose_example_p331, ExampleDiagnosisP331

        if not hasattr(self, "_p331_example_phase_idx"):
            self._p331_example_phase_idx = {1: 0, 2: 0}
            self._p331_example_subflags = {1: set(), 2: set()}

        # awaiting_next 检查
        awaiting_key = getattr(self, "_p331_example_done_awaiting_next", None)
        if awaiting_key is not None:
            if _looks_like_ready_to_continue(text):
                delattr(self, "_p331_example_done_awaiting_next")
                return self._continue_to_next_p331_example(awaiting_key)
            return LessonStep(
                stage=self.stage.value,
                message=f"例 {awaiting_key} 已经完成 🎉 看完右边的图后回个『好』/『继续』就切到下一题；想再看图随便拖。",
            )

        # 跨例跳级
        skip = _looks_like_skip_to_example_331(text)
        if skip and skip != example_key:
            return self._jump_to_p331_example(skip)

        config = EXAMPLE_CONFIGS_P331[example_key]
        phases = config["phases"]
        idx = self._p331_example_phase_idx[example_key]
        current_phase = phases[idx] if idx < len(phases) else phases[-1]

        # Layer 1: 诊断器扫描所有 goal
        dx = diagnose_example_p331(text, example_key)

        # Layer 2: 协议兜底
        if dx is None:
            protocol = self._llm_p331_example_protocol(text, example_key, current_phase)
            if protocol is not None:
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = (protocol.get("ack_text") or "请继续。")[:300]
                skip_n = protocol.get("skip_to_example")

                # (a) skip_request → 跳例
                if diag == "skip_request" and skip_n in (1, 2):
                    return self._jump_to_p331_example(skip_n)

                # (b) correct + advance → 模拟诊断器命中
                if diag == "correct" and protocol.get("advance") is True:
                    goal_name = protocol.get("hit_goal") or "equation"
                    flags = set(config["implies"].get(goal_name, set()))
                    if not flags:
                        flags = {f"{goal_name}_done"}
                    dx = ExampleDiagnosisP331(
                        hit_goal=goal_name, hit_goals=[goal_name],
                        implied_flags=flags,
                        label="完全正确（协议）", via="protocol",
                    )
                    # fall through

                elif diag in ("partial", "wrong", "off_topic"):
                    return LessonStep(stage=self.stage.value, message=ack_text)

        # Layer 3: 仍 None → deterministic 提示
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？或者把你的答案写完整些（坐标可以写成 (a, b)，方程写成 y²=2px 这样）。",
            )

        # 命中：累积 + 判定收尾或继续节奏
        self._p331_example_subflags[example_key] |= dx.implied_flags
        subflags = self._p331_example_subflags[example_key]

        done_fn = config["done_fn"]
        if done_fn(subflags):
            self._p331_example_phase_idx[example_key] = len(phases)
            return self._advance_p331_example(example_key, ack="✅ 完全正确！")

        # 部分命中：找下一未答完 phase（按教学节奏）
        next_phase = None
        next_missing: set = set()
        for ph in phases:
            required = _P331_PHASE_REQUIRED_FLAGS.get((example_key, ph), set())
            missing = required - subflags
            if missing:
                next_phase = ph
                next_missing = missing
                break
        if next_phase is None:
            return self._advance_p331_example(example_key, ack="✅ 完全正确！")

        self._p331_example_phase_idx[example_key] = phases.index(next_phase)

        # missing-aware prompt（多-flag phase 内部部分命中时）
        next_prompt = None
        next_required = _P331_PHASE_REQUIRED_FLAGS.get((example_key, next_phase), set())
        if len(next_missing) == 1 and len(next_required) >= 2:
            single_missing = next(iter(next_missing))
            next_prompt = _P331_PHASE_PROMPT_BY_MISSING.get(
                (example_key, next_phase, single_missing)
            )
        if next_prompt is None:
            # 学生可见提问（不含答案）；找不到再退回通用语
            next_prompt = _EXAMPLE_STUDENT_PROMPT_P331.get(
                (example_key, next_phase),
                "请继续。",
            )

        # 干净 ack（不暴露内部 goal 名）
        ack_msg = "✅ 收到。"
        # 例 2：建系（ask_setup）答完进入后续 phase 时，才发坐标系图（setup 图无坐标轴，不剧透建系）
        canvas = None
        if (example_key == 2 and next_phase in ("ask_p", "ask_conclude")
                and not getattr(self, "_p331_ex2_coords_shown", False)):
            self._p331_ex2_coords_shown = True
            canvas = {"action": "show_p331_example_2_coords"}
        return LessonStep(stage=self.stage.value, message=ack_msg + "\n\n" + next_prompt,
                          canvas_action=canvas)

    # ---- 12 个 stage handler ----


    def _handle_p331_intro(self, text: str) -> LessonStep:
        """1. 开场。学生第一句即对『回忆椭圆+双曲线定义』的作答 → 走 RECALL 累积逻辑。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        # 第一句答案直接进入 RECALL_CONIC 累积（真实检验两条定义）
        self.stage = LessonStage.P331_RECALL_CONIC
        step = self._p331_recall_accumulate(text)
        if step is not None:
            return step
        # 一个定义都没答出 → 角色 3 苏格拉底提示（罐头兜底）
        sub = ("学生要回忆椭圆和双曲线的定义，但还没答到点上。引导他：椭圆是到两焦点的**距离之和**为定值，"
               "双曲线是到两焦点的**距离之差的绝对值**为定值。不要直接报完整定义，启发他自己说。")
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "recall_both", sub, P331_RECALL_CONIC_MSG))


    def _handle_p331_recall_conic(self, text: str) -> LessonStep:
        """2. 回忆椭圆 / 双曲线定义。确定性关键词推进 + 角色 1 enum 兜底 + partial 累积 + 角色 3 提示。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        step = self._p331_recall_accumulate(text)
        if step is not None:
            return step
        # 都没命中 → 角色 3 苏格拉底提示（罐头兜底）
        sub = ("学生要回忆椭圆和双曲线的定义，但还没答到点上。引导他：椭圆是到两焦点的**距离之和**为定值，"
               "双曲线是到两焦点的**距离之差的绝对值**为定值。不要直接报完整定义，启发他自己说。")
        fb = ("提示：椭圆是『到两个焦点距离**之和**为定值』；双曲线是『距离**之差的绝对值**为定值』。"
              "请把这两条都说一遍试试（可以分多次答）。")
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "recall_both", sub, fb))


    def _handle_p331_probe_equal(self, text: str) -> LessonStep:
        """3. 思维实验：让学生大胆猜。无论答什么都推进到 EXPLORE_LOCUS（**此时发 locus viz**）。
        确定性 ack（仿 3.2.1 _handle_h321_probe_difference，不走角色 4 自由 ack）。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        if any(kw in text for kw in ["不知道", "不清楚", "没想法"]):
            ack = "没关系，动手画一画就清楚了。\n\n"
        elif any(kw in text for kw in ["抛物线", "parabola"]):
            ack = "👍 不错的猜想！我们去画布验证一下。\n\n"
        else:
            ack = "好，我们去画布上看看。\n\n"
        self.stage = LessonStage.P331_EXPLORE_LOCUS
        viz = P331_MANDATORY_VIZ.get(LessonStage.P331_EXPLORE_LOCUS)
        return LessonStep(
            stage=self.stage.value,
            message=ack + P331_EXPLORE_LOCUS_MSG,
            canvas_action=viz,
            expect_event="trail_completed",
        )


    def _handle_p331_explore_locus(self, text: str) -> LessonStep:
        """4. 探究 1。前端 p331_trail_completed 触发推进；学生发关键词也可推进（确定性）。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        # 学生直接说"抛物线"：跳过 SHAPE_NAME 直接 DEFINITION（确定性转场）
        if _looks_like_parabola_name_p331(text):
            self.stage = LessonStage.P331_AWAIT_DEFINITION
            return LessonStep(stage=self.stage.value, message=P331_AWAIT_DEFINITION_MSG)
        # 学生命中 |MF|=|MH| 关键意思（宽松识别『相等』『一样』『MF=MH』等）（确定性转场）
        if _looks_like_mf_eq_mh_p331(text):
            self._p331_clear_stuck("explore")
            self.stage = LessonStage.P331_AWAIT_SHAPE_NAME
            return LessonStep(stage=self.stage.value, message=P331_AWAIT_SHAPE_NAME_MSG)
        # 卡住 → 角色 3 苏格拉底提示（罐头兜底）
        sub = ("学生在拖动点 M 观察 |MF|（到焦点距离）和 |MH|（到准线距离）的关系，还没看出关系。"
               "引导他注意左侧两个实时读数始终相等。不要直接说出『相等』，让他自己发现。")
        fb = "拖动橙点 $M$，看左边 $|MF|$ 和 $|MH|$ 两个实时数值 —— 它们是什么关系？看出来后告诉我（比如『相等』）。"
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "explore", sub, fb))


    def _handle_p331_await_shape_name(self, text: str) -> LessonStep:
        """5. 等学生说『抛物线』。确定性关键词推进 + 角色 1 enum 兜底 + 角色 3 提示。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        # Layer 1 关键词 + Layer 2 enum 兜底
        hit_name = _looks_like_parabola_name_p331(text)
        if not hit_name:
            cls = self._resolve_phase_answer(text, "p331_shape_name", lambda _t: None)[0]
            hit_name = (cls == "parabola")
        if hit_name:
            self._p331_clear_stuck("shape")
            self.stage = LessonStage.P331_AWAIT_DEFINITION
            return LessonStep(stage=self.stage.value, message=P331_AWAIT_DEFINITION_MSG)
        # 卡住 → 角色 3 苏格拉底提示（罐头兜底）
        sub = ("学生画出了一条开放的 U 形曲线，要他说出名字『抛物线』。"
               "引导：物理课抛出去的小球做的就是这种运动，名字以『抛』开头。不要直接说出『抛物线』。")
        fb = "提示：这条开放曲线在物理课讲过 —— 抛出去的小球做的就是这种运动。你猜叫什么？"
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "shape", sub, fb))


    def _handle_p331_await_definition(self, text: str) -> LessonStep:
        """6. 学生归纳定义。**partial 累积**：距离相等 + l 不过 F 两要素跨轮累积，
        两个都命中才推进；只命中一项给针对性追问另一项。"""
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        if not hasattr(self, "_p331_def_done"):
            self._p331_def_done = set()
        # Layer 1：关键词
        if _looks_like_parabola_def_has_equal(text):
            self._p331_def_done.add("def_equal")
        if _looks_like_parabola_def_has_constraint(text):
            self._p331_def_done.add("def_constraint")
        # Layer 2：角色 1 enum 兜底（捕捉关键词漏掉的口语；只分类不驱动状态）
        if not {"def_equal", "def_constraint"}.issubset(self._p331_def_done):
            hit = self._resolve_phase_answer(text, "p331_await_definition", lambda _t: None)[0]
            if hit == "equal":
                self._p331_def_done.add("def_equal")
            elif hit == "constraint":
                self._p331_def_done.add("def_constraint")
            elif hit == "both":
                self._p331_def_done.update({"def_equal", "def_constraint"})
        done = self._p331_def_done
        # 两要素齐 → 推进 REFLECT_COORD（确定性转场）
        if {"def_equal", "def_constraint"}.issubset(done):
            self._p331_clear_stuck("def_equal", "def_constraint", "def_both")
            self.stage = LessonStage.P331_REFLECT_COORD
            return LessonStep(stage=self.stage.value, message=P331_REFLECT_COORD_MSG)
        # 只命中距离相等 → 角色 3 追问限制条件（罐头兜底）
        if "def_equal" in done:
            sub = ("学生已说出抛物线定义的『距离相等』要素（到定点=到定直线的距离），"
                   "还差**限制条件**：定直线 l **不经过**定点 F（否则轨迹退化）。引导他想这个限制，不要直接说出。")
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "def_equal", sub, P331_AWAIT_DEF_EQUAL_NUDGE_MSG))
        # 只命中限制条件 → 角色 3 追问距离关系（罐头兜底）
        if "def_constraint" in done:
            sub = ("学生已说出『定直线不过定点』的限制，还差**核心距离关系**：到定点 F 的距离 = 到定直线 l 的距离。"
                   "引导他说出这个相等关系，不要直接给出。")
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "def_constraint", sub, P331_AWAIT_DEF_LINE_NUDGE_MSG))
        # 一个都没命中 → 角色 3 提示（罐头兜底）
        sub = ("学生在归纳抛物线定义，还没答到点上。两要素：① 到定点和到定直线的**距离相等**；"
               "② 定直线**不经过**定点。引导他往这两点想，不要直接给出完整定义。")
        fb = "提示：抛物线定义两要素 ——（1）到**定点**和到**定直线**的距离是什么关系？（2）这条**定直线**对定点有什么要求？"
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "def_both", sub, fb))


    def _handle_p331_reflect_coord(self, text: str) -> LessonStep:
        """7. 思考 1：建系（**两子阶段**）。
        子阶段 build：① x 轴 = 过 F 垂直准线；② 原点 = KF 中点 —— 两要素累积。
        子阶段 locate_focus：build 完成后右侧画出抛物线，引导学生写出
                             焦点 F(p/2,0) + 准线 x=-p/2；两个都对 → 推进 DERIVE。
        全程确定性 + 角色 1 enum 兜底（只分类不驱动状态）。
        """
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)
        if not hasattr(self, "_p331_coord_subphase"):
            self._p331_coord_subphase = "build"

        # ───── 子阶段 2：locate_focus（焦点坐标 + 准线方程）─────
        if self._p331_coord_subphase == "locate_focus":
            if not hasattr(self, "_p331_focus_done"):
                self._p331_focus_done = set()
            # Layer 1 关键词
            if _looks_like_p331_focus_pq(text):
                self._p331_focus_done.add("focus")
            if _looks_like_p331_directrix_pq(text):
                self._p331_focus_done.add("directrix")
            # Layer 2 enum 兜底
            if not {"focus", "directrix"}.issubset(self._p331_focus_done):
                hit = self._resolve_phase_answer(text, "p331_locate_focus", lambda _t: None)[0]
                if hit == "focus":
                    self._p331_focus_done.add("focus")
                elif hit == "directrix":
                    self._p331_focus_done.add("directrix")
                elif hit == "both":
                    self._p331_focus_done.update({"focus", "directrix"})
            fdone = self._p331_focus_done
            # 两个都对 → 建系阶段完成，推进 DERIVE
            if {"focus", "directrix"}.issubset(fdone):
                self.stage = LessonStage.P331_DERIVE_AND_RESULT
                viz = P331_MANDATORY_VIZ.get(LessonStage.P331_DERIVE_AND_RESULT)
                return LessonStep(
                    stage=self.stage.value,
                    message=P331_DERIVE_START_MSG,
                    canvas_action=viz,
                )
            # 只答对焦点 → 角色 3 追问准线（罐头兜底）
            if "focus" in fdone:
                sub = ("学生已写对焦点 $F(p/2,0)$，还差**准线方程**：$K$ 在 x 轴负半轴、$OK=p/2$，"
                       "准线是过 K 的竖直线，方程 $x=-p/2$。引导他自己写出，不要直接报答案。")
                fb = "✅ 焦点坐标对了。那 **准线 $l$ 的方程**呢？$K$ 在 x 轴负半轴、$OK=\\dfrac{p}{2}$，准线过 $K$ 竖直 —— 方程是？"
                return LessonStep(stage=self.stage.value,
                                  message=self._p331_socratic(text, "lf_focus", sub, fb))
            # 只答对准线 → 角色 3 追问焦点（罐头兜底）
            if "directrix" in fdone:
                sub = ("学生已写对准线 $x=-p/2$，还差**焦点坐标**：$F$ 在 x 轴正半轴、$OF=p/2$，"
                       "焦点 $(p/2,0)$。引导他自己写出，不要直接报答案。")
                fb = "✅ 准线方程对了。那 **焦点 $F$ 的坐标**呢？$F$ 在 x 轴正半轴、$OF=\\dfrac{p}{2}$ —— 坐标是？"
                return LessonStep(stage=self.stage.value,
                                  message=self._p331_socratic(text, "lf_dir", sub, fb))
            # 都没对 → 角色 3 提示（罐头兜底）
            sub = ("学生要由 $|KF|=p$、$O$ 是 KF 中点 写出焦点坐标和准线方程。$OF=OK=p/2$，"
                   "$F$ 在正半轴 → $(p/2,0)$；$K$ 在负半轴、准线过 K 竖直 → $x=-p/2$。引导他想，不要直接报答案。")
            fb = ("提示：$O$ 是 $KF$ 中点、$|KF|=p$，所以 $OF=OK=\\dfrac{p}{2}$。"
                  "$F$ 在正半轴 → 焦点坐标？准线过 $K$ 竖直 → 准线方程？（用 $p$ 表示）")
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "lf_both", sub, fb))

        # ───── 子阶段 1：build（x 轴 + 原点）─────
        if not hasattr(self, "_p331_coord_done"):
            self._p331_coord_done = set()
        # Layer 1：关键词
        if _looks_like_p331_axis_correct(text):
            self._p331_coord_done.add("axis")
        if _looks_like_p331_origin_correct(text):
            self._p331_coord_done.add("origin")
        directrix_misuse = _looks_like_p331_directrix_as_axis(text)
        # Layer 2：角色 1 enum 兜底（只分类不驱动状态）
        if not {"axis", "origin"}.issubset(self._p331_coord_done):
            hit = self._resolve_phase_answer(text, "p331_reflect_coord", lambda _t: None)[0]
            if hit == "axis":
                self._p331_coord_done.add("axis")
            elif hit == "origin":
                self._p331_coord_done.add("origin")
            elif hit == "both":
                self._p331_coord_done.update({"axis", "origin"})
            elif hit == "directrix_as_axis":
                directrix_misuse = True
        done = self._p331_coord_done

        # build 两要素齐 → 进入 locate_focus 子阶段（右侧画出抛物线 + 引导求焦点/准线）
        if {"axis", "origin"}.issubset(done):
            self._p331_clear_stuck("coord_axis", "coord_origin", "coord_both")
            self._p331_coord_subphase = "locate_focus"
            self._p331_focus_done = set()
            return LessonStep(
                stage=self.stage.value,
                message=P331_LOCATE_FOCUS_MSG,
                canvas_action={"action": "show_p331_coord_solved"},
            )
        # 只答对 x 轴 → 角色 3 追问原点（罐头兜底）
        if "axis" in done:
            sub = ("学生已答对 x 轴（过焦点 F 垂直准线），还差**原点位置**：应取在焦点 F 和准线 l 之间的"
                   "**中点**（最对称）。引导他想原点取哪最对称，不要直接说出。")
            fb = "✅ $x$ 轴选得好。那 **原点** 该取在哪里最对称？想想焦点 $F$ 和准线 $l$ 之间，哪个位置左右对称？"
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "coord_origin", sub, fb))
        # 只答对原点 → 角色 3 追问 x 轴（罐头兜底）
        if "origin" in done:
            sub = ("学生已答对原点（焦点和准线之间的中点），还差 **x 轴**：应取**过焦点 F 且垂直于准线 l** 的那条直线"
                   "（它是抛物线的对称轴）。引导他想 x 轴怎么取，不要直接说出。")
            fb = "✅ 原点位置想得对。那 **$x$ 轴** 该怎么取？提示：过焦点 $F$ 且和准线 $l$ 有什么位置关系的直线？"
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "coord_axis", sub, fb))
        # 误区：把准线当坐标轴 → 角色 3 针对性纠正（罐头兜底）
        if directrix_misuse:
            sub = ("学生把准线 l 本身当成了坐标轴（误区）。纠正：准线本身不作坐标轴；"
                   "椭圆/双曲线用焦点连线作 x 轴，抛物线只有 1 个焦点，但**过 F 且垂直准线**的直线天然左右对称，"
                   "把它作 x 轴更合适。温和纠正后引导他重想 x 轴和原点。")
            fb = ("🤔 准线 $l$ 本身**不**作坐标轴哦。过 $F$ 且垂直于准线 $l$ 的那条直线天然左右对称 —— "
                  "把**它**作为 $x$ 轴更合适。你同意吗？那原点取在哪？")
            return LessonStep(stage=self.stage.value,
                              message=self._p331_socratic(text, "coord_both", sub, fb))
        # 一个都没答对 → 角色 3 提示（罐头兜底）
        sub = ("学生在想怎么给抛物线建系，还没答到点上。正确：x 轴 = 过焦点 F 垂直准线的直线；"
               "原点 = 焦点和准线之间的中点。引导他往这两点想，不要直接给出。")
        fb = ("提示：抛物线只有 1 个焦点 $F$ 和 1 条准线 $l$。**过 $F$ 且垂直 $l$** 的那条直线天然是对称轴 —— "
              "把它作为哪条轴？原点又该取在 $F$ 和 $l$ 之间的什么位置？")
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, "coord_both", sub, fb))


    def _handle_p331_derive_and_result(self, text: str) -> LessonStep:
        """8. 推导标准方程，角色 3 协议 4 子阶段链。
        子阶段顺序：write_distance → setup_equation → square_both_sides → final_form。
        （焦点坐标 / 准线方程 已在上一阶段 REFLECT_COORD 的 locate_focus 子阶段由学生导出。）
        """
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)

        if not hasattr(self, "_p331_derive_phase"):
            self._p331_derive_phase = "write_distance"
        current_phase = self._p331_derive_phase

        derive_phases = ["write_distance", "setup_equation", "square_both_sides", "final_form"]

        # awaiting_next：推导完成等学生确认
        if getattr(self, "_p331_derive_awaiting_next", False):
            if _looks_like_ready_to_continue(text):
                self._p331_derive_awaiting_next = False
                self.stage = LessonStage.P331_FOUR_FORMS
                # 进入探究 2：一次一图，从开口向左开始
                first_dir = _P331_FORM_ORDER[0]
                return LessonStep(
                    stage=self.stage.value,
                    message=(
                        "🎉 推导完成 —— 标准方程 $y^2=2px$（$p>0$，开口向右）。\n\n"
                        "**接下来探究 2**（教材 p131）：换个方向建系，方程会怎么变？我们一种一种来。\n\n"
                        + _p331_form_prompt(first_dir)
                    ),
                    canvas_action={"action": f"show_p331_form_{first_dir}"},
                )
            return LessonStep(
                stage=self.stage.value,
                message="推导已经做完啦 🎉 回个『好』/『继续』我们进入 4 种开口方向的对照。",
            )

        # 学生直答最终方程 → 跳过所有子阶段直接收尾
        if _looks_like_p331_final_eq(text):
            self._p331_derive_awaiting_next = True
            return LessonStep(
                stage=self.stage.value,
                message="✅ 完全正确！你直接导出了标准方程 $y^2=2px$（$p>0$）。\n\n"
                        "回个『好』/『继续』，我们进入**探究 2**：看看换个方向建系，方程会怎么变 👉",
                canvas_action={"action": "show_p331_derive_solved"},
            )

        # ── 确定性逐步检测（主路径，不做小错诊断；多设问 write_distance 跨轮累积）──
        def _derive_advance(next_phase: str, msg: str, viz=None) -> LessonStep:
            self._p331_derive_phase = next_phase
            return LessonStep(stage=self.stage.value, message=msg, canvas_action=viz)

        if current_phase == "write_distance":
            if not hasattr(self, "_p331_wd_done"):
                self._p331_wd_done = set()
            if _looks_like_p331_mf_formula(text):
                self._p331_wd_done.add("mf")
            if _looks_like_p331_d_formula(text):
                self._p331_wd_done.add("d")
            wd = self._p331_wd_done
            if {"mf", "d"}.issubset(wd):
                return _derive_advance(
                    "setup_equation",
                    "✅ 两个距离都写对了！\n\n**下一步**：由抛物线定义『到焦点距离 = 到准线距离』，"
                    "即 $|MF|=d$，把这个等式写出来。",
                )
            if "mf" in wd:
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ $|MF|$ 写对了！还差另一半 —— $M(x,y)$ 到准线 $x=-\\dfrac{p}{2}$ 的距离 $d$ 怎么表示？",
                )
            if "d" in wd:
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ $d$ 写对了！还差另一半 —— $M(x,y)$ 到焦点 $F\\left(\\dfrac{p}{2},0\\right)$ "
                            "的距离 $|MF|$ 用两点间距离公式怎么写？",
                )
            # 本轮两者都没命中 → 落到协议兜底（给思路，不纠小错）

        elif current_phase == "setup_equation":
            if _looks_like_p331_setup_eq(text):
                return _derive_advance(
                    "square_both_sides",
                    "✅ 方程建立得对！\n\n**下一步**：等号两边都是非负量，**两边平方**化掉根号和绝对值，写写看？",
                )

        elif current_phase == "square_both_sides":
            if _looks_like_p331_squared(text):
                return _derive_advance(
                    "final_form",
                    "✅ 平方对了！\n\n**最后一步**：展开两边的完全平方式，相同项会消掉，化简成最简形式。",
                )

        elif current_phase == "final_form":
            if _looks_like_p331_final_eq(text):
                self._p331_derive_awaiting_next = True
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 完全正确！化简得到标准方程 **$y^2=2px$**（$p>0$）。\n\n"
                            "回个『好』/『继续』，我们进入**探究 2**：换个方向建系，方程会怎么变 👉",
                    canvas_action={"action": "show_p331_derive_solved"},
                )

        # ── 走协议兜底（确定性没命中时；只给思路，不纠书写小错）──
        protocol = self._llm_p331_derive_protocol(text, current_phase)
        if protocol is None:
            # 协议挂 → deterministic fallback
            return LessonStep(
                stage=self.stage.value,
                message=_P331_DERIVE_PHASE_CONTEXT.get(current_phase, "继续推导。"),
            )

        diag = protocol.get("diagnosis", "off_topic")
        ack_text = (protocol.get("ack_text") or "继续。")[:300]

        if diag == "skip_request":
            skip_n = protocol.get("skip_to_example")
            if skip_n in (1, 2):
                return self._jump_to_p331_example(skip_n)

        # correct + advance：推到下一子阶段
        if diag == "correct" and protocol.get("advance") is True:
            cur_idx = derive_phases.index(current_phase)
            if cur_idx + 1 < len(derive_phases):
                self._p331_derive_phase = derive_phases[cur_idx + 1]
                return LessonStep(
                    stage=self.stage.value,
                    message=ack_text,
                )
            else:
                # 已是最后一子阶段 → 整个推导完成
                self._p331_derive_awaiting_next = True
                return LessonStep(
                    stage=self.stage.value,
                    message=ack_text + "\n\n🎉 整个推导完成，标准方程 $y^2=2px$（$p>0$）。\n\n"
                            "回个『好』/『继续』，我们进入**探究 2**：换个方向建系，方程会怎么变 👉",
                    canvas_action={"action": "show_p331_derive_solved"},
                )

        # partial / wrong / off_topic：ack 但不推进
        return LessonStep(stage=self.stage.value, message=ack_text)


    def _handle_p331_four_forms(self, text: str) -> LessonStep:
        """9. 探究 2：4 种开口方向（**一次一图，逐方向探究**）。
        开口向右已在推导阶段导出；本阶段按对称变换依次探究 左 → 上 → 下 3 种。
        每个方向：学生输入 ① 标准方程 ② 焦点坐标 ③ 准线方程，三项累积齐 → 出下一幅图。
        确定性结构检测（不计书写格式），无角色 4 自由 ack。
        """
        skip = _looks_like_skip_to_example_331(text)
        if skip:
            return self._jump_to_p331_example(skip)

        # awaiting_next：3 个方向都探究完
        if getattr(self, "_p331_ff_awaiting_next", False):
            if _looks_like_ready_to_continue(text):
                self._p331_ff_awaiting_next = False
                self.stage = LessonStage.P331_EXAMPLE_1
                viz = P331_MANDATORY_VIZ.get(LessonStage.P331_EXAMPLE_1)
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 4 种开口方向全部探究完成。接下来做 2 道例题巩固。\n\n" + P331_EXAMPLE_1_INTRO,
                    canvas_action=viz,
                )
            return LessonStep(
                stage=self.stage.value,
                message="4 种开口方向都探究完啦 🎉 回个『好』/『继续』我们做例 1。",
            )

        # 初始化逐方向状态
        if not hasattr(self, "_p331_ff_idx"):
            self._p331_ff_idx = 0
            self._p331_ff_done = {d: set() for d in _P331_FORM_ORDER}

        cur_dir = _P331_FORM_ORDER[self._p331_ff_idx]
        spec = _P331_FORM_SPEC[cur_dir]
        done = self._p331_ff_done[cur_dir]

        # 当前方向：检测 方程 / 焦点 / 准线（确定性结构匹配，跨轮累积）
        if _p331_form_item_hit(text, spec["eq_patterns"]):
            done.add("eq")
        if _p331_form_item_hit(text, spec["focus_patterns"]):
            done.add("focus")
        if _p331_form_item_hit(text, spec["dir_patterns"]):
            done.add("directrix")

        # 当前方向三项齐 → 下一方向 / 全部完成
        if {"eq", "focus", "directrix"}.issubset(done):
            self._p331_clear_stuck(f"ff_{cur_dir}")
            if self._p331_ff_idx + 1 < len(_P331_FORM_ORDER):
                self._p331_ff_idx += 1
                nxt = _P331_FORM_ORDER[self._p331_ff_idx]
                return LessonStep(
                    stage=self.stage.value,
                    message=f"🎉 **{spec['label']}** 全对了！进入下一种 👇\n\n" + _p331_form_prompt(nxt),
                    canvas_action={"action": f"show_p331_form_{nxt}"},
                )
            else:
                self._p331_ff_awaiting_next = True
                return LessonStep(
                    stage=self.stage.value,
                    message="🎉 **开口向下** 也对了！4 种开口方向全部探究完毕。\n\n"
                            "回个『好』/『继续』我们做例题。",
                    canvas_action={"action": "show_p331_four_forms_solved"},
                )

        # 部分命中 / 卡住 → 角色 3 苏格拉底提示（罐头兜底），按方向 + 缺项给递进引导
        item_names = {"eq": "标准方程", "focus": "焦点坐标", "directrix": "准线方程"}
        missing = [item_names[k] for k in ("eq", "focus", "directrix") if k not in done]
        got = [item_names[k] for k in ("eq", "focus", "directrix") if k in done]
        head = ("✅ " + "、".join(got) + " 收到。\n\n") if got else ""
        sub = (f"学生在探究**{spec['label']}**的抛物线（由 {spec['from']} {spec['transform']} 得到）。"
               f"已答对：{('、'.join(got)) if got else '无'}；还差：{', '.join(missing)}。"
               f"标准答案（仅供你判断，**不要直接报给学生**）：方程 {spec['eq_show']}、"
               f"焦点 {spec['focus_show']}、准线 {spec['dir_show']}。"
               f"用对称变换『{spec['transform']}』引导学生自己写出还差的项，都用 p 表示。")
        fb = (f"{head}**{spec['label']}** 还差：**{', '.join(missing)}**。"
              f"（提示：由 {spec['from']} {spec['transform']}，都用 $p$ 表示）")
        return LessonStep(stage=self.stage.value,
                          message=self._p331_socratic(text, f"ff_{cur_dir}", sub, fb))


    def _handle_p331_example_1(self, text: str) -> LessonStep:
        return self._handle_p331_example_generic(text, 1)


    def _handle_p331_example_2(self, text: str) -> LessonStep:
        return self._handle_p331_example_generic(text, 2)


    def _handle_p331_summary(self, text: str) -> LessonStep:
        """12. 总结。deterministic 结课。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            return LessonStep(
                stage=self.stage.value,
                message=(
                    "👏 恭喜完成 3.3.1 课程！\n\n"
                    "下一节 **3.3.2 抛物线的简单几何性质** 我们会研究范围、对称性、顶点、焦准距等性质。\n\n"
                    "[LESSON_END]"
                ),
            )
        # 未结课 → 确定性提示（不走角色 4 自由 ack）
        return LessonStep(
            stage=self.stage.value,
            message="还有什么问题想问？或者输入「结束」结课。",
        )

    # ================================================================
    # 抛物线 3.3.2 几何性质（P332）handler
    # 架构：性质短答 = 确定性关键词推进 + 角色1 enum 兜底 + 角色3 苏格拉底阶梯反馈；
    #       例题/思考 = 角色2 路径2 协议 + sympy 三层防御 + partial 累积 + awaiting_next。
    # ================================================================

    # ---- 角色 3：短答阶段苏格拉底递进提示（只给提示，不改状态）----

