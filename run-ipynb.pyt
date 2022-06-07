import arcpy
from subprocess import *
import os

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
        self.description = "This is Script runs the notebok and saves a html on notebooks folder"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        parameters = []
        param0 = arcpy.Parameter(
            name="ipynb",
            displayName="Notebook",
            parameterType="Required",
            direction="Input",
            datatype="DEFile")
        param0.filter.list = ['ipynb']
        parameters.append(param0)

        param1 = arcpy.Parameter(
            name="Folder",
            displayName="Pasta do ambiente python",
            parameterType="Required",
            direction="Input",
            datatype="DEFolder")

        parameters.append(param1)

        param2 = arcpy.Parameter(
            name="resultado",
            displayName="resultado do script",
            parameterType="Derived",
            direction="Output",
            datatype="GPString")
        parameters.append(param2)

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
        toolStatus = f'{self.label} Sucess'
        try:
            jupyter_path = parameters[0].valueAsText
            env_path = parameters[1].valueAsText
            html_folder = os.path.dirname(jupyter_path)
            cmd = f'{env_path}\\Scripts\\jupyter nbconvert --allow-errors\
            --output-dir="{html_folder}" --ExecutePreprocessor.timeout=-1\
            --ExecutePreprocessor.store_widget_state=True --to html --execute "{jupyter_path}"'
            result = call(cmd, shell=True)
            if result == 1:
                arcpy.AddError('Notebook Failed to execute')

        except:
            toolStatus = f'{self.label} Error'
            messages = arcpy.GetMessages()
            arcpy.AddError(f'{messages}')
        finally:
            parameters[2].value = toolStatus
            arcpy.AddMessage(f'Result html: {jupyter_path.replace(".ipynb",".html")}')
            arcpy.AddMessage(f'Status {toolStatus}')
