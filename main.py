from helpers import exec_wait, remote_exec_sync

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size=1 -num-ops=10000 -read-ratio=1.0 -num-clients=5'

if __name__ == '__main__':
    exec_wait('10.10.1.1', 'cd /local && sh run_etcd0.sh',
              'Starting etcd...')
    exec_wait('10.10.1.2', 'cd /local && sh run_etcd1.sh',
              'Starting etcd...')
    exec_wait('10.10.1.3', 'cd /local && sh run_etcd2.sh',
              'Starting etcd...')

    print(remote_exec_sync('10.10.1.4',
          ETCD_CLIENT_CMD).splitlines()[-1].strip())
