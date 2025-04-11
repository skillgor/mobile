import subprocess
from appium import webdriver
from pathlib import Path
from appium.options.android import UiAutomator2Options  # Android 平台
from appium.options.ios import XCUITestOptions        # iOS 平台
import yaml
_appium_processes = {}

def get_driver(device):
    """动态加载设备配置并初始化驱动"""
    with open(Path(__file__).parent.parent / "config/devices.yaml") as f:
        devices = yaml.safe_load(f)["devices"]
        print(devices)
    if device == "ios":
        caps = devices["ios_ios11"]
        options = XCUITestOptions().load_capabilities(caps)
    else:
        caps = devices["aos_huawei_p40"]
        options = UiAutomator2Options().load_capabilities(caps)
    driver = webdriver.Remote(
        command_executor="http://127.0.0.1:4723",
        options=options
    )
    driver.implicitly_wait(10)
    return driver

def start_appium_server(port=4723):
    """启动Appium服务"""
    cmd = [
        "appium",
        "-p", str(port),
        "--allow-insecure=adb_shell",
        "--allow-cors",
        "--log-level", "warn"
    ]
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT
    )
    _appium_processes[port] = process


def stop_appium_server(port=4723):
    """停止Appium服务"""
    process = _appium_processes.get(port)
    if process:
        process.terminate()
        process.wait()
