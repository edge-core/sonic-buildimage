import functools
import subprocess
from sonic_py_common.logger import Logger

logger = Logger()

# flags to indicate whether this process is running in docker or host
_is_host = None


def read_from_file(file_path, target_type, default='', raise_exception=False, log_func=logger.log_error):
    """
    Read content from file and convert to target type
    :param file_path: File path
    :param target_type: target type
    :param default: Default return value if any exception occur
    :param raise_exception: Raise exception to caller if True else just return default value
    :param log_func: function to log the error
    :return: String content of the file
    """
    try:
        with open(file_path, 'r') as f:
            value = target_type(f.read().strip())
    except (ValueError, IOError) as e:
        if log_func:
            log_func('Failed to read from file {} - {}'.format(file_path, repr(e)))
        if not raise_exception:
            value = default
        else:
            raise e

    return value


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


def _key_value_converter(content):
    ret = {}
    for line in content.splitlines():
        k,v = line.split(':')
        ret[k.strip()] = v.strip()
    return ret


def read_key_value_file(file_path, default={}, raise_exception=False, log_func=logger.log_error):
    """Read file content and parse the content to a dict. The file content should like:
       key1:value1
       key2:value2

    Args:
        file_path (str): file path
        default (dict, optional): default return value. Defaults to {}.
        raise_exception (bool, optional): If exception should be raised or hiden. Defaults to False.
        log_func (optional): logger function.. Defaults to logger.log_error.
    """
    return read_from_file(file_path=file_path, target_type=_key_value_converter, default=default, raise_exception=raise_exception, log_func=log_func)


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


def default_return(return_value):
    def wrapper(method):
        @functools.wraps(method)
        def _impl(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except:
                return return_value
        return _impl
    return wrapper
