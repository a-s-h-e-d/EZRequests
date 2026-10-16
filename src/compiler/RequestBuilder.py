import json
import mimetypes
import os
import re
from urllib.parse import urlparse, unquote

import requests

from src.compiler.Type import TYPE


class Builder:
    def __init__(self, headers, data, url, type):
        self.headers = headers
        self.data = data
        self.url = url
        self.type = type
        self.output = None
        self.path = None  # set when a response body is saved to disk

    def _headers(self):
        # HTTP header values must be strings; JSON values are serialized
        out = {}
        for key, value in self.headers.items():
            out[key] = value if isinstance(value, str) else json.dumps(value)
        return out

    def _body(self):
        if any(isinstance(v, (dict, list)) for v in self.data.values()):
            return {"json": self.data}
        return {"data": self.data}

    def createRequest(self):
        if self.type == TYPE.TYPE_GET:
            self.output = requests.get(self.url, headers=self._headers(), **self._body())
        elif self.type == TYPE.TYPE_POST:
            self.output = requests.post(self.url, headers=self._headers(), **self._body())

    def getJson(self):
        return self.output.json()
    def getText(self):
        return self.output.text
    def getRaw(self):
        return self.output
    def getResponseCode(self):
        return self.output.status_code
    def getHeaders(self):
        return self.output.headers

    # ---------- saving files ----------
    def _save(self, filename):
        path = os.path.abspath(filename)
        with open(path, 'wb') as file:      # open the PATH, not the Response
            file.write(self.output.content)  # write the body bytes
        self.path = path
        return path

    def url_name(self):
        name = os.path.basename(unquote(urlparse(self.url).path))
        return name if os.path.splitext(name)[1] else ""

    def getImage(self, path=None):
        """Save the response if it is an image. Returns the saved path or None."""
        content_type = self.output.headers.get('content-type', '')
        if not content_type.startswith('image/') or self.output.status_code != 200:
            return None
        mime = content_type.split(';')[0].strip()
        ext = mimetypes.guess_extension(mime) or '.img'
        if ext == '.jpe':
            ext = '.jpg'
        return self._save(self.url_name() or f"response_image{ext}")  if path is None else self._save(path)

    def getFile(self):
        """Save the response if the server marks it as an attachment. Returns the path or None."""
        content_disp = self.output.headers.get("Content-Disposition", "")
        if self.output.status_code != 200:
            return None
        if "attachment" in content_disp or "filename=" in content_disp:
            match = re.search(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?', content_disp)
            name = os.path.basename(match.group(1)) if match else "response_file"
            return self._save(name)
        return None

    def getAll(self):
        return {'raw': self.getRaw(), "text": self.getText(), "json": self.getJson()}