from shared import SshConnection

import pathlib
import threading


def main(robot_code_path: str, team_number: int, net_console: bool = False):
    team_str = str(team_number)

    user='lvuser'

    home_dir = pathlib.PurePosixPath('/home/lvuser')
    py_deploy_dir = home_dir / 'py'
    py_deploy_temp_dir = home_dir / 'py_temp'

    #f'10.{team_str[0:2]}.{team_str[2:]}.2'
    with SshConnection(f'10.31.17.2', 'lvuser', '') as client:
        deploy_dir = pathlib.PurePosixPath('/home/lvuser')

        deployed_cmd = (
            'env LD_LIBRARY_PATH=/usr/local/frc/lib/ '
            f'/usr/local/bin/python3 -u -O -m robotpy --main {py_deploy_dir}/robot.py run'
        )
        deployed_cmd_filename = 'robotCommand'
        bash_cmd = '/bin/bash -ce'

        replace_cmd = f'rm -rf {py_deploy_dir}; mv {py_deploy_temp_dir} {py_deploy_dir}'

        try:
            client.exec_cmd(
                cmd=f'echo "{deployed_cmd}" > {home_dir}/{deployed_cmd_filename}; mkdir -p {py_deploy_temp_dir}',
                check=True,
                print_output=True
            )
        except Exception as e:
            print(e)
            return None

        try:
            client.put_scp(robot_code_path, f'{py_deploy_temp_dir}', recursive=True)
        except Exception as e:
            print(e)
            return None

        sshcmd = (
            f"{bash_cmd} '"
            f"{replace_cmd};"
            "sh /home/lvuser/py/frc-3117-tools-python/build-roborio.sh;"
            f"/home/admin/rpip install --force-reinstall --no-deps -r {py_deploy_dir}/requirements-roborio.txt; "
            "/home/admin/rpip install --force-reinstall --no-cache-dir /home/lvuser/py/whl/*;"
            f"/usr/local/bin/python3 -O -m compileall -q -r 5 /home/lvuser/py;"
            ". /etc/profile.d/frc-path.sh; "
            ". /etc/profile.d/natinst-path.sh; "
            f"chown -R lvuser:ni {py_deploy_dir}; "
            "sync; "
            "/usr/local/frc/bin/frcKillRobot.sh -t -r || true"
            "'"
        )

        try:
            client.exec_cmd(sshcmd,
                            check=True,
                            print_output=True)
        except Exception as e:
            print(e)
            return None

        if net_console:
            from netconsole import run

            nc_event = threading.Event()
            nc_thread = threading.Thread(
                target=run,
                args=(client, ),
                kwargs=dict(connect_event=nc_event, fakeds=True),
                daemon=True,
            )
            nc_thread.start()
            nc_event.wait(5)

            return nc_thread


if __name__ == '__main__':
    main('./robot/', 3117, True)
