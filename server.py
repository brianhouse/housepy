#!/usr/bin/env python3

from . import config, log, strings
import os, re, datetime, hashlib, __main__, base64, uuid, sys
import tornado.auth
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
import json as jsonlib
import gzip as gziplib
try:
    import jinja2
    from jinja2 import Environment, FileSystemLoader
except SyntaxError:
    # jinja2 not supported in Python 3.2
    pass

"""
    Tornado server!
    Usage:

    class Home(server.Handler):
        def get(self, page=None):
            return self.text("OK")
    handlers = [
        (r"/?([^/]*)", Home),
    ]    
    server.start(handlers)

"""


"""Include all functions in string module as jinja2 filters"""
filters = {}
for function_name in dir(strings):
    if '__' in function_name:
        continue
    filters[function_name] = eval("strings." + function_name)
# note nice built-in filters: int, e (html_escape)

class Application(tornado.web.Application):
    
    def __init__(self, handlers):
                
        settings = {
            'template_path': os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates")),
            'static_path': os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "static")),
            'cookie_secret': base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes),
            'xsrf_cookies': False
        }
        
        if 'mongo' in config:    
            log.info("Initializing mongo")
            try:
                mongo = config['mongo']
                from pymongo import MongoClient
                client = MongoClient(mongo['host'], mongo['port'])
                self.db = client[mongo['database']]
                log.info("--> %s" % self.db)
            except Exception as e:
                log.error("Could not connect to mongo: %s" % log.exc(e))        
        if 'server' in config:
            tornado_settings = config['server']
            for key in list(tornado_settings.keys()):
                settings[key] = tornado_settings[key]    

        tornado.web.Application.__init__(self, handlers, **settings)
                    
        self.jobs = None    
        if 'beanstalk' in config:    
            log.info("--> tornado initializing beanstalk")
            from . import jobs
            self.jobs = jobs.Jobs()  
                        
        Application.instance = self          
        
    def log_request(self, handler):
        return

        
class render_jinja:

    def __init__(self, *a, **kwargs):
        extensions = kwargs.pop('extensions', [])
        globals = kwargs.pop('globals', {})

        self._lookup = Environment(loader=FileSystemLoader(*a, **kwargs), extensions=extensions)
        self._lookup.globals.update(globals)

    def __getitem__(self, name):
        t = self._lookup.get_template(name)
        return t.render
                       


