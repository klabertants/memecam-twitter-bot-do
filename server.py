import os
import http.server
import socketserver

from http import HTTPStatus

from twitter_service import run_main_loop
from apscheduler.schedulers.background import BlockingScheduler


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(HTTPStatus.OK)
        self.end_headers()
        msg = 'Hello! you requested %s' % (self.path)
        self.wfile.write(msg.encode())


port = int(os.getenv('PORT', 80))
print('Listening on port %s' % (port))
httpd = socketserver.TCPServer(('', port), Handler)
httpd.serve_forever()

sched = BlockingScheduler()
sched.add_job(run_main_loop, 'interval', seconds=60)

sched.start()
