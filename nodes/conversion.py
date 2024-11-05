import json
import re
import hashlib
from .core import DBItem, copy_visit_all_items

class DBConvertToBoolean:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": ("DB_ITEM", {"defaultInput": None, "tooltip": "Input from a DBGet* node."}),
                    },
                }

    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, input):
        output = False

        try:
            if isinstance (input, DBItem):
                value = input.item
                if isinstance(value, bool):
                    output = value
                elif isinstance(value, float):
                    output = value != 0.0
                elif isinstance(value, int):
                    output = value != 0
                elif isinstance(value, str):
                    output = value.lower() == "true"
        except Exception as ex:
            pass

        return (output,)

class DBConvertToInt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": ("DB_ITEM", {"defaultInput": None, "tooltip": "Input from a DBGet* node."}),
                    },
                }

    RETURN_TYPES = ("INT",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, input):
        output = 0

        try:
            if isinstance (input, DBItem):
                value = input.item
                if isinstance(value, bool):
                    output = 1 if value else 0
                elif isinstance(value, float):
                    output = int(value)
                elif isinstance(value, int):
                    output = value
                elif isinstance(value, str):
                    output = int(value)
        except Exception as ex:
            pass

        return (output,)

class DBConvertToFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": ("DB_ITEM", {"defaultInput": None, "tooltip": "Input from a DBGet* node."}),
                    },
                }

    RETURN_TYPES = ("FLOAT",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, input):
        output = 0.0

        try:
            if isinstance (input, DBItem):
                value = input.item
                if isinstance(value, bool):
                    output = 1.0 if value else 0
                elif isinstance(value, float):
                    output = float(value)
                elif isinstance(value, int):
                    output = value
                elif isinstance(value, str):
                    output = float(value)
        except Exception as ex:
            pass

        return (output,)

class DBConvertToString:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": ("DB_ITEM", {"defaultInput": None, "tooltip": "Input from a DBGet* node."}),
                    "filesafe": ('BOOLEAN', {"defaultInput": False, "tooltip": "If True, make it safe for use in file paths. \nThis is a lossy operation that replaces non-alphanumeric characters with single _s"}),
                    "shortenize": ('BOOLEAN', {"defaultInput": False, "tooltip": "If True, shorten component strings severely by removing vowels and adding hash codes for long strings. Works on a per-string basis for deep data structures like dict."}),
                    },
                }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, input, filesafe, shortenize):
        output = ""

        def shorten_string_visitor(item, max_len):
            if isinstance(item, str):
                if len(item) > max_len:
                    hash4 = hashlib.sha256(item.encode('utf-8')).hexdigest()[:4].upper()
                    return f"{item[:max_len]}{hash4}"
                else:
                    return item
            else:
                return item

        def shortenize_string(s):
            s = s.lower()
            s = re.sub(r'[^a-zA-Z \t]', '', s)
            s = re.sub(r'[aeiouAEIOU]', '', s)
            s = ''.join(word.capitalize() for word in s.split())
            s = re.sub(r'[ \t]+', '', s)
            return s

        def small_string_visitor(item):
            if isinstance(item, str):
                item = shortenize_string(item)
            return shorten_string_visitor(item, 16)

        try:
            # unwrap
            input = input.item

            if shortenize:
                # simply replace non-alphanumeric characters with single _s.
                if isinstance(input, dict) or isinstance(input, list):
                    output = copy_visit_all_items(input, small_string_visitor)
                    output = json.dumps(output)
                else:
                    output = small_string_visitor(str(input))
            else:
                if isinstance(input, dict) or isinstance(input, list):
                    output = json.dumps(input)
                else:
                    output = str(input)

            if filesafe:
                output = re.sub(r'[^\w\-]', '_', output)
                output = re.sub(r'_+', '_', output)
                output = output.strip('_')

        except Exception as ex:
            pass

        return (output,)

NODE_CLASS_MAPPINGS = {
    "DBConvertToBoolean //DataBeast": DBConvertToBoolean,
    "DBConvertToInt //DataBeast": DBConvertToInt,
    "DBConvertToFloat //DataBeast": DBConvertToFloat,
    "DBConvertToString //DataBeast": DBConvertToString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DBConvertToBoolean //DataBeast": "DB Convert to Boolean",
    "DBConvertToInt //DataBeast": "DB Convert to Int",
    "DBConvertToFloat //DataBeast": "DB Convert to Float",
    "DBConvertToString //DataBeast": "DB Convert to String",
}
