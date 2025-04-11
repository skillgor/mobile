# test_cases/conftest.py
import logging
import time

import pytest
import allure
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from appium import webdriver
from utils.appium_helper import get_driver
from utils.logger import configure_logger
from utils.appium_helper import start_appium_server,stop_appium_server
from utils.delete_files import clean_directory
from config import cfg
from utils.insert_js import insert_js_to_html
# 基础配置
LOG_DIR = Path(__file__).parent.parent / "logs"
SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"
REPORTS_DIR = Path(__file__).parent.parent / "reports" / "allure_results"
Report_html = Path(__file__).parent.parent / "reports" / "allure_report" / "index.html"
LOG_DIR.mkdir(exist_ok=True)
SCREENSHOT_DIR.mkdir(exist_ok=True)
platformName = cfg.platformName

# 日志配置
configure_logger(LOG_DIR)


def pytest_addoption(parser):
    """添加自定义命令行参数"""
    parser.addoption(
        "--device",
        action="store",
        default="pixel_6",
        help="指定测试设备名称（参考devices.yaml）"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="无界面模式运行（仅限模拟器）"
    )


@pytest.fixture(scope="session")
def device_config(request):
    """加载设备配置"""
    device_name = request.config.getoption("--device")
    with open(Path(__file__).parent.parent / "config" / "devices.yaml") as f:
        config = yaml.safe_load(f)
    return config["devices"][device_name]


@pytest.fixture(scope="class")
def appium_driver(request):
    start_appium_server()
    time.sleep(6)
    """核心Fixture：初始化并管理Appium驱动"""
    # 初始化驱动
    driver = get_driver(platformName)
    driver.implicitly_wait(5)

    # 添加设备信息到Allure报告
    # allure.dynamic.label("device", device_config["deviceName"])
    # allure.dynamic.label("platform", f"Android {driver.capabilities['platformVersion']}")

    # 前置操作示例：清除应用数据
    # if not device_config.get("noReset", False):
    #     driver.reset()

    yield driver
    # 后置清理
    try:
        # if driver is not None:
        #     # if request.node.rep_call.failed:  # 仅失败时保留会话
        #     #     logging.error(f"Test {test_name} failed, keeping session alive")
        #     # else:
        #     #     driver.quit()
        #     # driver.quit()
        #     driver.quit()
        driver.quit()
        driver.execute_script("mobile: terminateApp", {"bundleId": "com.maxwealthfl.mwhoe"})

    except Exception:
        pass
    finally:
        stop_appium_server()



@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """处理测试报告并添加截图"""
    outcome = yield
    report = outcome.get_result()
    setattr(item, "rep_" + report.when, report)

    if report.when == "call" and report.failed:
        driver = item.funcargs.get("appium_driver")
        if driver is not None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = SCREENSHOT_DIR / f"{item.name}_{timestamp}.png"

            try:
                driver.save_screenshot(str(screenshot_path))
                allure.attach(
                    driver.get_screenshot_as_png(),
                    name="failure_screenshot",
                    attachment_type=allure.attachment_type.PNG
                )
                logging.info(f"Screenshot saved: {screenshot_path}")
            except Exception as e:
                logging.error(f"Failed to capture screenshot: {str(e)}")


@pytest.fixture(autouse=True)
def log_test_info(request):
    """自动记录测试元信息"""
    logging.info(f"\n=== Starting test: {request.node.name} ===")
    logging.debug(f"Test tags: {request.node.keywords}")
    yield
    logging.info(f"=== Finished test: {request.node.name} ===\n")


# ------------------- 高级功能扩展 -------------------
@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """全局初始化（如API Token获取）"""
    logging.info("Initializing global test environment")
    clean_directory(REPORTS_DIR)
    clean_directory(SCREENSHOT_DIR)
    yield
    time.sleep(3)
    insert_js_to_html(Report_html)
    logging.info("Cleaning up global test environment")


@pytest.fixture
def login_user(appium_driver):
    """用户登录状态预置条件"""
    pass


@pytest.fixture(params=["light", "dark"])
def theme_config(request):
    """参数化主题配置"""
    return {"mode": request.param}