from re import compile, Pattern

from helpers import exec_wait, extract_num, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size=1 -num-ops=10000 -read-ratio=1.0 -num-clients=5'

OPS_PATTERN: Pattern = compile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = compile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = compile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = compile(r' 99th\(\d+\) ')

if __name__ == '__main__':
    exec_wait('10.10.1.1', 'cd /local && sh run_etcd0.sh',
              'Starting etcd...')
    exec_wait('10.10.1.2', 'cd /local && sh run_etcd1.sh',
              'Starting etcd...')
    exec_wait('10.10.1.3', 'cd /local && sh run_etcd2.sh',
              'Starting etcd...')

    out: str = remote_exec_sync(
        '10.10.1.4', ETCD_CLIENT_CMD).splitlines()[-1].strip()
    print(f'ops: {extract_num(out, OPS_PATTERN)}')
    print(f'med: {extract_num(out, MED_PATTERN)}')
    print(f'p95: {extract_num(out, P95_PATTERN)}')
    print(f'p99: {extract_num(out, P99_PATTERN)}')
