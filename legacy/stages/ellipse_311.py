"""椭圆 3.1.1 椭圆及其标准方程 —— stage handlers + 静态数据"""
from legacy.lesson_flow import (
    LessonStage,
    LessonStep,
    _looks_like_circle_def_311,
    _looks_like_ellipse_name_311,
    _looks_like_e311_definition,
    _looks_like_coord_choice,
    _looks_like_geom_insight,
    _looks_like_understood,
    _looks_like_yaxis_ellipse_eq,
    _looks_like_lesson_end,
)


# ---- 静态文本 ----

E311_INTRO_MSG = (
    "你好！今天我们一起学习 **3.1.1 椭圆及其标准方程**。\n\n"
    "在动手探究之前，我们先做一个简单的回顾。\n\n"
    "**问题：圆的定义是什么？** 你能用自己的话描述一下吗？\n"
    "（试着用上：定点、距离、定长 这些词）"
)

# 学生答出圆的定义 → 进入 PREDICT_SHAPE
E311_PREDICT_SHAPE_MSG = (
    "👍 答得很好！圆的定义是：**平面内到一个定点的距离等于定长的所有点的轨迹**。\n\n"
    "也可以这样想：拿一根**定长的细绳** 🧵，把它的**两端固定在同一点**，"
    "套上铅笔拉紧绳子绕一圈，笔尖画出的就是一个圆 ⭕。\n\n"
    "🔵 **现在做一个实验（教材 p105 探究）**：\n"
    "如果把绳子的**两端拉开一段距离**，分别钉在两个不同的点上，再套铅笔拉紧绳子绕一圈，"
    "**你猜笔尖会画出什么形状？**\n\n"
    "（先猜一下，不一定要答对～）"
)

# 学生预测后 → 进入 EXPLORE_STRING（实际操作画布）
E311_EXPLORE_STRING_MSG = (
    "🎨 **来动手画画看！**\n\n"
    "右侧画布上已经放好了两个图钉 📍📍 —— 我们把它们叫做 $F_1$、$F_2$。\n"
    "请**拖动笔尖 ✏️ 绕一圈**，把整个轨迹画出来。\n\n"
    "在拖动过程中，注意：**笔尖到 $F_1$、$F_2$ 的距离**满足什么关系？"
)

# 学生画完轨迹 → 进入 AWAIT_SHAPE_NAME（不剧透）
E311_AWAIT_SHAPE_NAME_MSG = (
    "🎯 漂亮！你画出了一条对称的封闭曲线。\n\n"
    "**你觉得这是什么图形？** 试着说出它的名字。"
)

# 学生说"椭圆" → 进入 AWAIT_DEFINITION（让学生归纳定义）
E311_AWAIT_DEFINITION_MSG = (
    "✅ 没错，这就是 **椭圆**！\n\n"
    "回忆一下刚才画图的过程：绳长**始终保持不变**，所以笔尖（动点 P）到 $F_1$、$F_2$ 的距离之间满足一个特定关系。\n\n"
    "**请你类比圆的定义，用自己的话归纳出椭圆的定义。**"
)

# 学生归纳定义 → 进入 REFLECT_COORD（精炼定义 + 提出建系问题）
E311_REFLECT_COORD_MSG = (
    "💡 你抓住了关键！\n\n"
    "教材里的标准说法是：\n\n"
    "> **平面内到两定点 $F_1$、$F_2$ 的距离之和等于常数（大于 $|F_1F_2|$）的点的轨迹叫做椭圆。**\n"
    "> 两定点 $F_1$、$F_2$ 叫做椭圆的**焦点**，焦距 $|F_1F_2| = 2c$，距离之和 $|MF_1|+|MF_2| = 2a$。\n\n"
    "🟣 **思考1**：\n"
    "现在我们要把这个几何条件**翻译成方程**。\n"
    "**怎样建立坐标系，能让所得到的方程形式最简单？**\n\n"
    "（提示：想想椭圆有什么对称性？$F_1$、$F_2$ 应该放在哪条轴上比较自然？）"
)

# v2.4: DERIVE 阶段入场——建系 + 让学生写第一个焦半径
E311_DERIVE_AND_RESULT_MSG = (
    "🧠 太对了！按你说的建坐标系：以 $F_1F_2$ 所在直线为 **x 轴**，"
    "$F_1F_2$ 的**中垂线**为 **y 轴**，原点 $O$ 在 $F_1F_2$ 中点。\n\n"
    "这样 $F_1(-c, 0)$，$F_2(c, 0)$。设椭圆上任意一点 $M(x, y)$。\n\n"
    "📐 **现在来推导方程**。先用距离公式写出 **$|MF_1| = ?$**（用 $x, y, c$ 表示）"
)

# v2.4: 两个焦半径都写出后——发起"挑战"，让学生先自己试着写最终方程
E311_DERIVE_CHALLENGE_MSG = (
    "🎯 太好了，两个焦半径都写出来了！代入椭圆定义 $|MF_1|+|MF_2|=2a$，我们得到方程①：\n"
    "$$\\sqrt{(x+c)^2+y^2}+\\sqrt{(x-c)^2+y^2}=2a$$\n\n"
    "**先别急着一步步算 —— 你能不能直接挑战一下，把焦点在 $x$ 轴上的椭圆方程的最终形式写出来？**\n"
    "大胆试，写不出来也完全没关系，我们再一起一步步推。"
)

# v2.4: 快速路径——学生直接写对了最终方程
E311_DERIVE_FAST_MSG = (
    "👏 厉害！你直接把方程的最终形式写出来了，说明你对化简很有感觉。\n\n"
    "我们整理一下：方程①经过 **移项 → 平方 → 整理 → 再平方 → 整理** 之后，会化简成：\n"
    "$$\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$$\n\n"
    "注意这里分母还是 $a^2-c^2$ —— 我们还**没有引入新字母**。接下来看看这个 $a^2-c^2$ 到底是什么。"
)

# v2.4: 引导路径——学生写不出，开始一步步苏格拉底引导
E311_DERIVE_GUIDED_START_MSG = (
    "没关系，这个方程有**两个根号**，直接平方会很乱。我们一步一步来。\n\n"
    "**第一步**：你觉得应该先怎么处理这两个根号？\n"
    "（提示：想办法让其中一个根号先「落单」—— 单独待在等号的一边）"
)

# v2.4: 引导路径——学生推到了最终结果
E311_DERIVE_RESULT_MSG = (
    "🎉 推出来了！经过移项、两次平方、整理，方程化简成：\n"
    "$$\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$$\n\n"
    "注意：现在分母还是 $a^2-c^2$，我们**还没有引入新字母 $b$**。\n"
    "接下来我们就来看看，这个 $a^2-c^2$ 在图上到底对应什么。"
)

# v2.4: REFLECT_GEOM 入场——思考2：在图上找 a、c、√(a²-c²) 的线段（此时还没有 b！）
E311_REFLECT_GEOM_MSG = (
    "🔍 **思考2（教材 p106 末）**\n\n"
    "现在方程是 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$，分母里有个 $\\sqrt{a^2-c^2}$。\n\n"
    "请观察右边的**图3.1-3**：在这个椭圆里，你能分别找出表示 $a$、$c$、$\\sqrt{a^2-c^2}$ 的**线段**吗？\n"
    "（提示：先看看椭圆**短轴的端点** $P$，它到两个焦点 $F_1$、$F_2$ 的距离是多少？）"
)

# v2.4: 学生找到线段后——这时才定义 b
E311_DEFINE_B_MSG = (
    "✨ 对！取短轴端点 $P$：\n"
    "- $|PF_1|=|PF_2|=a$（由椭圆定义，距离之和 $=2a$，$P$ 关于 $y$ 轴对称）\n"
    "- $|OF_1|=|OF_2|=c$\n"
    "- 由勾股定理：$|PO|=\\sqrt{a^2-c^2}$\n\n"
    "既然 $\\sqrt{a^2-c^2}$ 就是 $|PO|$ 这条**实实在在的线段**（短半轴），"
    "我们就**给它起个名字**：令 $b=|PO|=\\sqrt{a^2-c^2}$。\n\n"
    "这样，椭圆的方程就写成了简洁的形式 —— **椭圆的标准方程**：\n"
    "$$\\boxed{\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1\\quad(a>b>0)}$$\n"
    "它表示焦点在 $x$ 轴上、$F_1(-c,0)$、$F_2(c,0)$ 的椭圆，这里 $c^2=a^2-b^2$。"
)

# v2.4: 思考3——y 轴形式
E311_REFLECT_YAXIS_MSG = (
    "🟣 **思考3（教材 p107）**\n\n"
    "如果焦点改在 **$y$ 轴**上（坐标变成 $(0,-c)$、$(0,c)$），$a$、$b$ 含义不变，"
    "那椭圆的方程会变成什么样？\n\n"
    "**你来推一推。**（提示：把刚才推导里的 $x$ 和 $y$ 互换一下试试）"
)

E311_EXAMPLE_1_INTRO = (
    "📘 **例 1（教材 p107 末）**\n\n"
    "已知椭圆的两个焦点坐标分别是 $(-2, 0)$、$(2, 0)$，"
    "并且经过点 $\\left(\\dfrac{5}{2},\\ -\\dfrac{3}{2}\\right)$，求它的**标准方程**。\n\n"
    "我们用 4 步教学法解这道题。\n\n"
    "**第 1 步 · 审题**：\n"
    "题目给了什么？要求什么？焦点位置告诉我们方程是什么形式？"
)

E311_EXAMPLE_2_INTRO = (
    "📘 **例 2（教材 p108）**\n\n"
    "如图3.1-5，在圆 $x^2+y^2=4$ 上任取一点 $P$，过 $P$ 作 $x$ 轴的垂线段 $PD$（$D$ 为垂足）。"
    "当 $P$ 在圆上运动时，**线段 $PD$ 的中点 $M$ 的轨迹是什么？为什么？**\n\n"
    "**第 1 步 · 审题**：\n"
    "动点 $P$ 在哪条曲线上？$M$ 与 $P$、$D$ 是什么关系？我们要找 $M$ 的轨迹方程。\n\n"
    "你能先描述一下 $M$ 与 $P$ 的坐标关系吗？"
)

