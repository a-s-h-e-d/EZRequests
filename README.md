# EZRequests

A lightweight compiler that turns a small, readable `.ezq` file into an HTTP request, sends it, and shows you the response.

Write the request in plain text, hit **Run**, and see the result in a viewer window. No curl flags and no boilerplate.

```
TYPE_POST

HEADERS
{
"Accept": "application/json"
}

DATA
{
"title": "hello",
"userId": 1
}

URL "https://jsonplaceholder.typicode.com/posts"
```

---

## Requirements

- Python 3 (developed on 3.13)
- [`requests`](https://pypi.org/project/requests/)
- Tkinter (bundled with most Python installs; on some Linux distros install `python3-tk`)

```bash
pip install requests
```

## Project layout

```
EZRequests/
├── Main.py                  # entry point
├── req.ezq                  # example request file
└── src/
    ├── Editor.py            # the editor window
    ├── Visualizer.py        # the response viewer window
    └── compiler/
        ├── Compiler.py      # parses .ezq into type / headers / data / url
        ├── Builder.py       # converts "key": value lines into a dict
        ├── RequestBuilder.py# sends the request using `requests`
        └── Type.py          # request type enum (GET / POST)
```

---

## Opening the editor

Run `Main.py` with no arguments **from the project root** (the folder containing `Main.py`):

```bash
python3 Main.py
```

The **EZ Requests editor** opens with line numbers and a status bar.

| Action | Menu | Shortcut |
| --- | --- | --- |
| New file | File → New | `Ctrl+N` |
| Open a `.ezq` file | File → Open... | `Ctrl+O` |
| Save | File → Save | `Ctrl+S` |
| Save as | File → Save As... | `Ctrl+Shift+S` |
| Compile and send the request | **Run** (next to the File menu) | none |

**Running a request**

1. Write your request, or open an existing `.ezq` file.
2. Save the file. **Run** shows an error if the file has never been saved.
3. Click **Run**. The editor saves again, compiles the file, sends the request, and opens the visualizer.


### Running a file without the editor

Pass a `.ezq` file to skip the editor and go straight to the visualizer:

```bash
python3 Main.py req.ezq
```

The file must be in the folder you run the command from. Anything other than `.ezq` is rejected with `invalid file extension`.

---

## Understanding the visualizer

After a request is sent, the visualizer opens in a read-only window. From top to bottom:

1. **Request summary.** The request type (`TYPE.TYPE_GET` or `TYPE.TYPE_POST`), the URL, and the response status line, such as `<Response [200]>`.
2. **Response headers** (hidden by default). Shown as sorted, indented JSON under a `RESPONSE-HEADERS` divider.
3. **Response body** (shown by default). Pretty-printed JSON under a `RESPONSE` divider. If the body is not valid JSON, you'll see `(response is not valid JSON)`.

Two checkboxes at the bottom control which sections appear:

| Checkbox | Default | Shows |
| --- | --- | --- |
| Response headers | off | The headers the server sent back |
| Response JSON | **on** | The response body, formatted as JSON |

The top bar has three buttons (**Button 1–3**). These are placeholders and don't do anything yet.

The response status line also prints to the terminal where you launched `Main.py`.

---

## The `.ezq` syntax

An `.ezq` file has up to four parts: a **type**, a **HEADERS** block, a **DATA** block, and a **URL**. Only the URL is needed to make a useful request.

### Full example

```
TYPE_POST
# this is a comment
// this is also a comment

HEADERS
{
"Accept": "application/json",
"X-Retries": 3
}

DATA
{
"name": "giancarlo",
"score": 9.5
}

URL "https://jsonplaceholder.typicode.com/posts/1"
```

### Request type

| Keyword | Result |
| --- | --- |
| `TYPE_POST` | Sends a POST request |
| *(omitted)* | Sends a GET request (default) |

The type must be on the **first line** of the file that isn't blank or a comment. Matching is case-insensitive.

### URL

```
URL "https://example.com/api"
URL = "https://example.com/api"
URL https://example.com/api
```

- The keyword is case-insensitive, and an `=` after it is optional.
- Quotes around the URL are optional. Single or double quotes both work.

### HEADERS and DATA blocks

Both use the same format: the keyword, then braces containing `"key": value` pairs.

```
HEADERS
{
"Content-Type": "application/x-www-form-urlencoded"
}

DATA = {
"user": "sam",
"age": 25,
}
```

- Keywords are case-insensitive. `HEADERS = {` and `HEADERS {` work as well as the keyword on its own line.
- The contents are JSON, so pairs can be spread over several lines or written on one. Trailing commas are fine.
- Either block can be left out. A missing block sends nothing.
- If the contents aren't valid JSON, the compiler falls back to a simpler **one pair per line** format, which also allows single-quoted strings and unquoted keys.

**Value types**

| You write | Sent as |
| --- | --- |
| `"text"` | string |
| `123` / `1.5` | number |
| `true` / `false` / `null` | boolean / null |
| `{ ... }` | nested object |
| `[ ... ]` | array |

**Nested JSON**

```
DATA
{
"user": {
  "name": "sam",
  "tags": ["a", "b"],
  "active": true
},
"count": 3
}
```

How values are sent:

- **`DATA`:** flat data (strings and numbers only) is sent form-encoded. If any value is an object or array, the whole block is sent as a **JSON body** instead (with `Content-Type: application/json`).
- **`HEADERS`:** HTTP header values must be text, so non-string values are serialized to JSON text. `"X-Meta": {"a": 1}` is sent as `{"a": 1}`, and `"X-Count": 3` as `3`.

### Comments

Lines starting with `#` or `//` are ignored, as are blank lines. Comments must be on their own line. Don't put one at the end of a code line.

### Current limitations
- No compile or editor level syntax check
- Only GET and POST are supported.
- Only one request per file.

---

## Quick start

```bash
git clone <this repo>
cd EZRequests
pip install requests
python3 Main.py          # opens the editor
```
