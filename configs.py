from typing import List, NotRequired, TypedDict


class ETCDConfig(TypedDict):
    '''type for etcd benchmark config'''
    server_count: NotRequired[int]
    test_name: NotRequired[str]
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int


class ETCDLConfig(TypedDict):
    '''type for etcd-light benchmark config'''
    server_count: NotRequired[int]
    test_name: NotRequired[str]
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int
    db_count: int
    read_mem: bool
    wal_file_count: int


class Config(TypedDict):
    '''type for etcd and etcd-light benchmark config'''
    etcd: List[ETCDConfig]
    etcdl: List[ETCDLConfig]
