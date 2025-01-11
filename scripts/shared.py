from typing import NamedTuple, Optional, List

import sys
import shlex
import io
import paramiko
import scp
import shutil
import requests
import os


class SuppressKeyPolicy(paramiko.MissingHostKeyPolicy):
    def missing_host_key(self, client, hostname, key):
        return


class SshExecResult(NamedTuple):
    returncode: int
    stdout: Optional[str]


class SshConnection:
    def __init__(self, hostname: str, username: str, password: str):
        self.hostname = hostname
        self.username = username
        self.password = password

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(SuppressKeyPolicy)

    def __enter__(self):
        self.client.connect(
            self.hostname,
            username=self.username,
            password=self.password,
            allow_agent=False,
            look_for_keys=False,
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def exec_cmd(self,
                 cmd: str,
                 check: bool = False,
                 get_output: bool = False,
                 print_output: bool = False) -> SshExecResult:

        output = None
        buffer = io.StringIO()

        transport = self.client.get_transport()
        assert transport is not None

        with transport.open_session() as channel:
            channel.set_combine_stderr(True)
            channel.exec_command(cmd)

            with channel.makefile("r") as stdout:
                for line in stdout:
                    if get_output:
                        buffer.write(line)
                    if print_output:
                        try:
                            print(line, end="")
                        except UnicodeEncodeError:
                            eline = line.encode(
                                sys.stdout.encoding,
                                "backslashreplace"
                            ).decode(sys.stdout.encoding)

                            print(eline, end="")
            retval = channel.recv_exit_status()
        if check and retval != 0:
            raise Exception(f'Command \'{cmd}\' returned non-zero error status {retval}')
        elif get_output:
            output = buffer.getvalue()

        return SshExecResult(retval, output)

    def exec_bash(self,
                  commands: List[str],
                  bash_opts: str = 'e',
                  check: bool = False,
                  get_output: bool = False,
                  print_output: bool = False) -> SshExecResult:

        parts = [ '/bin/bash' ]
        if bash_opts:
            parts.append(f'-{bash_opts}')
        parts.append('-c')

        parts.append(';'.join(commands))
        cmd = shlex.join(parts)

        return self.exec_cmd(cmd=cmd, check=check, get_output=get_output, print_output=print_output)

    def get_scp(self, remote_source: str, local_target: str, recursive: bool = False):
        with self.scp_client() as scp_client:
            scp_client.get(remote_source, local_target, recursive=recursive)

    def put_scp(self, local_source: str, remote_target: str, recursive: bool = False):
        with self.scp_client() as scp_client:
            scp_client.put(local_source, remote_target, recursive=recursive)

    def scp_client(self):
        return scp.SCPClient(self.client.get_transport())


class CoProcessorAppDeployer:
    def __init__(self, app_name: str, app_folder: str, hostname: str):
        self.app_name = app_name
        self.app_folder = app_folder
        self.hostname = hostname

    def deploy(self, set_as_current: bool = False, auto_start: bool = True, auto_restart: bool = True):
        zip_path = shutil.make_archive(self.app_name, 'zip', self.app_folder)
        with open(zip_path, 'rb') as file:
            file_data = file.read()

        args = {
            'set_as_current': set_as_current,
            'auto_start': auto_start,
            'auto_restart': auto_restart
        }
        query_string = '&'.join([f'{k}={v}' for k, v in args.items()])

        response = requests.post(f'{self.hostname}/manager/upload_app/{self.app_name}?{query_string}', files={'app': file_data})
        os.remove(zip_path)

        return response.status_code
