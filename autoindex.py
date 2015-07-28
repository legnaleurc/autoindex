#! /usr/bin/env python3

import sys
import os.path as op
import logging
import os
import mimetypes

from tornado import ioloop, web, log, iostream, gen


class IndexHandler(web.RequestHandler):

    def initialize(self, root, *args, **kwargs):
        self._root = root

    @gen.coroutine
    def get(self, path):
        full_path = self._full_path(path)

        if not op.exists(full_path):
            raise web.HTTPError(404)

        if op.isfile(full_path):
            type_, encoding = mimetypes.guess_type(full_path)
            if not type_:
                self.set_header('Content-Type', 'application/octet-stream')
            else:
                self.set_header('Content-Type', type_)

            with open(full_path, 'rb') as fin:
                while True:
                    chunk = fin.read(65536)
                    if not chunk:
                        return
                    try:
                        self.write(chunk)
                        yield self.flush()
                    except iostream.StreamClosedError:
                        return

        if op.isdir(full_path):
            items = os.listdir(full_path)
            items = [(op.join(path, __), __) for __ in items]
            self.render('list.html', here=path, items=items)
            return

        raise web.HTTPError(401)

    def _full_path(self, path):
        return op.join(self._root, path)

    def _is_file(self, base, name):
        return op.isfile(op.join(base, name))


def main(args=None):
    if args is None:
        args = sys.argv

    log.enable_pretty_logging()

    main_loop = ioloop.IOLoop.instance()

    application = web.Application([
        (r'/(.*)', IndexHandler, {'root': '.'}),
    ], debug=True)

    application.listen(8000)

    main_loop.start()

    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
