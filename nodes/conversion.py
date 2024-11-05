import json
import re
import hashlib
from .core import any_typ, DBItem, copy_visit_all_items

class DBConvertToInt:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": (any_typ, {"defaultInput": None, "tooltip": "Any input type."}),
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
                output = int(input.item)
            else:
                output = int(input)
        except Exception as ex:
            pass

        return (output,)

class DBConvertToFloat:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": (any_typ, {"defaultInput": None, "tooltip": "Any input type."}),
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
                output = float(input.item)
            else:
                output = float(input)
        except Exception as ex:
            pass

        return (output,)

class DBConvertToString:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "input": (any_typ, {"defaultInput": None, "tooltip": "Any input type."}),
                    "filesafe": ('BOOLEAN', {"defaultInput": False, "tooltip": "If True, safe for use in file paths."}),
                    },
                }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, input, filesafe):
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

        try:
            # unwrap
            if isinstance (input, DBItem):
                input = input.item

            if isinstance(input, dict) or isinstance(input, list):
                if filesafe:
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

                    input = copy_visit_all_items(input, small_string_visitor)

                output = json.dumps(input)
            else:
                output = str(input)
        except Exception as ex:
            pass

        if filesafe:
            # replace sequences of non-alphnum chars with _, and abbreviate all sequences of alpha-num to 6 max
            output = re.sub(r'[^\w\-]', '_', output)
            output = re.sub(r'_+', '_', output)
            output = output.strip('_')
            output = shorten_string_visitor(output, 64)
        return (output,)


NODE_CLASS_MAPPINGS = {
    "DBConvertToInt //DataBeast": DBConvertToInt,
    "DBConvertToFloat //DataBeast": DBConvertToFloat,
    "DBConvertToString //DataBeast": DBConvertToString,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DBConvertToInt //DataBeast": "DB Convert to Int",
    "DBConvertToFloat //DataBeast": "DB Convert to Float",
    "DBConvertToString //DataBeast": "DB Convert to String",
}
