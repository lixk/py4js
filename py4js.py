# -*- coding: utf-8 -*-
"""
py4js is a fast and simple micro-framework for small web applications. Its goal is to enable you to develop
web applications in a simple and understandable way. With it, you don't need to know the HTTP protocol, or how
Python communicates with JavaScript. You can use Python functions in JavaScript just like native JavaScript functions.
"""
__author__ = 'Xiangkui Li'
__license__ = 'MIT'

import glob
import importlib
import inspect
import json
import os
import random
import sys

from bottle import request, Bottle, response

JS = """//base path of the remote service 
var basePath = "%(base_path)s";

//init service function
function createService(serviceName) {
    var variables = serviceName.split('.');
    var p = window;
    for (var i = 0; i < variables.length; i++) {
        var v = variables[i];
        p[v] = p[v] || {};
        p = p[v];
    }
}

//execute service function
function executeService(serviceName, data, success, error) {
    var xhr = new XMLHttpRequest();
    var formData = new FormData();
    for(var key in data) { formData.append(key, data[key]); }
    success = success || function (data) {};
    error = error || function (e) { console.error(e) };
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4) {
            if (xhr.status == 200) {
                var r = eval('('+xhr.response+')');
                if(r.code == 200 && success){
                    success(r.data);
                    return;
                } 
                if(r.code != 200 && error) {
                    error(r.message);
                    return;
                }
            } else {
                if(error){
                    error(xhr.response);
                } else {
                    console.error(xhr.response);
                }
            }
        }
    }
    xhr.open("POST", basePath + serviceName.replace(/\./g, '/'), true);
    xhr.send(formData);
}
"""


class Server(object):
    """
    With this server, you can use the functions defined in the Python module in JavaScript, just like using
    JavaScript functions.

    :param host: Server address to bind to. Pass `0.0.0.0` to listens on all services including the external one.
    :param port: Server port to bind to. Values below 1024 require root privileges. (default: 5000)
        if port is None, server will use a random port.
    :param server: As the server is based on Bottle, please refer to {@link https://www.bottlepy.org/docs/dev/deployment.html}
         for more details of the server adapter.
         (default: `wsgiref`, others: `paste`/`waitress`/`gevent`/`cherrypy`/`gunicorn`.etc)
    :param service_package: A package that will be scanned by the server. All modules and public functions
        in the package will be loaded as service for JavaScript. Default package name is `service`,
        also you can change it to another name if you like.
    :param js_route: the path of JavaScript for browser to load.
    :param access_control_allow_origin: default: `*` , allow all request.
    """

    def __init__(self, host='0.0.0.0', port=5000, server='wsgiref', service_package='service', js_route='/service.js',
                 access_control_allow_origin='*'):

        self.app = Bottle()
        self.host = host
        self.port = port
        if self.port is None:
            self.port = random.randint(5000, 10000)
        self.server = server
        self.service_package = service_package
        os.makedirs(self.service_package, exist_ok=True)
        self.js_route = js_route
        self.access_control_allow_origin = access_control_allow_origin
        self.services = {}  # all service collection
        self._load_service()

    def _load_service(self):
        """load service modules and functions"""
        module_files = glob.glob(self.service_package + '/**.py', recursive=True)
        for module_path in module_files:
            module_name = os.path.splitext(module_path)[0].replace(os.path.sep, '.')
            module = importlib.import_module(module_name)
            # extract Non-private functions as service
            for func_name, func in module.__dict__.items():
                if not func_name.startswith('_') and inspect.isfunction(func):
                    service_name = module_name + '.' + func_name
                    self.services[service_name] = func

        sys.stdout.write('Service loading completed!\n')

    def _init_js(self):
        """create JavaScript service functions"""
        content = JS
        base_path = '{0}://{1}/'.format(request.urlparts.scheme, request.urlparts.netloc)
        content = content % {'base_path': base_path}
        content += '\n/********************** create service ****************************/\n'
        for service_name in self.services.keys():
            content += 'createService("%s");\n' % service_name
        content += '\n/************************ init service ****************************/\n'
        for service_name, service_func in self.services.items():
            # function doc
            doc = inspect.getdoc(service_func)
            if doc:
                content += '\n/**\n' + ''.join(['* %s\n' % line for line in doc.split('\n')]) + '*/\n'
            # function args
            args = inspect.getfullargspec(service_func).args
            data = ', '.join(['{0}: {0}'.format(arg) for arg in args])
            js_args = ', '.join(args + ['success', 'error'])
            # create js service function
            content += 'window.%(service_name)s = function(%(args)s)' \
                       '{ executeService("%(service_name)s", {%(data)s}, success, error); }\n' % {
                           "service_name": service_name,
                           "args": js_args,
                           "data": data
                       }

        # set content type
        response.headers['Content-Type'] = 'application/javascript'

        return content

    def _dispatcher(self, path):
        """dispatcher requests to the corresponding service functions"""
        params = dict(request.POST)
        service_function = self.services.get(path.replace('/', '.'), None)
        if service_function is None:
            return json.dumps({'code': 404, 'message': 'Service "%s" not found!' % path}, ensure_ascii=False)
        try:
            return json.dumps({'code': 200, 'data': service_function(**params)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'code': 500, 'message': 'Server error: %s' % e}, ensure_ascii=False)

    def _enable_cors(self):
        response.headers['Access-Control-Allow-Origin'] = self.access_control_allow_origin

    def run(self):
        """
        Start the server instance. This method blocks until the server terminates.

        :return:
        """
        # add route for dispatcher
        self.app.route('/<path:path>', method=['POST'], callback=self._dispatcher)
        # add route for JS
        self.app.route(self.js_route, callback=self._init_js)
        # allow cross domain request
        self.app.add_hook('after_request', self._enable_cors)
        # startup wsgi server
        self.app.run(host=self.host, port=self.port, server=self.server)


# test
if __name__ == '__main__':
    Server(port=80, server='waitress').run()