E311_EXAMPLE_3_INTRO = (
    "📘 **例 3（教材 p108-p109）**\n\n"
    "如图3.1-6，设 $A$、$B$ 两点的坐标分别为 $(-5, 0)$、$(5, 0)$。"
    "直线 $AM$、$BM$ 相交于点 $M$，且它们的**斜率之积是 $-\\dfrac{4}{9}$**，求点 $M$ 的轨迹方程。\n\n"
    "**第 1 步 · 审题**：\n"
    "$A$、$B$ 是定点，$M$ 是动点；$k_{AM} \\cdot k_{BM} = -\\dfrac{4}{9}$ 是约束条件。\n"
    "你能先把 $k_{AM}$ 和 $k_{BM}$ 用 $M(x,y)$ 表示出来吗？"
)

E311_SUMMARY_MSG = (
    "🎉 恭喜完成 **3.1.1 椭圆及其标准方程** 全部内容！\n\n"
    "📊 **本节回顾**\n"
    "1. 🔵 **探究**：绳画法 → 椭圆定义（距离之和 = 常数 $2a$）\n"
    "2. 🟣 **思考1**：选 $F_1F_2$ 为 x 轴 → 方程对称简洁\n"
    "3. 🧩 **标准方程**：$\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$（$a>b>0$，$c^2=a^2-b^2$）\n"
    "4. 🟣 **思考2+3**：$b$ = 短半轴 = $\\sqrt{a^2-c^2}$；y 轴形式 $\\dfrac{y^2}{a^2}+\\dfrac{x^2}{b^2}=1$\n"
    "5. 🟡 **例 1**：已知焦点+过点 → 由定义算 $2a$\n"
    "6. 🟡 **例 2**：圆压缩 → 椭圆（坐标变换法）\n"
    "7. 🟡 **例 3**：斜率积 $=-\\dfrac{4}{9}$ → 椭圆\n\n"
    "📚 **下节预告**（3.1.2）：椭圆的简单几何性质（范围 / 对称性 / 顶点 / **离心率**）\n\n"
    "你还有哪些问题想问？或者输入「**结束**」「**没问题了**」结课。\n"
    "[LESSON_END_HINT]"
)

# ── 例题"完成话术"模块常量 ──
E311_EXAMPLE_1_DONE_BODY = (
    "✅ 例 1 完成！答案：$\\dfrac{x^2}{10}+\\dfrac{y^2}{6}=1$。\n\n"
    + E311_EXAMPLE_2_INTRO
)
E311_EXAMPLE_2_DONE_BODY = (
    "✅ 例 2 完成！答案：$\\dfrac{x^2}{4}+y^2=1$，$M$ 的轨迹是椭圆。\n\n"
    "🟣 **顺势思考**（教材紧跟的思考）：\n"
    "由例 2 我们发现，圆通过「**压缩**」（y 方向缩到一半）得到椭圆。"
    "你能由圆通过「**拉伸**」得到椭圆吗？想到圆和椭圆是什么关系吗？\n\n"
    "（思考一下后，我们继续例 3 👇）\n\n" + E311_EXAMPLE_3_INTRO
)
E311_EXAMPLE_3_DONE_BODY = (
    "✅ 例 3 完成！答案：$\\dfrac{x^2}{25}+\\dfrac{y^2}{100/9}=1$"
    "（除去 $(\\pm 5, 0)$ 两点）。\n\n" + E311_SUMMARY_MSG
)


# ---- Stage Goals ----

E311_STAGE_GOALS = {
    LessonStage.E311_INTRO: (
        "📒 开场阶段：让学生回忆**圆的定义**（关键词：定点、距离、定长、相等）。\n"
        "学生答出 ≥2 个关键词即推进到 PREDICT_SHAPE。\n"
        "如果学生卡住，提示：「圆上每个点到圆心的距离都怎么样？」\n"
        "**严禁**：直接告诉学生定义、提及椭圆/焦点/标准方程。"
    ),
    LessonStage.E311_RECALL_CIRCLE: (
        "📒 等学生说出圆的定义。检测关键词：定点 / 距离 / 定长 / 相等 / 圆心 / 半径。"
        "命中 ≥1 个核心关键词即推进。"
        "**严禁**：剧透椭圆答案。"
    ),
    LessonStage.E311_PREDICT_SHAPE: (
        "🔵 探究第 1 步（预测）：学生听完两端拉开的实验描述后，预测会画出什么形状。\n"
        "**请先识别学生回复的类型，再给出贴合的回应**（1-2 句，简短）：\n"
        "  · 学生说「不知道 / 不清楚 / 没想法」→ 安慰他「没关系，不知道很正常，动手画一画就清楚了」，不要硬说「好的猜想」。\n"
        "  · 学生猜了某个形状（椭圆 / 鸡蛋形 / 不规则曲线 等）→ 肯定他「这是个不错的猜想」，但**不评判对错**。\n"
        "  · 学生答非所问 → 温和地说「我们待会儿就知道了」，拉回到画布探究。\n"
        "无论哪种情况，都自然过渡到「去画布上亲手画出来验证」。学生发任何回复后系统都会推进到 EXPLORE_STRING。\n"
        "**严禁**：在此阶段确认或否定「椭圆」答案，让学生自己通过画图发现。"
    ),
    LessonStage.E311_EXPLORE_STRING: (
        "🔵 探究第 2 步（操作）：学生应该去画布拖动笔尖，画出轨迹。\n"
        "trail_completed 事件会自动推进到 AWAIT_SHAPE_NAME。\n"
        "如果学生只发文字不操作，提醒先去右边画布拖动。\n"
        "**严禁**：剧透「椭圆」二字。"
    ),
    LessonStage.E311_AWAIT_SHAPE_NAME: (
        "👀 学生画完曲线，等他说出名字「椭圆」。\n"
        "学生说出「椭圆」或类似词（鸭蛋、椭圆形）即推进到 AWAIT_DEFINITION。\n"
        "答不上来时给提示：「这个图形像鸭蛋一样的，在数学里它有一个以『椭』字开头的名字…」\n"
        "**严禁**：直接告诉答案。"
    ),
    LessonStage.E311_AWAIT_DEFINITION: (
        "🧩 学生确认是椭圆，等他用自己的话归纳定义。\n"
        "检测关键词：定点 / 距离之和 / 常数 / 焦点 / 之和。命中 ≥2 个推进。\n"
        "如果学生概念有偏差，苏格拉底式追问。\n"
        "**严禁**：直接给完整定义文本（教材原话由下一阶段进入时显示）。"
    ),
    LessonStage.E311_REFLECT_COORD: (
        "🟣 思考1：怎样建立坐标系使方程简单？\n"
        "期望的完整答案：以 $F_1F_2$ 所在直线为 x 轴，$F_1F_2$ 的中垂线为 y 轴（原点在 $F_1F_2$ 中点）。\n"
        "**判断学生回答的完整度**：\n"
        "  · 学生只说了「椭圆是轴对称的 / 有对称性」→ 这是好的**观察**，但还没回答「轴放哪」。\n"
        "    要先肯定他的观察，再追问：「很好，那利用这个对称性，你觉得 x 轴、y 轴具体应该放在哪里？」\n"
        "    （不要替他说出答案，让他自己说出「F₁F₂ 连线作 x 轴、中垂线作 y 轴」）\n"
        "  · 学生说出了具体的轴放置方案（焦点连线作 x 轴、中垂线作 y 轴等）→ 系统会自动推进。\n"
        "如果学生完全答非所问，引导他先想椭圆有什么对称性。\n"
        "**严禁**：直接告诉答案、提前给标准方程。"
    ),
    LessonStage.E311_DERIVE_AND_RESULT: (
        "🧩 标准方程**推导**阶段。本阶段终点是 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$ —— "
        "**注意：本阶段全程不引入字母 $b$**（$b$ 要等到下一阶段几何观察后才定义，严格按教材）。\n\n"
        "本阶段有三个子环节，由系统状态机控制，你只需按当前子环节引导：\n\n"
        "【子环节1 · 收集焦半径】学生用距离公式写 $|MF_1|$、$|MF_2|$。"
        "只写了一个就引导写另一个，**严禁替学生写完**。\n\n"
        "【子环节2 · 挑战】两个焦半径都写出后，系统会让学生**先自己尝试**直接写出最终方程。"
        "  · 学生写得出最终方程 → 系统走快速路径（确认 + 你帮他梳理化简主线，不必逐步抠）\n"
        "  · 学生写不出 / 说不会 → 系统转入引导路径\n\n"
        "【子环节3 · 引导化简】这是真正的苏格拉底式逐步引导，**一步一问，让学生自己输入每一步**：\n"
        "  (1) 移项：把一个根号单独留在一边 → 学生写出 $\\sqrt{(x+c)^2+y^2}=2a-\\sqrt{(x-c)^2+y^2}$\n"
        "  (2) 第一次平方 + 整理 → 引导学生得到 $a^2-cx=a\\sqrt{(x-c)^2+y^2}$\n"
        "  (3) 第二次平方 + 整理 → $(a^2-c^2)x^2+a^2y^2=a^2(a^2-c^2)$\n"
        "  (4) 两边除以 $a^2(a^2-c^2)$ → $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{a^2-c^2}=1$\n"
        "  每一步都先问学生「这一步你觉得该怎么做 / 做出来是什么」，等他答了再确认、纠正、推进。\n"
        "  学生卡住时给**提示**而不是直接给答案。\n\n"
        "**严禁**：替学生跳步、引入字母 $b$、提及离心率（属于 3.1.2）。"
    ),
    LessonStage.E311_REFLECT_GEOM_YAXIS: (
        # ⚠️ 该 stage 内部有两个 phase（find_segments / yaxis），
        # _build_system_prompt 会按 phase 动态替换为下面 _E311_GEOM_PHASE_GOALS 里的细分目标。
        # 这里只放一个兜底（兼容历史调用）。
        "🟣 几何观察阶段。请按教材 p106-107 顺序：先找线段、再定义 b、最后推 y 轴形式。"
    ),
    LessonStage.E311_EXAMPLE_1: (
        "🟡 例 1：已知焦点 (±2,0) 和过点 (5/2, -3/2) 求椭圆标准方程。\n"
        "4 步教学法。关键引导：① 由焦点位置 → 标准方程形式；② 由定义直接算 2a；③ 由 b²=a²-c² 得 b²=6。\n"
        "答案：x²/10 + y²/6 = 1。学生确认理解后推进到 EXAMPLE_2。"
    ),
    LessonStage.E311_EXAMPLE_2: (
        "🟡 例 2：圆 x²+y²=4 上动点 P，PD 中点 M 的轨迹。\n"
        "4 步教学法。引导：① 设 M(x,y), P(x₀,y₀)；② 中点关系 x=x₀, y=y₀/2；"
        "③ 代入圆方程消元 → x²+4y²=4 → x²/4+y²=1。\n"
        "**内嵌🟣思考**：例题完成后追问『圆通过「压缩」得椭圆，能通过「拉伸」得椭圆吗？』"
    ),
    LessonStage.E311_EXAMPLE_3: (
        "🟡 例 3：A(-5,0), B(5,0), AM·BM 斜率积=-4/9 求 M 轨迹。\n"
        "4 步教学法。引导：① k_AM=y/(x+5), k_BM=y/(x-5)；② 代入 → 化简 → x²/25+y²/(100/9)=1；③ 注意排除 (±5,0)。"
    ),
    LessonStage.E311_SUMMARY: (
        "📒 总结阶段。回顾 3.1.1 全部内容，预告 3.1.2 离心率/几何性质。\n"
        "学生说「没问题」/「结束」时附加 [LESSON_END] 标记。"
    ),
}


