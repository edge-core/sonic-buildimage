import json
import filecmp
import os
import re
import sys

PY3x = sys.version_info >= (3, 0)
PYvX_DIR = "py3" if PY3x else "py2"
PYTHON_INTERPRETTER = "python3" if PY3x else "python2"

def tuple_to_str(tuplestr):
    """ Convert Python tuple '('elem1', 'elem2')' representation into string on the for "elem1|elem2" """
    def to_str(tupleobj):
        tupleobj = re.sub(r"([\(\)])", '"', tupleobj.group(0))
        return re.sub(r"( *, *)", '|', tupleobj).replace("'", '')

    return re.sub(r"(\(.*?\))", to_str, tuplestr)

def to_dict(dictstr):
    """ Convert string represention of Python dict into dict """
    # handle tuple elements
    dictstr = tuple_to_str(dictstr)

    return json.loads(dictstr.replace("'", '"'))

def liststr_to_dict(liststr):
    """ Convert string represention of Python list into dict with list key and sorted liststr as its value """
    # handle tuple elements
    liststr = tuple_to_str(liststr)

    list_obj = json.loads("{\"list\":" + liststr.replace("'", '"') +'}')
    list_obj["list"] = sorted(list_obj["list"])

    return list_obj

def cmp(file1, file2):
    """ compare files """
    try:
        with open(file1, 'r') as f:
            obj1 = json.load(f)
        with open(file2, 'r') as f:
            obj2 = json.load(f)
        return obj1 == obj2
    except:
        return filecmp.cmp(file1, file2)

