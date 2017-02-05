from sanic.server import HttpProtocol, CIMultiDict
from sanic.request import Request as _Request
from sanic.response import text, json


class Request(_Request):
    __slots__ = (
        'url', 'headers', 'version', 'method', '_cookies',
        'query_string', 'body', 'start', 'limit',
        'parsed_json', 'parsed_args', 'parsed_form', 'parsed_files',
    )


class JSONHttpProtocol(HttpProtocol):
    def on_headers_complete(self):
        remote_addr = self.transport.get_extra_info('peername')
        if remote_addr:
            self.headers.append(('Remote-Addr', '%s:%s' % remote_addr))

        self.request = Request(
            url_bytes=self.url,
            headers=CIMultiDict(self.headers),
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode()
        )

    def write_response(self, response):
        if isinstance(response, str):
            response = text(response)
        elif isinstance(response, list):
            response = {'rs': response}
        if isinstance(response, dict):
            response = json(response)

        return super().write_response(response)