# ---- Course Config ----

E311_COURSE_CONFIG = {
    "ellipse_311": {
        "name_cn": "3.1.1 椭圆及其标准方程",
        "scope": "ellipse",
        "first_stage": LessonStage.E311_INTRO,
        "start_stage": LessonStage.E311_RECALL_CIRCLE,
        "kg_nodes_basic": [
            "foundation_distance_formula", "foundation_locus",
            "ellipse_311_explore_string", "ellipse_definition",
        ],
        "kg_nodes_equation": [
            "ellipse_311_reflect_coord", "ellipse_311_derivation",
            "ellipse_standard_equation_x", "ellipse_standard_equation_y",
            "ellipse_311_reflect_geometry_yaxis", "ellipse_parameter_triangle",
        ],
        # 例题节点：随阶段动态注入（在 _get_stage_kg_nodes 中处理）
        "kg_nodes_examples": {
            LessonStage.E311_EXAMPLE_1: ["ellipse_311_example_1"],
            LessonStage.E311_EXAMPLE_2: ["ellipse_311_example_2"],
            LessonStage.E311_EXAMPLE_3: ["ellipse_311_example_3"],
        },
        # 3.1.1 不涉及离心率（属于 3.1.2），保持空集
        "kg_nodes_eccentricity": [],
        "eccentricity_stages": set(),
        "summary_kg_nodes": [
            "ellipse_definition", "ellipse_standard_equation_x",
            "ellipse_311_example_1", "ellipse_311_example_2", "ellipse_311_example_3",
        ],
    },
}


# ---- Mandatory VIZ ----

E311_MANDATORY_VIZ = {
    # ---- 椭圆 3.1.1 课（v2.2 调整）：12 阶段，确定性 VIZ 在合适阶段才触发 ----
    # 注意：INTRO/RECALL_CIRCLE/PREDICT_SHAPE 阶段不出画布，让学生先思考
    # v2.2: EXPLORE_STRING 阶段 show_axes=false（学生还没建系，画布不应该有坐标轴）
    LessonStage.E311_EXPLORE_STRING: {"action": "init_two_foci_locus", "config": {"F1": [-2, 0], "F2": [2, 0], "sum_dist": 6, "tolerance": 0.15, "show_axes": False}},
    LessonStage.E311_DERIVE_AND_RESULT: {"action": "show_e311_derivation_steps"},        # 分步推导动画（学生点"下一步"）
    LessonStage.E311_REFLECT_GEOM_YAXIS: {"action": "show_e311_abc_triangle_setup"},     # 图3.1-3 题目版（不剧透答案）
    # 例题 viz 分两版（v3.11 拆分）：
    #   · setup：进入例题时发，**不剧透**——只画题目装备（点、圆等）+ 提示，
    #            不画答案曲线、不写推导和最终方程
    #   · solved：学生答完最终方程推进时发，**完成版**——补上推导和答案
    # 历史上的 show_e311_example_N_viz 在前端 dispatcher 里保留作为 solved 的别名。
    LessonStage.E311_EXAMPLE_1: {"action": "show_e311_example_1_setup"},                  # 题目版（不剧透）
    LessonStage.E311_EXAMPLE_2: {"action": "show_e311_example_2_setup"},
    LessonStage.E311_EXAMPLE_3: {"action": "show_e311_example_3_setup"},
}


# ---- VIZ on Request ----

E311_VIZ_ON_REQUEST = {
    # 前期阶段（圆 → 探究）：学生要动画 → 给"圆的定义"动画（安全、是知识起点、不剧透椭圆）
    LessonStage.E311_INTRO: {"action": "show_e311_circle"},
    LessonStage.E311_RECALL_CIRCLE: {"action": "show_e311_circle"},
    LessonStage.E311_PREDICT_SHAPE: {"action": "show_e311_circle"},
    LessonStage.E311_EXPLORE_STRING: {"action": "show_e311_circle"},
    LessonStage.E311_AWAIT_SHAPE_NAME: {"action": "show_e311_circle"},
    LessonStage.E311_AWAIT_DEFINITION: {"action": "show_e311_circle"},
    # 建系 + 推导：给几何参考图
    LessonStage.E311_REFLECT_COORD: {"action": "show_e311_derivation_steps"},
    LessonStage.E311_DERIVE_AND_RESULT: {"action": "show_e311_derivation_steps"},
    # 思考2/3：学生主动要动画 → 给 setup 版（找线段题目，不剧透答案）
    LessonStage.E311_REFLECT_GEOM_YAXIS: {"action": "show_e311_abc_triangle_setup"},
    # 例题：学生在解题中要动画 → 给题目版（不剧透）。完成后才换 solved。
    LessonStage.E311_EXAMPLE_1: {"action": "show_e311_example_1_setup"},
    LessonStage.E311_EXAMPLE_2: {"action": "show_e311_example_2_setup"},
    LessonStage.E311_EXAMPLE_3: {"action": "show_e311_example_3_setup"},
    LessonStage.E311_SUMMARY: {"action": "show_e311_abc_triangle"},
}


# ---- Stage Dispatch Registry ----

E311_STAGE_DISPATCH = {
    LessonStage.E311_RECALL_CIRCLE: ("_handle_e311_recall_circle", {}),
    LessonStage.E311_PREDICT_SHAPE: ("_handle_e311_predict_shape", {}),
    LessonStage.E311_EXPLORE_STRING: None,  # handled inline in on_student_message
    LessonStage.E311_AWAIT_SHAPE_NAME: ("_handle_e311_await_shape_name", {}),
    LessonStage.E311_AWAIT_DEFINITION: ("_handle_e311_await_definition", {}),
    LessonStage.E311_REFLECT_COORD: ("_handle_e311_reflect_coord", {}),
    LessonStage.E311_DERIVE_AND_RESULT: ("_handle_e311_derive_and_result", {}),
    LessonStage.E311_REFLECT_GEOM_YAXIS: ("_handle_e311_reflect_geom_yaxis", {}),
    LessonStage.E311_EXAMPLE_1: ("_handle_e311_example", {"example_num": 1}),
    LessonStage.E311_EXAMPLE_2: ("_handle_e311_example", {"example_num": 2}),
    LessonStage.E311_EXAMPLE_3: ("_handle_e311_example", {"example_num": 3}),
    LessonStage.E311_SUMMARY: ("_handle_e311_summary", {}),
}


