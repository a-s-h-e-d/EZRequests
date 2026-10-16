from src.compiler import Builder, Type


class Compiler:
    def __init__(self, path):
        self.path = path
        self.jsonBuider = Builder.BuildJson()
        self.types = Type.TYPE

        self.headers = {}
        self.data = {}
        self.url = ""
        self.type = self.types.TYPE_GET  # default to get request

        with open(self.path, 'r') as f:
            self.raw = f.read()
            self.code = [
                line for line in self.raw.splitlines()
                if line.strip() and not line.strip().startswith(('#', '//'))
            ]

    def pullRequestType(self):
        identifier = self.code[0].upper()
        if "TYPE_POST" in identifier:
            self.type = self.types.TYPE_POST

    def pullUrl(self):
        for line in self.code:
            stripped = line.strip()
            if stripped.upper().startswith("URL"):
                rest = stripped[3:].strip()
                if rest.startswith('='):
                    rest = rest[1:].strip()
                return rest.strip('"').strip("'")
        return ""

    # dont ask me how this method works, but it does
    def pullJson(self, type):
        block = []
        marker = type.lower()

        for i, line in enumerate(self.code):
            stripped = line.strip()
            first = stripped.split('=')[0].split('{')[0].strip().lower()
            if first != marker:
                continue

            rest = stripped[len(first):].strip()
            if rest.startswith('='):
                rest = rest[1:].strip()
            if rest and not rest.startswith('{'):
                continue

            remaining = ([rest] if rest else []) + self.code[i + 1:]

            depth = 0
            started = False
            for jsonLine in remaining:
                block.append(jsonLine)
                depth += jsonLine.count('{') - jsonLine.count('}')
                if '{' in jsonLine:
                    started = True
                if started and depth == 0:
                    break
            break

        # Drop the outer braces, keep only the key/value lines
        text = "\n".join(block).strip()
        if text.startswith('{'):
            text = text[1:]
        if text.endswith('}'):
            text = text[:-1]
        lineStack = [l.strip().rstrip(',') for l in text.splitlines() if l.strip()]

        return self.jsonBuider.parse(text, lineStack)

    def compileCode(self):
        self.pullRequestType()
        self.data = self.pullJson('data')
        self.headers = self.pullJson('headers')
        self.url = self.pullUrl()


if __name__ == "__main__":
    c = Compiler('../../req.ezq')
    c.compileCode()
    print(c.headers, c.data, c.url, c.type)