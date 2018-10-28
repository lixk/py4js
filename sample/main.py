from py4js import Server

# Server(server='waitress').run()

from gevent import monkey
monkey.patch_all()

Server(server='gevent').run()
