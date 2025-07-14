'''main benchmarking logic'''

from json import load
from pathlib import Path
from re import Pattern
from re import compile as rcompile
from subprocess import Popen, TimeoutExpired
from sys import exit

from configs import ClusterConfig, Config
from helpers import (config_get, exec_wait, extract_num, git_interact,
                     kill_servers, remote_exec_sync)

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses={server_addrs} -data-size={data_size} -num-ops={num_operations} -read-ratio={read_ratio} -num-clients={num_clients}'
ETCDL_SERVER_CMD: str = 'export PATH=\$PATH:/usr/local/go/bin && cd /local/go_networking_benchmark/run && cd .. && git fetch && git checkout dev && git pull && go build && mv networking_benchmark run/ && cd /local/go_networking_benchmark/run && ./networking_benchmark server -num-dbs={num_dbs} -max-db-index={db_indices) -node={node_num} -memory=false -wal-file-count={wal_file_count} -manual=fsync -flags=none -peer-connections=1 -peer-listen="10.10.1.{ip_num}:6900" -client-listen="10.10.1.{ip_num}:7000" -peer-addresses="{peer_addrs}" -fast-path-writes={fast_path_writes}'
ETCDL_CLIENT_CMD: str = 'cd /local/go_networking_benchmark && git fetch && git checkout dev && git pull && go build && ./networking_benchmark client -addresses={server_addrs} -data-size={data_size} -ops={num_operations} -read-ratio={read_ratio} -clients={num_clients} -read-mem=false -write-mem=false -find-leader=false'

CSV_HEADER: str = 'system,server_count,data_size,read_ratio,num_clients,num_dbs,wal_file_count,fast_path_writes,ops,med,p95,p99\n'
CSV_ENTRY: str = '{system},{server_count},{data_size},{read_ratio},{num_clients},{num_dbs},{wal_file_count},{fast_path_writes},{ops},{med},{p95},{p99}\n'

OPS_PATTERN: Pattern = rcompile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = rcompile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = rcompile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = rcompile(r' 99th\(\d+\) ')


if __name__ == '__main__':
    config: Config = {'cluster': {'servers': [],
                                  'client': None}, 'etcd': [], 'etcdl': []}
    with open('config.json', encoding='utf-8') as config_file:
        config = load(config_file)
    cluster: ClusterConfig = config.pop('cluster')

    for system, configs in config.items():
        for cfg in configs:
            server_cmd: str = ''
            client_cmd: str = ''
            clean_cmd: str = ''
            term_cmd: str = ''
            server_target: str = ''
            servers: list[int] = []
            cluster_servers: list[int] = cluster['servers']
            server_count: int = len(cluster_servers)
            match system:
                case 'etcd':
                    server_cmd = 'cd /local && sh run_etcd{node_num}.sh'
                    client_cmd = ETCD_CLIENT_CMD
                    clean_cmd = 'rm -rf /local/etcd/storage.etcd'
                    server_target = 'Starting etcd...'
                    term_cmd = '"killall etcd"'
                    servers = range(server_count)
                case 'etcdl':
                    server_cmd = ETCDL_SERVER_CMD
                    client_cmd = ETCDL_CLIENT_CMD
                    clean_cmd = 'rm -rf /local/go_networking_benchmark/run/*'
                    server_target = 'Trying to connect to peer '
                    term_cmd = '"killall networking_benc"'
                    servers = cluster_servers

            num_operations: int = cfg['num_operations']
            data_size: int = cfg['data_size']
            read_ratio: float = cfg['read_ratio']
            num_clients: int = cfg['num_clients']
            test_name: str = cfg['test_name']

            num_dbs: int = config_get(cfg, 'num_dbs')
            wal_file_count: int = config_get(cfg, 'wal_file_count')
            fast_path_writes: str = config_get(cfg, 'fast_path_writes')

            data_filepath: str = f'data/{test_name}.csv'
            addrs: str = ':{port_num},'.join(
                [f'10.10.1.{server}' for server in servers]) + ':{port_num}'

            processes: list[Popen] = []
            for i, server in enumerate(servers):
                server_cmd_fmt: str = ''
                match system:
                    case 'etcd':
                        server_cmd_fmt = server_cmd.format(node_num=server)
                    case 'etcdl':
                        server_cmd_fmt = server_cmd.format(num_dbs=num_dbs,
                                                           db_indices=num_operations + 100,
                                                           node_num=i,
                                                           wal_file_count=wal_file_count,
                                                           ip_num=server + 1,
                                                           peer_addrs=addrs.format(
                                                               port_num=6900),
                                                           fast_path_writes=fast_path_writes)
                processes.append(
                    exec_wait(server + 1, server_cmd_fmt, server_target))

            try:
                match system:
                    case 'etcd':
                        client_cmd = client_cmd.format(server_addrs=addrs.format(port_num=2379),
                                                       data_size=data_size,
                                                       num_operations=num_operations,
                                                       read_ratio=read_ratio,
                                                       num_clients=num_clients)
                    case 'etcdl':
                        client_cmd = client_cmd.format(server_addrs=addrs.format(port_num=7000),
                                                       data_size=data_size,
                                                       num_operations=num_operations,
                                                       read_ratio=read_ratio,
                                                       num_clients=num_clients)
                out: str = remote_exec_sync(
                    cluster['client'], client_cmd).splitlines()[-1].strip()
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
                                                     data_size=data_size,
                                                     read_ratio=read_ratio,
                                                     num_clients=num_clients,
                                                     num_dbs=num_dbs,
                                                     wal_file_count=wal_file_count,
                                                     fast_path_writes=fast_path_writes,
                                                     ops=ops,
                                                     med=med,
                                                     p95=p95,
                                                     p99=p99))

                kill_servers(processes, servers, clean_cmd, term_cmd)
            except KeyboardInterrupt:
                kill_servers(processes, servers, clean_cmd, term_cmd)
                exit(1)

    print('saving data')
    git_interact('add data/*')
    git_interact('commit -m "data update"')
    git_interact('push')
