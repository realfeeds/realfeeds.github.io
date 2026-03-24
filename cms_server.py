import http.server
import socketserver
import json
import os
import base64
import uuid

PORT = 8080

class CMSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/cms_ui.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            super().end_headers() # Bypass cache headers just in case
            with open('cms_ui.html', 'rb') as f:
                self.wfile.write(f.read())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/api/add_project':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
                return

            os.makedirs('assets/images', exist_ok=True)
            os.makedirs('data', exist_ok=True)
            
            final_pictures = []
            for pic in data.get('pictures', []):
                if pic['type'] == 'url':
                    final_pictures.append(pic['value'])
                elif pic['type'] == 'file':
                    b64_str = pic['base64']
                    if ',' in b64_str:
                        b64_str = b64_str.split(',')[1]
                    try:
                        file_data = base64.b64decode(b64_str)
                        ext = pic.get('filename', 'image.jpg').split('.')[-1]
                        if not ext.isalnum():
                            ext = 'jpg'
                        new_filename = f"{uuid.uuid4().hex[:8]}.{ext}"
                        filepath = f"assets/images/{new_filename}"
                        with open(filepath, 'wb') as f:
                            f.write(file_data)
                        final_pictures.append(filepath)
                    except Exception as e:
                        print(f"Error saving image: {e}")
            
            project = {
                "title": data.get("title", "").strip(),
                "date": data.get("date", "").strip(),
                "description": data.get("description", "").strip(),
                "link": data.get("link", "").strip(),
                "unlisted": data.get("unlisted", False),
                "pictures": final_pictures
            }
            if final_pictures:
                project["thumbnail"] = final_pictures[0]
            
            portfolio_file = 'data/portfolio.json'
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    try:
                        db = json.load(f)
                    except Exception:
                        db = {"projects": []}
            else:
                db = {"projects": []}
                
            edit_index = data.get("index", -1)
            if edit_index >= 0 and edit_index < len(db["projects"]):
                db["projects"][edit_index] = project
            else:
                db["projects"].insert(0, project)
            
            with open(portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(db, f, indent=2)
                
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
        elif self.path == '/api/delete_project':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
                return

            del_index = data.get("index", -1)
            
            portfolio_file = 'data/portfolio.json'
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    try:
                        db = json.load(f)
                    except Exception:
                        db = {"projects": []}
                
                if del_index >= 0 and del_index < len(db["projects"]):
                    db["projects"].pop(del_index)
                    
                with open(portfolio_file, 'w', encoding='utf-8') as f:
                    json.dump(db, f, indent=2)
                    
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == '/api/move_project':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            idx = data.get("index", -1)
            direction = data.get("direction", 0)
            portfolio_file = 'data/portfolio.json'
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    try:
                        db = json.load(f)
                    except Exception:
                        db = {"projects": []}
                new_idx = idx + direction
                if 0 <= idx < len(db["projects"]) and 0 <= new_idx < len(db["projects"]):
                    db["projects"][idx], db["projects"][new_idx] = db["projects"][new_idx], db["projects"][idx]
                    with open(portfolio_file, 'w', encoding='utf-8') as f:
                        json.dump(db, f, indent=2)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == '/api/toggle_unlisted':
            content_length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(content_length).decode('utf-8'))
            idx = data.get("index", -1)
            unlisted = data.get("unlisted", False)
            portfolio_file = 'data/portfolio.json'
            if os.path.exists(portfolio_file):
                with open(portfolio_file, 'r', encoding='utf-8') as f:
                    try:
                        db = json.load(f)
                    except Exception:
                        db = {"projects": []}
                if 0 <= idx < len(db["projects"]):
                    db["projects"][idx]["unlisted"] = unlisted
                    with open(portfolio_file, 'w', encoding='utf-8') as f:
                        json.dump(db, f, indent=2)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status": "success"}')
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    with ReusableTCPServer(("", PORT), CMSHandler) as httpd:
        print(f"CMS Admin Panel running at http://localhost:{PORT}")
        print("To close, press Ctrl+C")
        httpd.serve_forever()
