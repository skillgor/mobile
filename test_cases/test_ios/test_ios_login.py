import time

from appium.webdriver.common.appiumby import AppiumBy
import allure
from page_objects.iosPage.login_ios_page import LoginPage
from appium_helper.swipeHelper import swipe_element
from appium_helper.mobileHandle import MobileAutomator

@allure.epic("移动端测试")
@allure.feature("首页tab")
class TestLogin:
    @allure.title("验证首页tab")
    @allure.story("验证首页tab正常跳转")
    def test_login(self, appium_driver):
        # swipe_element(appium_driver,LoginPage._username_target,10)
        login_page = LoginPage(appium_driver)
        with allure.step("进入首页"):
            login_page.click_continue()
        with allure.step("新机市场"):
            MobileAutomator(appium_driver).assert_element_present(login_page._username_target,5)
        with allure.step("验证通过截图"):
            allure.attach(appium_driver.get_screenshot_as_png(), name="新机市场页面截图",
                          attachment_type=allure.attachment_type.PNG)


