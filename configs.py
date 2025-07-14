'''type definitions'''

from typing import NotRequired, TypedDict


class ClusterConfig(TypedDict):
    '''type for cluster configuration'''
    servers: list[str]
    client: str


class ETCDConfig(TypedDict):
    '''type for etcd benchmark config'''
    test_name: NotRequired[str]
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int


class ETCDLConfig(TypedDict):
    '''type for etcd-light benchmark config'''
    test_name: NotRequired[str]
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int
    db_count: int
    wal_file_count: int
    fast_path_writes: bool


class Config(TypedDict):
    '''type for etcd and etcd-light benchmark config'''
    cluster: ClusterConfig
    etcd: list[ETCDConfig]
    etcdl: list[ETCDLConfig]
