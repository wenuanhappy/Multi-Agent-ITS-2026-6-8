"""
知识图谱模块使用示例

演示如何使用parser和neo4j_client模块来：
1. 加载和查询知识图谱
2. 获取节点及其上下文
3. 连接到Neo4j并导入数据
"""

import logging
import sys
from pathlib import Path

# Add parent directory to path to enable relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge_graph import (
    ConicKnowledgeGraph,
    get_all_nodes,
    get_node_with_context,
    Neo4jClient,
    connect,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_load_graph():
    """示例1：加载知识图谱并查看基本统计"""
    logger.info("=" * 60)
    logger.info("示例1：加载知识图谱")
    logger.info("=" * 60)

    graph = ConicKnowledgeGraph()

    logger.info(f"总节点数: {len(graph.nodes)}")
    logger.info(f"总关系数: {len(graph.relationships)}")

    # 按分类统计
    categories = {}
    for node in graph.nodes.values():
        cat = node.category.value
        categories[cat] = categories.get(cat, 0) + 1

    logger.info("\n按分类统计:")
    for cat, count in sorted(categories.items()):
        logger.info(f"  {cat}: {count}")


def example_2_query_node():
    """示例2：查询单个节点及其上下文"""
    logger.info("\n" + "=" * 60)
    logger.info("示例2：查询单个节点及其上下文")
    logger.info("=" * 60)

    # 查询椭圆离心率节点
    node_id = "ellipse_eccentricity"
    context = get_node_with_context(node_id)

    node = context["node"]
    logger.info(f"\n节点: {node['name']}")
    logger.info(f"分类: {node['category']}")
    logger.info(f"内容: {node['content']}")
    logger.info(f"描述: {node['description']}")

    logger.info(f"\n前置节点 ({len(context['prerequisites'])}):")
    for prereq in context["prerequisites"]:
        logger.info(f"  - {prereq['name']} ({prereq['category']})")

    logger.info(f"\n相关节点 ({len(context['related'])}):")
    for related in context["related"]:
        rel_type = related["relation_type"]
        rel_name = related["node"]["name"]
        logger.info(f"  - [{rel_type}] {rel_name}")


def example_3_get_all_nodes():
    """示例3：获取所有节点"""
    logger.info("\n" + "=" * 60)
    logger.info("示例3：获取所有节点")
    logger.info("=" * 60)

    all_nodes = get_all_nodes()
    logger.info(f"\n返回 {len(all_nodes)} 个节点")

    # 显示前5个
    logger.info("\n前5个节点:")
    for i, (node_id, node) in enumerate(list(all_nodes.items())[:5]):
        logger.info(f"  {i+1}. {node['name']} ({node['category']})")


def example_4_find_ellipse_nodes():
    """示例4：查找所有椭圆相关的节点"""
    logger.info("\n" + "=" * 60)
    logger.info("示例4：查找所有椭圆相关的节点")
    logger.info("=" * 60)

    all_nodes = get_all_nodes()
    ellipse_nodes = [
        (node_id, node) for node_id, node in all_nodes.items()
        if "ellipse" in node_id
    ]

    logger.info(f"\n找到 {len(ellipse_nodes)} 个椭圆相关节点:")
    for node_id, node in ellipse_nodes:
        logger.info(f"  - {node['name']} ({node['category']})")


def example_5_cypher_statements():
    """示例5：生成Neo4j Cypher语句"""
    logger.info("\n" + "=" * 60)
    logger.info("示例5：生成Neo4j Cypher语句")
    logger.info("=" * 60)

    graph = ConicKnowledgeGraph()
    cypher = graph.generate_cypher_statements()

    lines = cypher.split('\n')
    logger.info(f"\n生成 {len(lines)} 行Cypher语句")
    logger.info("\n前10行:")
    for i, line in enumerate(lines[:10]):
        if line.strip():
            logger.info(f"  {line[:100]}...")


def example_6_neo4j_connection():
    """示例6：Neo4j连接测试（不实际连接）"""
    logger.info("\n" + "=" * 60)
    logger.info("示例6：Neo4j客户端初始化")
    logger.info("=" * 60)

    client = Neo4jClient()
    logger.info(f"客户端初始化: {client}")
    logger.info(f"已连接: {client.is_connected}")
    logger.info(f"驱动: {client.driver}")

    logger.info("\n可用方法:")
    methods = [
        "connect", "disconnect", "run_query", "clear_database",
        "create_node", "create_relationship", "find_node",
        "find_prerequisites", "find_related_nodes", "import_knowledge_graph"
    ]
    for method in methods:
        logger.info(f"  - {method}()")

    logger.info("\n要连接到实际的Neo4j数据库:")
    logger.info("  1. 确保 neo4j 包已安装: pip install neo4j")
    logger.info("  2. 在 config/settings.py 中配置 NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD")
    logger.info("  3. 运行 client.connect()")
    logger.info("  4. 运行 client.import_knowledge_graph()")


def main():
    """运行所有示例"""
    logger.info("\n" + "█" * 60)
    logger.info("圆锥曲线知识图谱 - 使用示例")
    logger.info("█" * 60)

    try:
        example_1_load_graph()
        example_2_query_node()
        example_3_get_all_nodes()
        example_4_find_ellipse_nodes()
        example_5_cypher_statements()
        example_6_neo4j_connection()

        logger.info("\n" + "█" * 60)
        logger.info("所有示例执行完毕！")
        logger.info("█" * 60)

    except Exception as e:
        logger.error(f"执行出错: {e}", exc_info=True)


if __name__ == "__main__":
    main()
