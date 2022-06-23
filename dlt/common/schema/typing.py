from typing import Dict, List, Literal, Mapping, Sequence, Set, TypedDict


DataType = Literal["text", "double", "bool", "timestamp", "bigint", "binary", "complex", "decimal", "wei"]
HintType = Literal["not_null", "partition", "cluster", "primary_key", "foreign_key", "sort", "unique"]
ColumnProp = Literal["name", "data_type", "nullable", "partition", "cluster", "primary_key", "foreign_key", "sort", "unique"]

DATA_TYPES: Set[DataType] = set(["text", "double", "bool", "timestamp", "bigint", "binary", "complex", "decimal", "wei"])
COLUMN_PROPS: Set[ColumnProp] = set(["name", "data_type", "nullable", "partition", "cluster", "primary_key", "foreign_key", "sort", "unique"])
COLUMN_HINTS: Set[HintType] = set(["partition", "cluster", "primary_key", "foreign_key", "sort", "unique"])

class ColumnBase(TypedDict, total=True):
    name: str
    data_type: DataType
    nullable: bool

class Column(ColumnBase, total=True):
    partition: bool
    cluster: bool
    unique: bool
    sort: bool
    primary_key: bool
    foreign_key: bool

Table = Dict[str, Column]
SchemaTables = Dict[str, Table]
SchemaUpdate = Dict[str, List[Column]]


class StoredSchema(TypedDict, total=True):
    version: int
    engine_version: int
    name: str
    tables: SchemaTables
    preferred_types: Mapping[str, DataType]
    hints: Mapping[HintType, Sequence[str]]
    excludes: Sequence[str]
    includes: Sequence[str]
