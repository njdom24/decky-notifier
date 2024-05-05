import os
import asyncio
from asyncio import QueueEmpty
import subprocess

# The decky plugin module is located at decky-loader/plugin
# For easy intellisense checkout the decky-loader code one directory up
# or add the `decky-loader/plugin` path to `python.analysis.extraPaths` in `.vscode/settings.json`
import decky_plugin

notif_queue = asyncio.Queue()

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

async def subprocess_async():
    env = os.environ
    env["DBUS_SESSION_BUS_ADDRESS"] = f'unix:path=/run/user/{os.getuid()}/bus'
    while True:
        decky_plugin.logger.info("Starting async subprocess")
        cmd_list = ["dbus-monitor", "--session", "interface=org.freedesktop.Notifications"]
        proc = await asyncio.create_subprocess_exec(
            *cmd_list,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env)

        while proc.returncode is None:
            decky_plugin.logger.info("Waiting to read")
            buf = await proc.stdout.readline()
            decky_plugin.logger.info("Read")
            if not buf:
                decky_plugin.logger.info("Breaking")
                buf = await proc.stderr.readline()
                if not buf:
                    break
                decky_plugin.logger.info("Error:", buf.decode())
                await asyncio.sleep(5)
                break

            decky_plugin.logger.info("Something:", buf.decode())
            
            if buf.decode() == '   string "notify-send"\n':
                await proc.stdout.readline() # Throw away
                icon = (await proc.stdout.readline()).decode().strip()[8:-1]
                summary = (await proc.stdout.readline()).decode().strip()[8:-1]
                body = (await proc.stdout.readline()).decode().strip()[8:-1]

                await notif_queue.put({
                    "summary": summary,
                    "body": body,
                    "icon": icon
                })
        decky_plugin.logger.info("Dead")

class Plugin:
    # A normal method. It can be called from JavaScript using call_plugin_function("method_1", argument1, argument2)
    async def add(self, left, right):
        return left + right

    # Asyncio-compatible long-running code, executed in a task when the plugin is loaded
    async def _main(self):
        decky_plugin.logger.info("Starting Decky Notifier")
        loop = asyncio.get_running_loop()
        loop.create_task(subprocess_async())
        decky_plugin.logger.info("Started thread!")

    # Function called first during the unload process, utilize this to handle your plugin being removed
    async def _unload(self):
        decky_plugin.logger.info("Goodbye Decky Notifier!")
        pass

    async def get_notification(self):
        try:
            return notif_queue.get_nowait()
        except QueueEmpty:
            return None

    # Migrations that should be performed before entering `_main()`.
    async def _migration(self):
        decky_plugin.logger.info("Migrating")
        # Here's a migration example for logs:
        # - `~/.config/decky-notifier/notifier.log` will be migrated to `decky_plugin.DECKY_PLUGIN_LOG_DIR/notifier.log`
        decky_plugin.migrate_logs(os.path.join(decky_plugin.DECKY_USER_HOME,
                                               ".config", "decky-notifier", "notifier.log"))
        # Here's a migration example for settings:
        # - `~/homebrew/settings/notifier.json` is migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/notifier.json`
        # - `~/.config/decky-notifier/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_SETTINGS_DIR/`
        decky_plugin.migrate_settings(
            os.path.join(decky_plugin.DECKY_HOME, "settings", "notifier.json"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".config", "decky-notifier"))
        # Here's a migration example for runtime data:
        # - `~/homebrew/notifier/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        # - `~/.local/share/decky-notifier/` all files and directories under this root are migrated to `decky_plugin.DECKY_PLUGIN_RUNTIME_DIR/`
        decky_plugin.migrate_runtime(
            os.path.join(decky_plugin.DECKY_HOME, "notifier"),
            os.path.join(decky_plugin.DECKY_USER_HOME, ".local", "share", "decky-notifier"))
