# py4js
py4js is a fast and simple micro-framework for small web applications. Its goal is to enable you to develop
web applications in a simple and understandable way. 

With it, you don't need to know the HTTP protocol, or how Python communicates with JavaScript. You can use Python functions in JavaScript just like native JavaScript functions.

## usage steps

### step 1
install py4js package: `pip install py4js` or `pip3 install py4js`

### step 2
First, create a package, named service, and then create a Python file in the package, such as `hello.py`:
```python
def say_hello():
    return 'Hello World!'
```

### step 3
create a Python file, such as `main.py`:
```python
from py4js import Server

Server().run()
```
Then run it(By default, the server will launch wsgiref server at port `5000`. You can also use other port and wsgi server).

### step 4
create a HTML file, such as `index.html`:
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>hello</title>
    <script src="http://localhost:5000/service.js"></script>
</head>
<body>
    <script>
        service.hello.say_hello('World', function(data){
            alert(data);
        });
    </script>
</body>
</html>
```

Open the `index.html`in browser and you will see the alert message:
![image](https://github.com/lixk/py4js/raw/master/sample/screenshots/alert-hello.png)

It's so easy, yes?

## Server
### Server parameters
The server has several startup parameters that can be specified, for example:

| Name | Description |
| :--- | :--- |
| host | Server address to bind to(default: `0.0.0.0`). Pass `0.0.0.0` to listens on  all services including the external one. |
| port | Server port to bind to(default: 5000). Values below 1024 require root privileges. if port is None, server will use a random port. |
| server | Specify the server adapter to use. For more details: [Server adapter](#serverAdapter). (default: `wsgiref`, others: `paste`/`waitress`/`gevent`/`cherrypy`/`gunicorn`.etc). |
| service_package | A package that will be scanned by the server. All modules and public functions in the package will be loaded as service for JavaScript. Default package name is `service`, also you can change it to another name if you like. |
| js_route | the path of JavaScript for browser to load. |
| access_control_allow_origin | default: `*` , all cross domain requests are allowed. |

### Server adapter
<span id="serverAdapter"></span>
As the py4js server is based on Bottle, the built-in default server is based on wsgiref WSGIServer. This non-threading HTTP server may become a performance bottleneck when server load increases. 
So it's better to use a different server that is either multi-threaded or supports asynchronous IO.

Bottle ships with a lot of ready-to-use adapters for the most common WSGI servers, such as:
`cherrypy`, `paste`, `waitress`, `gevent`, `eventlet`, `tornado`, `twisted`.etc. 
Usage:
 1. waitress
    ```python
    from py4js import Server

    Server(server='waitress').run()
    ```
    If you haven't installed the `waitress` package, please install it first by `pip install waitress` or `pip3 install waitress`.

 2. gevent
    ```python
    from gevent import monkey

    from py4js import Server
    
    monkey.patch_all()
    
    Server(server='gevent').run()
    ```
    If you haven't installed the `gevent` package, please install it first by `pip install gevent` or `pip3 install gevent`.  
    As `gevent` is Asynchronous, the server can be very fast, can handle a virtually unlimited number of concurrent connections and are easy to manage. 

