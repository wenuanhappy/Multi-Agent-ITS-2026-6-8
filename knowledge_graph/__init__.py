"""
知识图谱模块

提供圆锥曲线知识图谱的解析、查询和Neo4j导入功能
"""

from .parser import (
    ConicKnowledgeGraph,
    KnowledgeNode,
    NodeCategory,
    RelationType,
    Relationship,
    get_all_nodes,
    get_node_with_context,
    import_to_neo4j,
)

from .neo4j_client import (
    Neo4jClient,
    connect,
    run_query,
    clear_database,
    import_knowledge_graph,
)

__all__ = [
    # Parser
    "ConicKnowledgeGraph",
    "KnowledgeNode",
    "NodeCategory",
    "RelationType",
    "Relationship",
    "get_all_nodes",
    "get_node_with_context",
    "import_to_neo4j",
    # Neo4j Client
    "Neo4jClient",
    "connect",
    "run_query",
    "clear_database",
    "import_knowledge_graph",
]

__version__ = "1.0.0"
