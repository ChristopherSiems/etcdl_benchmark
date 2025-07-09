from helpers import remote_execute

if __name__ == '__main__':
    print(remote_execute('10.10.1.1',
          'echo "hello world"').communicate()[0].strip())
