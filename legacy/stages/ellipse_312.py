"""椭圆 3.1.2 椭圆的简单几何性质 —— stage handlers + 静态数据"""
import re
from legacy.lesson_flow import (
    LessonStage,
    LessonStep,
    _looks_like_ready_to_continue,
    _looks_like_understood,
    _looks_like_lesson_end,
    _ma_d1_advance_enabled,
)

# ---- 静态文本 ----

E312_INTRO_MSG = (
    "欢迎来到 3.1.2 节 **椭圆的简单几何性质** 🌿\n\n"
    "上节课（3.1.1）我们由「**椭圆的定义**」推出了**标准方程** "
    "$\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1\\,(a>b>0)$。\n\n"
    "今天我们要做相反的事 ——\n"
    "**从已有的方程出发，反过来研究椭圆的几何性质**。\n\n"
    "先回顾一下：你还记得 $a$、$b$、$c$ 分别表示椭圆图形上的**哪条线段**吗？"
)

# ── E312_RANGE 消息 ──
E312_RANGE_PREDICT_MSG = (
    "好的！我们正式开始研究椭圆的几何性质。\n\n"
    "**第一个问题：范围**\n"
    "椭圆是一条**封闭曲线**，它上面的点不可能跑得太远。\n"
    "看着方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$，"
    "你**猜想** $x$ 和 $y$ 各自的取值范围是什么？"
)
E312_RANGE_DERIVE_MSG = (
    "猜得不错！我们来**用代数方法严格证明**。\n\n"
    "因为 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$，而 $\\dfrac{y^2}{b^2}\\ge 0$，\n"
    "所以 $\\dfrac{x^2}{a^2}\\le 1$。**这个不等式告诉你 $x$ 的范围是？**"
)
E312_RANGE_DONE_MSG = (
    "完全正确 ✅：$-a\\le x\\le a$，$-b\\le y\\le b$。\n"
    "**几何意义**：椭圆完全被矩形 $[-a,a]\\times[-b,b]$ 框住。"
)

# ── E312_SYMMETRY 消息 ──
E312_SYMMETRY_Y_MSG = (
    "👀 **接下来研究对称性**。\n\n"
    "把方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$ 中的 $x$ 换成 $-x$，方程会怎样？\n"
    "进一步：这说明椭圆关于**哪条轴**对称？"
)
E312_SYMMETRY_X_MSG = (
    "对，**关于 y 轴对称** ✅。\n\n"
    "类似地，把 $y$ 换成 $-y$，方程也不变 —— 这说明椭圆关于**哪条轴**对称？"
)
E312_SYMMETRY_O_MSG = (
    "**关于 x 轴对称** ✅。\n\n"
    "既然关于两条坐标轴都对称，把 $x$ 和 $y$ **同时**都换成相反数呢？\n"
    "这又说明椭圆关于**什么**对称？"
)
E312_SYMMETRY_DONE_MSG = (
    "完美 ✅：椭圆关于 **x 轴、y 轴、原点** 三重对称。\n"
    "数学上把 x 轴、y 轴叫**对称轴**，原点叫**对称中心**。"
)

# ── E312_VERTICES 消息 ──
E312_VERTICES_COMPUTE_MSG = (
    "🔍 **顶点探究**\n\n"
    "现在我们要找出椭圆上几个**特殊的点**。\n"
    "看方程 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$：\n"
    "  · 令 $y=0$，得 $x=?$\n"
    "  · 令 $x=0$，得 $y=?$\n\n"
    "**右侧画布上有 8 个点**，请你点击你认为是「顶点」的点（**只点 4 个**）。"
)
E312_VERTICES_NAME_MSG = (
    "👏 全选对了！这四个点就是椭圆的 **顶点**。\n\n"
    "教材把它们规范命名为：\n"
    "  · 长轴上的两个顶点：$A_1(-a,0)$、$A_2(a,0)$\n"
    "  · 短轴上的两个顶点：$B_1(0,-b)$、$B_2(0,b)$\n\n"
    "**线段 $A_1A_2$ 叫长轴，长度 $|A_1A_2|=2a$；**\n"
    "**线段 $B_1B_2$ 叫短轴，长度 $|B_1B_2|=2b$**。\n\n"
    "记下这两个术语：**长轴 = 2a**，**短轴 = 2b**。下面我们进入今天的重点——**离心率**。"
)

# ── E312_ECCENTRICITY 消息 ──
E312_ECC_EXPLORE_C_MSG = (
    "⭐ **重点：离心率**\n\n"
    "我们已经知道椭圆有 $a$、$b$、$c$ 三个量。它们和椭圆的「**圆扁程度**」有什么关系？\n\n"
    "**第一组实验**（看右边沙盒）：固定 $a$ 不变，**改变 $c$**（焦距）。\n"
    "拖动滑块，观察椭圆变化。**$c$ 越大，椭圆变扁还是变圆**？"
)
E312_ECC_EXPLORE_A_MSG = (
    "很好 ✅ —— $c$ 越大椭圆**越扁**。\n\n"
    "**第二组实验**：现在反过来，固定 $c$ 不变，**改变 $a$**（长半轴）。\n"
    "**$a$ 越大，椭圆变扁还是变圆**？"
)
E312_ECC_INDUCE_MSG = (
    "✅ 你发现了：$a$ 越大椭圆**越圆**。\n\n"
    "也就是说：单看 $a$ 或单看 $c$ 都判断不了椭圆的圆扁——\n"
    "**它们要一起看**。你能想出一个**最简单的量**来同时反映 $a$ 和 $c$ 吗？\n"
    "（提示：和、差、积、商，哪一种最能反映「两者一起变化」的程度？）"
)
E312_ECC_DEFINE_MSG = (
    "完全正确 ✅ —— **比值** 才能同时反映 $a$ 和 $c$。\n\n"
    "**定义**：把比值 $\\dfrac{c}{a}$ 叫做椭圆的**离心率**，记作 $e$。\n"
    "$$e = \\dfrac{c}{a}$$\n"
    "记住这个定义。**回个「好」或「明白」**，我们就看 $e$ 是怎么反映椭圆形状的 👇"
)
E312_ECC_GEOMETRY_MSG = (
    "✅ 看右边的 **e 滑块** ——\n"
    "拖动它感受 $e$ 从小到大变化时，椭圆形状如何改变。\n\n"
    "**问题**：用一句话描述 $e$ 与椭圆形状的关系？"
)
E312_ECC_RANGE_MSG = (
    "✅ 漂亮总结：**e 越接近 1 越扁，e 越接近 0 越圆**。\n\n"
    "**最后一个问题**：椭圆里 $a>c>0$，所以 $e=\\dfrac{c}{a}$ 的**取值范围**是？\n"
    "更进一步想想：如果 **$a=b$** 时，由 $b^2=a^2-c^2$ 可知 $c=?$，那么 $e=?$\n"
    "此时椭圆会变成什么图形？"
)
E312_ECC_DONE_MSG = (
    "✅✅✅ 太棒了：**$0<e<1$**，且 $e=0$ 时椭圆变成圆 ——\n"
    "**圆是椭圆在 $e\\to 0$ 时的极限**。\n\n"
    "至此，椭圆 5 大几何性质（范围、对称性、顶点、长短轴、离心率）已全部学完。"
    "下面我们做 3 道经典例题来巩固。"
)

