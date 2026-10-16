import json
import re


class BuildJson:
    def __init__(self):
        pass

    def parse(self, body, stack):
        if not body.strip():
            return {}
        text = "{" + body + "}"
        text = re.sub(r',\s*([}\]])', r'\1', text)  # allow trailing commas
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except ValueError:
            pass
        return self.build(stack)

    def build(self, stack):
        built = {}
        for line in stack:
            key, value = line.split(':', 1)
            key = key.strip().strip('"').strip("'")
            value = value.strip()

            if value[:1] in ('"', "'"):
                value = value.strip('"').strip("'")
            else:
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        pass
            built[key] = value
        return built