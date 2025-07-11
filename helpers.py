from re import Pattern
from re import compile as rcompile
from re import findall
from subprocess import PIPE, Popen, run
from typing import List

SSH_KWS: List[str] = ['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no']
ADDR: str = 'root@{addr}'
CMD: str = 'PATH=$PATH:/usr/local/go/bin && {cmd}'


def exec_print(addr: str, cmd: str) -> None:
    '''
    prints the command and IP address given in a shell-like format
    :param addr: the IP address connected to
    :type addr: str
    :param cmd: the command being executed
    :type cmd: str
    '''

    print(f'{addr}$ {cmd}')


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


def remote_exec(addr: str, cmd: str) -> Popen:
    '''
    execute a given command on an addressed computer
    :param addr: the IP address of the computer to execute on
    :type addr: str
    :param cmd: the command to execute
    :type cmd: str
    :returns: the process being executed
    :rtype: Popen
    '''

    exec_print(addr, cmd)
    return Popen(SSH_KWS + [ADDR.format(addr=addr), CMD.format(cmd=cmd)],
                 stdout=PIPE, stderr=PIPE, text=True)


def remote_exec_sync(addr: str, cmd: str) -> str:
    '''
    execute a given command on an addressed computer and wait for it to
    complete
    :param addr: the IP address of the computer to execute on
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


def wait_output(process: Popen, target: str) -> None:
    '''
    wait for a specific output from a process
    :param process: the running process
    :type process: Popen
    :param target: the output to look for
    :type target: str
    '''

    while True:
        if target in process.stdout.readline():
            return


def exec_wait(addr: str, cmd: str, target: str) -> None:
    '''
    execute a given command on an addressed computer, then wait for a specific
    output from the process
    :param addr: the IP address of the computer to execute on
    :type addr: str
    :param cmd: the command to execute
    :type cmd: str
    :param target: the output to look for
    :type target: str
    '''

    wait_output(remote_exec(addr, cmd), target)
