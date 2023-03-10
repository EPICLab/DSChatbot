import json
import sys

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado

class RouteHandler(APIHandler):
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self):
        restrict = []
        for arg in sys.argv:
            if arg.startswith('--Newtonchat.restrict='):
                restrict = arg[len('--Newtonchat.restrict='):].strip('"').strip("'").split(',')
        self.finish(json.dumps({
            'restrict': restrict
        }))


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "newton", "config")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
