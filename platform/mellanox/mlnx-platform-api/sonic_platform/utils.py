import subprocess

# flags to indicate whether this process is running in docker or host
_is_host = None


def read_str_from_file(file_path, default='', raise_exception=False):
    """
    Read string content from file
    :param file_path: File path
    :param default: Default return value if any exception occur
    :param raise_exception: Raise exception to caller if True else just return default value
    :return: String content of the file
    """
    try:
        with open(file_path, 'r') as f:
            value = f.read().strip()
    except (ValueError, IOError) as e:
        if not raise_exception:
            value = default
        else:
            raise e

    return value


def read_int_from_file(file_path, default=0, raise_exception=False):
    """
    Read content from file and cast it to integer
    :param file_path: File path
    :param default: Default return value if any exception occur
    :param raise_exception: Raise exception to caller if True else just return default value
    :return: Integer value of the file content
    """
    try:
        with open(file_path, 'r') as f:
            value = int(f.read().strip())
    except (ValueError, IOError) as e:
        if not raise_exception:
            value = default
        else:
            raise e

    return value


def write_file(file_path, content, raise_exception=False):
    """
    Write the given value to a file
    :param file_path: File path
    :param content: Value to write to the file
    :param raise_exception: Raise exception to caller if True
    :return: True if write success else False
    """
    try:
        with open(file_path, 'w') as f:
            f.write(str(content))
    except (ValueError, IOError) as e:
        if not raise_exception:
            return False
        else:
            raise e
    return True


def is_host():
    """
    Test whether current process is running on the host or an docker
    return True for host and False for docker
    """
    global _is_host
    if _is_host is not None:
        return _is_host
        
    _is_host = False
    try:
        proc = subprocess.Popen("docker --version 2>/dev/null", 
                                stdout=subprocess.PIPE, 
                                shell=True, 
                                stderr=subprocess.STDOUT, 
                                universal_newlines=True)
        stdout = proc.communicate()[0]
        proc.wait()
        result = stdout.rstrip('\n')
        if result != '':
            _is_host = True

    except OSError as e:
        pass

    return _is_host
