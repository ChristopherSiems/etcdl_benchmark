from re import compile, findall, Pattern

from helpers import exec_wait, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size=1 -num-ops=10000 -read-ratio=1.0 -num-clients=5'

OPS_PATTERN: Pattern = compile(r' OPS\(\d+\) ')
MED_PATTERN: Pattern = compile(r' 50th\(\d+\) ')
P95_PATTERN: Pattern = compile(r' 95th\(\d+\) ')
P99_PATTERN: Pattern = compile(r' 99th\(\d+\) ')
NUM_PATTERN: Pattern = compile(r'\d+')

if __name__ == '__main__':
    exec_wait('10.10.1.1', 'cd /local && sh run_etcd0.sh',
              'Starting etcd...')
    exec_wait('10.10.1.2', 'cd /local && sh run_etcd1.sh',
              'Starting etcd...')
    exec_wait('10.10.1.3', 'cd /local && sh run_etcd2.sh',
              'Starting etcd...')

    out: str = remote_exec_sync(
        '10.10.1.4', ETCD_CLIENT_CMD).splitlines()[-1].strip()
    print(f'ops: {findall(NUM_PATTERN, findall(OPS_PATTERN, out)[0])[0]}')
    print(f'med: {findall(NUM_PATTERN, findall(MED_PATTERN, out)[0])[0]}')
    print(f'p95: {findall(NUM_PATTERN, findall(P95_PATTERN, out)[0])[0]}')
    print(f'p99: {findall(NUM_PATTERN, findall(P99_PATTERN, out)[0])[0]}')
