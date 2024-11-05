from .core import DBItem, safe_eval

class DBStringExpression:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "expression": ("STRING", {"defaultInput": None, "tooltip": "Python string expression taking any of inputs a,b,c,d."}),
                    "a": ("STRING", {"defaultInput": None, "tooltip": "Input a."}),
                    "b": ("STRING", {"defaultInput": None, "tooltip": "Input b."}),
                    "c": ("STRING", {"defaultInput": None, "tooltip": "Input c."}),
                    "d": ("STRING", {"defaultInput": None, "tooltip": "Input d."}),
                    },
                }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("output",)

    FUNCTION = "exec"
    CATEGORY = "DataBeast"

    def exec(self, expression, a, b, c, d):
        output = 0
        try:
            local_vars = {"a": a, "b": b, "c": c, "d": d}
            output = str(safe_eval(expression, local_vars, "<DBStringExpression>"))
        except Exception as ex:
            pass

        return (output,)

NODE_CLASS_MAPPINGS = {
    "DBStringExpression //DataBeast": DBStringExpression,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "DBStringExpression //DataBeast": "DB String Expression",
}
