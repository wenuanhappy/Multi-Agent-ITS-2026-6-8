"""
Neo4j数据库客户端

提供Neo4j连接管理、查询执行和知识图谱导入功能。
支持在Neo4j不可用时的内存图谱降级。
"""

import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import contextmanager

try:
    from neo4j import GraphDatabase, Driver, Session
    HAS_NEO4J = True
except ImportError:
    HAS_NEO4J = False
    Driver = None
    Session = None

from config.settings import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logger = logging.getLogger(__name__)


class Neo4jClient:
    """Neo4j数据库客户端"""

    def __init__(self):
        """初始化客户端"""
        self.driver: Optional[Driver] = None
        self.is_connected = False

    def connect(self) -> bool:
        """连接到Neo4j数据库

        Returns:
            True if connected successfully, False otherwise
        """
        if not HAS_NEO4J:
            logger.warning("neo4j package not installed. Please run: pip install neo4j")
            return False

        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD),
                encrypted=True,
                trust="TRUST_SYSTEM_CA_SIGNED_CERTIFICATES"
            )
            # 测试连接
            with self.driver.session() as session:
                session.run("RETURN 1")
            self.is_connected = True
            logger.info("Successfully connected to Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.is_connected = False
            return False

    def disconnect(self):
        """断开连接"""
        if self.driver:
            self.driver.close()
            self.is_connected = False
            logger.info("Disconnected from Neo4j")

    @contextmanager
    def session(self):
        """创建Neo4j会话的上下文管理器

        Yields:
            neo4j.Session instance
        """
        if not self.is_connected or not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
        session = self.driver.session()
        try:
            yield session
        finally:
            session.close()

    def run_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """执行Cypher查询

        Args:
            query: Cypher查询语句
            params: 查询参数（可选）
            **kwargs: 其他参数

        Returns:
            查询结果列表

        Raises:
            RuntimeError: 如果未连接到Neo4j
        """
        if not self.is_connected or not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")

        with self.session() as session:
            result = session.run(query, params or {})
            return [dict(record) for record in result]

    def clear_database(self) -> bool:
        """清空数据库中的所有节点和关系

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
            logger.info("Database cleared successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to clear database: {e}")
            return False

    def create_node(
        self,
        label: str,
        properties: Dict[str, Any]
    ) -> bool:
        """创建单个节点

        Args:
            label: 节点标签
            properties: 节点属性字典

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.session() as session:
                # 构建属性字符串
                props_list = [f"{k}: ${k}" for k in properties.keys()]
                props_str = "{" + ", ".join(props_list) + "}"
                query = f"CREATE (n:{label} {props_str})"
                session.run(query, **properties)
            return True
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            return False

    def create_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """创建两个节点之间的关系

        Args:
            source_id: 源节点id
            target_id: 目标节点id
            relation_type: 关系类型
            properties: 关系属性（可选）

        Returns:
            True if successful, False otherwise
        """
        try:
            with self.session() as session:
                props_list = [f"{k}: ${k}" for k in (properties or {}).keys()]
                props_str = ""
                if props_list:
                    props_str = "{" + ", ".join(props_list) + "}"

                query = (
                    f'MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) '
                    f'CREATE (a)-[:{relation_type} {props_str}]->(b)'
                )
                params = {
                    "source_id": source_id,
                    "target_id": target_id,
                    **(properties or {})
                }
                session.run(query, **params)
            return True
        except Exception as e:
            logger.error(f"Failed to create relationship: {e}")
            return False

    def find_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """根据id查找节点

        Args:
            node_id: 节点id

        Returns:
            节点数据字典，如果不存在则返回None
        """
        try:
            results = self.run_query(
                "MATCH (n {id: $id}) RETURN n",
                {"id": node_id}
            )
            return results[0] if results else None
        except Exception as e:
            logger.error(f"Failed to find node: {e}")
            return None

    def find_prerequisites(self, node_id: str) -> List[Dict[str, Any]]:
        """查找节点的所有前置节点

        Args:
            node_id: 节点id

        Returns:
            前置节点列表
        """
        try:
            results = self.run_query(
                'MATCH (a {id: $id})-[:PREREQUISITE*]->(n) RETURN DISTINCT n',
                {"id": node_id}
            )
            return results
        except Exception as e:
            logger.error(f"Failed to find prerequisites: {e}")
            return []

    def find_related_nodes(
        self,
        node_id: str,
        relation_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """查找与节点相关的其他节点

        Args:
            node_id: 节点id
            relation_type: 关系类型过滤（可选）

        Returns:
            相关节点列表
        """
        try:
            if relation_type:
                query = (
                    f'MATCH (a {{id: $id}})-[:{relation_type}]->(n) RETURN DISTINCT n'
                )
            else:
                query = 'MATCH (a {id: $id})-[]->(n) RETURN DISTINCT n'
            results = self.run_query(query, {"id": node_id})
            return results
        except Exception as e:
            logger.error(f"Failed to find related nodes: {e}")
            return []

    def import_knowledge_graph(self) -> bool:
        """从parser导入完整的知识图谱

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected:
            logger.error("Not connected to Neo4j")
            return False

        try:
            from .parser import ConicKnowledgeGraph

            graph = ConicKnowledgeGraph()

            # 清空现有数据
            if not self.clear_database():
                logger.warning("Failed to clear database, continuing with import...")

            # 创建所有节点
            logger.info(f"Importing {len(graph.nodes)} nodes...")
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

                if not self.create_node(node.category.value, props):
                    logger.warning(f"Failed to create node {node_id}")

            # 创建所有关系
            logger.info(f"Importing {len(graph.relationships)} relationships...")
            for rel in graph.relationships:
                if not self.create_relationship(
                    rel.source_id,
                    rel.target_id,
                    rel.type.value,
                    {"label": rel.label} if rel.label else None
                ):
                    logger.warning(f"Failed to create relationship {rel.source_id}->{rel.target_id}")

            logger.info("Knowledge graph imported successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to import knowledge graph: {e}")
            return False


def connect() -> Optional[Neo4jClient]:
    """创建并连接到Neo4j

    Returns:
        Neo4jClient instance if successful, None otherwise
    """
    client = Neo4jClient()
    if client.connect():
        return client
    return None


def run_query(
    driver: Neo4jClient,
    cypher: str,
    params: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """执行查询（兼容旧接口）

    Args:
        driver: Neo4jClient instance
        cypher: Cypher查询
        params: 查询参数

    Returns:
        查询结果
    """
    return driver.run_query(cypher, params)


def clear_database(driver: Neo4jClient) -> bool:
    """清空数据库（兼容旧接口）

    Args:
        driver: Neo4jClient instance

    Returns:
        True if successful
    """
    return driver.clear_database()


def import_knowledge_graph(driver: Neo4jClient) -> bool:
    """导入知识图谱（兼容旧接口）

    Args:
        driver: Neo4jClient instance

    Returns:
        True if successful
    """
    return driver.import_knowledge_graph()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    # 尝试连接
    client = connect()
    if client:
        print("Connected to Neo4j!")

        # 导入知识图谱
        if client.import_knowledge_graph():
            print("Knowledge graph imported successfully!")

            # 测试查询
            results = client.run_query("MATCH (n) RETURN COUNT(n) as count")
            if results:
                print(f"Total nodes: {results[0].get('count', 0)}")

        client.disconnect()
    else:
        print("Failed to connect to Neo4j")
        print("Make sure:")
        print("1. Neo4j is running")
        print("2. neo4j package is installed: pip install neo4j")
        print("3. NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD are set in config/settings.py")
