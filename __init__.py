"""
@author: hanoixan
@title: DataBeast
@nickname: DataBeast
@description: This extension provides nodes for controlling data-driven processing in Comfy-UI
"""

import importlib

version_code = [1, 0]
version_str = f"V{version_code[0]}.{version_code[1]}" + (f'.{version_code[2]}' if len(version_code) > 2 else '')
print(f"### Loading: ComfyUI-DataBeast ({version_str})")

node_list = [
    "conversion",
    "general",
    "math",
    "string"
]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

for module_name in node_list:
    imported_module = importlib.import_module(".nodes.{}".format(module_name), __name__)

    NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **imported_module.NODE_CLASS_MAPPINGS}
    NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

try:
    import cm_global
    cm_global.register_extension('ComfyUI-DataBeast',
                                 {'version': version_code,
                                  'name': 'DataBeast',
                                  'nodes': set(NODE_CLASS_MAPPINGS.keys()),
                                  'description': 'This extension provides nodes for data-driven processing in Comfy-UI', })
except:
    pass
