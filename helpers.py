'''helper functions'''

from re import Pattern
from re import compile as rcompile
from re import findall
from subprocess import PIPE, Popen, run

from configs import ETCDLConfig

SSH_KWS: list[str] = ['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no']
ADDR: str = 'root@{addr}'
CMD: str = '{cmd}'


def config_get(config: ETCDLConfig, key: str) -> int | str:
    '''
    get the value from a key in a config object and return an empty string if the key does not exist
    :param config: the config object
    :type config: ETCDLConfig
    :param key: the key
    :type key: str
    :returns: the value of the key in the config
    :rtype: int | str
    '''

    val: int | bool = config.get(key, '')
    if isinstance(val, bool):
        return str(val).lower()
    return val


def exec_print(addr: str, cmd: str) -> None:
    '''
    prints the command and IP address given in a shell-like format
    :param addr: the IP address connected to
    :type addr: str
    :param cmd: the command being executed
    :type cmd: str
    '''

    print(f'{addr}$ {cmd}')


def exec_wait(addr: str, cmd: str, target: str) -> Popen:
    '''
    execute a given command on an addressed computer, then wait for a specific
    output from the process
    :param addr: IP address of the computer 
    :type addr: str 
    :param cmd: the command to execute
    :type cmd: str
    :param target: the output to look for
    :type target: str
    :returns: the running process
    :rtype: Popen
    '''

    addr_fmt: str = ADDR.format(addr=addr)
    exec_print(addr_fmt, cmd)
    process: Popen = Popen(
        SSH_KWS + [addr_fmt, CMD.format(cmd=cmd)], stdout=PIPE, stderr=PIPE, text=True)
    while True:
        if target in process.stdout.readline():
            return process


def extract_num(txt: str, pattern: Pattern) -> int:
    '''
    extracts a number from a piece of text based on a given regex
    :param txt: the text to extract the number from
    :type txt: str
    :param pattern: the pattern to find the number using
    :type pattern: Pattern
    :returns: the extracted number
    :rtype: int
    '''

    return int(findall(rcompile(r'\d+'), findall(pattern, txt)[0])[-1])


def kill_servers(processes: list[Popen], servers: list[str]) -> None:
    '''
    kill running servers and remove stored data
    :param processes: the server processes
    :type: processes: list[Popen]
    :param servers: the number of servers
    :type servers: list[str]
    :param clean_cmd: the command to clean stored data
    :type clean_cmd: str
    :param term_cmd: the command to terminate the server process
    :type term_cmd: str
    '''

    print('terminating servers')
    for server in servers:
        remote_exec_sync(server, 'killall etcd')
        remote_exec_sync(server, 'killall networking_benc')
        remote_exec_sync(server, 'rm -rf /local/etcd/storage.etcd')
        remote_exec_sync(server, 'rm -rf /local/go_networking_benchmark/run/*')

    for process in processes:
        process.kill()
        process.wait()


def remote_exec_sync(addr: str, cmd: str) -> str:
    '''
    execute a given command on an addressed computer and wait for it to complete
    :param addr: the IP of the computer
    :type addr: int 
    :param cmd: the command to execute
    :type cmd: str
    :returns: the output of the command
    :rtype: str
    '''
    addr_fmt: str = ADDR.format(addr=addr)
    exec_print(addr_fmt, cmd)
    return run(SSH_KWS + [addr_fmt, CMD.format(cmd=cmd)], stdout=PIPE, text=True).stdout
