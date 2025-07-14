'''helper functions'''

from os import environ
from re import Pattern
from re import compile as rcompile
from re import findall
from subprocess import PIPE, Popen, run

from configs import ETCDLConfig

SSH_KWS: list[str] = ['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no']
ADDR: str = 'root@10.10.1.{addr}'
CMD: str = '\'stdbuf -oL -eL bash -c "{cmd}"\''


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


def exec_wait(addr: int, cmd: str, target: str) -> Popen:
    '''
    execute a given command on an addressed computer, then wait for a specific
    output from the process
    :param addr: the final digit of the IP address of the server
    :type addr: int 
    :param cmd: the command to execute
    :type cmd: str
    :param target: the output to look for
    :type target: str
    :returns: the running process
    :rtype: Popen
    '''

    env: dict[str, str] = environ.copy()
    env['PATH'] = env['PATH'] + ':/usr/local/go/bin'
    addr_fmt: str = ADDR.format(addr=addr)
    exec_print(addr_fmt, cmd)
    process: Popen = Popen(
        SSH_KWS + [addr_fmt, CMD.format(cmd=cmd)], stdout=PIPE, stderr=PIPE, text=True, env=env)
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


def kill_servers(processes: list[Popen], servers: list[int], clean_cmd: str, term_cmd: str) -> None:
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
    for process, server in zip(processes, servers):
        remote_exec_sync(server, term_cmd)
        process.kill()
        process.wait()
        remote_exec_sync(server, clean_cmd)


def remote_exec_sync(addr: str, cmd: str) -> str:
    '''
    execute a given command on an addressed computer and wait for it to complete
    :param addr: the final digit of the IP address of the server
    :type addr: int 
    :param cmd: the command to execute
    :type cmd: str
    :returns: the output of the command
    :rtype: str
    '''
    addr_fmt: str = ADDR.format(addr=addr)
    exec_print(addr_fmt, cmd)
    out: str = run(SSH_KWS + [addr_fmt, CMD.format(cmd=cmd)],
                   stdout=PIPE, stderr=PIPE, text=True).stdout
    return out