# ── E312_EXAMPLE 消息 ──
E312_EXAMPLE_1_INTRO = (
    "🟡 **例 1**（教材 p112）\n"
    "求椭圆 $16x^2+25y^2=400$ 的**长轴长、短轴长、离心率、焦点坐标、顶点坐标**。\n\n"
    "我们一项一项来。**先求长轴长 $2a$**：你能从方程读出 $a$，进而得到 $2a$ 吗？"
)
E312_EXAMPLE_2_INTRO = (
    "🟡 **例 2**（教材 p113 例 6）\n"
    "动点 $M(x,y)$ 与定点 $F(4,0)$ 的距离 和 $M$ 到定直线 $l:x=\\dfrac{25}{4}$ 的距离的比是常数 "
    "$\\dfrac{4}{5}$，求动点 $M$ 的轨迹。\n\n"
    "**第一步**：用集合或式子写出 $M$ 满足的**距离关系**。"
)
E312_EXAMPLE_3_INTRO = (
    "🟡 **例 3**（教材 p114 例 7）\n"
    "已知直线 $l:4x-5y+m=0$ 和椭圆 $C:\\dfrac{x^2}{25}+\\dfrac{y^2}{9}=1$。$m$ 为何值时:\n"
    "  (1) 直线与椭圆有 **两个公共点**？\n"
    "  (2) 有且**仅有 1 个公共点**？\n"
    "  (3) **没有公共点**？\n\n"
    "**先回答 (1)**：$m$ 在什么范围时，直线与椭圆有两个公共点？"
)
E312_SUMMARY_MSG = (
    "🎓 **3.1.2 总结**\n\n"
    "我们今天系统研究了椭圆的几何性质：\n"
    "  1. **范围**：$-a\\le x\\le a$，$-b\\le y\\le b$\n"
    "  2. **对称性**：关于 x 轴、y 轴、原点对称\n"
    "  3. **顶点**：4 个 $A_1A_2B_1B_2$；**长轴 $=2a$**、**短轴 $=2b$**\n"
    "  4. **离心率** $e=\\dfrac{c}{a}\\in(0,1)$：$e$ 越接近 1 越扁，越接近 0 越圆，$e=0$ 即圆\n"
    "  5. 三道例题：化方程定形状、用比例反推椭圆、直线与椭圆的位置关系\n\n"
    "**下一节（3.2.1）**：把「两点距离之和为常数」改成「两点距离之差为常数」——双曲线 🌀。"
)


# ---- Skip function ----

def _looks_like_skip_to_example_312(text: str):
    """v3.35: 识别学生「直接跳到例 N」意图。
    返回 1/2/3（对应 E312_EXAMPLE_1/2/3）或 None。"""
    t = text.replace(" ", "")
    has_skip_intent = any(kw in t for kw in ["直接", "跳到", "跳过", "看例", "进入例", "看第", "进入第"])
    if not has_skip_intent:
        return None
    if "例1" in t or "例一" in t or "第一题" in t or "第1题" in t:
        return 1
    if "例2" in t or "例二" in t or "第二题" in t or "第2题" in t:
        return 2
    if "例3" in t or "例三" in t or "第三题" in t or "第3题" in t:
        return 3
    return None


# ---- E312-specific keyword helpers ----

# INTRO 阶段：学生回忆 a/b/c 含义
_E312_ABC_KEYWORDS_A = ["长半轴", "长轴的一半", "半长轴", "长轴", "a 是", "a=", "a 表示"]
_E312_ABC_KEYWORDS_B = ["短半轴", "短轴的一半", "半短轴", "短轴", "b 是", "b=", "b 表示"]
_E312_ABC_KEYWORDS_C = ["焦距的一半", "半焦距", "焦距", "c 是", "c=", "c 表示", "焦点"]

def _looks_like_abc_recall_312(text: str) -> bool:
    """学生回忆出 a/b/c 几何含义（命中 ≥2 个量）"""
    low = text.lower()
    hits = 0
    if any(kw.lower() in low for kw in _E312_ABC_KEYWORDS_A):
        hits += 1
    if any(kw.lower() in low for kw in _E312_ABC_KEYWORDS_B):
        hits += 1
    if any(kw.lower() in low for kw in _E312_ABC_KEYWORDS_C):
        hits += 1
    return hits >= 2

# RANGE 阶段：识别学生答出 -a≤x≤a 这种范围
_RANGE_X_PATTERNS = [
    "-a≤x≤a", "-a<=x<=a", "−a≤x≤a", "|x|≤a", "|x|<=a", "x∈[-a,a]",
]
_RANGE_Y_PATTERNS = [
    "-b≤y≤b", "-b<=y<=b", "−b≤y≤b", "|y|≤b", "|y|<=b", "y∈[-b,b]",
]

def _looks_like_range_x_correct(text: str) -> bool:
    """学生答出 -a ≤ x ≤ a 形式（容忍空格、不等号符号变体）"""
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    for pat in _RANGE_X_PATTERNS:
        p = pat.replace(" ", "").replace("−", "-").replace("≤", "<=")
        if p in t:
            return True
    return False

def _looks_like_range_y_correct(text: str) -> bool:
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    for pat in _RANGE_Y_PATTERNS:
        p = pat.replace(" ", "").replace("−", "-").replace("≤", "<=")
        if p in t:
            return True
    return False

# SYMMETRY 阶段：识别 y 轴 / x 轴 / 原点对称
# v3.29 放宽：单字"y轴"/"x轴"/"原点"也算命中（学生简短回答常见）
def _looks_like_y_axis_symmetry(text: str) -> bool:
    t = text.lower().replace(" ", "")
    return any(kw in t for kw in ["y轴对称", "关于y轴", "y-axis", "y轴", "纵轴"])

def _looks_like_x_axis_symmetry(text: str) -> bool:
    t = text.lower().replace(" ", "")
    return any(kw in t for kw in ["x轴对称", "关于x轴", "x-axis", "x轴", "横轴"])

def _looks_like_origin_symmetry(text: str) -> bool:
    t = text.replace(" ", "")
    return any(kw in t for kw in ["原点对称", "关于原点", "中心对称", "原点", "对称中心"])

# ECCENTRICITY 阶段
# v3.32 严格化：方向必须明确（不能"含 a + 扁/圆"通吃）
# - 学生说"扁"且没说"圆" → flat
# - 学生说"圆"（非"椭圆"）且没说"扁" → round
# - 两者都说或都不说 → 返回 False，让方案 D 的 LLM 兜底判断
def _has_real_circle(t: str) -> bool:
    """文本含有"圆"且不只是"椭圆"里的'圆'"""
    return "圆" in t and t.count("圆") > t.count("椭圆")

def _looks_like_e_shape_flat(text: str) -> bool:
    """c 大 → 椭圆变扁（phase explore_c 期待答案）。
    严格：明确说"扁"且不同时说"圆"。"""
    t = text.replace(" ", "")
    has_flat = "扁" in t
    has_circle = _has_real_circle(t)
    if has_flat and not has_circle:
        return True
    # 临界情况：明确说"c 接近 a"（不含"扁/圆"但语义等价 flat）
    if not has_flat and not has_circle:
        if "接近a" in t or "c接近a" in t or "c→a" in t:
            return True
    return False

def _looks_like_e_shape_round(text: str) -> bool:
    """a 大 → 椭圆变圆（phase explore_a 期待答案）。
    严格：明确说"圆"（独立词，非"椭圆"里的'圆'）且不同时说"扁"。"""
    t = text.replace(" ", "")
    has_circle = _has_real_circle(t)
    has_flat = "扁" in t
    if has_circle and not has_flat:
        return True
    return False

def _looks_like_ratio_insight(text: str) -> bool:
    """诱导比值 phase：学生答出 比值 / 比 / c/a / 比例 等关键词"""
    t = text.lower().replace(" ", "")
    if any(kw in t for kw in ["比值", "c/a", "c比a", "ratio", "比例", "c÷a"]):
        return True
    # 放宽：同时提到 c 和 a 即算（学生说"看 c 和 a 的关系"也算）
    if "c" in t and "a" in t and ("比" in t or "/" in t or "÷" in t or "除" in t):
        return True
    return False

def _looks_like_e_define(text: str) -> bool:
    """define phase：学生写出 e = c/a"""
    t = text.lower().replace(" ", "")
    # 严格：e = c/a
    if "e=" in t and (("c/a" in t) or ("c÷a" in t)):
        return True
    # 放宽：含 e 和 c/a 形式（学生写"离心率 = c/a"也算）
    if "c/a" in t and ("e" in t or "离心率" in text):
        return True
    # 含 e、c、a 三符号 + 任一关系符
    if "e" in t and "c" in t and "a" in t and ("/" in t or "÷" in t or "比" in t or "除" in t):
        return True
    return False

def _looks_like_e_shape_relation(text: str) -> bool:
    """geometry phase：学生说 e 越接近 1 越扁、越接近 0 越圆"""
    has_flat = "扁" in text
    has_round = "圆" in text
    if not (has_flat or has_round):
        return False
    # 严格：含"接近 1 / 接近 0 / e 大 / e 小"
    has_near_1 = ("接近1" in text.replace(" ", "")) or ("e大" in text.replace(" ", ""))
    has_near_0 = ("接近0" in text.replace(" ", "")) or ("e小" in text.replace(" ", ""))
    if has_near_1 or has_near_0:
        return True
    # 放宽：只要提到 e 同时含"扁/圆"也算（学生写"e 越大越扁"也认）
    if "e" in text.lower() and (has_flat or has_round):
        return True
    return False

