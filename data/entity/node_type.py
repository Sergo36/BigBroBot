from enum import Enum


class NodeType(Enum):
    Shardeum = 1
    EYWA = 2
    Muon = 3


class NodeTypeClass():
    id: int = 0
    name: str = ""
    discription: str = ""
    cost: float = 0.0


    def initialisation_sql(self, sql_res):
        self.id = sql_res[0]
        self.name = sql_res[1]
        self.discription = sql_res[2]
        self.cost = sql_res[3]
        return self
