import arcpy
from subprocess import *
import os
import sys
import json
from pathlib import Path

FORMAT_LIST = [
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


def get_arcgispro_envs(scripts_folder: str) -> dict:
    bat = 'activate.bat arcgispro-py3 && conda info --envs --json'
    cmd = os.path.join(scripts_folder, bat)

    result = Popen(cmd, stdout=PIPE, shell=False, creationflags=CREATE_NO_WINDOW)
    output = result.communicate()[0]
    result.terminate()

    envs_json = json.loads(output.decode().replace('\x1b[0m', ''))['envs'][1::]
    envs_name = {path.split('\\')[-1]: path for path in envs_json}

    return envs_name


def check_required():
    global FORMAT_LIST

    cmd1 = 'where xelatex'
    cmd2 = 'where pandoc'
    result1 = call(cmd1, shell=True)
    result2 = call(cmd2, shell=True)
    if result1 == 1:
        FORMAT_LIST.remove('pdf')
        arcpy.AddWarning('If you want to convert do pdf, download the miktex:\n'
                         'https://miktex.org/download')

    if result2 == 1:
        arcpy.AddWarning('If you want to convert to markdown, download the pandoc:\n'
                         'https://pandoc.org/installing.html#windows')
        FORMAT_LIST.remove('markdown')


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "IpynbToolbox"
        self.alias = "IpynbToolbox"

        # List of tool classes associated with this toolbox
        self.tools = [RunIpynb]


class RunIpynb(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "RunIpynb"
        self.description = "This is Script runs the notebok and saves a html on notebooks folder v2."
        self.canRunInBackground = True
        self.parameters_dict = {}
        self.envs = {}

    def getParameterInfo(self):
        """Define parameter definitions"""
        global FORMAT_LIST
        acgispro_scripts = arcpy.Parameter(
            name="acgispro_scripts",
            displayName="Arcgis Pro Scripts Folder",
            parameterType="Required",
            direction="Input",
            datatype="DEFolder")
        acgispro_scripts.value = r'C:\Program Files\ArcGIS\Pro\bin\Python\Scripts'
        acgispro_scripts.dialogref = r'Your ArcgisPro script program path, typicaly at' \
                                     r'  "C:\Program Files\ArcGIS\Pro\bin\Python\Scripts".'
        self.parameters_dict[acgispro_scripts.name] = acgispro_scripts

        env_name = arcpy.Parameter(
            name="env_name",
            displayName="Env name",
            parameterType="Required",
            direction="Input",
            datatype="GPString")

        env_name.filter.type = "ValueList"
        self.envs = get_arcgispro_envs(acgispro_scripts.valueAsText)
        envs_names = list(self.envs.keys())
        env_name.filter.list = envs_names
        env_name.value = envs_names[0]
        env_name.dialogref = 'Your arcgis python env name.'
        self.parameters_dict[env_name.name] = env_name

        nb_to_format = arcpy.Parameter(
            name="nb_to_format",
            displayName="Convert notebook to format",
            parameterType="Required",
            direction="Input",
            datatype="GPString")
        nb_to_format.filter.type = "ValueList"

        check_required()

        nb_to_format.filter.list = FORMAT_LIST

        nb_to_format.value = 'html_toc'
        nb_to_format.dialogref = 'The format in wich you want to convert your notebook to.'
        self.parameters_dict[nb_to_format.name] = nb_to_format

        ipynb_file = arcpy.Parameter(
            name="ipynb_file",
            displayName="Notebook",
            parameterType="Required",
            direction="Input",
            datatype="DEFile")
        ipynb_file.filter.list = ['ipynb']
        ipynb_file.dialogref = 'The notebook file you want to use.'
        self.parameters_dict[ipynb_file.name] = ipynb_file

        output_folder = arcpy.Parameter(
            name="output_folder",
            displayName="Output Folder",
            parameterType="Required",
            direction="Input",
            datatype="DEFolder")
        output_folder.dialogref = 'The output folder where the export file(s) goes to.'
        self.parameters_dict[output_folder.name] = output_folder

        output_basename = arcpy.Parameter(
            name="output_basename",
            displayName="Output Basename",
            parameterType="Required",
            direction="Input",
            datatype="GPString")
        output_basename.value = 'Default'
        output_basename.dialogref = 'The base name of your file without extension type.'
        self.parameters_dict[output_basename.name] = output_basename

        no_inputs = arcpy.Parameter(
            name="no_inputs",
            displayName="No inputs",
            parameterType="Optional",
            direction="Input",
            datatype="GPBoolean")
        no_inputs.value = False
        no_inputs.dialogref = 'Exclude input cells and output prompts from converted document.\n' \
                              'This mode is ideal for generating code-free reports.'
        self.parameters_dict[no_inputs.name] = no_inputs

        embed_images = arcpy.Parameter(
            name="embed_images",
            displayName="Embed images ",
            parameterType="Optional",
            direction="Input",
            datatype="GPBoolean")
        embed_images.value = False
        embed_images.dialogref = 'To enable embedding images with NbConvert.'
        self.parameters_dict[embed_images.name] = embed_images

        execute_notebook = arcpy.Parameter(
            name="execute_notebook",
            displayName="Execute notebook",
            parameterType="Optional",
            direction="Input",
            datatype="GPBoolean")
        execute_notebook.value = True
        execute_notebook.dialogref = 'Execute the notebook prior to export.'
        self.parameters_dict[execute_notebook.name] = execute_notebook

        allow_errors = arcpy.Parameter(
            name="allow_errors",
            displayName="Allow Errors",
            parameterType="Optional",
            direction="Input",
            datatype="GPBoolean")
        allow_errors.parameterDependencies = [execute_notebook.name]
        allow_errors.value = True
        allow_errors.dialogref = 'Continue notebook execution even if one of the cells throws an error' \
                                 'and include the error message in the cell output' \
                                 ' (the default behaviour is to abort conversion).\n' \
                                 'This flag is only relevant if "execute" was specified, too.'
        self.parameters_dict[allow_errors.name] = allow_errors

        timeout_seconds = arcpy.Parameter(
            name="timeout_seconds",
            displayName="Timeout in seconds (-1 equal no Timeout)",
            parameterType="Required",
            direction="Input",
            datatype="GPLong")
        timeout_seconds.parameterDependencies = [execute_notebook.name]
        timeout_seconds.value = -1
        timeout_seconds.dialogref = "The time to wait (in seconds) for output from executions." \
                                    " If a cell execution takes longer, an exception (TimeoutError on python 3+" \
                                    ") is raised. `-1` will disable the timeout."
        self.parameters_dict[timeout_seconds.name] = timeout_seconds

        result = arcpy.Parameter(
            name="result",
            displayName="Script Result",
            parameterType="Derived",
            direction="Output",
            datatype="GPString")
        result.dialogref = 'The Toolbox status indicating success or error as string'
        self.parameters_dict[result.name] = result

        parameters = [k for k in self.parameters_dict.values()]

        return parameters

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
         validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
       parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        tool_status = f'{self.label} Sucess'
        self.parameters_dict = {param.name: param for param in parameters}

        ipynb_file = self.parameters_dict['ipynb_file'].valueAsText
        tex_default = Path(ipynb_file).stem + '.tex'
        env_path = self.envs[self.parameters_dict['env_name'].valueAsText]
        nb_to_format = self.parameters_dict['nb_to_format'].valueAsText
        out_folder = self.parameters_dict['output_folder'].valueAsText
        output_basename = self.parameters_dict['output_basename'].valueAsText
        try:
            if nb_to_format == 'pdf':
                nb_to_format = 'latex'

            cmd = f'{env_path}\\Scripts\\jupyter nbconvert --output-dir="{out_folder}" --to {nb_to_format}'
            if self.parameters_dict['no_inputs'].value:
                cmd += ' --no-input'

            if self.parameters_dict['embed_images'].value and 'hml' in nb_to_format and not 'embed' in nb_to_format:
                cmd += ' --EmbedImagesPreprocessor.embed_images=True'

            if output_basename.lower() != 'default':
                cmd += f' --output="{output_basename}"'

            if self.parameters_dict['execute_notebook'].value:
                cmd += ' --execute'
                if self.parameters_dict['allow_errors'].value:
                    cmd += ' --allow-errors'

                timeout_seconds = self.parameters_dict['timeout_seconds'].valueAsText
                cmd += f' --ExecutePreprocessor.timeout={timeout_seconds}'

            cmd += f' "{ipynb_file}"'
            arcpy.AddMessage(f'Running command:\n {cmd}')
            result = call(cmd, shell=True, cwd=out_folder)
            if nb_to_format == 'latex':
                output_basename = output_basename if output_basename.lower() != 'default' else tex_default
                std_err = (b'xelatex: security risk: running with elevated privileges\r\nmiktex-dvipdfmx: '
                           + b'security risk: running with elevated privileges\r\n', b'')
                cmd = f'xelatex "{out_folder}\\{output_basename}" -quiet'
                arcpy.AddMessage(f'Running command:\n {cmd}')
                result = Popen(cmd, cwd=out_folder, stderr=PIPE)
                _, err = result.communicate()
                result.terminate()
                if err in std_err:
                    result = 0
                else:
                    result = 1

            if result == 1:
                arcpy.AddError('Notebook Failed to execute')

        except arcpy.ExecuteError:
            tool_status = f'{self.label} Error'

        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError(e.args[0])
        finally:
            self.parameters_dict['result'].value = tool_status
            arcpy.AddMessage(f'Status {tool_status}')
