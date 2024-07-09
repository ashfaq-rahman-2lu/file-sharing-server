import http.server
import socketserver
from urllib.parse import parse_qs
import re

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        content_type = self.headers['Content-Type']
        if not content_type.startswith('multipart/form-data'):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Bad request: Content-Type must be multipart/form-data')
            return
        
        # Extract boundary from content type header
        boundary = content_type.split("boundary=")[1].encode()
        content_length = int(self.headers['Content-Length'])
        
        body = self.rfile.read(content_length)
        
        # Split the content by boundary
        parts = body.split(b'--' + boundary)[1:-1]  # Skip the first and last parts (boundary is at the beginning and end of the body)
        file_data = None
        for part in parts:
            # Find the header and content of the part
            header, content = part.split(b'\r\n\r\n', 1)
            content = content.rstrip(b'\r\n')  # Remove trailing CRLF
            
            # Check if this part contains the file data
            disposition_header = [line for line in header.split(b'\r\n') if b'Content-Disposition: form-data;' in line]
            if disposition_header:
                disposition_parts = disposition_header[0].split(b';')
                name_part = [part.strip() for part in disposition_parts if b'name="file"' in part]
                filename_part = [part.strip() for part in disposition_parts if b'filename="' in part]
                
                if name_part and filename_part:
                    # Extract filename
                    filename = filename_part[0].split(b'filename="')[1].rstrip(b'"')
                    file_data = content
                    # Decode filename to string if necessary
                    filename = filename.decode('utf-8')
                
                print(filename, file_data)
                if file_data:
                    with open("resource/" + filename, "wb") as f:
                        f.write(file_data)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(b'File uploaded successfully!')
                else:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'Bad request: No file data')

with socketserver.TCPServer(("localhost", PORT), Handler) as httpd:
    print("Serving at port", PORT)
    httpd.serve_forever()
