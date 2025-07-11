'''main benchmarking logic'''

from json import load
from pathlib import Path
from re import Pattern
from re import compile as rcompile
from subprocess import Popen
from typing import List, NotRequired, TypedDict

from helpers import exec_wait, extract_num, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size={data_size} -num-ops={num_operations} -read-ratio={read_ratio} -num-clients={num_clients}'

OPS_PATTERN: Pattern = rcompile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = rcompile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = rcompile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = rcompile(r' 99th\(\d+\) ')

CSV_HEADER: str = 'system,server_count,num_operations,read_ratio,num_clients,ops,med,p95,p99\n'
CSV_ENTRY: str = '{system},{server_count},{num_operations},{read_ratio},{num_clients},{ops},{med},{p95},{p99}\n'


class ETCDConfig(TypedDict):
    '''type for etcd benchmark config'''
    server_count: NotRequired[int]
    test_name: NotRequired[str]
    data_size: int
    num_operations: int
    read_ratio: float
    num_clients: int


class Config(TypedDict):
    '''type for etcd and etcd-light benchmark config'''
    etcd: List[ETCDConfig]


if __name__ == '__main__':
    config: Config = {'etcd': []}
    with open('config.json', encoding='utf-8') as config_file:
        config = load(config_file)

    for cfg in config['etcd']:
        server_count: int = cfg.pop('server_count')
        test_name: str = cfg.pop('test_name')
        data_filepath: str = f'data/{test_name}.csv'

        processes: List[Popen] = []
        for i in range(server_count):
            processes.append(exec_wait(
                f'10.10.1.{i + 1}', f'cd /local && sh run_etcd{i}.sh', 'Starting etcd...'))

        out: str = remote_exec_sync(
            '10.10.1.4', ETCD_CLIENT_CMD.format(**cfg)).splitlines()[-1].strip()
        ops: int = extract_num(out, OPS_PATTERN)
        med: int = extract_num(out, MED_PATTERN)
        p95: int = extract_num(out, P95_PATTERN)
        p99: int = extract_num(out, P99_PATTERN)
        print(f'ops: {ops}')
        print(f'med: {med}')
        print(f'p95: {p95}')
        print(f'p99: {p99}')

        if not Path(data_filepath).exists():
            with open(data_filepath, 'w', encoding='utf-8') as data_file:
                data_file.write(CSV_HEADER)
        with open(data_filepath, 'a', encoding='utf-8') as data_file:
            data_file.write(CSV_ENTRY.format(
                system='etcd', server_count=server_count, ops=ops, med=med, p95=p95, p99=p99, **cfg))

        print('terminating servers')
        for process in processes:
            process.terminate()
            try:
                process.wait(timeout=15)
            except TimeoutExpired:
                process.kill()
                process.wait()

        print('clearing storage')
        for i in range(server_count):
            remote_exec_sync(f'10.10.1.{i + 1}',
                             'rm -rf /local/etcd/storage.etcd')
