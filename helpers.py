from subprocess import PIPE, Popen, STDOUT


def remote_execute(address: str, cmd: str) -> Popen:
    '''
    execute a given command on an addressed computer
    :param address: the IP address of the computer to execute on
    :type address: str
    :param cmd: the command to execute
    :type cmd: str
    :returns: the process being executed
    :rtype: Popen
    '''

    print(f'$ {cmd}')
    return Popen(['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no',
                  f'root@{address}', f'PATH=$PATH:/usr/local/go/bin && {cmd}'],
                 stdout=PIPE, stderr=STDOUT, text=True)


def wait_output(process: Popen, target: str) -> None:
    '''
    wait for a specific output from a process
    :param process: the running process
    :type process: Popen
    :param target: the output to look for
    :type target: str
    '''

    print('waiting... ', end='')
    while True:
        if target in process.stdout.readline():
            print('continuing')
            return


def execute_wait(address: str, cmd: str, target: str) -> None:
    '''
    execute a given command on an addressed computer, then wait for a specific
    output from the process
    :param address: the IP address of the computer to execute on
    :type address: str
    :param cmd: the command to execute
    :type cmd: str
    :param target: the output to look for
    :type target: str
    '''

    wait_output(remote_execute(address, cmd), target)