class Ellipse311Mixin:
    """椭圆 3.1.1 课 stage handlers（作为 LessonFlow 的 mixin 使用）"""

    # v3.21：REFLECT_GEOM_YAXIS yaxis phase 的"隐式 viz 意图"关键词（无歧义的纯 viz 词）。
    _E311_YAXIS_IMPLICIT_VIZ_KWS = ["对比", "比较", "两种", "两个", "区别", "差别"]
    # y 轴类词：含义模糊（可能是给答案，也可能是想看 y 轴 viz）。
    # 用"是否带 = 等号"区分：含 y 轴 + 无 = → 算 viz；含 y 轴 + 有 = → 算给答案。
    _E311_YAXIS_AMBIGUOUS_KWS = ["y轴", "y 轴", "Y轴", "Y 轴", "竖椭圆"]

    def _e311_is_viz_intent(self, text: str) -> bool:
        """v3.21: 综合判断学生是否在请求 viz。
        优先级：① 显式 viz 词（动画/图/画一/...）→ True
                ② yaxis phase + 对比类纯 viz 词 → True
                ③ yaxis phase + 含"y 轴" + 没有等号 → True（区分给答案 vs 想看图）
        """
        if self._wants_viz(text):
            return True
        if (self.stage == LessonStage.E311_REFLECT_GEOM_YAXIS
                and getattr(self, "_e311_geom_phase", "find_segments") == "yaxis"):
            if any(kw in text for kw in self._E311_YAXIS_IMPLICIT_VIZ_KWS):
                return True
            if "=" not in text and any(kw in text for kw in self._E311_YAXIS_AMBIGUOUS_KWS):
                return True
        return False

    def _e311_resolve_request_viz(self, stage, text: str):
        """v3.15 方案 A + v3.21/v3.22：学生主动要动画时的 stage 内关键词细分路由。

        E311_REFLECT_GEOM_YAXIS 覆盖：
          · "对比 / 比较 / 两种 / 区别" → `show_e311_ellipse_comparison`
          · "y 轴 / Y 轴 / 竖椭圆"       → `show_e311_yaxis_ellipse`
          · 其它 viz 请求：
              - find_segments phase → `show_e311_abc_triangle_setup`（可点击线段）
              - yaxis phase → `show_e311_yaxis_ellipse`（教材 p107 配图，find_segments 已完成）
        优先级：对比 > yaxis 关键词 > phase-aware 默认。
        """
        if stage == LessonStage.E311_REFLECT_GEOM_YAXIS:
            cmp_kws = ["对比", "比较", "两种", "两个", "区别", "差别"]
            if any(kw in text for kw in cmp_kws):
                return {"action": "show_e311_ellipse_comparison"}
            yaxis_kws = ["y轴", "y 轴", "Y轴", "Y 轴", "焦点在y", "焦点在 y",
                         "焦点在Y", "焦点在 Y", "竖着", "竖椭圆", "y 轴上"]
            if any(kw in text for kw in yaxis_kws):
                return {"action": "show_e311_yaxis_ellipse"}
            # v3.22：phase-aware 默认 —— yaxis phase 学生模糊请求"动画"时给 y 轴椭圆图，
            # 不要给 abc_triangle_setup（那是 find_segments 阶段的，已经做完了）
            phase = getattr(self, "_e311_geom_phase", "find_segments")
            if phase == "yaxis":
                return {"action": "show_e311_yaxis_ellipse"}
        return E311_VIZ_ON_REQUEST.get(stage)

    # v2.3.1: 阶段感知的 VIZ 请求（学生说"我要动画"时，用这个生成而非学生原话）
    # 键：阶段；值：(给 LLM 的生成请求, 干净的标题)
    _E311_STAGE_VIZ_REQUEST = {
        LessonStage.E311_INTRO: (
            "画一个圆，标注圆心 O 和半径 r，用动画展示圆上的动点绕圆心一周，"
            "强调动点到圆心的距离始终等于 r。不要出现椭圆。",
            "圆的定义动画",
        ),
        LessonStage.E311_RECALL_CIRCLE: (
            "画一个圆，标注圆心 O 和半径 r，展示圆规画圆：针尖固定在圆心，"
            "铅笔绕一圈，铅笔到圆心的距离恒为 r。只画圆，不要画椭圆。",
            "圆的定义动画",
        ),
        LessonStage.E311_PREDICT_SHAPE: (
            "画两个分开的定点 F1、F2，和一支可拖动的笔尖 P，P 到 F1、F2 的两段距离"
            "用线段表示。**不要画出完整椭圆轨迹**，只展示「两个定点+一支笔」的实验装置，"
            "让学生自己拖动探索。",
            "绳画法实验装置",
        ),
        LessonStage.E311_EXPLORE_STRING: (
            "画两个定点 F1、F2 和一支可拖动笔尖 P，两段线段连接 P 与 F1、F2。"
            "**不要预先画出椭圆**，让学生拖动 P 自己描出轨迹。",
            "绳画法实验装置",
        ),
        LessonStage.E311_DERIVE_AND_RESULT: (
            "画一个直角坐标系，F1(-c,0)、F2(c,0) 两个焦点，椭圆上一点 M(x,y)，"
            "用线段连接 M 到两焦点，标注 |MF1|、|MF2|。展示距离公式的几何意义。",
            "标准方程推导示意图",
        ),
        LessonStage.E311_REFLECT_GEOM_YAXIS: (
            "画椭圆 + 直角坐标系，高亮短轴端点 P，画出直角三角形 OPF1，"
            "标注 a、b、c 三条边，展示 a²=b²+c² 的几何关系。",
            "a、b、c 几何关系图",
        ),
    }

    def _handle_e311_recall_circle(self, text: str) -> LessonStep:
        """📒 等学生说出圆的定义。命中关键词即推进到 PREDICT_SHAPE。"""
        if _looks_like_circle_def_311(text):
            self.stage = LessonStage.E311_PREDICT_SHAPE
            reply = self._llm_respond(text, fallback=E311_PREDICT_SHAPE_MSG)
            return LessonStep(stage=self.stage.value, message=reply)
        # 学生答不上 → 引导
        fallback = (
            "再想想哦～提示：圆上的任意一点到**圆心**有什么特点？\n"
            "关键词：「定点」「距离」「相等」。"
        )
        reply = self._llm_respond(text, fallback=fallback)
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e311_predict_shape(self, text: str) -> LessonStep:
        """🔵 学生预测形状后，激活画布让其动手画。
        v2.3.2: 用 LLM 识别学生回复状态（不知道 / 猜了某个形状 / 答非所问），
        生成"贴合学生实际回复"的过渡语，而不是硬编码"好的猜想"。"""
        # 注意：先在 PREDICT_SHAPE 阶段调 LLM（让 LLM 用本阶段的 stage goal 上下文回应），
        # 再切换到 EXPLORE_STRING。
        ack_fallback = "好的，不论你心里怎么想，**我们去画布上亲手画出来验证看看吧！** 👉"
        ack = self._llm_respond(text, fallback=ack_fallback)
        # 回应完毕，推进到探究阶段
        self.stage = LessonStage.E311_EXPLORE_STRING
        mandatory_viz = E311_MANDATORY_VIZ.get(LessonStage.E311_EXPLORE_STRING)
        full_msg = ack + "\n\n" + E311_EXPLORE_STRING_MSG
        return LessonStep(
            stage=self.stage.value,
            message=full_msg,
            canvas_action=mandatory_viz,
            expect_event="trail_completed",
        )

    def _handle_e311_await_shape_name(self, text: str) -> LessonStep:
        """👀 学生看到画出的曲线，需要说出"椭圆"才推进。"""
        if _looks_like_ellipse_name_311(text):
            self.stage = LessonStage.E311_AWAIT_DEFINITION
            reply = self._llm_respond(text, fallback=E311_AWAIT_DEFINITION_MSG)
            return LessonStep(stage=self.stage.value, message=reply)
        # 答不上来 → 提示
        fallback = (
            "这个图形像鸭蛋、像橄榄… 在数学里它有一个以「**椭**」字开头的名字，你再想想？"
        )
        reply = self._llm_respond(text, fallback=fallback)
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e311_await_definition(self, text: str) -> LessonStep:
        """🧩 等学生归纳椭圆定义。命中关键词推进到 REFLECT_COORD。"""
        if _looks_like_e311_definition(text):
            self.stage = LessonStage.E311_REFLECT_COORD
            # v2.1: 不再附加冗余 footer，REFLECT_COORD_MSG 已包含教材原话
            reply = self._llm_respond(text, fallback=E311_REFLECT_COORD_MSG)
            return LessonStep(stage=self.stage.value, message=reply)
        fallback = (
            "差一点点～回想一下：笔尖到 $F_1$、$F_2$ 的距离\n"
            "之间满足什么关系？这个关系等于什么？"
        )
        reply = self._llm_respond(text, fallback=fallback)
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e311_reflect_coord(self, text: str) -> LessonStep:
        """🟣 思考1：建坐标系。学生答出对称性/x 轴/中垂线即推进到 DERIVE_AND_RESULT。
        v2.1: 不立即触发推导动画，先让学生尝试写出 |MF₁|+|MF₂|=2a 的展开式。
        v2.2: 推进时先在画布上"激活"坐标系（淡入坐标轴 + F₁/F₂ 坐标标注），
              再让学生写距离公式。这样画布上的坐标轴出现与学生的回答同步。"""
        if _looks_like_coord_choice(text):
            self.stage = LessonStage.E311_DERIVE_AND_RESULT
            reply = self._llm_respond(text, fallback=E311_DERIVE_AND_RESULT_MSG)
            # 触发坐标系激活：在原 board 上动画式加入坐标轴
            return LessonStep(
                stage=self.stage.value,
                message=reply,
                canvas_action={"action": "establish_coordinate_axes"},
            )
        fallback = (
            "提示：椭圆有什么**对称性**？利用对称性来选坐标轴，方程会更简洁。\n"
            "$F_1F_2$ 的连线和它的中垂线，分别可以做什么？"
        )
        reply = self._llm_respond(text, fallback=fallback)
        return LessonStep(stage=self.stage.value, message=reply)

    @staticmethod
    def _radius_forms_in(text: str) -> tuple:
        """【loose 主题启发，仅供 fallback 用】检测文本含 (x+c) / (x-c) 形态。
        **不保证学生写对**——只表示"在尝试焦半径相关内容"。strict 正确性请用
        derive_diagnostician 返回的 matched_step + label=='完全正确'。"""
        low = text.lower().replace(" ", "")
        has_plus_c = ("x+c" in low) or ("(x＋c)" in low)
        has_minus_c = ("x-c" in low) or ("x−c" in low)
        # 也兼容只写了 2 个根号但没展开 (x±c) 的情况
        radical_count = low.count("√") + low.count("sqrt")
        if radical_count >= 2:
            return True, True
        return has_plus_c, has_minus_c

    @staticmethod
    def _wrote_ellipse_equation(text: str) -> bool:
        """【loose 主题启发，仅供 fallback 用】粗略判断"看起来像最终方程"。
        判据：含 x、y、a、'=1'、分数线、平方——只看形态、**不验证正确性**。
        strict 正确性请用 derive_diagnostician 的 FINAL_EQ 比较。"""
        low = text.lower().replace(" ", "")
        has_eq1 = ("=1" in low) or ("＝1" in low)
        has_frac = ("/" in low) or ("frac" in low)
        has_sq = ("²" in low) or ("^2" in low)
        has_xya = ("x" in low and "y" in low and "a" in low)
        return has_eq1 and has_frac and has_sq and has_xya

    # 注：v3.2 删除了 _detect_transpose_sign_error / _detect_correct_transpose /
    # _detect_symbol_concat_error / _normalize_math_text / _e311_step_sign_error /
    # _e311_step_concat_error / _e311_step_correct_transpose ——
    # 这些已被 derive_diagnostician（sympy + canonical + diff 分类器）完全替代，
    # 且在主流程里不再可达。_radius_forms_in / _wrote_ellipse_equation 保留，
    # 仅 fallback 主题启发用（见各自 docstring）。

    # 推进所需的硬性条件已满足时的轮次上限（防卡死）
    _E311_DERIVE_TURN_LIMIT = 14

    def _compose_e311_next_step_guidance(self, dx, DStep) -> str:
        """根据 diagnostician 结论 + strict 状态，合成"对了之后说什么"。
        诊断器只管对错；下一步走哪条路是状态机的责任——本方法在这里实现。
        非完全正确（错误诊断）不附加任何 follow-up，让诊断器原话提问。"""
        if dx is None or DStep is None or not dx.label.startswith("完全正确"):
            return ""
        step = dx.matched_step
        if step == DStep.COLLECT_MF1:
            if self._e311_mf2_correct:
                return ("两个焦半径都齐了 🎯 现在用椭圆定义 "
                        "$|MF_1|+|MF_2|=2a$ 把方程写出来。")
            return "那**另一个** $|MF_2|$ 呢？ $M(x,y)$ 到 $F_2(c,0)$ 的距离怎么写？"
        if step == DStep.COLLECT_MF2:
            if self._e311_mf1_correct:
                return ("两个焦半径都齐了 🎯 现在用椭圆定义 "
                        "$|MF_1|+|MF_2|=2a$ 把方程写出来。")
            return "那**另一个** $|MF_1|$ 呢？ $M(x,y)$ 到 $F_1(-c,0)$ 的距离怎么写？"
        if step == DStep.ORIGINAL_EQ:
            return ("现在开始**化简**：第①步——把**一个根号移到等号另一边**"
                    "让它落单（移项记得**变号**），写出来给我看～")
        if step == DStep.AFTER_TRANSPOSE:
            return ("**第②步**：等号两边同时**平方**，把这个落单的根号消掉。"
                    "注意右边是 $(2a - |MF_2|)^2$，展开时别漏中间的交叉项。"
                    "整理好写给我看～")
        if step == DStep.AFTER_SQUARE1:
            # AFTER_SQUARE1 内三档：
            #   · 根号已孤立 → 引导第④步第二次平方
            #   · 已化简未孤立 → 鼓励"再把 a√r₂ 移到等号另一边" 让 √ 落单
            #   · raw 展开（默认）→ 引导整理
            if dx.label == "完全正确·根号已孤立":
                return ("根号项已经孤立到等号一边了——这就是**第④步第二次平方**的入口！\n\n"
                        "把等号两边再**同时平方**，左边的根号就消掉了。"
                        "右边记得展开 $(a^2 - cx)^2 = a^4 - 2a^2 \\cdot cx + c^2 x^2$，"
                        "中间是 $-2a^2 \\cdot cx$（乘积，别拆成 $-2a^2 + cx$）。"
                        "整理好写给我看～")
            if dx.label == "完全正确·已化简未孤立":
                return ("已经化简得差不多了 ✨ 离「根号孤立」还差**最后一步**——"
                        "把含 $\\sqrt{}$ 的项**移到等号另一边**让它落单：\n\n"
                        "比如把 $cx = a^2 - a\\sqrt{(x-c)^2+y^2}$ 改写成 "
                        "$a\\sqrt{(x-c)^2+y^2} = a^2 - cx$（移项变号）。\n\n"
                        "写好了发我，下一步就可以平方了～")
            return ("**第③步**：整理一下——把含 $\\sqrt{}$ 的项放到等号一边，"
                    "不含根号的项放到另一边；再除以公因子让系数干净（比如除以 4），"
                    "为下一次平方做准备。写好给我看～")
        if step == DStep.AFTER_SQUARE2:
            return ("**第④步**：把同类项收一下——左右展开后，按 $x^2$、$y^2$ 提系数，"
                    "整理成 $(a^2-c^2)x^2 + a^2 y^2 = a^2(a^2-c^2)$ 的样子，"
                    "最后两边除以 $a^2(a^2-c^2)$ 就能得到椭圆的标准方程。")
        # FINAL_EQ：caller 自己接 stage 推进，不需要 follow-up
        return ""

    def _compose_e311_escalated_guidance(self, dx, DStep) -> str:
        """v3.13 B: 连续 ≥3 轮卡在同一档时的"手把手"升级提示。
        直接给出目标式子让学生抄写，避免反复给同一句模糊引导。"""
        if dx is None or DStep is None or not dx.label.startswith("完全正确"):
            return self._compose_e311_next_step_guidance(dx, DStep)
        step = dx.matched_step
        if step in (DStep.COLLECT_MF1, DStep.COLLECT_MF2):
            # 距离公式只写对一个，反复 3 次 → 直接给另一个
            need_mf2 = self._e311_mf1_correct and not self._e311_mf2_correct
            need_mf1 = self._e311_mf2_correct and not self._e311_mf1_correct
            if need_mf2:
                return ("我们直接来 👉 另一个焦半径：$M(x,y)$ 到 $F_2(c, 0)$ 的距离\n\n"
                        "$$|MF_2| = \\sqrt{(x-c)^2 + y^2}$$\n\n"
                        "把这个发给我，两个焦半径就齐了。")
            if need_mf1:
                return ("我们直接来 👉 另一个焦半径：$M(x,y)$ 到 $F_1(-c, 0)$ 的距离\n\n"
                        "$$|MF_1| = \\sqrt{(x+c)^2 + y^2}$$\n\n"
                        "把这个发给我，两个焦半径就齐了。")
            # 两个都对了还卡 → 走原 guidance（提示写定义式）
            return self._compose_e311_next_step_guidance(dx, DStep)
        if step == DStep.ORIGINAL_EQ:
            return ("我们直接来 👉 把刚才的 $\\sqrt{(x+c)^2+y^2} + \\sqrt{(x-c)^2+y^2} = 2a$，"
                    "把 $\\sqrt{(x-c)^2+y^2}$ 移到等号右边（变号）：\n\n"
                    "$$\\sqrt{(x+c)^2+y^2} = 2a - \\sqrt{(x-c)^2+y^2}$$\n\n"
                    "把这个发给我，进入第②步平方。")
        if step == DStep.AFTER_TRANSPOSE:
            return ("我们直接来 👉 两边同时平方，左边的根号消掉：\n\n"
                    "$$(x+c)^2 + y^2 = (2a - \\sqrt{(x-c)^2+y^2})^2$$\n\n"
                    "右边记得展开 $(2a-B)^2 = 4a^2 - 4aB + B^2$（中间项 $-4a \\cdot \\sqrt{(x-c)^2+y^2}$）。"
                    "整理后发给我。")
        if step == DStep.AFTER_SQUARE1:
            if dx.label == "完全正确·已化简未孤立":
                return ("我们直接来 👉 把 $\\sqrt{...}$ 项**移到等号另一边**让它落单：\n\n"
                        "比如现在是 $cx = a^2 - a\\sqrt{(x-c)^2+y^2}$，"
                        "把 $-a\\sqrt{(x-c)^2+y^2}$ 整体移到左边（变成 $+$），"
                        "$cx$ 移到右边（变成 $-$）：\n\n"
                        "$$a\\sqrt{(x-c)^2+y^2} = a^2 - cx$$\n\n"
                        "把这个等式发给我，下一步就是第二次平方。")
            if dx.label == "完全正确·根号已孤立":
                return ("我们直接来 👉 两边再同时平方，最后一个根号消掉：\n\n"
                        "$$a^2[(x-c)^2 + y^2] = (a^2 - cx)^2$$\n\n"
                        "右边展开 $(a^2-cx)^2 = a^4 - 2a^2 cx + c^2 x^2$，整理后发给我。")
            # raw 展开形态卡 3 轮 → 给整理目标
            return ("我们直接来 👉 把左边 $(x+c)^2$ 和右边 $(x-c)^2$ 都展开，"
                    "合并同类项后大部分项消掉，只剩：\n\n"
                    "$$4cx = 4a^2 - 4a\\sqrt{(x-c)^2+y^2}$$\n\n"
                    "两边除以 4：\n\n"
                    "$$cx = a^2 - a\\sqrt{(x-c)^2+y^2}$$\n\n"
                    "把这个化简后的式子发给我。")
        if step == DStep.AFTER_SQUARE2:
            return ("我们直接来 👉 展开整理：\n\n"
                    "$$(a^2-c^2)x^2 + a^2 y^2 = a^2(a^2-c^2)$$\n\n"
                    "两边除以 $a^2(a^2-c^2)$：\n\n"
                    "$$\\dfrac{x^2}{a^2} + \\dfrac{y^2}{a^2-c^2} = 1$$\n\n"
                    "把这个标准方程发给我，例 1 的推导就结束了～")
        # FINAL_EQ / 其它：fall back
        return self._compose_e311_next_step_guidance(dx, DStep)

    def _handle_e311_derive_and_result(self, text: str) -> LessonStep:
        """🧩 标准方程推导。v3 MVP：教学动作协议 + 状态机 advance 裁决。
           - 主路径：调 _llm_action_protocol 拿 JSON（诊断+苏格拉底文本+动画动作+推进建议）
           - advance 裁决：硬条件未满足→否决；满足但轮次超限→强制推进；否则采纳 LLM 建议
           - 协议不可用（无 API / 解析失败）→ 降级到 _handle_e311_derive_fallback 规则行为
           终点 = x²/a²+y²/(a²-c²)=1，**全程不引入 b**。"""
        # ---- v3.2 状态追踪：strict 标志（由 diagnostician 驱动）+ 主题启发（loose） ----
        # strict：表示学生**真的写对了**，仅在 diagnostician 返回"完全正确*"时置 True。
        #         用于 hard_ok 判断、下一步引导分支。
        # loose ：表示学生输入**含有相关字符串**（不保证正确），仅供 fallback 兜底分支用。
        for flag in (
            "_e311_mf1_correct", "_e311_mf2_correct",
            "_e311_wrote_original", "_e311_wrote_transpose",
            "_e311_wrote_square1", "_e311_wrote_square2",  # v3.4：教材 4.5+4.6 / 4.7+4.8
            "_e311_wrote_radical_isolated",  # v3.7：教材 4.6 形态（根号孤立到一边，准备第②次平方）
            "_e311_wrote_final_eq",          # 兼容旧名，作 strict 用
            "_e311_radius_plus", "_e311_radius_minus",  # loose（仅 fallback 用）
        ):
            if not hasattr(self, flag):
                setattr(self, flag, False)
        if not hasattr(self, '_e311_derive_turns'):
            self._e311_derive_turns = 0
        # v3.13 B: 连续 N 轮卡在同一 (step, label) 时升级提示 ── 跟踪 (key, count)
        if not hasattr(self, '_e311_derive_label_streak'):
            self._e311_derive_label_streak = ("", 0)
        self._e311_derive_turns += 1

        # loose 启发（仅供 fallback 用）：学生输入含 (x±c) / 最终方程形态
        p, m = self._radius_forms_in(text)
        if p: self._e311_radius_plus = True
        if m: self._e311_radius_minus = True

        # ---- v3 符号诊断器（sympy）：高置信结构化诊断有最终决策权，先于 LLM 短路 ----
        # 决策原则：
        #   · 能被符号代数高置信判断（diff 结构清晰）→ 规则层最终决策
        #   · 开放性 / 语义性 / 概念性问题 → LLM 负责
        #   · 二者冲突 → 高置信规则优先
        # 完全不调 LLM、不做 LLM 润色 → 不受 LLM 通道波动影响。
        # 引擎细节见 tutor_agent/derive_diagnostician.py（canonical + diff 分类器）。
        try:
            from .derive_diagnostician import diagnose as _sym_diagnose, DeriveStep as _DStep
            dx = _sym_diagnose(text)
        except Exception as _e:
            print(f"[符号诊断] ⚠️ 诊断器异常，跳过：{type(_e).__name__}: {_e}")
            dx = None; _DStep = None

        # 据 diagnostician 结论更新 strict 标志（"真的写对了"才计数）
        if dx is not None and dx.label.startswith("完全正确") and _DStep is not None:
            if dx.matched_step == _DStep.COLLECT_MF1:    self._e311_mf1_correct = True
            elif dx.matched_step == _DStep.COLLECT_MF2:  self._e311_mf2_correct = True
            elif dx.matched_step == _DStep.ORIGINAL_EQ:  self._e311_wrote_original = True
            elif dx.matched_step == _DStep.AFTER_TRANSPOSE: self._e311_wrote_transpose = True
            elif dx.matched_step == _DStep.AFTER_SQUARE1:
                self._e311_wrote_square1 = True
                # "根号已孤立"是 SQUARE1 区间内的细分进度——再置一个细粒度标志
                if dx.label == "完全正确·根号已孤立":
                    self._e311_wrote_radical_isolated = True
            elif dx.matched_step == _DStep.AFTER_SQUARE2: self._e311_wrote_square2 = True
            elif dx.matched_step == _DStep.FINAL_EQ:     self._e311_wrote_final_eq = True

        # 硬条件：strict 标志为准——学生真的写对过其中任何一个推导节点都算
        hard_ok = (
            (self._e311_mf1_correct and self._e311_mf2_correct)
            or self._e311_wrote_original or self._e311_wrote_transpose
            or self._e311_wrote_square1 or self._e311_wrote_radical_isolated
            or self._e311_wrote_square2 or self._e311_wrote_final_eq
        )

        if dx is not None and dx.confidence >= 0.8:
            # v3.13 B: 更新"同 label 连续命中" streak。若学生连续 ≥3 轮停在同一档
            # （step + label 完全相同），切换到"手把手"升级提示，给目标式子。
            label_key = f"{dx.matched_step.value if dx.matched_step else ''}|{dx.label}"
            prev_key, prev_count = self._e311_derive_label_streak
            new_count = prev_count + 1 if label_key == prev_key else 1
            self._e311_derive_label_streak = (label_key, new_count)
            print(f"[符号诊断] ✅ {dx.label}（step={dx.matched_step.value if dx.matched_step else '-'}, "
                  f"conf={dx.confidence}），轮 {self._e311_derive_turns}，"
                  f"同档连击 {new_count}，跳过 LLM。")
            # 合成"对了之后说什么"：根据 dx.matched_step + strict 状态 + 连击次数
            if new_count >= 3:
                follow_up = self._compose_e311_escalated_guidance(dx, _DStep)
            else:
                follow_up = self._compose_e311_next_step_guidance(dx, _DStep)
            full_msg = dx.message + (("\n\n" + follow_up) if follow_up else "")
            # 通用原则：**标准方程代数推导阶段内部不再发新的 canvas_action**。
            # 进入该 stage 时由 _STAGE_MANDATORY_VIZ 发一次几何参考图，stage 内部
            # 所有诊断 / follow-up 都不刷新 viz——代数化简无需在图上纠错。
            # 这条原则适用于椭圆 / 双曲线 / 抛物线的标准方程推导阶段。
            # 例外：dx 自己**主动**给了 viz_action（v3 viz_action 引擎接入后才会触发），
            # 那是个性化高亮，应当 emit。
            # advance：仅 FINAL_EQ 且 strict 命中 → 推进到 REFLECT_GEOM（**新 stage 入口**）
            if (_DStep is not None and dx.matched_step == _DStep.FINAL_EQ
                    and dx.label == "完全正确" and self._e311_wrote_final_eq):
                self.stage = LessonStage.E311_REFLECT_GEOM_YAXIS
                geom_viz = E311_MANDATORY_VIZ.get(LessonStage.E311_REFLECT_GEOM_YAXIS)
                return LessonStep(
                    stage=self.stage.value,
                    message=full_msg + "\n\n" + E311_REFLECT_GEOM_MSG,
                    canvas_action=geom_viz,  # 新 stage 入口的 viz 正常发
                )
            # DERIVE stage 内部 → 不发 canvas_action（保持已有画面）
            return LessonStep(
                stage=self.stage.value,
                message=full_msg,
                canvas_action=dx.canvas_action,  # dx 主动给了才发，否则 None
            )

        # ---- 主路径：教学动作协议（开放性 / 语义性 / 概念性问题交给 LLM 诊断）----
        context_note = (
            f"已确认写对 |MF₁|：{self._e311_mf1_correct}；"
            f"已确认写对 |MF₂|：{self._e311_mf2_correct}；"
            f"已确认写对原方程：{self._e311_wrote_original}；"
            f"已确认写对正确移项：{self._e311_wrote_transpose}；"
            f"已确认写对最终方程：{self._e311_wrote_final_eq}；"
            f"本阶段已对话 {self._e311_derive_turns} 轮。"
        )
        protocol = self._llm_action_protocol(text, context_note=context_note)

        if protocol is not None:
            socratic_text = (protocol.get("socratic_text") or "").strip() or "我们继续一步步推导吧。"
            viz_action = protocol.get("viz_action")
            llm_advance = bool(protocol.get("advance"))

            # ---- 状态机复核 advance（LLM 提议 + 状态机裁决）----
            if self._e311_derive_turns >= self._E311_DERIVE_TURN_LIMIT:
                final_advance = True              # 防卡死：强制推进
            elif not hard_ok:
                final_advance = False             # 硬条件否决
            else:
                final_advance = llm_advance       # 采纳 LLM 建议

            # ---- 构建画布动作：把协议的 viz_action 包成 render_viz_action ----
            canvas = None
            if isinstance(viz_action, dict) and viz_action.get("scene"):
                canvas = {"action": "render_viz_action", "spec": viz_action}

            if final_advance:
                self.stage = LessonStage.E311_REFLECT_GEOM_YAXIS
                geom_viz = E311_MANDATORY_VIZ.get(LessonStage.E311_REFLECT_GEOM_YAXIS)
                msg = socratic_text + "\n\n" + E311_REFLECT_GEOM_MSG
                return LessonStep(stage=self.stage.value, message=msg, canvas_action=geom_viz)
            return LessonStep(stage=self.stage.value, message=socratic_text, canvas_action=canvas)

        # ---- 降级路径：协议不可用 → 规则行为 ----
        return self._handle_e311_derive_fallback(text, hard_ok)

    def _handle_e311_derive_fallback(self, text: str, hard_ok: bool) -> LessonStep:
        """协议不可用（无 API / JSON 解析失败）时的降级。
        v3.4 起按 **strict 标志倒推**判进度，**永远不回退到更早的子步**。
        诊断器没命中、LLM 又挂了时只剩"给个通用方向引导"作为兜底；
        但兜底引导必须贴当前 substep，不能让学生退回去重做之前已写对的步骤。

        v3.6：DERIVE stage 内部所有分支 canvas_action 都为 None ——
        进入 DERIVE 阶段时由 _STAGE_MANDATORY_VIZ 发一次几何参考图，
        stage 内部所有诊断/兜底都不刷新画板（代数化简不需要在图上纠错）。"""
        # 推进条件：写出最终方程，或轮次兜底（防卡死）
        if self._e311_wrote_final_eq or self._e311_derive_turns >= self._E311_DERIVE_TURN_LIMIT:
            self.stage = LessonStage.E311_REFLECT_GEOM_YAXIS
            geom_viz = E311_MANDATORY_VIZ.get(LessonStage.E311_REFLECT_GEOM_YAXIS)
            return LessonStep(
                stage=self.stage.value,
                message=E311_DERIVE_RESULT_MSG + "\n\n" + E311_REFLECT_GEOM_MSG,
                canvas_action=geom_viz,  # 新 stage 入口的 viz 正常发
            )

        # ─── 按 strict 标志倒推：从最远进度往回挑当前子步，**绝不回退** ───
        # 注：所有分支 canvas_action 都不发（None）—— DERIVE 内只一张图。
        if self._e311_wrote_square2:
            msg = (
                "你已经做完两次平方了 👍 现在把同类项收一下：按 $x^2$、$y^2$ 提系数，"
                "整理成 $(a^2-c^2)x^2 + a^2 y^2 = a^2(a^2-c^2)$ 的样子，"
                "最后两边除以 $a^2(a^2-c^2)$ 就能得到椭圆的标准方程。"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_wrote_radical_isolated:
            msg = (
                "你已经把根号项孤立到等号一边了 ✅ 现在**第④步**：两边再同时**平方**，"
                "左边的根号就彻底消掉。右边记得展开 $(a^2 - cx)^2$，"
                "中间是乘积 $-2a^2 \\cdot cx$（不是 $-2a^2 + cx$）。整理好写给我看～"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_wrote_square1:
            msg = (
                "第①次平方做对了 ✅ 现在整理一下——把含 $\\sqrt{}$ 的项放到等号一边，"
                "不含根号的项放到另一边；除以公因子（如 4）让系数干净，再做第②次平方。"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_wrote_transpose:
            msg = (
                "你已经把一个根号移到等号一边了 ✅ 现在**第②步**：等号两边同时平方，"
                "把这个落单的根号消掉。注意右边 $(2a-|MF_2|)^2$ 展开时别漏中间的交叉项 "
                "$-4a\\cdot|MF_2|$（是乘积，不是 $-4a+|MF_2|$ 两个独立项）。"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_wrote_original:
            msg = (
                "原方程已经写出来了 ✅ 开始**化简**：第①步——把**一个根号移到等号另一边**"
                "让它落单（**移项记得变号**），写出来给我看～"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_mf1_correct and self._e311_mf2_correct:
            msg = (
                "两个焦半径都齐了 🎯 现在用椭圆定义 $|MF_1|+|MF_2|=2a$ 把方程写出来。"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        if self._e311_mf1_correct or self._e311_mf2_correct:
            # 只一个写对：追问另一个（用 strict 标志，不被 loose 字符串干扰）
            missing = "|MF_2|" if self._e311_mf1_correct else "|MF_1|"
            focus = "F_2(c,0)" if self._e311_mf1_correct else "F_1(-c,0)"
            msg = (
                f"已经写对一个 ✅ 那**另一个** ${missing}$ 呢？\n"
                f"提示：$M(x,y)$ 到 ${focus}$ 的距离，套距离公式 "
                "$d=\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}$ 写出来。"
            )
            return LessonStep(stage=self.stage.value, message=msg)
        # 都还没写对——给最初的距离公式提示
        msg = (
            "先用**距离公式**写出 $|MF_1|$：$F_1(-c,0)$、$M(x,y)$，\n"
            "$|MF_1|=\\sqrt{(x_2-x_1)^2+(y_2-y_1)^2}=?$"
        )
        return LessonStep(stage=self.stage.value, message=msg)

    def _handle_e311_reflect_geom_yaxis(self, text: str) -> LessonStep:
        """🟣 几何观察 → 定义 b → 思考3。v2.4：严格教材顺序，分两个子环节。
           find_segments（思考2 找线段）→ 学生发现 √(a²-c²)=|PO| → 定义 b
           → yaxis（思考3 y 轴形式）→ 推进到例 1。"""
        if not hasattr(self, '_e311_geom_phase'):
            self._e311_geom_phase = "find_segments"
        if not hasattr(self, '_e311_geom_turns'):
            self._e311_geom_turns = 0
        self._e311_geom_turns += 1
        phase = self._e311_geom_phase

        # ===== 子环节 1：思考2 —— 在图上找 a / c / √(a²-c²) 的线段 =====
        if phase == "find_segments":
            found = (
                _looks_like_geom_insight(text)
                or any(kw in text for kw in ["PO", "po", "OP", "短轴", "短半轴", "勾股", "|OP|", "|PO|"])
            )
            if found or self._e311_geom_turns >= 4:
                # 学生发现 √(a²-c²) 就是 |PO| 这条线段 → 这时才定义 b，再进入思考3
                self._e311_geom_phase = "yaxis"
                reply = self._llm_respond(
                    text,
                    fallback=E311_DEFINE_B_MSG + "\n\n" + E311_REFLECT_YAXIS_MSG,
                )
                # v3.14 #2：从 find_segments 子环节推进到 yaxis 时，发图3.1-3 完成版
                # （此时学生已经答出"|OP|=√(a²-c²)"等关系，可以揭晓答案标注）
                solved_viz = {"action": "show_e311_abc_triangle_solved"}
                return LessonStep(stage=self.stage.value, message=reply,
                                  canvas_action=solved_viz)
            # 还没找到 → 引导（不提 b）
            fallback = (
                "提示：看椭圆**短轴的端点** $P$（在 $y$ 轴上那个点）。\n"
                "$P$ 到两个焦点 $F_1$、$F_2$ 的距离各是多少？$P$ 到原点 $O$ 的距离 $|PO|$ 又是多少？\n"
                "（在直角三角形 $OPF_1$ 里用勾股定理算算 $|PO|$）"
            )
            reply = self._llm_respond(text, fallback=fallback)
            return LessonStep(stage=self.stage.value, message=reply)

        # ===== 子环节 2：思考3 —— y 轴形式 =====
        # phase == "yaxis"
        # 修复：÷ 归一化为 /，让"字母通式 + ÷"（如 y²÷a²+x²÷b²=1）也能命中下面的关键词推进
        low = text.replace(" ", "").replace("÷", "/").replace("／", "/")
        # v3.15 + v3.21：学生主动请求 viz 时（"画一个 y 轴椭圆"/"对比一下两种"），
        # 不要因为含"y轴/对比"等词就误认为"宣告理解 → 推进"。viz 路由后处理负责。
        is_viz_request = self._e311_is_viz_intent(text)
        got_yaxis = (
            # 1) 关键词字面命中（学生用 y²/a² 等通用符号回答）——但请求 viz 时不算
            (not is_viz_request and any(kw in low for kw in
                ["y²/a²", "y^2/a^2", "y轴", "y²/a", "y^2/a"]))
            # 2) sympy 结构匹配：学生写**具体方程**（如 y²/9 + x²/4 = 1）—— 强证据，不被 viz 请求拦截
            or _looks_like_yaxis_ellipse_eq(text)
            # 3) 学生主动表示懂了——请求 viz 时不算（"我想看图懂了"主要是想看图）
            or (not is_viz_request and _looks_like_understood(text))
            # 4) 防卡死：轮次兜底（无视 viz 请求，强推）
            or self._e311_geom_turns >= 7
        )
        if got_yaxis:
            self.stage = LessonStage.E311_EXAMPLE_1
            viz = E311_MANDATORY_VIZ.get(LessonStage.E311_EXAMPLE_1)
            reply = self._llm_respond(text, fallback=E311_EXAMPLE_1_INTRO)
            return LessonStep(stage=self.stage.value, message=reply, canvas_action=viz)
        fallback = (
            "焦点在 $y$ 轴上时，$F_1(0,-c)$、$F_2(0,c)$。\n"
            "把刚才推导里的 $x$ 和 $y$ 互换，方程会变成什么？试试看。"
        )
        reply = self._llm_respond(text, fallback=fallback)
        return LessonStep(stage=self.stage.value, message=reply)

    def _handle_e311_example(self, text: str, example_num: int) -> LessonStep:
        """🟡 例 1/2/3：sympy 诊断器 + 状态机 + LLM 兜底。

        v3.9：引入 example_diagnostician 数值/方程 canonical 比对——
          · 学生答任一 canonical goal（PF1/PF2/2a/a/b/equation 等）→ 命中 +
            置 sub_flag + 精准 ack + 引导下一步
          · 整道题做完（equation 命中 或 a_done AND b_done）→ 推进到下一阶段
          · 诊断器未命中 → 走原 LLM/understands 逻辑兜底
          · 跳步直答（如 2a / 标准方程）→ shortcut 推进
        """
        if not hasattr(self, '_e311_example_turns'):
            self._e311_example_turns = {1: 0, 2: 0, 3: 0}
        if not hasattr(self, '_e311_example_subflags'):
            self._e311_example_subflags = {1: set(), 2: set(), 3: set()}
        self._e311_example_turns[example_num] += 1

        # ---- v3.9：sympy 诊断器（数值/方程比对）----
        try:
            from .example_diagnostician import diagnose_example
            from .example_canonicals import EXAMPLE_CONFIGS
            dx = diagnose_example(text, example_num)
        except Exception as _e:
            print(f"[例题诊断] ⚠️ 异常：{type(_e).__name__}: {_e}")
            dx = None

        if dx is not None and dx.label == "完全正确":
            # 命中 goal → 累积 sub_flag
            sub_flags = self._e311_example_subflags[example_num]
            new_flags = dx.implied_flags - sub_flags
            sub_flags |= dx.implied_flags
            print(f"[例题诊断] ✅ 例 {example_num} 命中 goals={dx.hit_goals}, "
                  f"新增 sub_flags={sorted(new_flags)}, 总 sub_flags={sorted(sub_flags)}")
            # 整道题做完 → 推进
            done_fn = EXAMPLE_CONFIGS[example_num].get("done_fn")
            if done_fn and done_fn(sub_flags):
                ack = self._compose_e311_example_ack(example_num, dx, full_done=True)
                return self._advance_e311_example(example_num, ack)
            # 没全做完 → 精准 ack + 引导下一步
            msg = self._compose_e311_example_ack(example_num, dx, full_done=False)
            return LessonStep(stage=self.stage.value, message=msg)

        # ---- 兜底：原 LLM/understands 逻辑 ----
        understands = _looks_like_understood(text) or self._e311_example_turns[example_num] >= 5

        if not understands:
            # 仍在 4 步循环中，LLM 引导
            fallback_map = {
                1: "回到例 1：焦点 (±2, 0) 在 x 轴 → 设 $\\dfrac{x^2}{a^2}+\\dfrac{y^2}{b^2}=1$。\n"
                   "由椭圆定义直接算 $2a = |PF_1| + |PF_2|$，过点 $(\\frac{5}{2}, -\\frac{3}{2})$ 代入计算 $a$。\n"
                   "你能算出 $2a$ 等于多少吗？",
                2: "回到例 2：$M$ 是 $PD$ 的中点 → $x = x_0,\\ y = \\dfrac{y_0}{2}$，\n"
                   "现在我们知道 $P(x_0, y_0)$ 在圆 $x^2+y^2=4$ 上，怎么消去 $x_0, y_0$？",
                3: "回到例 3：$k_{AM} = \\dfrac{y}{x+5}$，$k_{BM} = \\dfrac{y}{x-5}$。\n"
                   "代入 $k_{AM} \\cdot k_{BM} = -\\dfrac{4}{9}$，化简后是什么形式？",
            }
            fallback = fallback_map[example_num]
            reply = self._llm_respond(text, fallback=fallback)
            return LessonStep(stage=self.stage.value, message=reply)

        # 推进到下一阶段（understands 兜底：学生说"我懂了"或轮次超限）
        # ──────────────────────────────────────────────────────────────
        # v3.10 修复：跨例题状态的"完成话术"必须 deterministic，不能让 LLM 改写。
        # 之前走 _llm_respond 时，LLM 有时会幻觉（比如例 1 → 例 2 推进时
        # LLM 编出例 3 的题目）。改用 _advance_e311_example("") 共用同一份
        # E311_EXAMPLE_N_DONE_BODY 文案，跟诊断器命中路径完全等价。
        return self._advance_e311_example(example_num, "")

    def _compose_e311_example_ack(self, example_num: int, dx, full_done: bool) -> str:
        """根据诊断器命中结果生成精准 ack + 下一步引导。
        子步顺序：
          · 例 1：PF1 → PF2 → 2a → a → b → equation
          · 例 2：mid_x、mid_y → equation
          · 例 3：k_AM、k_BM → slope_product → equation
        允许跳步（命中 2a 直接跳过 PF1/PF2 的引导；命中 equation 直接 done）。"""
        primary = dx.matched_canonical
        # 头部：根据主命中 goal 给精准 ack（按例题分头部表）
        ack_head_table = {
            1: {
                "PF1":        "$|PF_1|$ 算对了 ✅",
                "PF2":        "$|PF_2|$ 算对了 ✅",
                "2a":         "$2a$ 算对了 ✅",
                "a":          "$a$ 算对了 ✅",
                "a_squared":  "$a^2$ 算对了 ✅",
                "c":          "$c$ 也对 ✅",
                "c_squared":  "$c^2$ 也对 ✅",
                "b":          "$b$ 算对了 ✅",
                "b_squared":  "$b^2$ 算对了 ✅",
                "equation":   "椭圆方程出来了 🎉",
            },
            2: {
                "mid_x":      "$x = x_0$ 对了 ✅",
                "mid_y":      "$y = \\dfrac{y_0}{2}$（即 $y_0 = 2y$）对了 ✅",
                "equation":   "$M$ 的轨迹方程出来了 🎉",
            },
            3: {
                "k_AM":           "$k_{AM} = \\dfrac{y}{x+5}$ 对了 ✅",
                "k_BM":           "$k_{BM} = \\dfrac{y}{x-5}$ 对了 ✅",
                "slope_product":  "斜率乘积代入对了 ✅",
                "equation":       "$M$ 的轨迹方程出来了 🎉",
            },
        }
        ack_head = ack_head_table.get(example_num, {}).get(primary, "对了 ✅")
        if full_done:
            return ack_head  # 推进时不需要 follow-up，外层加 EXAMPLE_N_INTRO 等

        sub_flags = self._e311_example_subflags[example_num]

        # ─── 例 1 follow-up（保留原逻辑）───
        if example_num == 1:
            if "a_done" not in sub_flags:
                if "two_a_done" in sub_flags:
                    follow = "\n\n接下来 $a$ 等于多少？（提示 $2a$ 除以 2）"
                elif "pf1_done" in sub_flags and "pf2_done" in sub_flags:
                    follow = "\n\n接下来用椭圆定义 $2a = |PF_1| + |PF_2|$,两个加起来等于多少?"
                elif "pf1_done" in sub_flags:
                    follow = "\n\n接下来算 $|PF_2|$($F_2(2,0)$ 到点 $P$ 的距离)。"
                elif "pf2_done" in sub_flags:
                    follow = "\n\n接下来算 $|PF_1|$($F_1(-2,0)$ 到点 $P$ 的距离)。"
                else:
                    follow = "\n\n先用距离公式算 $|PF_1|$($F_1(-2,0)$ 到 $P$ 的距离)。"
            elif "b_done" not in sub_flags:
                follow = "\n\n现在 $a = \\sqrt{10}$、$c = 2$。由 $b^2 = a^2 - c^2$ 算 $b$。"
            else:
                follow = ("\n\n现在 $a^2 = 10$、$b^2 = 6$,焦点在 $x$ 轴上 → 椭圆标准方程是"
                          "$\\dfrac{x^2}{a^2} + \\dfrac{y^2}{b^2} = 1$。代入写出来给我看~")
            return ack_head + follow
        # NOTE: 上面例 1 的话术与改造前一致（这里 ASCII/中文混排都不影响 ack 内含的 LaTeX 与 sub_flag 推进）

        # ─── 例 2 follow-up ───
        if example_num == 2:
            if "mid_x_done" not in sub_flags and "mid_y_done" not in sub_flags:
                follow = ("\n\n接下来用 $M$ 是 $PD$ 中点的关系，"
                          "把 $x_0$、$y_0$ 用 $x$、$y$ 表示出来：$x_0 = ?$，$y_0 = ?$")
            elif "mid_y_done" not in sub_flags:
                follow = "\n\n再写 $y$ 与 $y_0$ 的关系（$M$ 是 $PD$ 的中点，$D$ 在 $x$ 轴上）。"
            elif "mid_x_done" not in sub_flags:
                follow = "\n\n再写 $x$ 与 $x_0$ 的关系（$PD \\perp x$ 轴 ⇒ $D$、$P$、$M$ 横坐标相同）。"
            else:
                follow = ("\n\n现在把 $x_0 = x$、$y_0 = 2y$ 代入圆 $x_0^2 + y_0^2 = 4$，"
                          "化简成 $M$ 的轨迹方程给我看~")
            return ack_head + follow

        # ─── 例 3 follow-up ───
        if example_num == 3:
            if "k_am_done" not in sub_flags and "k_bm_done" not in sub_flags:
                follow = ("\n\n先把两条斜率写出来："
                          "$k_{AM} = \\dfrac{y - 0}{x - (-5)}$、$k_{BM} = \\dfrac{y - 0}{x - 5}$。")
            elif "k_bm_done" not in sub_flags:
                follow = "\n\n再写 $k_{BM}$（$B(5,0)$ 到 $M(x, y)$ 的斜率）。"
            elif "k_am_done" not in sub_flags:
                follow = "\n\n再写 $k_{AM}$（$A(-5, 0)$ 到 $M(x, y)$ 的斜率）。"
            elif "slope_product_done" not in sub_flags:
                follow = ("\n\n把 $k_{AM}$、$k_{BM}$ 代入 $k_{AM} \\cdot k_{BM} = -\\dfrac{4}{9}$，"
                          "写出代入后的方程。")
            else:
                follow = "\n\n现在化简代入后的方程，整理成 $M$ 的轨迹标准方程。"
            return ack_head + follow

        return ack_head

    def _advance_e311_example(self, example_num: int, ack: str) -> LessonStep:
        """例题完整做完后推进到下一阶段。ack 是诊断器的精准 ack 消息（前缀）。

        A3 重构：文案体复用模块常量 E311_EXAMPLE_N_DONE_BODY（与 understands 兜底
        路径同源），改文案只在一处改。

        v3.11 viz 拆分：推进时发两个 canvas_action：
          · 上一例的 solved（完成版，展示推导和答案，作为犒赏）
          · 下一例的 setup（题目版，铺台子让学生开始下一题，不剧透）
        前端按数组顺序渲染，viz 历史画廊里两条相邻，自然成线。
        例 3 推进到 SUMMARY 只发 example_3_solved（SUMMARY 无 setup）。
        """
        body_table = {
            1: (LessonStage.E311_EXAMPLE_2, E311_EXAMPLE_1_DONE_BODY),
            2: (LessonStage.E311_EXAMPLE_3, E311_EXAMPLE_2_DONE_BODY),
            3: (LessonStage.E311_SUMMARY,   E311_EXAMPLE_3_DONE_BODY),
        }
        next_stage, body = body_table[example_num]
        self.stage = next_stage
        msg = (ack + "\n\n" if ack else "") + body
        # 上一例的 solved viz（完成版犒赏）—— 三例都发
        solved_viz = {"action": f"show_e311_example_{example_num}_solved"}
        if example_num == 3:
            # 例 3 → SUMMARY：追加知识图谱 footer；只发 solved（SUMMARY 无 example setup）
            msg += self._kg_footer(
                self.course_config["summary_kg_nodes"],
                heading="\n📚 本节对应教材知识点",
            )
            return LessonStep(stage=self.stage.value, message=msg, canvas_action=solved_viz)
        # 例 1/2：发上一例 solved + 下一例 setup（数组）
        setup_viz = E311_MANDATORY_VIZ.get(next_stage)
        return LessonStep(stage=self.stage.value, message=msg,
                          canvas_action=[solved_viz, setup_viz])

    def _handle_e311_summary(self, text: str) -> LessonStep:
        """📒 3.1.1 总结阶段。复用通用 _handle_summary 的结课检测逻辑。"""
        self.summary_turns += 1
        if _looks_like_lesson_end(text) or self.summary_turns >= 6:
            self.lesson_ended = True
            fallback = (
                "👏 恭喜完成 3.1.1 课程！\n\n"
                "下次见 — 我们将一起探究 3.1.2「椭圆的简单几何性质」，"
                "重点研究椭圆的范围、对称性、顶点和**离心率**。\n\n"
                "[LESSON_END]"
            )
            reply = self._llm_respond(text, fallback=fallback)
            return LessonStep(stage=self.stage.value, message=reply)
        # 学生还有问题 → LLM 基于知识图谱回答
        reply = self._llm_respond(text, fallback="还有什么问题想问？或者输入「结束」结课。")
        return LessonStep(stage=self.stage.value, message=reply)
