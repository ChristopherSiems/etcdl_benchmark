from re import Pattern
from re import compile as rcompile
from re import findall
from subprocess import PIPE, Popen, TimeoutExpired, run
from typing import List

from configs import ETCDLConfig

SSH_KWS: List[str] = ['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no']
ADDR: str = 'root@{addr}.utah.cloudlab.us'
CMD: str = 'sudo bash -c "PATH=$PATH:/usr/local/go/bin && {cmd}"'


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
    :param addr: the name of the server
    :type addr: str
    :param cmd: the command to execute
    :type cmd: str
    :param target: the output to look for
    :type target: str
    :returns: the running process
    :rtype: Popen
    '''

    exec_print(addr, cmd)
    process: Popen = Popen(
        SSH_KWS + [ADDR.format(addr=addr), CMD.format(cmd=cmd)], stdout=PIPE, stderr=PIPE, text=True)
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


def git_interact(cmd: str) -> None:
    '''
    executes git command
    :param cmd: the git command
    :type cmd: str
    '''

    print(f'$ git {cmd}')
    run(['sudo', 'git', cmd], stdout=PIPE, stderr=PIPE, text=True)


def kill_servers(processes: List[Popen], servers: List[str], clean_cmd: str) -> None:
    '''
    kill running servers and remove stored data
    :param processes: the server processes
    :type: processes: List[Popen]
    :param servers: the number of servers
    :type servers: List[str]
    :param clean_cmd: the command to clean stored data
    :type clean_cmd: str
    '''

    print('terminating servers')
    for process in processes:
        process.terminate()
        try:
            process.wait(timeout=15)
        except TimeoutExpired:
            process.kill()
            process.wait()

    for vm in servers:
        remote_exec_sync(vm, clean_cmd)


def remote_exec_sync(addr: str, cmd: str) -> str:
    '''
    execute a given command on an addressed computer and wait for it to
    complete
    :param addr: the name of the server
    :type addr: str
    :param cmd: the command to execute
    :type cmd: str
    :returns: the output of the command
    :rtype: str
    '''

    exec_print(addr, cmd)
    out: str = run(SSH_KWS + [ADDR.format(addr=addr), CMD.format(cmd=cmd)],
                   stdout=PIPE, stderr=PIPE, text=True).stdout
    return out
