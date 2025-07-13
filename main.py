'''main benchmarking logic'''

from json import load
from pathlib import Path
from re import Pattern
from re import compile as rcompile
from subprocess import Popen, TimeoutExpired, run
from typing import List, NotRequired, TypedDict

from helpers import exec_wait, extract_num, kill_servers, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses={server_addrs} -data-size={data_size} -num-ops={num_operations} -read-ratio={read_ratio} -num-clients={num_clients}'
ETCDL_SERVER_CMD: str = 'cd /local/go_networking_benchmark/run && cd .. && git fetch && git checkout dev && git pull && go build && mv networking_benchmark run/ && cd /local/go_networking_benchmark/run && ./networking_benchmark server -num-dbs=5 -max-db-index={num_operations} -node={i} -memory=false -wal-file-count={wal_file_count} -manual=fsync -flags=none -peer-connections=1 -peer-listen="10.10.1.{j}:6900" -client-listen="10.10.1.{j}:7000" -peer-addresses="{peer_addrs}" -fast-path-writes=false'
ETCDL_CLIENT_CMD: str = 'cd /local/go_networking_benchmark && git fetch &&  git checkout dev && git pull && go build && ./networking_benchmark client -addresses={server_addrs} -data-size={data_size} -ops={num_operations} -read-ratio={read_ratio} -clients={num_clients} -read-mem={read_mem} -write-mem=false -find-leader=false'

CSV_HEADER: str = 'system,server_count,data_size,read_ratio,num_clients,read_mem,wal_file_count,ops,med,p95,p99\n'
CSV_ENTRY: str = '{system},{server_count},{data_size},{read_ratio},{num_clients},{read_mem},{wal_file_count},{ops},{med},{p95},{p99}\n'

OPS_PATTERN: Pattern = rcompile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = rcompile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = rcompile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = rcompile(r' 99th\(\d+\) ')


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
    read_mem: bool
    wal_file_count: int


class Config(TypedDict):
    '''type for etcd and etcd-light benchmark config'''
    etcd: List[ETCDConfig]
    etcdl: List[ETCDLConfig]


if __name__ == '__main__':
    config: Config = {'etcd': [], 'etcdl': []}
    with open('config.json', encoding='utf-8') as config_file:
        config = load(config_file)

    for system, configs in config.items():
        server_cmd: str = ''
        client_cmd: str = ''
        clean_cmd: str = ''
        server_target: str = ''
        match system:
            case 'etcd':
                server_cmd = 'cd /local && sh run_etcd{i}.sh'
                client_cmd = ETCD_CLIENT_CMD
                clean_cmd = 'rm -rf /local/etcd/storage.etcd'
                server_target = 'Starting etcd...'
            case 'etcdl':
                server_cmd = ETCDL_SERVER_CMD
                client_cmd = ETCDL_CLIENT_CMD
                clean_cmd = 'rm -rf /local/go_networking_benchmark/run/*'
                server_target = 'Trying to connect to peer '

        for cfg in configs:
            server_count: int = cfg['server_count']
            test_name: str = cfg['test_name']
            data_filepath: str = f'data/{test_name}.csv'
            addrs: str = ':{port_num},'.join(
                [f'10.10.1.{i}' for i in range(1, server_count + 1)]) + ':{port_num}'

            processes: List[Popen] = []
            for i in range(server_count):
                server_cmd_fmt: str = ''
                match system:
                    case 'etcd':
                        server_cmd_fmt = server_cmd.format(i=i)
                    case 'etcdl':
                        server_cmd_fmt = server_cmd.format(i=i,
                                                           j=i + 1,
                                                           num_operations=cfg['num_operations'] + 100,
                                                           wal_file_count=cfg['wal_file_count'],
                                                           peer_addrs=addrs.format(port_num=6900))
                processes.append(
                    exec_wait(f'10.10.1.{i + 1}', server_cmd_fmt, server_target))

            try:
                match system:
                    case 'etcd':
                        client_cmd = client_cmd.format(server_addrs=addrs.format(port_num=2379),
                                                       data_size=cfg['data_size'],
                                                       num_operations=cfg['num_operations'],
                                                       read_ratio=cfg['read_ratio'],
                                                       num_clients=cfg['num_clients'])
                    case 'etcdl':
                        client_cmd = client_cmd.format(server_addrs=addrs.format(port_num=7000),
                                                       data_size=cfg['data_size'],
                                                       num_operations=cfg['num_operations'],
                                                       read_ratio=cfg['read_ratio'],
                                                       num_clients=cfg['num_clients'],
                                                       read_mem=str(cfg['read_mem']).lower())
                out: str = remote_exec_sync(
                    f'10.10.1.{server_count + 1}', client_cmd).splitlines()[-1].strip()
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
                    data_file.write(CSV_ENTRY.format(system=system,
                                                     server_count=server_count,
                                                     data_size=cfg['data_size'],
                                                     read_ratio=cfg['read_ratio'],
                                                     num_clients=cfg['num_clients'],
                                                     read_mem=cfg.get(
                                                         'read_mem', ''),
                                                     wal_file_count=cfg.get(
                                                         'wal_file_count', ''),
                                                     ops=ops,
                                                     med=med,
                                                     p95=p95,
                                                     p99=p99))

                kill_servers(processes, server_count, clean_cmd)
            except KeyboardInterrupt:
                kill_servers(processes, server_count, clean_cmd)

    print('saving data')
    run(['sudo', 'git', 'add', 'data/*'], stdout=PIPE, stderr=PIPE, text=True)
    run(['sudo', 'git', 'commit', '-m', '"data update"'],
        stdout=PIPE, stderr=PIPE, text=True)
    run(['sudo', 'git', 'push'], stdout=PIPE, stderr=PIPE, text=True)
