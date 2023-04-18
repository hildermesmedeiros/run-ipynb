import sys
import os
from importlib import machinery
from importlib import util

pyt_path = (os.path.join(os.path.abspath("./"), 'run-ipynb.pyt'))

loader = machinery.SourceFileLoader(fullname='Toolbox', path=pyt_path)
spec = util.spec_from_loader(loader.name, loader)
mod = util.module_from_spec(spec)
loader.exec_module(mod)

def get_my_doc_path():
    import ctypes.wintypes
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value

    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    return os.path.abspath(buf.value)

def debug():
    """
    Debug with pydevd (I use pycharm but people could just change the aproach)
    """

    toolbox = mod.Toolbox()
    tool = mod.RunIpynb()
    print('Debugging tool: {}'.format(tool.label))
    params = tool.getParameterInfo()
    test = [
            'html',
            'html_ch',
            'html_embed',
            'html_toc',
            'markdown',
            'notebook',
            'pdf',
            'python',
            'script'
        ]
    try:
        for t in test:
            my_documents_path = get_my_doc_path()
            _params = {
                'acgispro_scripts': r"C:\Program Files\ArcGIS\Pro\bin\Python\Scripts",
                'env_name': "arcgispro-py3-clone",
                'nb_to_format': t,
                'ipynb_file':  os.path.join(my_documents_path, r'ArcGIS\Readme.ipynb'),
                'output_folder': os.path.join(os.path.abspath('.'), 'export_examples'),
                'output_basename': f"{t}_result_example",
                'no_inputs': False,
                'embed_images': True,
                'execute_notebook': True,
                'allow_errors': True,
                'timeout_seconds': -1
            }
            for p in params[:-1]:
                p.value = _params[p.name]
            tool.execute(params, None)
    except:
        print('error')


if "__main__" == __name__ and "pydevd" in sys.modules:
    debug()