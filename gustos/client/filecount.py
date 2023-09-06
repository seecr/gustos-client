from gustos.common.units import COUNT
from glob import glob
from os.path import isfile, isdir, dirname

class FileCount(object):
    def __init__(self, file_pattern, group='File count'):
        self._file_patterns = file_pattern if type(file_pattern) is list else [file_pattern]
        for pattern in self._file_patterns:
            pattern_dirname = dirname(pattern)
            if not isdir(pattern_dirname):
                raise ValueError("No such directory: {}".format(pattern_dirname))

        self._group = group

    def values(self):
        result = { self._group: {} }
        for file_pattern in self._file_patterns:
            matches = glob(file_pattern)
            files = len([match for match in matches if isfile(match)])
            directories = len([match for match in matches if isdir(match)])
            result[self._group][file_pattern] = {"files": {COUNT: files}, "directories": {COUNT: directories}}

        return result

    def __repr__(self):
        return 'FileCount(file_pattern={})'.format(repr(self._file_patterns))
