from helpers import remote_execute, wait_output

ETCD_CLIENT_CMD: str = 'cd /local/etcd-client && git pull && go build && ./etcd-client -addresses=10.10.1.1:2379,10.10.1.2:2379,10.10.1.3:2379 -data-size=1 -num-ops=10000 -read-ratio=1.0 -num-clients=5'

if __name__ == '__main__':
    wait_output(remote_execute(
        '10.10.1.1', 'cd /local && sh run_etcd0.sh'), '')
