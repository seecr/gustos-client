from urllib.request import urlopen, Request
from gustos.common.units import COUNT
from gustos.client import VERSION

class UrlStatus(object):
    def __init__(self, url, label="", group="Url Status", timeout=1):
        self._url = url
        self._label = label if label else url
        self._group = group
        self._timeout = timeout
        self._errorCount = 0

    def values(self):
        status = self._getUrlStatus()
        if status >= 400:
            self._errorCount += 1
            print(('Url status %s for url %s' % (status, self._url)))
            from sys import stdout; stdout.flush()
        return {
            self._group: {
                self._label: { 'Error': {COUNT: self._errorCount}}
            }
        }

    def _getUrlStatus(self):
        try:
            return self._urlopen()
        except Exception as e:
            print(("Error for url %s:\n%s" % (self._url, str(e))))
            from sys import stdout; stdout.flush()
            return 1024

    def _urlopen(self):
        request = Request(self._url)
        request.add_header('User-Agent', 'Seecr-Gustos-UrlStatus-%s' % VERSION)
        urlStatus = urlopen(request, timeout=self._timeout)
        result = urlStatus.getcode()
        urlStatus.close()
        return result

    def __repr__(self):
        return 'UrlStatus(url="{}", label="{}", timeout={})'.format(self._url, self._label, self._timeout)
