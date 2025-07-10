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

    return Popen(['sudo', 'ssh', '-o', 'StrictHostKeyChecking=no',
                  f'root@{address}', cmd], stdout=PIPE, stderr=STDOUT,
                 text=True)


def wait_output(process: Popen, target: str) -> None:
    while True:
        if target in process.stdout.readline():
            print('found')
            return
