"""
圆锥曲线知识图谱解析器

本模块将Markdown知识图谱解析为结构化数据，并生成Neo4j Cypher语句。
知识图谱涵盖椭圆、双曲线、抛物线的定义、标准方程、几何性质和易错点。

数据结构：
- KnowledgeNode：知识节点，包含id、name、category、content等
- 关系类型：PREREQUISITE（前置条件）、CONTAINS（包含）、COMPARES_WITH（对比）、COMMON_ERROR（易错点）
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum


class NodeCategory(str, Enum):
    """知识节点分类"""
    DEFINITION = "定义"          # 定义
    STANDARD_EQUATION = "标准方程"   # 标准方程
    FORMULA = "公式"            # 公式
    PROPERTY = "性质"           # 几何性质
    PARAMETER = "参数"          # 参数关系
    COMPARISON = "对比"         # 横向对比
    ERROR_PRONE = "易错点"       # 易错点
    CONCEPT = "概念"            # 基础概念
    # ---- 教材结构性节点（v2 新增，对齐人教A版正文栏目）----
    EXPLORATION = "探究"         # 教材"探究"框（如绳画法、两圆相交画双曲线等）
    REFLECTION = "思考"          # 教材"思考"框（启发式提问）
    OBSERVATION = "观察"         # 教材"观察"框
    EXAMPLE = "例题"             # 教材"例 N"（含题目、分析、解答、关联知识点）


class RelationType(str, Enum):
    """关系类型"""
    PREREQUISITE = "PREREQUISITE"      # A是B的前置条件
    CONTAINS = "CONTAINS"              # 父节点包含子节点
    COMPARES_WITH = "COMPARES_WITH"    # 与其他概念对比
    COMMON_ERROR = "COMMON_ERROR"      # 链接到易错点
    SPECIALIZED_BY = "SPECIALIZED_BY"  # 通过...特化
    # ---- 教材结构性关系（v2 新增）----
    EXPLORES = "EXPLORES"              # 探究/思考/观察 引出/巩固 某知识点
    APPLIES = "APPLIES"                # 例题应用某知识点


@dataclass
class KnowledgeNode:
    """知识节点"""
    id: str                              # 唯一标识
    name: str                            # 节点名称
    category: NodeCategory               # 分类
    content: str                         # 主要内容
    params: Dict[str, Any] = field(default_factory=dict)  # 数学参数
    prerequisites: List[str] = field(default_factory=list)  # 前置节点id列表
    description: str = ""               # 详细描述
    examples: List[str] = field(default_factory=list)  # 示例


@dataclass
class Relationship:
    """知识关系"""
    source_id: str          # 源节点id
    target_id: str          # 目标节点id
    type: RelationType      # 关系类型
    label: str = ""         # 关系标签（可选）


class ConicKnowledgeGraph:
    """圆锥曲线知识图谱

    包含所有椭圆、双曲线、抛物线的知识节点和关系
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relationships: List[Relationship] = []
        self._initialize_knowledge_graph()

    def _initialize_knowledge_graph(self):
        """初始化整个知识图谱"""
        self._add_foundation_concepts()
        self._add_ellipse_knowledge()
        self._add_hyperbola_knowledge()
        self._add_parabola_knowledge()
        self._add_unified_definition()
        self._add_comparisons()
        self._add_common_errors()
        # ---- 教材结构性节点（v2，按节追加，先做 3.1.1）----
        self._add_section_311_content()

    def _add_foundation_concepts(self):
        """添加基础概念节点"""
        concepts = [
            KnowledgeNode(
                id="foundation_coordinate_system",
                name="坐标系 Oxy",
                category=NodeCategory.CONCEPT,
                content="直角坐标系，两条互相垂直的轴组成",
                description="圆锥曲线的标准方程均在直角坐标系中建立"
            ),
            KnowledgeNode(
                id="foundation_distance_formula",
                name="距离公式",
                category=NodeCategory.FORMULA,
                content="两点间距离公式：d = √[(x₂-x₁)² + (y₂-y₁)²]",
                description="用于推导圆锥曲线的定义"
            ),
            KnowledgeNode(
                id="foundation_locus",
                name="集合与轨迹",
                category=NodeCategory.CONCEPT,
                content="轨迹是满足特定条件的点的集合",
                description="圆锥曲线都是通过轨迹定义得到的"
            ),
        ]
        for node in concepts:
            self.nodes[node.id] = node

    def _add_ellipse_knowledge(self):
        """添加椭圆相关知识"""
        nodes = [
            # 椭圆定义
            KnowledgeNode(
                id="ellipse_definition",
                name="椭圆定义",
                category=NodeCategory.DEFINITION,
                content="平面内到两定点F₁、F₂距离之和为常数2a（2a > |F₁F₂|）的点的轨迹",
                description="椭圆的集合定义基于焦点和距离之和",
                examples=["绳长固定，两端钉在焦点，笔尖绷紧绳子画出的曲线"],
                prerequisites=["foundation_distance_formula", "foundation_locus"],
                params={"constraint": "2a > |F₁F₂|", "a_gt_c": True}
            ),
            # 椭圆参数关系
            KnowledgeNode(
                id="ellipse_parameter_triangle",
                name="椭圆参数三角形关系",
                category=NodeCategory.PARAMETER,
                content="a² = b² + c²，其中a > c > 0，b² = a² - c²，a > b > 0",
                description="椭圆中a是最大的，c是焦距一半，b是短半轴",
                prerequisites=["ellipse_definition"],
                params={
                    "formula": "a² = b² + c²",
                    "constraints": ["a > b > 0", "a > c > 0"]
                }
            ),
            # 椭圆标准方程（x轴）
            KnowledgeNode(
                id="ellipse_standard_equation_x",
                name="椭圆标准方程（焦点在x轴）",
                category=NodeCategory.STANDARD_EQUATION,
                content="x²/a² + y²/b² = 1，其中a > b > 0",
                description="焦点在x轴时的标准方程",
                prerequisites=["ellipse_definition"],
                params={
                    "equation": "x²/a² + y²/b² = 1",
                    "foci": "F₁(-c, 0), F₂(c, 0)",
                    "focal_distance": "2c",
                    "relation": "b² = a² - c²"
                }
            ),
            # 椭圆标准方程（y轴）
            KnowledgeNode(
                id="ellipse_standard_equation_y",
                name="椭圆标准方程（焦点在y轴）",
                category=NodeCategory.STANDARD_EQUATION,
                content="x²/b² + y²/a² = 1，其中a > b > 0",
                description="焦点在y轴时的标准方程",
                prerequisites=["ellipse_definition"],
                params={
                    "equation": "x²/b² + y²/a² = 1",
                    "foci": "F₁(0, -c), F₂(0, c)",
                    "focal_distance": "2c"
                }
            ),
            # 椭圆范围
            KnowledgeNode(
                id="ellipse_range",
                name="椭圆范围",
                category=NodeCategory.PROPERTY,
                content="-a ≤ x ≤ a，-b ≤ y ≤ b",
                description="椭圆是封闭曲线，有确定的范围",
                prerequisites=["ellipse_standard_equation_x"],
            ),
            # 椭圆对称性
            KnowledgeNode(
                id="ellipse_symmetry",
                name="椭圆对称性",
                category=NodeCategory.PROPERTY,
                content="关于x轴、y轴和原点均对称，原点为对称中心",
                description="椭圆具有三重对称性",
                prerequisites=["ellipse_standard_equation_x"],
            ),
            # 椭圆顶点
            KnowledgeNode(
                id="ellipse_vertices",
                name="椭圆顶点",
                category=NodeCategory.PROPERTY,
                content="长轴顶点A₁(-a,0)、A₂(a,0)，短轴顶点B₁(0,-b)、B₂(0,b)",
                description="长轴长2a，短轴长2b",
                prerequisites=["ellipse_standard_equation_x"],
                params={
                    "major_axis_length": "2a",
                    "minor_axis_length": "2b",
                    "major_vertices": "[(-a,0), (a,0)]",
                    "minor_vertices": "[(0,-b), (0,b)]"
                }
            ),
            # 椭圆离心率
            KnowledgeNode(
                id="ellipse_eccentricity",
                name="椭圆离心率",
                category=NodeCategory.PROPERTY,
                content="e = c/a，0 < e < 1",
                description="离心率刻画椭圆的扁平程度。e→0时趋近圆，e→1时越来越扁",
                prerequisites=["ellipse_parameter_triangle"],
                params={
                    "formula": "e = c/a",
                    "range": "(0, 1)",
                    "interpretation": "e接近0→接近圆；e接近1→越来越扁"
                }
            ),
            # 椭圆准线
            KnowledgeNode(
                id="ellipse_directrix",
                name="椭圆准线",
                category=NodeCategory.PROPERTY,
                content="x = ±a²/c = ±a/e",
                description="由焦点-准线统一定义推出：椭圆上任意一点到焦点的距离与到对应准线的距离之比为常数e（0<e<1）。每个焦点对应一条准线",
                prerequisites=["ellipse_eccentricity"],
                params={
                    "formula": "x = ±a²/c = ±a/e",
                    "count": 2
                }
            ),
        ]
        for node in nodes:
            self.nodes[node.id] = node

        # 添加椭圆内部关系
        self._add_relationship("ellipse_definition", "ellipse_parameter_triangle", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_definition", "ellipse_standard_equation_x", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_standard_equation_x", "ellipse_standard_equation_y", RelationType.CONTAINS)
        self._add_relationship("ellipse_standard_equation_x", "ellipse_range", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_standard_equation_x", "ellipse_symmetry", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_standard_equation_x", "ellipse_vertices", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_parameter_triangle", "ellipse_eccentricity", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_eccentricity", "ellipse_directrix", RelationType.PREREQUISITE)

    def _add_hyperbola_knowledge(self):
        """添加双曲线相关知识"""
        nodes = [
            # 双曲线定义
            KnowledgeNode(
                id="hyperbola_definition",
                name="双曲线定义",
                category=NodeCategory.DEFINITION,
                content="平面内到两定点F₁、F₂距离之差的绝对值为常数2a（0 < 2a < |F₁F₂|）的点的轨迹",
                description="与椭圆不同：椭圆是距离之和，双曲线是距离之差的绝对值",
                prerequisites=["foundation_distance_formula", "foundation_locus"],
                params={"constraint": "0 < 2a < |F₁F₂|", "c_gt_a": True}
            ),
            # 双曲线参数关系
            KnowledgeNode(
                id="hyperbola_parameter_triangle",
                name="双曲线参数三角形关系",
                category=NodeCategory.PARAMETER,
                content="c² = a² + b²，其中c > a > 0，b > 0",
                description="双曲线中c是最大的，与椭圆相反！",
                prerequisites=["hyperbola_definition"],
                params={
                    "formula": "c² = a² + b²",
                    "constraints": ["c > a > 0", "b > 0"],
                    "equilateral": "等轴双曲线：a = b → c = √2·a"
                }
            ),
            # 双曲线标准方程（x轴）
            KnowledgeNode(
                id="hyperbola_standard_equation_x",
                name="双曲线标准方程（焦点在x轴）",
                category=NodeCategory.STANDARD_EQUATION,
                content="x²/a² - y²/b² = 1，其中a > 0, b > 0",
                description="焦点在x轴时的标准方程，注意是减号",
                prerequisites=["hyperbola_definition"],
                params={
                    "equation": "x²/a² - y²/b² = 1",
                    "foci": "F₁(-c, 0), F₂(c, 0)",
                    "focal_distance": "2c",
                    "relation": "c² = a² + b²"
                }
            ),
            # 双曲线标准方程（y轴）
            KnowledgeNode(
                id="hyperbola_standard_equation_y",
                name="双曲线标准方程（焦点在y轴）",
                category=NodeCategory.STANDARD_EQUATION,
                content="y²/a² - x²/b² = 1，其中a > 0, b > 0",
                description="焦点在y轴时的标准方程",
                prerequisites=["hyperbola_definition"],
                params={
                    "equation": "y²/a² - x²/b² = 1",
                    "foci": "F₁(0, -c), F₂(0, c)"
                }
            ),
            # 双曲线范围
            KnowledgeNode(
                id="hyperbola_range",
                name="双曲线范围",
                category=NodeCategory.PROPERTY,
                content="x ≤ -a 或 x ≥ a（焦点在x轴时）",
                description="双曲线由两支组成，无-a < x < a的部分",
                prerequisites=["hyperbola_standard_equation_x"],
            ),
            # 双曲线对称性
            KnowledgeNode(
                id="hyperbola_symmetry",
                name="双曲线对称性",
                category=NodeCategory.PROPERTY,
                content="关于x轴、y轴和原点均对称，原点为对称中心",
                description="与椭圆相同的对称性",
                prerequisites=["hyperbola_standard_equation_x"],
            ),
            # 双曲线顶点
            KnowledgeNode(
                id="hyperbola_vertices",
                name="双曲线顶点",
                category=NodeCategory.PROPERTY,
                content="实轴顶点A₁(-a,0)、A₂(a,0)，虚轴端点B₁(0,-b)、B₂(0,b)（不在曲线上）",
                description="实轴长2a，虚轴长2b。注意虚轴端点不是曲线上的点！",
                prerequisites=["hyperbola_standard_equation_x"],
                params={
                    "real_axis_length": "2a",
                    "imaginary_axis_length": "2b",
                    "real_vertices": "[(-a,0), (a,0)]",
                    "imaginary_endpoints": "[(0,-b), (0,b)]",
                    "warning": "虚轴端点不在双曲线上"
                }
            ),
            # 双曲线离心率
            KnowledgeNode(
                id="hyperbola_eccentricity",
                name="双曲线离心率",
                category=NodeCategory.PROPERTY,
                content="e = c/a，e > 1",
                description="离心率>1。e越接近1，双曲线两支越窄（渐近线夹角越小）；e越大，两支越宽（渐近线夹角越大）",
                prerequisites=["hyperbola_parameter_triangle"],
                params={
                    "formula": "e = c/a",
                    "range": "(1, +∞)",
                    "interpretation": "e接近1→两支窄、渐近线夹角小；e越大→两支宽、渐近线夹角大"
                }
            ),
            # 双曲线渐近线
            KnowledgeNode(
                id="hyperbola_asymptote",
                name="双曲线渐近线",
                category=NodeCategory.PROPERTY,
                content="y = ±(b/a)x（焦点在x轴时）",
                description="双曲线特有的性质。渐近线过中心，曲线无限靠近但永不相交",
                prerequisites=["hyperbola_standard_equation_x"],
                params={
                    "formula": "y = ±(b/a)x",
                    "passes_through": "原点",
                    "equilateral_note": "等轴双曲线(a=b)的渐近线为y=±x，互相垂直"
                }
            ),
        ]
        for node in nodes:
            self.nodes[node.id] = node

        # 添加双曲线内部关系
        self._add_relationship("hyperbola_definition", "hyperbola_parameter_triangle", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_definition", "hyperbola_standard_equation_x", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_standard_equation_x", "hyperbola_standard_equation_y", RelationType.CONTAINS)
        self._add_relationship("hyperbola_standard_equation_x", "hyperbola_range", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_standard_equation_x", "hyperbola_symmetry", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_standard_equation_x", "hyperbola_vertices", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_standard_equation_x", "hyperbola_asymptote", RelationType.PREREQUISITE)
        self._add_relationship("hyperbola_parameter_triangle", "hyperbola_eccentricity", RelationType.PREREQUISITE)

    def _add_parabola_knowledge(self):
        """添加抛物线相关知识"""
        nodes = [
            # 抛物线定义
            KnowledgeNode(
                id="parabola_definition",
                name="抛物线定义",
                category=NodeCategory.DEFINITION,
                content="平面内到定点F（焦点）和定直线l（准线，不经过F）距离相等的点的轨迹",
                description="定义要求焦点不在准线上（否则轨迹退化为直线）。抛物线是焦点-准线定义中e=1的特例",
                prerequisites=["foundation_distance_formula", "foundation_locus"],
            ),
            # 抛物线标准方程（右）
            KnowledgeNode(
                id="parabola_standard_equation_right",
                name="抛物线标准方程（向右）",
                category=NodeCategory.STANDARD_EQUATION,
                content="y² = 2px（p > 0）",
                description="开口向右的抛物线",
                prerequisites=["parabola_definition"],
                params={
                    "equation": "y² = 2px",
                    "focus": "(p/2, 0)",
                    "directrix": "x = -p/2",
                    "axis": "x轴",
                    "vertex": "(0, 0)"
                }
            ),
            # 抛物线标准方程（左）
            KnowledgeNode(
                id="parabola_standard_equation_left",
                name="抛物线标准方程（向左）",
                category=NodeCategory.STANDARD_EQUATION,
                content="y² = -2px（p > 0）",
                description="开口向左的抛物线",
                prerequisites=["parabola_definition"],
                params={
                    "equation": "y² = -2px",
                    "focus": "(-p/2, 0)",
                    "directrix": "x = p/2",
                    "axis": "x轴",
                    "vertex": "(0, 0)"
                }
            ),
            # 抛物线标准方程（上）
            KnowledgeNode(
                id="parabola_standard_equation_up",
                name="抛物线标准方程（向上）",
                category=NodeCategory.STANDARD_EQUATION,
                content="x² = 2py（p > 0）",
                description="开口向上的抛物线",
                prerequisites=["parabola_definition"],
                params={
                    "equation": "x² = 2py",
                    "focus": "(0, p/2)",
                    "directrix": "y = -p/2",
                    "axis": "y轴",
                    "vertex": "(0, 0)"
                }
            ),
            # 抛物线标准方程（下）
            KnowledgeNode(
                id="parabola_standard_equation_down",
                name="抛物线标准方程（向下）",
                category=NodeCategory.STANDARD_EQUATION,
                content="x² = -2py（p > 0）",
                description="开口向下的抛物线",
                prerequisites=["parabola_definition"],
                params={
                    "equation": "x² = -2py",
                    "focus": "(0, -p/2)",
                    "directrix": "y = p/2",
                    "axis": "y轴",
                    "vertex": "(0, 0)"
                }
            ),
            # 抛物线范围
            KnowledgeNode(
                id="parabola_range",
                name="抛物线范围",
                category=NodeCategory.PROPERTY,
                content="以y² = 2px为例：x ≥ 0，y ∈ ℝ",
                description="抛物线是无界的，但在一个方向上有下界",
                prerequisites=["parabola_standard_equation_right"],
            ),
            # 抛物线对称性
            KnowledgeNode(
                id="parabola_symmetry",
                name="抛物线对称性",
                category=NodeCategory.PROPERTY,
                content="关于对称轴一侧对称，对称轴即抛物线的轴",
                description="只有一条对称轴，无中心对称",
                prerequisites=["parabola_standard_equation_right"],
            ),
            # 抛物线顶点
            KnowledgeNode(
                id="parabola_vertex",
                name="抛物线顶点",
                category=NodeCategory.PROPERTY,
                content="唯一顶点为原点(0,0)，是抛物线上离焦点最近的点",
                description="顶点为抛物线与对称轴的交点",
                prerequisites=["parabola_standard_equation_right"],
            ),
            # 抛物线离心率
            KnowledgeNode(
                id="parabola_eccentricity",
                name="抛物线离心率",
                category=NodeCategory.PROPERTY,
                content="e = 1",
                description="抛物线离心率恒等于1，这是其定义的几何本质",
                prerequisites=["parabola_definition"],
                params={
                    "formula": "e = 1",
                    "meaning": "焦点-准线定义的几何本质"
                }
            ),
        ]
        for node in nodes:
            self.nodes[node.id] = node

        # 添加抛物线内部关系
        self._add_relationship("parabola_definition", "parabola_standard_equation_right", RelationType.PREREQUISITE)
        self._add_relationship("parabola_standard_equation_right", "parabola_standard_equation_left", RelationType.CONTAINS)
        self._add_relationship("parabola_standard_equation_right", "parabola_standard_equation_up", RelationType.CONTAINS)
        self._add_relationship("parabola_standard_equation_right", "parabola_standard_equation_down", RelationType.CONTAINS)
        self._add_relationship("parabola_standard_equation_right", "parabola_range", RelationType.PREREQUISITE)
        self._add_relationship("parabola_standard_equation_right", "parabola_symmetry", RelationType.PREREQUISITE)
        self._add_relationship("parabola_standard_equation_right", "parabola_vertex", RelationType.PREREQUISITE)
        self._add_relationship("parabola_definition", "parabola_eccentricity", RelationType.PREREQUISITE)

    def _add_unified_definition(self):
        """添加焦点-准线统一定义节点（教材p.115-117, p.128）"""
        node = KnowledgeNode(
            id="concept_focus_directrix_unified",
            name="圆锥曲线的焦点-准线统一定义",
            category=NodeCategory.CONCEPT,
            content="平面内动点M到定点F（焦点）的距离与到定直线l（准线）的距离之比为常数e（离心率）：|MF|/d(M,l) = e",
            description="当0<e<1时轨迹为椭圆，e=1时为抛物线，e>1时为双曲线。这是三种圆锥曲线的统一定义框架（教材p.115-117推导椭圆准线，p.128引出抛物线定义）",
            prerequisites=["foundation_distance_formula", "foundation_locus"],
            params={
                "e<1": "椭圆",
                "e=1": "抛物线",
                "e>1": "双曲线",
                "key_insight": "三类圆锥曲线本质上是同一定义在不同e值下的表现"
            }
        )
        self.nodes[node.id] = node

        # 关系：统一定义 → 各曲线定义
        self._add_relationship("concept_focus_directrix_unified", "ellipse_definition", RelationType.SPECIALIZED_BY, "e<1")
        self._add_relationship("concept_focus_directrix_unified", "parabola_definition", RelationType.SPECIALIZED_BY, "e=1")
        self._add_relationship("concept_focus_directrix_unified", "hyperbola_definition", RelationType.SPECIALIZED_BY, "e>1")
        # 关系：统一定义 → 准线
        self._add_relationship("concept_focus_directrix_unified", "ellipse_directrix", RelationType.PREREQUISITE)

    def _add_comparisons(self):
        """添加三种圆锥曲线的对比节点和关系"""
        comparison_node = KnowledgeNode(
            id="comparison_three_conics",
            name="三种圆锥曲线横向对比",
            category=NodeCategory.COMPARISON,
            content="从焦点数、距离条件、参数关系、离心率、对称性等维度对比椭圆、双曲线、抛物线",
            description="统一理解三种圆锥曲线的异同",
            prerequisites=[
                "ellipse_definition", "hyperbola_definition", "parabola_definition"
            ]
        )
        self.nodes[comparison_node.id] = comparison_node

        # 添加对比关系
        self._add_relationship("ellipse_definition", "comparison_three_conics", RelationType.COMPARES_WITH)
        self._add_relationship("hyperbola_definition", "comparison_three_conics", RelationType.COMPARES_WITH)
        self._add_relationship("parabola_definition", "comparison_three_conics", RelationType.COMPARES_WITH)

        # 离心率统一
        eccentricity_node = KnowledgeNode(
            id="concept_eccentricity_unified",
            name="离心率统一了三类圆锥曲线",
            category=NodeCategory.CONCEPT,
            content="0 < e < 1 → 椭圆；e = 1 → 抛物线；e > 1 → 双曲线",
            description="这是圆锥曲线焦点-准线统一定义的核心。动点到焦点的距离与到准线的距离之比为常数e，e的取值决定曲线类型",
            prerequisites=[
                "ellipse_eccentricity", "hyperbola_eccentricity", "parabola_eccentricity"
            ]
        )
        self.nodes[eccentricity_node.id] = eccentricity_node

    def _add_common_errors(self):
        """添加易错点节点"""
        errors = [
            KnowledgeNode(
                id="error_parameter_triangle_direction",
                name="易错点：椭圆vs双曲线的参数三角形方向相反",
                category=NodeCategory.ERROR_PRONE,
                content="椭圆：a最大，a² = b² + c²（a是斜边）\n双曲线：c最大，c² = a² + b²（c是斜边）",
                description="这是最容易混淆的地方，决定了两种曲线的本质不同",
                prerequisites=["ellipse_parameter_triangle", "hyperbola_parameter_triangle"]
            ),
            KnowledgeNode(
                id="error_hyperbola_imaginary_axis",
                name="易错点：双曲线的虚轴端点不在曲线上",
                category=NodeCategory.ERROR_PRONE,
                content="虚轴端点(0, ±b)只是作图辅助，不是曲线上的点",
                description="与椭圆不同，椭圆的短轴顶点在曲线上",
                prerequisites=["hyperbola_vertices"]
            ),
            KnowledgeNode(
                id="error_parabola_no_center",
                name="易错点：抛物线没有中心对称，离心率恒等于1",
                category=NodeCategory.ERROR_PRONE,
                content="抛物线是唯一没有中心对称的圆锥曲线。其e恒等于1，不是范围而是固定值",
                description="不要把抛物线的性质与椭圆、双曲线混淆",
                prerequisites=["parabola_symmetry", "parabola_eccentricity"]
            ),
            KnowledgeNode(
                id="error_equation_coefficient_sign",
                name="易错点：方程系数判断曲线类型",
                category=NodeCategory.ERROR_PRONE,
                content="两项均为正且相等→圆；两项均为正且不等→椭圆；一正一负→双曲线；只含一个变量的平方→抛物线",
                description="根据二次方程的形式快速判断曲线类型",
                prerequisites=["ellipse_standard_equation_x", "hyperbola_standard_equation_x", "parabola_standard_equation_right"]
            ),
        ]

        for error_node in errors:
            self.nodes[error_node.id] = error_node

        # 添加易错点关系
        self._add_relationship("ellipse_parameter_triangle", "error_parameter_triangle_direction", RelationType.COMMON_ERROR)
        self._add_relationship("hyperbola_parameter_triangle", "error_parameter_triangle_direction", RelationType.COMMON_ERROR)
        self._add_relationship("hyperbola_vertices", "error_hyperbola_imaginary_axis", RelationType.COMMON_ERROR)
        self._add_relationship("parabola_symmetry", "error_parabola_no_center", RelationType.COMMON_ERROR)
        self._add_relationship("parabola_eccentricity", "error_parabola_no_center", RelationType.COMMON_ERROR)

    # ==================================================================
    # 教材结构性节点 —— 按节追加（v2 升级，UPGRADE_PLAN.md）
    # ------------------------------------------------------------------
    # 设计原则（亦即"PDF→KG 节点"的复用方法论，详见知识图谱 .md 文末附录）：
    #   1. 一个"探究/思考/观察/例题"框 = 一个独立 KG 节点，不与"知识点结论"
    #      节点合并，便于状态机按教材栏目精确控制教学节奏。
    #   2. 节点 ID 命名约定：{曲线}_{节号}_{类型}_{标识}
    #      —— 例 ellipse_311_explore_string、hyperbola_321_example_2
    #   3. 关系：探究/思考/观察 用 EXPLORES（引出某知识点）；
    #             例题 用 APPLIES（应用了哪些知识点）；
    #             例题之间的承接顺序仍可用 PREREQUISITE。
    #   4. params 字段约定（用于状态机/前端读取）：
    #        - "pdf_page": "p105"            ——溯源教材页码
    #        - "textbook_label": "探究"/"思考"/"例 1"  ——教材原栏目名
    #        - "given": "..."                ——例题已知条件
    #        - "goal": "..."                 ——例题目标
    #        - "analysis": "..."             ——分析思路（教材原文）
    #        - "solution_steps": [...]       ——解答关键步骤（4 步教学循环用）
    #        - "answer": "..."               ——最终答案
    #        - "viz_action": "..."           ——配套确定性 VIZ 标识符
    # ==================================================================

    def _add_section_311_content(self):
        """3.1.1 椭圆及其标准方程 —— 新增 8 个教材结构性节点（PDF p3-p7 / 教材 p105-p109）"""
        nodes = [
            # ---- 🔵 探究：绳画法 ----
            KnowledgeNode(
                id="ellipse_311_explore_string",
                name="探究：绳画法引出椭圆",
                category=NodeCategory.EXPLORATION,
                content=(
                    "取一条定长的细绳，把它的两端都固定在图板的同一点，套上铅笔拉紧绳子，"
                    "移动笔尖画出的轨迹是一个圆。如果把细绳的两端拉开一段距离，分别固定在"
                    "图板的两点 F₁、F₂（图3.1-1），套上铅笔拉紧绳子，移动笔尖画出的轨迹是什么曲线？"
                    "在这一过程中，移动的笔尖（动点）满足的几何条件是什么？"
                ),
                description=(
                    "教材通过「两端同点→圆」到「两端不同点→？」的对比实验引出椭圆定义。"
                    "教学引导：让学生观察笔尖到两定点的距离之和恒等于绳长（常数）。"
                ),
                prerequisites=["foundation_locus", "foundation_distance_formula"],
                params={
                    "pdf_page": "p105",
                    "textbook_label": "探究（3.1.1 第一栏）",
                    "viz_action": "show_explore_string_setup",  # 双焦点+可拖动笔尖+绳长可视化
                    "key_observation": "|PF₁| + |PF₂| = 绳长 = 常数",
                }
            ),
            # ---- 🟣 思考1：建坐标系 ----
            KnowledgeNode(
                id="ellipse_311_reflect_coord",
                name="思考1：怎样建立坐标系使椭圆方程形式简单？",
                category=NodeCategory.REFLECTION,
                content="观察椭圆的形状，你认为怎样建立坐标系可能使所得的椭圆方程形式简单？",
                description=(
                    "在引出椭圆定义之后、推导方程之前的过渡思考，目的是让学生意识到"
                    "对称性—— F₁F₂ 连线为 x 轴、其中垂线为 y 轴，可让方程对称简洁。"
                ),
                prerequisites=["ellipse_definition"],
                params={
                    "pdf_page": "p105 末",
                    "textbook_label": "思考（3.1.1 思考1）",
                    "viz_action": "show_axis_choice_animation",  # 标轴动画：演示"为什么以 F₁F₂ 为 x 轴"
                    "expected_answer": "以 F₁F₂ 所在直线为 x 轴, 其中垂线为 y 轴",
                }
            ),
            # ---- 🧩 标准方程推导（合并推导+结论；含 y 轴形式）----
            KnowledgeNode(
                id="ellipse_311_derivation",
                name="椭圆标准方程的推导（含 y 轴形式）",
                category=NodeCategory.STANDARD_EQUATION,
                content=(
                    "由 |MF₁|+|MF₂|=2a 出发：√((x+c)²+y²)+√((x-c)²+y²)=2a (式①) "
                    "→ 移项平方 → 整理为 (a²-c²)x²+a²y²=a²(a²-c²) → 两边除以 a²(a²-c²) "
                    "→ 令 b²=a²-c² 得 x²/a²+y²/b²=1 (a>b>0)。焦点在 y 轴时方程为 y²/a²+x²/b²=1。"
                ),
                description=(
                    "本节核心知识点：从定义出发的代数推导全过程。状态机将本节作为一个完整阶段"
                    "（DERIVE_AND_RESULT），不再拆分推导/结论，配合 VIZ 分步动画。"
                    "教学要点：① 设 2a 而非 a 是为简化，② 两次平方都是同解变形，③ b² = a²-c² 的几何含义留到下一思考。"
                ),
                prerequisites=["ellipse_definition", "ellipse_311_reflect_coord", "foundation_distance_formula"],
                params={
                    "pdf_page": "p106-p107",
                    "textbook_label": "标准方程推导 + 结论",
                    "viz_action": "show_derivation_steps",  # 推导分步动画（5 步）
                    "result_x": "x²/a² + y²/b² = 1 (a>b>0)",
                    "result_y": "y²/a² + x²/b² = 1 (a>b>0)",
                    "key_relation": "b² = a² - c², 即 c² = a² - b²",
                }
            ),
            # ---- 🟣 思考2/3 合并：a/b/c 几何关系 + y 轴形式 ----
            KnowledgeNode(
                id="ellipse_311_reflect_geometry_yaxis",
                name="思考2+3：a/b/c 几何关系与焦点在 y 轴的形式",
                category=NodeCategory.REFLECTION,
                content=(
                    "思考2：观察图3.1-3，能从中找出表示 a, c, √(a²-c²) 的线段吗？ "
                    "→ 取短轴端点 P，则 |PF₁|=|PF₂|=a, |OF₁|=|OF₂|=c, |PO|=√(a²-c²)=b。 "
                    "思考3：如果焦点 F₁、F₂ 在 y 轴上（坐标 (0,±c)），椭圆方程是什么？"
                    "→ y²/a² + x²/b² = 1 (a>b>0)，也是椭圆的标准方程。"
                ),
                description=(
                    "推导完成后的两个反思追问，合并为一个状态机阶段。教学顺序：先回看几何意义"
                    "（让 b 不再只是符号），再举一反三看 y 轴形式。"
                ),
                prerequisites=["ellipse_311_derivation"],
                params={
                    "pdf_page": "p106 末 + p107 中",
                    "textbook_label": "思考2 + 思考3（合并）",
                    "viz_action": "show_abc_triangle",  # 图3.1-3 几何三角形高亮
                    "key_insight_1": "b 不是凭空引入的符号，而是椭圆短轴端点到焦点的距离 = √(a²-c²)",
                    "key_insight_2": "焦点轴变化只是 x↔y 互换，其余结构相同",
                }
            ),
            # ---- 🟡 例1：已知焦点和过点求方程 ----
            KnowledgeNode(
                id="ellipse_311_example_1",
                name="例1：已知焦点和过点求椭圆标准方程",
                category=NodeCategory.EXAMPLE,
                content=(
                    "已知椭圆的两个焦点坐标分别是 (-2, 0)、(2, 0)，并且经过点 (5/2, -3/2)，"
                    "求它的标准方程。"
                ),
                description=(
                    "考查：① 由焦点位置判断焦点在 x 轴 → 设标准方程形式；"
                    "② 由椭圆定义直接计算 2a；③ 由 b² = a² - c² 得 b²。"
                ),
                prerequisites=["ellipse_311_derivation", "ellipse_definition"],
                params={
                    "pdf_page": "p107 末",
                    "textbook_label": "例 1",
                    "viz_action": "show_example_1_visualization",  # 焦点+过点+最终椭圆描出
                    "given": "F₁(-2,0), F₂(2,0), 过点 P(5/2, -3/2)",
                    "goal": "求椭圆的标准方程",
                    "analysis": "焦点在 x 轴 → 设 x²/a² + y²/b² = 1; 由定义 2a = |PF₁|+|PF₂| 直接求出 a",
                    "solution_steps": [
                        "1. 焦点在 x 轴 → 设方程为 x²/a² + y²/b² = 1 (a>b>0), c = 2",
                        "2. 由椭圆定义 2a = √((5/2+2)²+(-3/2)²) + √((5/2-2)²+(-3/2)²) = √(49/4+9/4) + √(1/4+9/4) = √(58/4) + √(10/4)",
                        "3. 化简 2a = (√58 + √10)/2 ... 教材给出 2a = 2√10",
                        "4. 由 a = √10, c = 2 → b² = a² - c² = 10 - 4 = 6",
                        "5. 标准方程：x²/10 + y²/6 = 1",
                    ],
                    "answer": "x²/10 + y²/6 = 1",
                }
            ),
            # ---- 🟡 例2：圆生椭圆（PD 中点轨迹）+ 内嵌🟣思考 ----
            KnowledgeNode(
                id="ellipse_311_example_2",
                name="例2：圆压缩生椭圆（PD 中点轨迹）",
                category=NodeCategory.EXAMPLE,
                content=(
                    "如图3.1-5，在圆 x²+y²=4 上任取一点 P，过 P 作 x 轴的垂线段 PD（D 为垂足）。"
                    "当 P 在圆上运动时，线段 PD 的中点 M 的轨迹是什么？为什么？"
                    "（P 经过圆与 x 轴的交点时，规定 M 与 P 重合。）"
                ),
                description=(
                    "考查：① 设动点关系（M 与 P 坐标）；② 用圆的方程消元；③ 得到椭圆方程并解释。"
                    "教学增量：本例之后教材紧跟一个🟣思考：圆通过「压缩」得椭圆，能通过「拉伸」得椭圆吗？"
                    "→ 让学生类比 y → 2y 得 x² + (2y)² = 4 → x² + 4y² = 4 → x²/4 + y² = 1，"
                    "实质是圆和椭圆通过坐标缩放互相对应。"
                ),
                prerequisites=["ellipse_311_example_1", "ellipse_definition"],
                params={
                    "pdf_page": "p108",
                    "textbook_label": "例 2 + 思考（压缩拉伸）",
                    "viz_action": "show_example_2_visualization",  # 圆+P 拖动+PD 垂线+M 轨迹描出
                    "given": "圆 x²+y²=4 上动点 P(x₀, y₀); D(x₀, 0); M 是 PD 中点",
                    "goal": "求 M 的轨迹方程",
                    "analysis": "M 与 P 的坐标关系: x = x₀, y = y₀/2 → 消元代入圆方程",
                    "solution_steps": [
                        "1. 设 M(x, y), P(x₀, y₀), D(x₀, 0)",
                        "2. M 是 PD 中点 → x = x₀, y = y₀/2",
                        "3. P 在圆上 → x₀² + y₀² = 4",
                        "4. 代入 x₀ = x, y₀ = 2y → x² + 4y² = 4",
                        "5. 化简 → x²/4 + y² = 1，所以 M 的轨迹是椭圆",
                    ],
                    "answer": "x²/4 + y² = 1（椭圆）",
                    "embedded_reflection": "思考：圆通过'压缩'得椭圆，能通过'拉伸'得椭圆吗？椭圆与圆的关系？",
                }
            ),
            # ---- 🟡 例3：斜率积 -4/9 ----
            KnowledgeNode(
                id="ellipse_311_example_3",
                name="例3：斜率之积为 -4/9 的轨迹",
                category=NodeCategory.EXAMPLE,
                content=(
                    "如图3.1-6，设 A、B 两点的坐标分别为 (-5, 0)、(5, 0)。"
                    "直线 AM、BM 相交于点 M，且它们的斜率之积是 -4/9，求 M 的轨迹方程。"
                ),
                description=(
                    "考查：① 用点斜式表示两条直线斜率；② 由斜率积条件得到 x, y 关系；"
                    "③ 化简得到椭圆方程并指出排除点。这是椭圆「非定义生成方式」的经典例子。"
                ),
                prerequisites=["ellipse_311_example_2", "ellipse_311_derivation"],
                params={
                    "pdf_page": "p108-p109",
                    "textbook_label": "例 3",
                    "viz_action": "show_example_3_visualization",  # A/B 定点+动点 M+实时显示斜率积
                    "given": "A(-5, 0), B(5, 0); 直线 AM, BM 相交于 M; k_AM · k_BM = -4/9",
                    "goal": "求 M 的轨迹方程",
                    "analysis": "k_AM = y/(x+5) (x≠-5), k_BM = y/(x-5) (x≠5); 两者之积 = -4/9 → 化简",
                    "solution_steps": [
                        "1. 设 M(x, y); A(-5, 0) → k_AM = y/(x+5) (x≠-5)",
                        "2. B(5, 0) → k_BM = y/(x-5) (x≠5)",
                        "3. 由条件: [y/(x+5)] · [y/(x-5)] = -4/9 (x≠±5)",
                        "4. 化简: y²/(x²-25) = -4/9 → 9y² = -4(x²-25) = -4x² + 100",
                        "5. 整理: 4x² + 9y² = 100 → x²/25 + y²/(100/9) = 1 (x≠±5)",
                    ],
                    "answer": "x²/25 + y²/(100/9) = 1 (x≠±5)，去除 (-5,0)、(5,0) 两点的椭圆",
                }
            ),
        ]
        for node in nodes:
            self.nodes[node.id] = node

        # ---- 关系：探究/思考用 EXPLORES，例题用 APPLIES ----
        # 探究 → 引出"椭圆定义"
        self._add_relationship("ellipse_311_explore_string", "ellipse_definition", RelationType.EXPLORES, "绳画法引出定义")
        # 思考1 → 引出"建坐标系"，最终通向标准方程
        self._add_relationship("ellipse_311_reflect_coord", "ellipse_311_derivation", RelationType.EXPLORES, "选择对称坐标系")
        # 推导 → 直接得到 x 轴形式标准方程（已存在节点）
        self._add_relationship("ellipse_311_derivation", "ellipse_standard_equation_x", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_311_derivation", "ellipse_standard_equation_y", RelationType.PREREQUISITE)
        # 思考2/3 → 巩固参数关系 + y 轴形式
        self._add_relationship("ellipse_311_reflect_geometry_yaxis", "ellipse_parameter_triangle", RelationType.EXPLORES, "a/b/c 几何意义")
        self._add_relationship("ellipse_311_reflect_geometry_yaxis", "ellipse_standard_equation_y", RelationType.EXPLORES, "焦点在 y 轴形式")
        # 例题 → 应用了哪些已有知识点
        self._add_relationship("ellipse_311_example_1", "ellipse_definition", RelationType.APPLIES)
        self._add_relationship("ellipse_311_example_1", "ellipse_standard_equation_x", RelationType.APPLIES)
        self._add_relationship("ellipse_311_example_2", "ellipse_definition", RelationType.APPLIES)
        self._add_relationship("ellipse_311_example_2", "ellipse_standard_equation_x", RelationType.APPLIES)
        self._add_relationship("ellipse_311_example_3", "ellipse_standard_equation_x", RelationType.APPLIES)
        # 例题之间的教学顺序（便于状态机推进）
        self._add_relationship("ellipse_311_example_1", "ellipse_311_example_2", RelationType.PREREQUISITE)
        self._add_relationship("ellipse_311_example_2", "ellipse_311_example_3", RelationType.PREREQUISITE)

    def _add_relationship(self, source_id: str, target_id: str, rel_type: RelationType, label: str = ""):
        """添加单条关系"""
        relationship = Relationship(
            source_id=source_id,
            target_id=target_id,
            type=rel_type,
            label=label
        )
        self.relationships.append(relationship)

    # ------------------------------------------------------------------
    # 关键词检索（GraphRAG：根据学生输入检索最相关的 KG 节点）
    # ------------------------------------------------------------------

    def _build_keyword_index(self) -> Dict[str, List[str]]:
        """为每个节点建立关键词 → node_id 的倒排索引。

        关键词来源：node.name + node.content + node.description + params 中的值。
        """
        index: Dict[str, List[str]] = {}
        for nid, node in self.nodes.items():
            # 收集所有文本
            texts = [node.name, node.content, node.description]
            for v in node.params.values():
                texts.append(str(v))
            blob = " ".join(texts)
            # 提取有意义的 token（中文按字/词，英文按空格）
            tokens = set()
            # 中文关键短语（2-4 字）
            for length in (2, 3, 4):
                for i in range(len(blob) - length + 1):
                    seg = blob[i:i+length]
                    if any('\u4e00' <= ch <= '\u9fff' for ch in seg):
                        tokens.add(seg)
            # 英文/数学 token
            import re
            for tok in re.findall(r'[a-zA-Z_²³]+|[0-9]+[a-zA-Z²³]*|[F₁F₂]+|[≤≥<>]+', blob):
                if len(tok) >= 1:
                    tokens.add(tok.lower())
            # 额外：把完整 name 也作为关键词
            tokens.add(node.name)
            for tok in tokens:
                index.setdefault(tok, [])
                if nid not in index[tok]:
                    index[tok].append(nid)
        return index

    def search_nodes(self, query: str, top_k: int = 3, scope: str = "ellipse") -> List["KnowledgeNode"]:
        """根据学生输入文字检索最相关的知识节点。

        Args:
            query:  学生的文字输入
            top_k:  返回的最大节点数
            scope:  课程范围过滤，"ellipse" / "hyperbola" / "parabola" / "all"

        Returns:
            按相关性降序排列的 KnowledgeNode 列表
        """
        if not hasattr(self, '_kw_index'):
            self._kw_index = self._build_keyword_index()

        # 对 query 提取 token（同样逻辑）
        import re
        q_tokens: set = set()
        for length in (2, 3, 4):
            for i in range(len(query) - length + 1):
                seg = query[i:i+length]
                if any('\u4e00' <= ch <= '\u9fff' for ch in seg):
                    q_tokens.add(seg)
        for tok in re.findall(r'[a-zA-Z_²³]+|[0-9]+[a-zA-Z²³]*', query):
            q_tokens.add(tok.lower())
        # 也加入单个关键中文字
        for ch in query:
            if '\u4e00' <= ch <= '\u9fff':
                q_tokens.add(ch)

        # 计分：每个节点按匹配到的 token 数量打分
        scores: Dict[str, int] = {}
        for tok in q_tokens:
            for nid in self._kw_index.get(tok, []):
                scores[nid] = scores.get(nid, 0) + 1

        # scope 过滤
        scope_prefixes = {
            "ellipse": ("ellipse_", "foundation_", "error_parameter", "error_equation", "concept_", "comparison_"),
            "hyperbola": ("hyperbola_", "foundation_", "error_parameter", "error_hyperbola", "error_equation", "concept_", "comparison_"),
            "parabola": ("parabola_", "foundation_", "error_parabola", "error_equation", "concept_", "comparison_"),
            "all": None,
        }
        prefixes = scope_prefixes.get(scope)
        if prefixes is not None:
            scores = {
                nid: s for nid, s in scores.items()
                if any(nid.startswith(p) for p in prefixes)
            }

        # 按分数降序，取 top_k
        ranked = sorted(scores.items(), key=lambda x: -x[1])[:top_k]
        return [self.nodes[nid] for nid, _ in ranked if nid in self.nodes]

    def retrieve_subgraph(
        self,
        query: str,
        stage_node_ids: List[str] | None = None,
        scope: str = "ellipse",
        seed_top_k: int = 3,
        max_hops: int = 2,
        max_nodes: int = 10,
    ) -> List["KnowledgeNode"]:
        """GraphRAG 子图检索：根据学生提问，从知识图谱中检索相关子图。

        流程：
          1. 用 search_nodes() 对学生 query 做关键词匹配，得到 seed 节点
          2. 从 seed 节点出发，沿 PREREQUISITE / COMPARES_WITH / COMMON_ERROR
             等边做 BFS 多跳遍历（最多 max_hops 跳）
          3. 与 stage_node_ids（阶段基础节点）合并、去重
          4. 返回去重后的节点列表（不超过 max_nodes）

        Args:
            query:          学生的自然语言输入
            stage_node_ids: 当前阶段的基础节点 ID 列表（保底注入）
            scope:          课程范围过滤
            seed_top_k:     关键词检索返回的种子节点数
            max_hops:       图遍历最大跳数
            max_nodes:      最终返回的最大节点数

        Returns:
            去重的 KnowledgeNode 列表
        """
        from collections import deque

        # ---------- 1. 构建邻接表（双向） ----------
        adj: Dict[str, List[str]] = {}
        for rel in self.relationships:
            adj.setdefault(rel.source_id, []).append(rel.target_id)
            adj.setdefault(rel.target_id, []).append(rel.source_id)

        # ---------- 2. 阶段基础节点（保底） ----------
        collected_ids: dict = {}          # node_id → priority (越小越优先)
        if stage_node_ids:
            for idx, nid in enumerate(stage_node_ids):
                if nid in self.nodes:
                    collected_ids[nid] = idx   # 阶段基础节点优先级最高

        # ---------- 3. 关键词检索得到 seed 节点 ----------
        seeds = self.search_nodes(query, top_k=seed_top_k, scope=scope)
        seed_ids = [n.id for n in seeds]

        # ---------- 4. BFS 多跳遍历 ----------
        visited: set = set()
        queue: deque = deque()            # (node_id, current_hop)
        for sid in seed_ids:
            if sid not in visited:
                queue.append((sid, 0))
                visited.add(sid)

        traversed_ids: List[str] = []
        while queue:
            nid, hop = queue.popleft()
            traversed_ids.append(nid)
            if hop < max_hops:
                for neighbor in adj.get(nid, []):
                    if neighbor not in visited and neighbor in self.nodes:
                        visited.add(neighbor)
                        queue.append((neighbor, hop + 1))

        # 把遍历结果也放入 collected_ids（优先级排在阶段节点之后）
        base_priority = len(collected_ids)
        for i, nid in enumerate(traversed_ids):
            if nid not in collected_ids:
                collected_ids[nid] = base_priority + i

        # ---------- 5. scope 过滤 ----------
        scope_prefixes = {
            "ellipse": ("ellipse_", "foundation_", "error_parameter", "error_equation", "concept_", "comparison_"),
            "hyperbola": ("hyperbola_", "foundation_", "error_parameter", "error_hyperbola", "error_equation", "concept_", "comparison_"),
            "parabola": ("parabola_", "foundation_", "error_parabola", "error_equation", "concept_", "comparison_"),
            "all": None,
        }
        prefixes = scope_prefixes.get(scope)
        if prefixes is not None:
            collected_ids = {
                nid: p for nid, p in collected_ids.items()
                if any(nid.startswith(pf) for pf in prefixes)
            }

        # ---------- 6. 按优先级排序，截断 ----------
        sorted_ids = sorted(collected_ids.keys(), key=lambda x: collected_ids[x])
        result_ids = sorted_ids[:max_nodes]

        return [self.nodes[nid] for nid in result_ids if nid in self.nodes]

    def format_nodes_for_prompt(self, nodes: List["KnowledgeNode"]) -> str:
        """把检索到的节点格式化为 LLM system prompt 中的教材引用块。"""
        if not nodes:
            return ""
        lines = ["【教材知识点（来自知识图谱，请基于以下内容回答）】"]
        for node in nodes:
            lines.append(f"- {node.name}（{node.category.value}）：{node.content}")
            if node.description:
                lines.append(f"  说明：{node.description}")
            if node.params:
                for k, v in node.params.items():
                    lines.append(f"  {k}：{v}")
        return "\n".join(lines)

    def get_all_nodes(self) -> Dict[str, Any]:
        """获取所有知识节点

        Returns:
            {node_id: {node_data_dict}}
        """
        return {
            node_id: {
                **asdict(node),
                "category": node.category.value,
            }
            for node_id, node in self.nodes.items()
        }

    def get_node_with_context(self, node_id: str) -> Dict[str, Any]:
        """获取单个节点及其上下文

        Args:
            node_id: 节点ID

        Returns:
            {
                "node": {...},
                "prerequisites": [{...}],  # 前置节点
                "related": [{...}]         # 相关节点（出边关系）
            }
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")

        node = self.nodes[node_id]
        result = {
            "node": {
                **asdict(node),
                "category": node.category.value,
            },
            "prerequisites": [],
            "related": []
        }

        # 获取前置节点
        for prereq_id in node.prerequisites:
            if prereq_id in self.nodes:
                prereq_node = self.nodes[prereq_id]
                result["prerequisites"].append({
                    **asdict(prereq_node),
                    "category": prereq_node.category.value,
                })

        # 获取相关节点（出边）
        for rel in self.relationships:
            if rel.source_id == node_id:
                if rel.target_id in self.nodes:
                    target_node = self.nodes[rel.target_id]
                    result["related"].append({
                        "node": {
                            **asdict(target_node),
                            "category": target_node.category.value,
                        },
                        "relation_type": rel.type.value,
                        "relation_label": rel.label
                    })

        return result

    def generate_cypher_statements(self) -> str:
        """生成Neo4j Cypher语句

        Returns:
            Cypher CREATE语句的字符串，包含：
            1. 创建所有节点
            2. 创建所有关系
        """
        cypher_statements = []

        # 1. 创建节点
        cypher_statements.append("// 创建知识节点")
        for node_id, node in self.nodes.items():
            props = {
                "id": node_id,
                "name": node.name,
                "category": node.category.value,
                "content": node.content,
                "description": node.description,
            }
            # 添加params和examples作为JSON字符串
            if node.params:
                props["params"] = str(node.params)
            if node.examples:
                props["examples"] = str(node.examples)

            prop_str = ", ".join([
                f"{k}: {repr(v)}" for k, v in props.items()
            ])
            cypher_statements.append(
                f'CREATE (:{node.category.value} {{{prop_str}}})'
            )

        # 2. 创建关系
        cypher_statements.append("\n// 创建关系")
        for rel in self.relationships:
            source = rel.source_id
            target = rel.target_id
            rel_type = rel.type.value
            label = rel.label or ""
            cypher_statements.append(
                f'MATCH (a {{id: "{source}"}}), (b {{id: "{target}"}}) '
                f'CREATE (a)-[:{rel_type} {{label: "{label}"}}]->(b)'
            )

        return "\n".join(cypher_statements)


def import_to_neo4j(driver):
    """将知识图谱导入Neo4j数据库

    Args:
        driver: neo4j.driver.Driver实例

    Raises:
        RuntimeError: 如果Neo4j连接失败
    """
    graph = ConicKnowledgeGraph()

    # 清空旧数据（可选）
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")

    # 创建所有节点
    with driver.session() as session:
        for node_id, node in graph.nodes.items():
            props = {
                "id": node_id,
                "name": node.name,
                "category": node.category.value,
                "content": node.content,
                "description": node.description,
            }
            if node.params:
                props["params"] = str(node.params)
            if node.examples:
                props["examples"] = str(node.examples)

            # 构建Cypher语句
            labels = f":{node.category.value}"
            create_query = f"CREATE (n{labels} ${{{','.join(props.keys())}}})"
            session.run(create_query, **props)

    # 创建所有关系
    with driver.session() as session:
        for rel in graph.relationships:
            query = (
                f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
                f"CREATE (a)-[:{rel.type.value} {{label: $label}}]->(b)"
            )
            session.run(query, source_id=rel.source_id, target_id=rel.target_id, label=rel.label)


def get_all_nodes() -> Dict[str, Any]:
    """返回完整的知识图谱（全局函数）"""
    graph = ConicKnowledgeGraph()
    return graph.get_all_nodes()


def get_node_with_context(node_id: str) -> Dict[str, Any]:
    """获取单个节点及其上下文（全局函数）"""
    graph = ConicKnowledgeGraph()
    return graph.get_node_with_context(node_id)


if __name__ == "__main__":
    # 测试：打印前几个节点
    graph = ConicKnowledgeGraph()
    print(f"Total nodes: {len(graph.nodes)}")
    print(f"Total relationships: {len(graph.relationships)}")
    print("\nFirst few nodes:")
    for i, (node_id, node) in enumerate(list(graph.nodes.items())[:5]):
        print(f"  {node_id}: {node.name} ({node.category.value})")
