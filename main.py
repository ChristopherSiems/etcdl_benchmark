from helpers import execute_wait

if __name__ == '__main__':
    execute_wait('10.10.1.1', 'cd /local && sh run_etcd0.sh',
                 'Starting etcd...')
    execute_wait('10.10.1.2', 'cd /local && sh run_etcd1.sh',
                 'Starting etcd...')
    execute_wait('10.10.1.3', 'cd /local && sh run_etcd2.sh',
                 'Starting etcd...')
