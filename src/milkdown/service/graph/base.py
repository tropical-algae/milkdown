from itertools import chain
from py2neo import Graph, Node, Relationship

from milkdown.app.models.model_relation_tuples import EntityModel, RelationTuplesModel
from milkdown.common.util import load_json


data = load_json("relation.json")
relations = {r[1] for r in data["relations"]}
objs = set(chain.from_iterable([[r[0], r[2]] for r in data["relations"]]))


uri = "bolt://localhost:10009"
username = "neo4j"
password = "1206669327"


graph = Graph(uri, auth=(username, password))

nodes: dict[str, Node] = {}
# 创建节点
for obj in objs:
    node = Node("text1", name=obj)
    graph.create(node)
    nodes[obj] = node

for relation in data["relations"]:
# 创建关系
    obj = nodes[relation[0]]
    sbj = nodes[relation[2]]
    rlt = relation[1]
    friendship = Relationship(obj, rlt, sbj)
    graph.create(friendship)

class GraphStore:
    def __init__(
        self,
        store_url: str,
        store_user: str,
        store_passwd: str
    ):
        self.store = Graph(store_url, auth=(store_user, store_passwd))
    
    def create_relation_tuples(self, relation_tuples: list[RelationTuplesModel]) -> None:
        node_caches: dict[str, Node] = {}

        def get_or_create_node(node_data):
            if node_data.id not in node_caches:
                node = Node(node_data.name, id=node_data.id)
                self.store.create(node)
                node_caches[node_data.id] = node
            return node_caches[node_data.id]

        for relation_tuple in relation_tuples:
            subject_node = get_or_create_node(relation_tuple.subject)
            object_node = get_or_create_node(relation_tuple.object)

            relation = Relationship(subject_node, relation_tuple.relation.name, object_node)
            self.store.create(relation)
        
        # for obj in objs:
        #     node = Node("text1", name=obj)
        #     graph.create(node)
        #     node_caches[obj] = node

        # for relation in data["relations"]:
        # # 创建关系
        #     obj = node_caches[relation[0]]
        #     sbj = node_caches[relation[2]]
        #     rlt = relation[1]
        #     friendship = Relationship(obj, rlt, sbj)
        #     graph.create(friendship)
