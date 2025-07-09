from subprocess import PIPE, Popen


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

    return Popen(['ssh', '-o', 'StrictHostKeyChecking=no', f'root@{address}', cmd], stdout=PIPE, stderr=PIPE, text=True)
