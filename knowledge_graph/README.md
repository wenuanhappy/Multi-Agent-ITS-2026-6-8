# 圆锥曲线知识图谱模块

本模块提供了圆锥曲线（椭圆、双曲线、抛物线）的完整知识图谱，包括定义、标准方程、几何性质和易错点。支持在内存中存储和查询，也支持导入到Neo4j图数据库。

## 功能概述

### 1. 知识图谱解析 (`parser.py`)

将Markdown知识图谱解析为结构化数据，包含36个知识节点和32条关系。

**主要类：**

- `KnowledgeNode`: 知识节点数据类
  - `id`: 唯一标识
  - `name`: 节点名称
  - `category`: 分类（定义、公式、性质、参数、标准方程、对比、易错点、概念）
  - `content`: 主要内容
  - `params`: 数学参数字典
  - `prerequisites`: 前置节点列表
  - `description`: 详细描述
  - `examples`: 示例列表

- `ConicKnowledgeGraph`: 完整的知识图谱
  - 包含所有椭圆、双曲线、抛物线的知识节点
  - 支持节点查询和关系遍历
  - 生成Neo4j Cypher语句

**主要函数：**

```python
# 获取所有节点
nodes = get_all_nodes()

# 获取单个节点及其上下文（前置节点、相关节点）
context = get_node_with_context("ellipse_definition")

# 导入到Neo4j（需要driver）
import_to_neo4j(driver)
```

### 2. Neo4j客户端 (`neo4j_client.py`)

提供Neo4j数据库连接管理和知识图谱导入功能。

**主要类：**

- `Neo4jClient`: Neo4j连接和操作封装
  - `connect()`: 连接到Neo4j
  - `disconnect()`: 断开连接
  - `run_query(query, params)`: 执行Cypher查询
  - `clear_database()`: 清空数据库
  - `create_node(label, properties)`: 创建节点
  - `create_relationship(source_id, target_id, type, properties)`: 创建关系
  - `find_node(node_id)`: 查找单个节点
  - `find_prerequisites(node_id)`: 查找前置节点
  - `find_related_nodes(node_id, relation_type)`: 查找相关节点
  - `import_knowledge_graph()`: 导入知识图谱

**主要函数：**

```python
# 创建并连接到Neo4j
client = connect()

# 执行查询
results = run_query(client, "MATCH (n) RETURN COUNT(n) as count")

# 清空数据库
clear_database(client)

# 导入知识图谱
import_knowledge_graph(client)
```

## 知识图谱结构

### 节点分类

| 分类 | 数量 | 说明 |
|-----|------|------|
| 定义 (DEFINITION) | 3 | 椭圆、双曲线、抛物线的定义 |
| 标准方程 (STANDARD_EQUATION) | 8 | 各种焦点位置和开口方向的标准方程 |
| 公式 (FORMULA) | 1 | 距离公式等基础公式 |
| 性质 (PROPERTY) | 14 | 范围、对称性、顶点、离心率、准线、渐近线等 |
| 参数 (PARAMETER) | 2 | 椭圆和双曲线的参数关系 |
| 对比 (COMPARISON) | 1 | 三种圆锥曲线的横向对比 |
| 易错点 (ERROR_PRONE) | 4 | 学生常见的混淆点 |
| 概念 (CONCEPT) | 3 | 基础概念和统一理论 |

**总计：36个节点**

### 关系类型

| 关系类型 | 说明 |
|--------|------|
| PREREQUISITE | A是B的前置条件（必须先掌握A） |
| CONTAINS | 父节点包含子节点 |
| COMPARES_WITH | 与其他概念对比 |
| COMMON_ERROR | 链接到相关的易错点 |

**总计：32条关系**

## 使用示例

### 示例1：在内存中查询知识图谱

```python
from knowledge_graph import get_node_with_context

# 查询椭圆离心率节点及其上下文
context = get_node_with_context("ellipse_eccentricity")

# 获取节点信息
node = context["node"]
print(f"名称: {node['name']}")
print(f"内容: {node['content']}")

# 获取前置节点（必须掌握的概念）
for prereq in context["prerequisites"]:
    print(f"前置: {prereq['name']}")

# 获取相关节点
for related in context["related"]:
    print(f"相关 [{related['relation_type']}]: {related['node']['name']}")
```

### 示例2：导入到Neo4j数据库