def _looks_like_e_range_0_1(text: str) -> bool:
    """range phase part 1：学生写出 0<e<1"""
    t = text.replace(" ", "").replace("−", "-").replace("≤", "<=")
    if "0<e<1" in t or "0<=e<=1" in t or "(0,1)" in t:
        return True
    # 放宽：含"0"和"1"和"e"和"<"
    if "0" in t and "1" in t and "e" in t.lower() and ("<" in t or "之间" in text):
        return True
    return False

def _looks_like_e_zero_circle(text: str) -> bool:
    """range phase part 2：学生答 a=b 时 e=0，椭圆变圆"""
    t = text.replace(" ", "")
    has_e0 = ("e=0" in t) or ("e为0" in t) or ("e等于0" in t) or ("e→0" in t) or ("e接近0" in t)
    has_circle = "圆" in t and "椭圆" not in t.replace("椭圆", "")
    # 也要排除 "椭圆" 的"圆"误判
    if "圆" in t:
        # 单独含独立的"圆"，且 t 不是只含"椭圆"这一个词
        only_ellipse_kw = (t.count("圆") == t.count("椭圆"))
        has_circle = not only_ellipse_kw
    return has_e0 or has_circle


# ---- Stage Goals ----

E312_STAGE_GOALS = {
    LessonStage.E312_INTRO: (
        "📒 3.1.2 开场。让学生回忆 $a$、$b$、$c$ 几何含义（a=长半轴、b=短半轴、c=半焦距）。\n"
        "学生答出 ≥2 个对应关系即推进到 RANGE。\n\n"
        "可用动画：`show_e312_recall`（沙盒，标准椭圆+焦点+abc 三角形）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_RANGE: (
        "📒 范围探究阶段。两 phase：predict（猜测 x、y 范围）→ derive（从 x²/a²≤1 严格推出）。\n"
        "学生答出 -a≤x≤a 与 -b≤y≤b 即推进到 SYMMETRY。\n\n"
        "可用动画：`show_e312_range_setup`（沙盒，椭圆 + x²/a² 项标注）、`show_e312_range_solved`（含 ±a/±b 虚线）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_SYMMETRY: (
        "📒 对称性探究阶段。三 phase 递进：y 轴 → x 轴 → 原点。每 phase 检测对应关键词推进。\n"
        "全部三种对称都答出后推进到 VERTICES。\n\n"
        "可用动画：`show_e312_symmetry_setup`（沙盒，椭圆 + 可拖点）、`show_e312_symmetry_solved`（蝴蝶 4 点伙伴）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_VERTICES: (
        "📒 顶点探究阶段。两 phase：compute（学生在沙盒点击 4 个顶点）→ name（介绍 A₁A₂B₁B₂ 长短轴术语）。\n"
        "compute 完成由前端 e312_vertex_clicked 事件累积命中后推进；name 后推进到 ECCENTRICITY。\n\n"
        "可用动画：`show_e312_vertices_setup`（沙盒，8 候选点）、`show_e312_vertices_solved`（4 顶点+轴）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_ECCENTRICITY: (
        "⭐ 离心率阶段（本课重点）：6 个 phase 苏格拉底诱导。\n"
        "_build_system_prompt 会按 phase 替换为 _E312_ECC_PHASE_GOALS 里的细分目标。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_EXAMPLE_1: (
        "🟡 例 1（教材 p112，16x²+25y²=400）。5 phase 苏格拉底逐项问：长轴→短轴→e→焦点→顶点。\n"
        "诊断器对答案严谨判等（焦点/顶点必须带坐标）。phase_goal 由 example_canonicals_312.EXAMPLE_4_PHASE_GOAL 控制。\n\n"
        "可用动画：`show_e312_example_1_setup`（沙盒，空椭圆+方程）、`show_e312_example_1_solved`（含 a/b/c/顶点全标注）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_EXAMPLE_2: (
        "🟡 例 2（教材 p113 例 6，|MF|/d=4/5）。3 phase：写出距离比关系 → 化简得方程 → 结论椭圆 长 10 短 6。\n"
        "完成后发 explore 动画让学生拖 M 点感受比值恒为 4/5。\n"
        "**题目原文（铁律：不得修改任何数值）**：动点 M(x,y) 与定点 F(4,0) 的距离 和 M 到定直线 l: x=25/4 的距离的比是常数 4/5，求动点 M 的轨迹。\n\n"
        "可用动画：`show_e312_example_2_setup`、`show_e312_example_2_solved`、`show_e312_example_2_explore`（拖 M）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_EXAMPLE_3: (
        "🟡 例 3（教材 p114 例 7，直线椭圆位置）。3 phase 直接对应教材 (1)(2)(3) 三问。\n"
        "判别式过程交 LLM 引导，只判 m 范围答案（多写法宽松判等）。完成后发 explore 动画让学生拖 m 滑块观察交点数。\n"
        "**题目原文（铁律：不得修改）**：直线 l: 4x-5y+m=0 与椭圆 C: x²/25+y²/9=1，求 m 何值时直线与椭圆有 2/1/0 个公共点。\n\n"
        "可用动画：`show_e312_example_3_setup`、`show_e312_example_3_solved`、`show_e312_example_3_explore`（m 滑块+交点计数）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
    LessonStage.E312_SUMMARY: (
        "📒 3.1.2 总结阶段。回顾 5 大几何性质 + 3 道例题。学生说「没问题」/「结束」时附加 [LESSON_END] 标记。\n"
        "可用动画：`show_e312_summary`（含 5 性质标注）。\n\n"
        "**关于可视化**：不要主动输出 [VIZ:...] 标记（关键阶段系统已自带确定性动画）。"
        "学生明确要求看动画时温和回应「好的，我们来看一个动画」，由系统自动配图。"
        "**严禁承诺画不出的图**：本章可用动画清单见各 phase。\n\n"
        "**【例题铁律 · 不得违反】**\n"
        "1. **严禁自己编造例题题目**：所有例题必须严格按教材原题，题目内容由系统的 deterministic 文案给出。\n"
        "2. **严禁修改例题数值**：不得把教材的 F(4,0) 换成 F(√3,0)，不得把 |MF|/d=4/5 换成「过点 P」等任何变形。\n"
        "3. **严禁宣告进入下一例题**：当前例题是否做完、是否进入下一题、下一题题目什么——**全部由系统决定**，你不要主动说「接下来我们看例 N+1」或编写下一题内容。\n"
        "4. **你的角色**：ack 学生当前答案的对错、给出引导提示、解释教材原理。**不要充当出题人**。\n"
        "5. 学生说「继续」/「下一题」等推进意图时，你只需简短 ack（如「好的」），由系统切到下一题并发出 deterministic 题目文案。"
    ),
}


# ---- Course Config ----

E312_COURSE_CONFIG = {
    "ellipse_312": {
        "name_cn": "3.1.2 椭圆的简单几何性质",
        "scope": "ellipse",
        "first_stage": LessonStage.E312_INTRO,
        "start_stage": LessonStage.E312_RANGE,  # 学生回顾完 abc 即推进到 RANGE
        "kg_nodes_basic": [
            "ellipse_definition", "ellipse_parameter_triangle",
        ],
        "kg_nodes_equation": [
            "ellipse_standard_equation_x", "ellipse_range",
            "ellipse_symmetry", "ellipse_vertices",
        ],
        "kg_nodes_eccentricity": [
            "ellipse_eccentricity", "concept_eccentricity_unified",
        ],
        "kg_nodes_examples": {
            LessonStage.E312_EXAMPLE_1: ["ellipse_312_example_1"],
            LessonStage.E312_EXAMPLE_2: ["ellipse_312_example_2"],
            LessonStage.E312_EXAMPLE_3: ["ellipse_312_example_3"],
        },
        "eccentricity_stages": {LessonStage.E312_ECCENTRICITY, LessonStage.E312_SUMMARY},
        "summary_kg_nodes": [
            "ellipse_range", "ellipse_symmetry", "ellipse_vertices",
            "ellipse_eccentricity",
        ],
    },
}


# ---- Mandatory VIZ ----

E312_MANDATORY_VIZ = {
    # ---- 椭圆 3.1.2 课（v3.23）：9 stage，每个 stage 入口的强制 viz ----
    # INTRO: 复用 3.1.1 风格的"点线段答题"互动复习 a/b/c 三条线段（v3.24 修复 a/c 标签重合 bug）
    LessonStage.E312_INTRO: {"action": "show_e312_abc_quiz"},
    # RANGE: 进入 range 阶段先发 setup（椭圆 + x²/a² 项标注）
    LessonStage.E312_RANGE: {"action": "show_e312_range_setup"},
    # SYMMETRY: 椭圆 + 可拖点（学生答题前不显示对称伙伴）
    LessonStage.E312_SYMMETRY: {"action": "show_e312_symmetry_setup"},
    # VERTICES: 8 候选点的点击交互（学生选 4 个顶点）
    LessonStage.E312_VERTICES: {"action": "show_e312_vertices_setup"},
    # ECCENTRICITY: 第一 phase explore_c 沙盒动画
    LessonStage.E312_ECCENTRICITY: {"action": "show_e312_explore_c"},
    # 3 道例题入口：setup 版（题目方程，不剧透答案）
    LessonStage.E312_EXAMPLE_1: {"action": "show_e312_example_1_setup"},
    LessonStage.E312_EXAMPLE_2: {"action": "show_e312_example_2_setup"},
    LessonStage.E312_EXAMPLE_3: {"action": "show_e312_example_3_setup"},
}


# ---- VIZ on Request ----

E312_VIZ_ON_REQUEST = {
    LessonStage.E312_INTRO:        {"action": "show_e312_abc_quiz"},
    LessonStage.E312_RANGE:        {"action": "show_e312_range_setup"},
    LessonStage.E312_SYMMETRY:     {"action": "show_e312_symmetry_setup"},
    LessonStage.E312_VERTICES:     {"action": "show_e312_vertices_setup"},
    LessonStage.E312_ECCENTRICITY: {"action": "show_e312_explore_c"},   # 默认给 phase 1 的图
    LessonStage.E312_EXAMPLE_1:    {"action": "show_e312_example_1_setup"},
    LessonStage.E312_EXAMPLE_2:    {"action": "show_e312_example_2_setup"},
    LessonStage.E312_EXAMPLE_3:    {"action": "show_e312_example_3_setup"},
    LessonStage.E312_SUMMARY:      {"action": "show_e312_summary"},
}


# ---- Stage Dispatch Registry ----

E312_STAGE_DISPATCH = {
    LessonStage.E312_INTRO:        ("_handle_e312_intro", {}),
    LessonStage.E312_RANGE:        ("_handle_e312_range", {}),
    LessonStage.E312_SYMMETRY:     ("_handle_e312_symmetry", {}),
    LessonStage.E312_VERTICES:     ("_handle_e312_vertices", {}),
    LessonStage.E312_ECCENTRICITY: ("_handle_e312_eccentricity", {}),
    LessonStage.E312_EXAMPLE_1:    ("_handle_e312_example", {"example_num": 4}),
    LessonStage.E312_EXAMPLE_2:    ("_handle_e312_example", {"example_num": 5}),
    LessonStage.E312_EXAMPLE_3:    ("_handle_e312_example", {"example_num": 6}),
    LessonStage.E312_SUMMARY:      ("_handle_e312_summary", {}),
}


class Ellipse312Mixin:
    """椭圆 3.1.2 课 stage handlers"""

    def _handle_e312_intro(self, text: str) -> LessonStep:
        """📒 3.1.2 开场：学生回忆 a/b/c 几何含义，命中 ≥2 个 → 推进到 RANGE。

        v3.35 增加跳级支持：学生说「直接进入例 N」时直接切到 E312_EXAMPLE_N stage。
        """
        # 跳级到例题（deterministic 路径，避免 LLM 自编 3.1.1 的例题）
        skip_n = _looks_like_skip_to_example_312(text)
        if skip_n is not None:
            target_stage, target_intro = {
                1: (LessonStage.E312_EXAMPLE_1, E312_EXAMPLE_1_INTRO),
                2: (LessonStage.E312_EXAMPLE_2, E312_EXAMPLE_2_INTRO),
                3: (LessonStage.E312_EXAMPLE_3, E312_EXAMPLE_3_INTRO),
            }[skip_n]
            self.stage = target_stage
            viz = E312_MANDATORY_VIZ.get(target_stage)
            return LessonStep(
                stage=self.stage.value,
                message=(f"好的，我们直接看例 {skip_n}（教材 3.1.2 节原题；"
                         f"跳过了几何性质探究，例题做完后可回到课程开头补 📒）：\n\n" + target_intro),
                canvas_action=viz,
            )
        # 正常路径：识别 abc_recall → 推 RANGE
        if _looks_like_abc_recall_312(text):
            self.stage = LessonStage.E312_RANGE
            self._maybe_enter_feynman_at_transition("e312_intro")  # 多 agent 钩子
            viz = E312_MANDATORY_VIZ.get(LessonStage.E312_RANGE)
            ack = self._llm_respond(text, fallback="✅ 回忆得很好。")
            full = ack + "\n\n" + E312_RANGE_PREDICT_MSG
            self._e312_range_phase = "predict"
            return self._decorate_step_with_peer(
                LessonStep(stage=self.stage.value, message=full, canvas_action=viz)
            )
        reply = self._llm_respond(
            text,
            fallback="提示：在椭圆图中，$a$ 是长半轴长（从中心到长轴端点），"
                     "$b$ 是短半轴长（从中心到短轴端点），$c$ 是半焦距（从中心到焦点）。"
                     "你能再说一遍它们各代表哪条线段吗？",
        )
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e312_range(self, text: str) -> LessonStep:
        """📒 范围：2 phase（predict → derive）+ v3.28 加 awaiting_next 过渡确认。"""
        if not hasattr(self, "_e312_range_phase"):
            self._e312_range_phase = "predict"
        if not hasattr(self, "_e312_range_x_done"):
            self._e312_range_x_done = False
            self._e312_range_y_done = False

        # v3.28: 已发 solved，等学生确认进入 SYMMETRY
        if getattr(self, "_e312_range_awaiting_next", False):
            hit, src = self._resolve_phase_answer(
                text, "awaiting_next",
                lambda t: "ready" if _looks_like_ready_to_continue(t) else None,
            )
            if hit == "ready":
                self._e312_range_awaiting_next = False
                self.stage = LessonStage.E312_SYMMETRY
                self._maybe_enter_feynman_at_transition("e312_range")  # 多 agent 钩子
                return self._decorate_step_with_peer(LessonStep(
                    stage=self.stage.value,
                    message=E312_SYMMETRY_Y_MSG,
                    canvas_action=E312_MANDATORY_VIZ.get(LessonStage.E312_SYMMETRY),
                ))
            if hit == "not_ready":
                return LessonStep(stage=self.stage.value,
                                  message="慢慢来。还有什么不清楚的可以问我，或者再看看右边的图。准备好了再说「好」就行。")
            reply = self._llm_respond(text, fallback="先看看右边的图——回个「好」/「准备好了」我们就开始下一节 🌿。")
            return LessonStep(stage=self.stage.value, message=reply)

        # phase 1: predict —— 学生发任何文字都自然过渡到 derive
        if self._e312_range_phase == "predict":
            self._e312_range_phase = "derive"
            ack = self._llm_respond(text, fallback="✅ 收到你的猜想。")
            return LessonStep(stage=self.stage.value,
                              message=ack + "\n\n" + E312_RANGE_DERIVE_MSG)
        # phase 2: derive —— v3.31 方案 D
        def _range_kw(t):
            x_ok = _looks_like_range_x_correct(t)
            y_ok = _looks_like_range_y_correct(t)
            if x_ok and y_ok: return "both"
            if x_ok: return "x_only"
            if y_ok: return "y_only"
            return None
        hit, src = self._resolve_phase_answer(text, "range_derive", _range_kw)
        if hit == "both":
            self._e312_range_x_done = True
            self._e312_range_y_done = True
        elif hit == "x_only":
            self._e312_range_x_done = True
        elif hit == "y_only":
            self._e312_range_y_done = True
        if self._e312_range_x_done and self._e312_range_y_done:
            self._e312_range_awaiting_next = True
            return LessonStep(
                stage=self.stage.value,
                message=E312_RANGE_DONE_MSG + "\n\n👀 接下来我们来**研究对称性**，准备好了吗？",
                canvas_action={"action": "show_e312_range_solved"},
            )
        # ── TA 自审（C/D 档）：在"追问另一边"之前先查变量错位 ──
        # 2026-05-28 修：之前 TA 自审在追问 if 之后，hit=None 但 x_done 已 True 时永远不可达。
        # 现在 hit=None（既不是 x_only 也不是 y_only）→ 先让 TA 看是不是结构错（如 -b≤x≤b）
        if hit is None:
            if self._e312_range_x_done and not self._e312_range_y_done:
                _expected = "当前正在追问 y 的范围，期望答 -b≤y≤b。若学生答 -b≤x≤b、-a≤y≤a 都属变量错位结构错"
            elif self._e312_range_y_done and not self._e312_range_x_done:
                _expected = "当前正在追问 x 的范围，期望答 -a≤x≤a。若学生答 -a≤y≤a、-b≤x≤b 都属变量错位结构错"
            else:
                _expected = "-a≤x≤a 或 -b≤y≤b（求 x 用 a，求 y 用 b，不要错位）"
            _ta_msg = self._maybe_ta_review_freetext(
                text, phase_label="3.1.2 RANGE.derive 求 x 或 y 的范围",
                expected_clue=_expected,
            )
            if _ta_msg:
                self._last_agent = "ta"
                return LessonStep(stage=self.stage.value, message=_ta_msg)
        # 只答一边 → 追问另一边
        if self._e312_range_x_done and not self._e312_range_y_done:
            return LessonStep(stage=self.stage.value,
                              message="✅ $-a\\le x\\le a$ 正确！那 **$y$ 的范围**呢？同样用 $\\dfrac{y^2}{b^2}\\le 1$ 推一下。")
        if self._e312_range_y_done and not self._e312_range_x_done:
            return LessonStep(stage=self.stage.value,
                              message="✅ $-b\\le y\\le b$ 正确！那 **$x$ 的范围**呢？同样用 $\\dfrac{x^2}{a^2}\\le 1$ 推一下。")
        reply = self._llm_respond(text, fallback="提示：由 $\\dfrac{x^2}{a^2}\\le 1$ 两边乘 $a^2$（$a>0$），得 $x^2\\le a^2$，即 $|x|\\le a$。")
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e312_symmetry(self, text: str) -> LessonStep:
        """📒 对称性：3 phase（y_axis → x_axis → origin）+ v3.28 加 awaiting_next 过渡确认。"""
        if not hasattr(self, "_e312_sym_phase"):
            self._e312_sym_phase = "y_axis"

        # v3.28: 已发 solved，等学生确认进入 VERTICES（v3.31 方案 D）
        if getattr(self, "_e312_sym_awaiting_next", False):
            hit, src = self._resolve_phase_answer(
                text, "awaiting_next",
                lambda t: "ready" if _looks_like_ready_to_continue(t) else None,
            )
            if hit == "ready":
                self._e312_sym_awaiting_next = False
                self.stage = LessonStage.E312_VERTICES
                self._maybe_enter_feynman_at_transition("e312_symmetry")  # 多 agent 钩子
                return self._decorate_step_with_peer(LessonStep(
                    stage=self.stage.value,
                    message=E312_VERTICES_COMPUTE_MSG,
                    canvas_action=E312_MANDATORY_VIZ.get(LessonStage.E312_VERTICES),
                ))
            if hit == "not_ready":
                return LessonStep(stage=self.stage.value,
                                  message="慢慢来，左边可以问我任何关于对称性的问题。准备好了说「好」继续 📍。")
            reply = self._llm_respond(text, fallback="先看看右边图里的 3 个对称伙伴——回个「好」/「准备好了」我们就开始顶点探究 📍。")
            return LessonStep(stage=self.stage.value, message=reply)

        phase = self._e312_sym_phase
        # v3.31 方案 D：每 phase 用 _resolve_phase_answer（symbolic 优先 + LLM 兜底）
        if phase == "y_axis":
            hit, src = self._resolve_phase_answer(
                text, "sym_y_axis",
                lambda t: "y_axis" if _looks_like_y_axis_symmetry(t) else None,
            )
            if hit == "y_axis":
                self._e312_sym_phase = "x_axis"
                return LessonStep(stage=self.stage.value, message=E312_SYMMETRY_X_MSG)
            if hit in ("x_axis", "origin"):
                return LessonStep(stage=self.stage.value,
                                  message=f"嗯，{('x 轴' if hit=='x_axis' else '原点')}是对的，但当前问题是 $x \\to -x$ 让方程不变，这对应**y 轴**对称。我们按顺序来 👇")
            # TA 自审：SYMMETRY.y_axis 学生易把对称轴写错（如说"x 轴"）
            _ta_msg = self._maybe_ta_review_freetext(
                text, phase_label="3.1.2 SYMMETRY.y_axis 判断对称轴",
                expected_clue="x→-x 方程不变 → 关于 y 轴对称（不是 x 轴，不是原点）",
            )
            if _ta_msg:
                self._last_agent = "ta"
                return LessonStep(stage=self.stage.value, message=_ta_msg)
            reply = self._llm_respond(text, fallback="提示：$x$ 换成 $-x$ 时 $(-x)^2=x^2$，方程不变，说明关于 **y 轴** 对称。")
            return LessonStep(stage=self.stage.value, message=reply)

        if phase == "x_axis":
            hit, src = self._resolve_phase_answer(
                text, "sym_x_axis",
                lambda t: "x_axis" if _looks_like_x_axis_symmetry(t) else None,
            )
            if hit == "x_axis":
                self._e312_sym_phase = "origin"
                return LessonStep(stage=self.stage.value, message=E312_SYMMETRY_O_MSG)
            if hit in ("y_axis", "origin"):
                return LessonStep(stage=self.stage.value,
                                  message=f"嗯，但当前问题是 $y \\to -y$ 方程不变 → **x 轴**对称。")
            # TA 自审：SYMMETRY.x_axis 学生易答错对称轴或复用上一 phase 答案
            _ta_msg = self._maybe_ta_review_freetext(
                text, phase_label="3.1.2 SYMMETRY.x_axis 判断对称轴",
                expected_clue="y→-y 方程不变 → 关于 x 轴对称（不是 y 轴，不是原点）",
            )
            if _ta_msg:
                self._last_agent = "ta"
                return LessonStep(stage=self.stage.value, message=_ta_msg)
            reply = self._llm_respond(text, fallback="提示：$y$ 换成 $-y$ 方程不变，关于 **x 轴** 对称。")
            return LessonStep(stage=self.stage.value, message=reply)

        # phase == "origin"
        hit, src = self._resolve_phase_answer(
            text, "sym_origin",
            lambda t: "origin" if _looks_like_origin_symmetry(t) else None,
        )
        if hit == "origin":
            self._e312_sym_awaiting_next = True
            return LessonStep(
                stage=self.stage.value,
                message=E312_SYMMETRY_DONE_MSG + "\n\n👀 接下来我们来**研究顶点**，准备好了吗？",
                canvas_action={"action": "show_e312_symmetry_solved"},
            )
        if hit in ("x_axis", "y_axis"):
            return LessonStep(stage=self.stage.value,
                              message="同时换 x 和 y → 这是**原点**对称（中心对称）。再答一次？")
        reply = self._llm_respond(text, fallback="提示：$x$ 和 $y$ 同时换成相反数方程不变，关于**原点**对称。")
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e312_vertices(self, text: str) -> LessonStep:
        """📒 顶点：2 phase（compute 含点击交互 → name）。

        compute phase 的推进由 on_canvas_event 处理 e312_vertex_clicked 事件累积命中。
        学生只发文字不点击 → 提醒去画布。
        """
        if not hasattr(self, "_e312_vertices_phase"):
            self._e312_vertices_phase = "compute"
            self._e312_vertices_correct_hits = set()
        phase = self._e312_vertices_phase
        if phase == "compute":
            reply = self._llm_respond(
                text,
                fallback="提示：先去**右边沙盒**点击 4 个你认为是顶点的点 —— 顶点是椭圆与坐标轴的交点。",
            )
            return LessonStep(stage=self.stage.value, message=reply)
        # phase == "name"（v3.31 方案 D）
        hit, src = self._resolve_phase_answer(
            text, "vertices_name",
            lambda t: "ready" if (_looks_like_understood(t) or "明白" in t or "继续" in t) else None,
        )
        if hit == "ready":
            self.stage = LessonStage.E312_ECCENTRICITY
            self._maybe_enter_feynman_at_transition("e312_vertices")  # 多 agent 钩子
            viz = E312_MANDATORY_VIZ.get(LessonStage.E312_ECCENTRICITY)
            self._e312_ecc_phase = "explore_c"
            return self._decorate_step_with_peer(LessonStep(
                stage=self.stage.value,
                message=E312_ECC_EXPLORE_C_MSG,
                canvas_action=viz,
            ))
        if hit == "not_ready":
            return LessonStep(stage=self.stage.value,
                              message="哪个术语不清楚？长轴 / 短轴 / 顶点 A₁A₂B₁B₂ / 对称中心？告诉我后我再讲一下。")
        reply = self._llm_respond(text, fallback="如果术语都清楚了，回个「明白」我们继续到下一节——**离心率**（本课重点）。")
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e312_eccentricity(self, text: str) -> LessonStep:
        """⭐ 离心率：6 phase（explore_c → explore_a → induce_ratio → define → geometry → range）。

        v3.29-2: 加跳级推进 —— 学生在前面 phase 直接答出后面 phase 的核心内容，
        系统快速带过中间 phase 直接进入对应 phase。避免 LLM 自由发挥 + phase 卡死。
        """
        if not hasattr(self, "_e312_ecc_phase"):
            self._e312_ecc_phase = "explore_c"
        if not hasattr(self, "_e312_ecc_range_part1"):
            self._e312_ecc_range_part1 = False
        phase = self._e312_ecc_phase

        # ── v3.29-2 跳级推进检测 ──
        # 学生在 phase 1/2/3/4 时若答出 geometry phase 内容（含 e + 扁/圆 组合）→ 跳到 geometry
        if phase in ("explore_c", "explore_a", "induce_ratio", "define"):
            if _looks_like_e_shape_relation(text):
                self._e312_ecc_phase = "geometry"
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 你已经把后面的几何意义说出来了——我们直接看综合实验：\n\n" + E312_ECC_GEOMETRY_MSG,
                    canvas_action={"action": "show_e312_eslider"},
                )
        # 学生在 phase 1/2/3 时若直接写出 e=c/a → 跳到 geometry（跳过 define 这步骤）
        if phase in ("explore_c", "explore_a", "induce_ratio"):
            if _looks_like_e_define(text):
                self._e312_ecc_phase = "geometry"
                return LessonStep(
                    stage=self.stage.value,
                    message="✅ 你已经写出 $e=\\dfrac{c}{a}$ 了——我们看一下它的几何意义：\n\n" + E312_ECC_GEOMETRY_MSG,
                    canvas_action={"action": "show_e312_eslider"},
                )

        # v3.30 方案 D：所有 phase 用 _resolve_phase_answer（关键词优先，LLM 兜底分类）

        if phase == "explore_c":
            hit, src = self._resolve_phase_answer(
                text, "ecc_explore_c",
                lambda t: "c_big_flat" if _looks_like_e_shape_flat(t) else None,
            )
            if hit == "c_big_flat":
                self._e312_ecc_phase = "explore_a"
                return LessonStep(stage=self.stage.value,
                                  message=E312_ECC_EXPLORE_A_MSG,
                                  canvas_action={"action": "show_e312_explore_a"})
            if hit == "c_big_round":
                return LessonStep(stage=self.stage.value,
                                  message="方向反了——$c$ 越大焦距越大，椭圆会被拉得更扁。再看一下沙盒：$c=0.1$ 时椭圆接近圆，$c$ 接近 $a$ 时椭圆压扁。再答一次：$c$ 越大椭圆变扁还是变圆？")
            reply = self._llm_respond(text, fallback="拖动 $c$ 滑块（$a$ 固定），观察椭圆变化。$c$ 越大椭圆变扁还是变圆？")
            return LessonStep(stage=self.stage.value, message=reply)

        if phase == "explore_a":
            hit, src = self._resolve_phase_answer(
                text, "ecc_explore_a",
                lambda t: "a_big_round" if _looks_like_e_shape_round(t) else None,
            )
            if hit == "a_big_round":
                self._e312_ecc_phase = "induce_ratio"
                return LessonStep(stage=self.stage.value, message=E312_ECC_INDUCE_MSG)
            if hit == "a_big_flat":
                return LessonStep(stage=self.stage.value,
                                  message="方向反了——$a$ 越大长轴越长，相比固定的 $c$，焦距占比变小，椭圆更接近圆。再答：$a$ 越大椭圆变扁还是变圆？")
            reply = self._llm_respond(text, fallback="拖动 $a$ 滑块（$c$ 固定），观察椭圆变化。$a$ 越大椭圆变扁还是变圆？")
            return LessonStep(stage=self.stage.value, message=reply)

        if phase == "induce_ratio":
            hit, src = self._resolve_phase_answer(
                text, "ecc_induce_ratio",
                lambda t: "ratio_c_a" if _looks_like_ratio_insight(t) else None,
            )
            if hit == "ratio_c_a":
                self._e312_ecc_phase = "define"
                return LessonStep(stage=self.stage.value, message=E312_ECC_DEFINE_MSG)
            if hit in ("sum", "diff", "product"):
                return LessonStep(stage=self.stage.value,
                                  message=f"想想看，{('和' if hit=='sum' else '差' if hit=='diff' else '积')}反映不了相对大小——"
                                          f"比如 a=10,c=1 和 a=100,c=10，圆扁程度差不多但 {('和' if hit=='sum' else '差' if hit=='diff' else '积')}相差很大。"
                                          f"哪种运算反映的是**相对**大小？")
            # TA 自审：ECC.induce_ratio 学生易选"差/和/积"而不是"商/比值"
            _ta_msg = self._maybe_ta_review_freetext(
                text, phase_label="3.1.2 ECC.induce_ratio 选择反映 a 和 c 的运算",
                expected_clue="比值（除法/商，c/a 形式）才能反映椭圆形状，不是差/和/积",
            )
            if _ta_msg:
                self._last_agent = "ta"
                return LessonStep(stage=self.stage.value, message=_ta_msg)
            reply = self._llm_respond(text, fallback="提示：和、差、积、商哪个最能反映两个量的相对大小？")
            return LessonStep(stage=self.stage.value, message=reply)

        if phase == "define":
            # v3.33: define 已剧透答案 e=c/a，学生只需 ack 后进 geometry
            # 但若学生主动写出 e=c/a 也直接推进（跳级逻辑已覆盖）
            hit, src = self._resolve_phase_answer(
                text, "awaiting_next",
                lambda t: "ready" if (_looks_like_ready_to_continue(t) or _looks_like_e_define(t)) else None,
            )
            if hit == "ready":
                self._e312_ecc_phase = "geometry"
                return LessonStep(stage=self.stage.value,
                                  message=E312_ECC_GEOMETRY_MSG,
                                  canvas_action={"action": "show_e312_eslider"})
            if hit == "not_ready":
                return LessonStep(stage=self.stage.value,
                                  message="离心率的定义就是 $e=\\dfrac{c}{a}$。回个「好」或「明白」我们继续看 e 滑块 👇")
            reply = self._llm_respond(text, fallback="回个「好」或「明白」，我们就看 $e$ 滑块 👇")
            return LessonStep(stage=self.stage.value, message=reply)

        if phase == "geometry":
            hit, src = self._resolve_phase_answer(
                text, "ecc_geometry",
                lambda t: "e_big_flat_e_small_round" if _looks_like_e_shape_relation(t) else None,
            )
            if hit == "e_big_flat_e_small_round":
                self._e312_ecc_phase = "range"
                return LessonStep(stage=self.stage.value, message=E312_ECC_RANGE_MSG)
            if hit == "e_big_round_e_small_flat":
                return LessonStep(stage=self.stage.value,
                                  message="方向反了——$e=c/a$，$c$ 大椭圆扁、$a$ 大椭圆圆，所以 $e$ 越大越**扁**，越小越**圆**。再观察一下滑块。")
            reply = self._llm_respond(text, fallback="拖动沙盒的 e 滑块。用一句话描述：$e$ 越大越...，$e$ 越小越...?")
            return LessonStep(stage=self.stage.value, message=reply)

        # phase == "range"
        if not self._e312_ecc_range_part1:
            hit, src = self._resolve_phase_answer(
                text, "ecc_range_part1",
                lambda t: "range_0_1" if _looks_like_e_range_0_1(t) else None,
            )
            if hit == "range_0_1":
                self._e312_ecc_range_part1 = True
                return LessonStep(stage=self.stage.value,
                                  message="✅ $0<e<1$。再追问一个**极限情况**：如果 $a=b$（椭圆的长短半轴相等），由 $b^2=a^2-c^2$ 得 $c=?$，那么 $e=?$ 此时图形变成什么？")
            if hit == "other":
                return LessonStep(stage=self.stage.value,
                                  message="再想想。椭圆里 $c$ 和 $a$ 满足 $0<c<a$，所以 $e=c/a$ 的范围是？")
            # TA 自审：ECC.range 学生易写错 e 的范围（含等号、方向反、变量名错）
            _ta_msg = self._maybe_ta_review_freetext(
                text, phase_label="3.1.2 ECC.range 求 e 的取值范围",
                expected_clue="0<e<1（严格不等号；左不含 0、右不含 1；不是 0≤e≤1 也不是 0<e≤1）",
            )
            if _ta_msg:
                self._last_agent = "ta"
                return LessonStep(stage=self.stage.value, message=_ta_msg)
            reply = self._llm_respond(text, fallback="提示：$0<c<a$，所以 $0<e=\\dfrac{c}{a}<1$。")
            return LessonStep(stage=self.stage.value, message=reply)
        # range part 2: a=b → e=0 → 圆
        hit, src = self._resolve_phase_answer(
            text, "ecc_range_part2",
            lambda t: "a_eq_b_circle" if _looks_like_e_zero_circle(t) else None,
        )
        if hit == "a_eq_b_circle":
            self.stage = LessonStage.E312_EXAMPLE_1
            self._maybe_enter_feynman_at_transition("e312_eccentricity")  # 多 agent 钩子（本节核心 stage）
            viz = E312_MANDATORY_VIZ.get(LessonStage.E312_EXAMPLE_1)
            return self._decorate_step_with_peer(LessonStep(
                stage=self.stage.value,
                message=E312_ECC_DONE_MSG + "\n\n" + E312_EXAMPLE_1_INTRO,
                canvas_action=viz,
            ))
        reply = self._llm_respond(text, fallback="提示：$a=b$ 时 $c=0$，$e=0$，椭圆退化为**圆**——圆是椭圆的极限情形。")
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e312_example(self, text: str, example_num: int) -> LessonStep:
        """🟡 3.1.2 例题（4/5/6）：苏格拉底逐 phase 问。

        v3.30 方案 D：
          · 诊断器命中 → 推进 phase
          · 诊断器不命中 + 是 point_set phase（focus/vertex）→ 尝试本地"部分命中累积"
              （学生分两次答 (-5,0)(5,0) 和 (0,4)(0,-4) 也能识别）
          · 仍不命中 → LLM 兜底分类（_PHASE_CLASSIFY_CONFIG_E312）
          · 最后兜底 → LLM 自由回复
        """
        from .example_canonicals_312 import EXAMPLE_CONFIGS_312
        from .example_diagnostician_312 import diagnose_example_312, partial_hit_point_set

        if not hasattr(self, "_e312_example_phase_idx"):
            self._e312_example_phase_idx = {4: 0, 5: 0, 6: 0}
            self._e312_example_subflags = {4: set(), 5: set(), 6: set()}
        if not hasattr(self, "_e312_example_partial_points"):
            # 累积 point_set phase 的部分命中（key=(example_num, phase)，value=已命中点集合）
            self._e312_example_partial_points = {}
        if not hasattr(self, "_e312_example_conclude_hits"):
            # v3.36b: ex5 ask_conclude 跨 turn 累积（"椭圆 + 长轴 10 + 短轴 6" 分次答）
            self._e312_example_conclude_hits = {}

        # v3.36b: awaiting_next 检查 —— 例题通关后等学生确认才切下一题
        awaiting_num = getattr(self, "_e312_example_done_awaiting_next", None)
        if awaiting_num is not None:
            if _looks_like_ready_to_continue(text):
                delattr(self, "_e312_example_done_awaiting_next")
                return self._continue_to_next_e312_example(awaiting_num)
            # 不 ready → 给提示（不调 LLM）
            ui_num = awaiting_num - 3
            return LessonStep(
                stage=self.stage.value,
                message=f"例 {ui_num} 已经完成 🎉 看完右边的图后回个「好」/「继续」就切到下一题；想再看图随便拖。",
            )

        config = EXAMPLE_CONFIGS_312[example_num]
        phases = config["phases"]
        idx = self._e312_example_phase_idx[example_num]
        if idx >= len(phases):  # 已经做完（边界保护）
            return self._advance_e312_example(example_num)
        current_phase = phases[idx]

        dx = diagnose_example_312(text, example_num, current_phase)

        # v3.36b path 1.5: ex5 ask_conclude 跨 turn 累积（"椭圆+长10+短6" 分多次答）
        if dx is None and example_num == 5 and current_phase == "ask_conclude":
            cache_key = (5, "ask_conclude")
            hits = self._e312_example_conclude_hits.get(
                cache_key, {"ellipse": False, "axis_10": False, "axis_6": False}
            )
            if "椭圆" in text:
                hits["ellipse"] = True
            if "10" in text:
                hits["axis_10"] = True
            if "6" in text:
                hits["axis_6"] = True
            self._e312_example_conclude_hits[cache_key] = hits
            if all(hits.values()):
                from .example_diagnostician_312 import ExampleDiagnosis312
                dx = ExampleDiagnosis312(
                    hit_goal="conclude_kw",
                    implied_flags={"conclude_done"},
                    label="完全正确（累积）",
                    via="conclude_accumulated",
                )
            elif any(hits.values()):
                missing = []
                if not hits["ellipse"]: missing.append("是什么图形？")
                if not hits["axis_10"]: missing.append("长轴长 2a=?")
                if not hits["axis_6"]:  missing.append("短轴长 2b=?")
                return LessonStep(
                    stage=self.stage.value,
                    message=f"✅ 这部分对了。还差：{'，'.join(missing)}",
                )

        # v3.30 path 1: 诊断器不命中 + 是 point_set phase → 试部分累积
        if dx is None and current_phase in ("ask_focus", "ask_vertex"):
            canonical = config["canonical"].get(
                "focus_set" if current_phase == "ask_focus" else "vertex_set"
            )
            if canonical:
                new_hits = partial_hit_point_set(text, canonical)
                if new_hits:
                    cache_key = (example_num, current_phase)
                    accumulated = self._e312_example_partial_points.get(cache_key, set())
                    accumulated |= new_hits
                    self._e312_example_partial_points[cache_key] = accumulated
                    if accumulated == set(canonical):
                        # 累积满 = 完整命中，重建 dx
                        from .example_diagnostician_312 import ExampleDiagnosis312
                        goal_name = "focus_set" if current_phase == "ask_focus" else "vertex_set"
                        dx = ExampleDiagnosis312(
                            hit_goal=goal_name,
                            implied_flags=set(config["implies"].get(goal_name, set())),
                            label="完全正确（累积）",
                            via="point_set_partial_accumulated",
                        )
                    else:
                        # 部分对，等学生继续答
                        missing = set(canonical) - accumulated
                        missing_str = ", ".join(f"({p[0]},{p[1]})" for p in sorted(missing))
                        return LessonStep(
                            stage=self.stage.value,
                            message=f"✅ {', '.join(f'({p[0]},{p[1]})' for p in sorted(new_hits))} 这部分对了！还差 {missing_str}，继续答 👇",
                        )

        # v3.36 path 2: 诊断器仍不命中 → 调例题协议（LLM 输出 JSON，后端与 LLM 绑死同步）
        if dx is None:
            protocol = self._llm_example_protocol(text, example_num, current_phase)
            if protocol is not None:
                # 协议字段读取
                diag = protocol.get("diagnosis", "off_topic")
                ack_text = protocol.get("ack_text", "请继续。")[:300]   # 截断防爆
                skip_n = protocol.get("skip_to_example")

                # (a) 学生要跳题 → 直接切 stage（用 deterministic 题目文案，不让 LLM 编）
                if diag == "skip_request" and skip_n in (1, 2, 3):
                    target_stage, target_intro = {
                        1: (LessonStage.E312_EXAMPLE_1, E312_EXAMPLE_1_INTRO),
                        2: (LessonStage.E312_EXAMPLE_2, E312_EXAMPLE_2_INTRO),
                        3: (LessonStage.E312_EXAMPLE_3, E312_EXAMPLE_3_INTRO),
                    }[skip_n]
                    self.stage = target_stage
                    viz = E312_MANDATORY_VIZ.get(target_stage)
                    return LessonStep(
                        stage=self.stage.value,
                        message=f"好的，切到例 {skip_n}（教材 3.1.2 节原题）：\n\n" + target_intro,
                        canvas_action=viz,
                    )

                # (b) 完整命中且 advance=true → 模拟诊断器命中
                if diag == "correct" and protocol.get("advance") is True:
                    # D-1（仅 D 档）：FSM 复核 LLM 提议；否决则走 partial 兜底
                    if _ma_d1_advance_enabled():
                        d1_ok = self._fsm_d1_review_advance(
                            text, protocol, example_num, current_phase,
                        )
                        if not d1_ok:
                            print(f"[lesson_flow.D1] FSM 否决 LLM 提议 ex{example_num}/{current_phase}, hit_goal={protocol.get('hit_goal')}")
                            self._last_event_type = "fsm_reject"
                            return LessonStep(
                                stage=self.stage.value,
                                message="嗯，再仔细看看——你的回答好像还差一点关键信息，再补一句？"
                            )
                        # 通过 FSM 复核 → 标 event_type，便于日志统计"D-1 提议通过率"
                        self._last_event_type = "llm_propose_advance"
                    from .example_diagnostician_312 import ExampleDiagnosis312
                    goal_name = (protocol.get("hit_goal")
                                 or config["phase_goal"].get(current_phase)
                                 or f"{current_phase}_kw")
                    flags = (set(config["implies"].get(goal_name, set()))
                             if goal_name in config["implies"]
                             else {f"{current_phase.replace('ask_', '')}_done"})
                    dx = ExampleDiagnosis312(hit_goal=goal_name, implied_flags=flags,
                                             label="完全正确（协议）", via="protocol")
                    # fall through 到正常推进逻辑

                # (c) partial / wrong / off_topic → 用 LLM 的 ack 但**不推进** phase
                elif diag in ("partial", "wrong", "off_topic"):
                    # 多 agent pilot：B/C/D 档在 partial/wrong 时召唤 TA 助教（sympy 校验）
                    final_msg, ta_agent = self._maybe_inject_ta_correction(
                        ack_text, text, protocol,
                        ctx=f"3.1.2 例 {example_num}, phase={current_phase}",
                    )
                    if ta_agent == "ta":
                        self._last_agent = "ta"
                        self._last_event_type = "normal"
                    return LessonStep(stage=self.stage.value, message=final_msg)

        # 仍 None → deterministic 提示（不再让 LLM 自由发挥）
        if dx is None:
            return LessonStep(
                stage=self.stage.value,
                message="再想想？或者把你的答案写完整些（如焦点请写 (-3,0) 这样的坐标形式）。",
            )

        # 命中：累积 subflags，推进 phase
        self._e312_example_subflags[example_num] |= dx.implied_flags
        self._e312_example_phase_idx[example_num] = idx + 1
        next_idx = idx + 1
        ack = f"✅ 完全正确！"

        # 整道题做完
        done_fn = config["done_fn"]
        if done_fn(self._e312_example_subflags[example_num]) or next_idx >= len(phases):
            return self._advance_e312_example(example_num, ack=ack)

        # 进下一 phase：发对应提问消息
        next_phase = phases[next_idx]
        next_prompt = self._e312_example_phase_prompt(example_num, next_phase)
        # v3.36b: ex5 ask_simplify 通关后发椭圆轮廓中间 viz（不剧透焦点/准线/比值）
        extra_action = None
        if example_num == 5 and current_phase == "ask_simplify":
            extra_action = {"action": "show_e312_example_2_curve_only"}
        return LessonStep(
            stage=self.stage.value,
            message=ack + "\n\n" + next_prompt,
            canvas_action=extra_action,
        )

    def _e312_example_phase_prompt(self, example_num: int, phase: str) -> str:
        """每道例题每 phase 的老师提问文案。"""
        prompts = {
            (4, "ask_minor_axis"):   "**那短轴长 $2b$ 呢？**",
            (4, "ask_eccentricity"): "**那离心率 $e$ 呢？**（提示：先求 $c$）",
            (4, "ask_focus"):        "**焦点坐标**是？（写成 $(x, y)$ 形式，两个焦点都写出来）",
            (4, "ask_vertex"):       "**4 个顶点坐标**是？（注意区分长轴和短轴上的顶点，用 $(x, y)$ 写）",
            (5, "ask_simplify"):     "**两边平方并化简**，得到的椭圆方程是？",
            (5, "ask_conclude"):     "✅ 化简正确。**结论**：$M$ 的轨迹是什么图形？**长轴、短轴**各多长？",
            (6, "ask_one_point"):    "**(2)** $m$ 为何值时直线与椭圆**有且仅有 1 个公共点**？（提示：$\\Delta=0$）",
            (6, "ask_no_point"):     "**(3)** $m$ 在什么范围时直线与椭圆**没有公共点**？（提示：$\\Delta<0$）",
        }
        return prompts.get((example_num, phase), "请继续。")

    def _advance_e312_example(self, example_num: int, ack: str = "") -> LessonStep:
        """v3.36b: 整道例题做完 → 发 solved/explore viz + 设 awaiting_next，等学生确认再切下一题。

        以前是 solved + next_setup 一起发，next_setup 把 solved 覆盖；现在拆两步，学生有充足时间
        看 solved 图、玩 explore 互动（例 2 拖 M、例 3 拖 m 滑块），然后说"好"才切下一题。
        """
        solved_action = {"action": f"show_e312_example_{example_num - 3}_solved"}
        actions = [solved_action]
        # 例 5 / 6 通关后还要 explore（可交互动画）
        if example_num in (5, 6):
            actions.append({"action": f"show_e312_example_{example_num - 3}_explore"})

        # 设 awaiting_next（不立刻切 stage）
        self._e312_example_done_awaiting_next = example_num
        ui_num = example_num - 3  # user 视角的例 1/2/3

        head = ack + "\n\n" if ack else ""
        if example_num == 6:
            tail = f"🎉 例 {ui_num} 完成！\n\n本节 3 道例题全部做完。准备好了回个「好」/「继续」我们看本课总结 📒。"
        else:
            explore_hint = ("拖动右侧画布上的点感受比值/交点变化，看完后" if example_num in (5, 6) else "")
            tail = (f"🎉 例 {ui_num} 完成！右边是完整答案图，{explore_hint}回个「好」/「继续」我们看下一题。")

        return LessonStep(
            stage=self.stage.value,
            message=head + tail,
            canvas_action=actions if len(actions) > 1 else actions[0],
        )

    def _continue_to_next_e312_example(self, completed_num: int) -> LessonStep:
        """v3.36b: 学生确认后真正切到下一例 / SUMMARY。"""
        if completed_num == 4:
            self.stage = LessonStage.E312_EXAMPLE_2
            next_msg = E312_EXAMPLE_2_INTRO
            viz = E312_MANDATORY_VIZ.get(LessonStage.E312_EXAMPLE_2)
        elif completed_num == 5:
            self.stage = LessonStage.E312_EXAMPLE_3
            next_msg = E312_EXAMPLE_3_INTRO
            viz = E312_MANDATORY_VIZ.get(LessonStage.E312_EXAMPLE_3)
        else:  # 6 → SUMMARY
            self.stage = LessonStage.E312_SUMMARY
            next_msg = E312_SUMMARY_MSG
            viz = {"action": "show_e312_summary"}
        return LessonStep(stage=self.stage.value, message=next_msg, canvas_action=viz)

    def _handle_e312_summary(self, text: str) -> LessonStep:
        """📒 3.1.2 总结阶段。复用通用结课检测逻辑。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            fallback = (
                "👏 恭喜完成 3.1.2 课程！\n\n"
                "下次见 —— 我们将一起进入 3.2.1「双曲线及其标准方程」，"
                "把『距离之和』换成『距离之差』，看看会出现什么新曲线。\n\n"
                "[LESSON_END]"
            )
            reply = self._llm_respond(text, fallback=fallback)
            return LessonStep(stage=self.stage.value, message=reply)
        reply = self._llm_respond(text, fallback="还有什么问题想问？或者输入「结束」结课。")
        return LessonStep(stage=self.stage.value, message=reply)
