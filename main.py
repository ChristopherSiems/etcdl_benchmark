'''main benchmarking logic'''

from json import load
from re import Pattern
from re import compile as rcompile
from typing import TypedDict

from helpers import exec_wait, extract_num, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size={data_size} -num-ops={num_operations} -read-ratio={read_ratio} -num-clients={num_clients}'

OPS_PATTERN: Pattern = rcompile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = rcompile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = rcompile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = rcompile(r' 99th\(\d+\) ')


class ETCDConfig(TypedDict):
    '''type for etcd benchmark config'''
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int


class Config(TypedDict):
    '''type for etcd-light benchmark config'''
    etcd: ETCDConfig


if __name__ == '__main__':
    config: Config = {}
    with open('config.json', encoding='utf-8') as file:
        config = load(file)

    exec_wait('10.10.1.1', 'cd /local && sh run_etcd0.sh',
              'Starting etcd...')
    exec_wait('10.10.1.2', 'cd /local && sh run_etcd1.sh',
              'Starting etcd...')
    exec_wait('10.10.1.3', 'cd /local && sh run_etcd2.sh',
              'Starting etcd...')
    print()

    for cfg in config['etcd']:
        out: str = remote_exec_sync(
            '10.10.1.4',
            ETCD_CLIENT_CMD.format(**cfg)).splitlines()[-1].strip()
        print()

        ops: int = extract_num(out, OPS_PATTERN)
        med: int = extract_num(out, MED_PATTERN)
        p95: int = extract_num(out, P95_PATTERN)
        p99: int = extract_num(out, P99_PATTERN)
        print(f'ops: {ops}')
        print(f'med: {med}')
        print(f'p95: {p95}')
        print(f'p99: {p99}')
        print()