class Handler(tornado.web.RequestHandler):
    """Adding custom output methods.""" 
    
    def initialize(self):
        log.info("---------- %s %s %s" % (self.request.remote_ip, self.request.method, self.request.uri))
        self.xsrf_form_html()    
        
    def get_current_user(self): # supports tornado auth
       return self.get_secure_cookie("user") 

    @property
    def user(self):
        try:
            return jsonlib.loads(self.get_secure_cookie('user'))
        except:
            return None

    @property
    def db(self):
        return self.application.db
    
    # @property
    # def cache(self):
    #     return self.application.cache
        
    @property
    def jobs(self):
        return self.application.jobs    
                                
    def render(self, template_name, template_values=None, **kwargs):
        if type(template_values) == dict:
            template_values.update(kwargs)
        else:
            template_values = kwargs
        template_values['uri'] = self.request.uri
        if 'log_templates' in config['server'] and config['server']['log_templates']:    
            log.info("TEMPLATE %s: %s" % (template_name, template_values))
        else:    
            log.info("TEMPLATE %s" % template_name)            
        for key in config: 
            if type(config[key]) is dict:
                for param in config[key]:
                    template_values["%s_%s" % (key, param)] = str(config[key][param])
            else:
                template_values[key] = config[key]                       
        template_values['template_name'] = template_name                         
        if 'user' not in template_values:
            template_values['user'] = self.user
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates"))
        renderer = render_jinja(template_dir)
        renderer._lookup.filters.update(filters)
        output = (renderer[template_name](template_values)).encode('utf-8')
        suffix = template_name.split('.')[-1]
        if suffix == "html":
            self.html(output)
        else:
            self.text(output)          
        
    def json(self, data, filename=False, gzip=False):
        try:
            import numpy as np
        except Exception:    
            output = jsonlib.dumps(data, indent=4, allow_nan=False, default=lambda obj: str(obj))
        else:    
            output = jsonlib.dumps(data, indent=4, allow_nan=False, default=lambda obj: str(obj) if type(obj) != np.ndarray else list(obj))
        self.set_header("Content-Type", "application/json")
        if gzip:
            output = gziplib.compress(output.encode('utf-8'))
            self.set_header("Content-Encoding", "gzip")
        if filename:
            self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(output)
        log.info("200 application/json")
        self.finish()        

    def xml(self, xml, filename=False):    
        self.set_header("Content-Type", "application/xml")
        if filename:
            self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(xml)
        log.info("200 application/xml")                            
        self.finish()

    def html(self, html):
        self.set_header("Content-Type", "text/html")
        self.write(html)    
        log.info("200 text/html")                
        self.finish()

    def text(self, string):
        self.set_header("Content-Type", "text/plain")
        self.write(string)
        log.info("200 text/plain")     
        self.finish()       

    def csv(self, string, filename):
        self.set_header("Content-Type", "text/csv")
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        self.write(string)
        log.info("200 text/csv") 
        self.finish()   

    def file(self, filename):
        self.set_header("Content-Type", "application/octet-stream")
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename.split('/')[-1])
        self.set_header("Content-Length", "%s" % os.path.getsize(filename))    
        self.write(open(filename, 'r').read())
        log.info("200 application/octet-stream (%s)" % filename)   
        self.finish()

    def image(self, image):
        import imaging
        self.set_header("Content-Type", "image/png")
        self.set_header("Expires", "Thu, 15 Apr 2050 20:00:00 GMT")
        if type(image) != str:
            image = imaging.to_string(image)            
        self.write(image)
        log.info("200 image/png")            
        self.finish()        

    def temp_image(self, image):
        import imaging
        self.set_header("Content-Type", "image/png")     
        self.set_header("Cache-Control", "no-cache")
        if type(image) != str:
            image = imaging.to_string(image)                    
        self.write(image)
        log.info("200 image/png (temporary)")     
        self.finish()

    def error(self, message="Error"):
        self.set_header("Status", "400 Bad Request")
        log.error("400: %s" % message)
        self.send_error(400, message=message)

    def not_found(self):
        log.warning("404: Page not found")
        raise tornado.web.HTTPError(404)        
                
    def redirect(self, url):
        log.info("--> redirecting to %s" % url)
        tornado.web.RequestHandler.redirect(self, url)     

    def write_error(self, status_code, **kwargs):
        message = kwargs['message'] if 'message' in kwargs else self._reason
        try:
            template_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates"))
            renderer = render_jinja(template_dir)
            renderer._lookup.filters.update(filters)
            output = (renderer["%s.html" % status_code]({'status_code': status_code, 'message': message})).encode('utf-8')
            self.finish(output)
        except:            
            self.finish("%(code)d: %(message)s" % {
                            "code": status_code,
                            "message": message,
                        })        


authenticated = tornado.web.authenticated

def start(handlers):
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "templates"))
    if not os.path.isdir(template_dir):
        os.makedirs(template_dir)
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__main__.__file__), "static"))
    if not os.path.isdir(static_dir):
        os.makedirs(static_dir)    
    tornado.options.logging = "none"
    ssl_options = None
    if 'ssl_options' in config['server']:
        ssl_options = {'certfile': config['server']['ssl_options']['certfile'], 'keyfile': config['server']['ssl_options']['keyfile']}
    if config['server']['port'] is None and len(sys.argv) > 1:
        config['server']['port'] = sys.argv[1]
    log.info("Starting tornado server on port %s" % config['server']['port'])
    http_server = tornado.httpserver.HTTPServer(Application(handlers), ssl_options=ssl_options, xheaders=True, max_buffer_size=209715200) # 200MB
    http_server.listen(config['server']['port'])
    tornado.ioloop.IOLoop.instance().start()
    