```python
from knowledge_graph import Neo4jClient

# 1. 创建并连接到Neo4j
client = Neo4jClient()
if not client.connect():
    print("Failed to connect to Neo4j")
    exit(1)

# 2. 导入知识图谱
if client.import_knowledge_graph():
    print("Knowledge graph imported successfully!")
else:
    print("Failed to import knowledge graph")

# 3. 执行查询
results = client.run_query(
    "MATCH (n {category: '定义'}) RETURN n.name, n.content"
)
for result in results:
    print(f"- {result['n.name']}: {result['n.content']}")

# 4. 断开连接
client.disconnect()
```

### 示例3：查找特定类型的节点

```python
from knowledge_graph import get_all_nodes

all_nodes = get_all_nodes()

# 找出所有性质节点
properties = {
    node_id: node for node_id, node in all_nodes.items()
    if node['category'] == '性质'
}

print(f"找到 {len(properties)} 个性质节点:")
for node_id, node in properties.items():
    print(f"- {node['name']}")
```

### 示例4：获取学习路径

```python
from knowledge_graph import get_node_with_context

# 获取双曲线标准方程节点
node_context = get_node_with_context("hyperbola_standard_equation_x")

print("学习路径（从基础到深入）:")
print("\n1. 前置基础概念:")
for prereq in node_context["prerequisites"]:
    print(f"   - {prereq['name']}")

print("\n2. 当前节点:")
print(f"   - {node_context['node']['name']}")
print(f"     {node_context['node']['content']}")

print("\n3. 后续相关知识:")
for related in node_context["related"]:
    print(f"   - [{related['relation_type']}] {related['node']['name']}")
```

## 配置

### Neo4j连接配置

在 `config/settings.py` 中配置以下环境变量或直接修改：

```python
NEO4J_URI = "neo4j+s://xxxxx.databases.neo4j.io"  # 数据库连接URL
NEO4J_USER = "neo4j"                               # 用户名
NEO4J_PASSWORD = "your-password"                   # 密码
```

### 获取Neo4j凭证

1. 访问 [Neo4j Aura Free](https://neo4j.com/cloud/aura-free)
2. 注册并创建免费数据库
3. 获取URI、用户名和密码
4. 填入 `config/settings.py`

## 依赖

```bash
# 仅使用内存图谱（无需额外依赖）
python3 -c "from knowledge_graph import get_all_nodes; print(len(get_all_nodes()))"

# 使用Neo4j导入功能
pip install neo4j
```

## 知识图谱文件

原始知识图谱文件：`../圆锥曲线知识图谱.md`

包含内容：
- 椭圆的定义、标准方程、几何性质
- 双曲线的定义、标准方程、几何性质
- 抛物线的定义、标准方程、几何性质
- 三种曲线的横向对比
- 易错点和学科逻辑提示

## 文件结构

```
knowledge_graph/
├── __init__.py          # 模块入口，导出主要类和函数
├── parser.py            # 知识图谱解析器
├── neo4j_client.py      # Neo4j客户端
├── example_usage.py     # 使用示例
└── README.md            # 本文件
```

## 常见问题

### Q: 我可以在没有Neo4j的情况下使用这个模块吗？

**A:** 可以。`parser.py` 中的所有函数都在内存中工作，无需任何外部依赖。只有 `neo4j_client.py` 需要Neo4j数据库。

### Q: 如何添加新的知识节点？

**A:** 在 `parser.py` 中的 `_add_*_knowledge()` 方法中添加新的 `KnowledgeNode`，然后调用 `_add_relationship()` 建立关系。

### Q: 节点ID有什么命名规则？

**A:** 推荐使用 `{category}_{concept}` 的格式，例如：
- `ellipse_definition`（椭圆定义）
- `hyperbola_asymptote`（双曲线渐近线）
- `error_parameter_triangle_direction`（易错点：参数三角形方向）

### Q: 如何查询Neo4j中的节点？

**A:** 使用 `Neo4jClient.run_query()` 方法：

```python
client = Neo4jClient()
client.connect()

# 查询所有定义节点
results = client.run_query(
    "MATCH (n {category: '定义'}) RETURN n.name, n.content"
)

# 查询单个节点的前置条件
results = client.run_query(
    "MATCH (a {id: $id})-[:PREREQUISITE*]->(n) RETURN n",
    {"id": "ellipse_eccentricity"}
)
```

## 许可证

本模块是苏格拉底式数学家庭教师项目的一部分。

## 版本信息

- 版本：1.0.0
- 最后更新：2026-04-06
- 知识图谱节点数：36
- 知识图谱关系数：32
