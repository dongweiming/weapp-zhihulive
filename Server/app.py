from sanic import Sanic
from elasticsearch_dsl.connections import connections

from views.api import bp
from views.protocol import JSONHttpProtocol

app = Sanic(__name__)
app.blueprint(bp)
app.static('/static', './static')


def set_loop(sanic, loop):
    conns = connections._conns
    for c in conns:
        conns[c].transport.loop = loop


@app.middleware('request')
async def halt_request(request):
    request.start = request.args.get('start', 0)
    request.limit = request.args.get('limit', 10)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8300, protocol=JSONHttpProtocol,
            before_start=[set_loop], workers=4, debug=True)
