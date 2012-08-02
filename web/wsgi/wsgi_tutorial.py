# This is our application object. It could have any name,
# except when using mod_wsgi where it must be "application"
def application( # It accepts two arguments:
      # environ points to a dictionary containing CGI like environment variables
      # which is filled by the server for each received request from the client
      environ,
      # start_response is a callback function supplied by the server
      # which will be used to send the HTTP status and headers to the server
      start_response):

   # build the response body possibly using the environ dictionary
   response_body = 'The request method was %s' % environ['REQUEST_METHOD']

   # HTTP response code and message
   status = '200 OK'

   # These are HTTP headers expected by the client.
   # They must be wrapped as a list of tupled pairs:
   # [(Header name, Header value)].
   response_headers = [('Content-Type', 'text/plain'),
                       ('Content-Length', str(len(response_body)))]

   # Send them to the server using the supplied function
   start_response(status, response_headers)

   # Return the response body.
   # Notice it is wrapped in a list although it could be any iterable.
   return [response_body]

#! /usr/bin/env python

# Our tutorial's WSGI server
from wsgiref.simple_server import make_server

def application(environ, start_response):

   # Sorting and stringifying the environment key, value pairs
   response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
   response_body = '\n'.join(response_body)

   status = '200 OK'
   response_headers = [('Content-Type', 'text/plain'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]

# Instantiate the WSGI server.
# It will receive the request, pass it to the application
# and send the application's response to the client
httpd = make_server(
   'localhost', # The host name.
   8051, # A port number where to wait for the request.
   application # Our application object name, in this case a function.
   )

# Wait for a single request, serve it and quit.
httpd.handle_request()


#! /usr/bin/env python

from wsgiref.simple_server import make_server

def application(environ, start_response):

   response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
   response_body = '\n'.join(response_body)

   # Response_body has now more than one string
   response_body = ['The Beggining\n',
                    '*' * 30 + '\n',
                    response_body,
                    '\n' + '*' * 30 ,
                    '\nThe End']

   # So the content-lenght is the sum of all string's lengths
   content_length = 0
   for s in response_body:
      content_length += len(s)

   status = '200 OK'
   response_headers = [('Content-Type', 'text/plain'),
                  ('Content-Length', str(content_length))]
   start_response(status, response_headers)

   return response_body

httpd = make_server('localhost', 8051, application)
httpd.handle_request()




#!/usr/bin/env python

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

html = """
<html>
<body>
   <form method="get" action="parsing_get.wsgi">
      <p>
         Age: <input type="text" name="age">
         </p>
      <p>
         Hobbies:
         <input name="hobbies" type="checkbox" value="software"> Software
         <input name="hobbies" type="checkbox" value="tunning"> Auto Tunning
         </p>
      <p>
         <input type="submit" value="Submit">
         </p>
      </form>
   <p>
      Age: %s<br>
      Hobbies: %s
      </p>
   </body>
</html>"""

def application(environ, start_response):

   # Returns a dictionary containing lists as values.
   d = parse_qs(environ['QUERY_STRING'])

   # In this idiom you must issue a list containing a default value.
   age = d.get('age', [''])[0] # Returns the first age value.
   hobbies = d.get('hobbies', []) # Returns a list of hobbies.

   # Always escape user input to avoid script injection
   age = escape(age)
   hobbies = [escape(hobby) for hobby in hobbies]

   response_body = html % (age or 'Empty',
               ', '.join(hobbies or ['No Hobbies']))

   status = '200 OK'

   # Now content type is text/html
   response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]

httpd = make_server('localhost', 8051, application)
# Now it is serve_forever() in instead of handle_request().
# In Windows you can kill it in the Task Manager (python.exe).
# In Linux a Ctrl-C will do it.
httpd.serve_forever()


#!/usr/bin/env python

from wsgiref.simple_server import make_server
from cgi import parse_qs, escape

html = """
<html>
<body>
   <form method="post" action="parsing_post.wsgi">
      <p>
         Age: <input type="text" name="age">
         </p>
      <p>
         Hobbies:
         <input name="hobbies" type="checkbox" value="software"> Software
         <input name="hobbies" type="checkbox" value="tunning"> Auto Tunning
         </p>
      <p>
         <input type="submit" value="Submit">
         </p>
      </form>
   <p>
      Age: %s<br>
      Hobbies: %s
      </p>
   </body>
</html>
"""
def application(environ, start_response):

   # the environment variable CONTENT_LENGTH may be empty or missing
   try:
      request_body_size = int(environ.get('CONTENT_LENGTH', 0))
   except (ValueError):
      request_body_size = 0

   # When the method is POST the query string will be sent
   # in the HTTP request body which is passed by the WSGI server
   # in the file like wsgi.input environment variable.
   request_body = environ['wsgi.input'].read(request_body_size)
   d = parse_qs(request_body)

   age = d.get('age', [''])[0] # Returns the first age value.
   hobbies = d.get('hobbies', []) # Returns a list of hobbies.

   # Always escape user input to avoid script injection
   age = escape(age)
   hobbies = [escape(hobby) for hobby in hobbies]

   response_body = html % (age or 'Empty',
               ', '.join(hobbies or ['No Hobbies']))

   status = '200 OK'

   response_headers = [('Content-Type', 'text/html'),
                  ('Content-Length', str(len(response_body)))]
   start_response(status, response_headers)

   return [response_body]

httpd = make_server('localhost', 8051, application)
httpd.serve_forever()
