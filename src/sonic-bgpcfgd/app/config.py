import os
import tempfile

from .vars import g_debug
from .log import log_crit, log_err
from .util import run_command


class ConfigMgr(object):
    """ The class represents frr configuration """
    def __init__(self):
        self.current_config = None

    def reset(self):
        """ Reset stored config """
        self.current_config = None

    def update(self):
        """ Read current config from FRR """
        self.current_config = None
        ret_code, out, err = run_command(["vtysh", "-c", "show running-config"])
        if ret_code != 0:
            log_crit("can't update running config: rc=%d out='%s' err='%s'" % (ret_code, out, err))
            return
        self.current_config = self.to_canonical(out)

    def push(self, cmd):
        """
        Push new changes to FRR
        :param cmd: configuration change for FRR. Type: String
        :return: True if change was applied successfully, False otherwise
        """
        return self.write(cmd)

    def write(self, cmd):
        """
        Write configuration change to FRR.
        :param cmd: new configuration to write into FRR. Type: String
        :return: True if change was applied successfully, False otherwise
        """
        fd, tmp_filename = tempfile.mkstemp(dir='/tmp')
        os.close(fd)
        with open(tmp_filename, 'w') as fp:
            fp.write("%s\n" % cmd)
        command = ["vtysh", "-f", tmp_filename]
        ret_code, out, err = run_command(command)
        if not g_debug:
            os.remove(tmp_filename)
        if ret_code != 0:
            err_tuple = str(cmd), ret_code, out, err
            log_err("ConfigMgr::push(): can't push configuration '%s', rc='%d', stdout='%s', stderr='%s'" % err_tuple)
        if ret_code == 0:
            self.current_config = None  # invalidate config
        return ret_code == 0

    @staticmethod
    def to_canonical(raw_config):
        """
        Convert FRR config into canonical format
        :param raw_config: config in frr format
        :return: frr config in canonical format
        """
        parsed_config = []
        lines_with_comments = raw_config.split("\n")
        lines = [line for line in lines_with_comments
                 if not line.strip().startswith('!') and line.strip() != '']
        if len(lines) == 0:
            return []
        cur_path = [lines[0]]
        cur_offset = ConfigMgr.count_spaces(lines[0])
        for line in lines:
            n_spaces = ConfigMgr.count_spaces(line)
            s_line = line.strip()
#            assert(n_spaces == cur_offset or (n_spaces + 1) == cur_offset or (n_spaces - 1) == cur_offset)
            if n_spaces == cur_offset:
                cur_path[-1] = s_line
            elif n_spaces > cur_offset:
                cur_path.append(s_line)
            elif n_spaces < cur_offset:
                cur_path = cur_path[:-2]
                cur_path.append(s_line)
            parsed_config.append(cur_path[:])
            cur_offset = n_spaces
        return parsed_config

    @staticmethod
    def count_spaces(line):
        """ Count leading spaces in the line """
        return len(line) - len(line.lstrip())

    @staticmethod
    def from_canonical(canonical_config):
        """
        Convert config from canonical format into FRR raw format
        :param canonical_config: config in a canonical format
        :return: config in the FRR raw format
        """
        out = ""
        for lines in canonical_config:
            spaces = len(lines) - 1
            out += " " * spaces + lines[-1] + "\n"

        return out