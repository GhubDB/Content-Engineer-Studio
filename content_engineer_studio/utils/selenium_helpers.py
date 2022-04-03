import time
import traceback
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotVisibleException,
)
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlencode


class Browser:
    def __init__(self):
        self.width = None
        self.height = None
        self.x = None
        self.y = None
        self.driver = None

    def setUp(
        self, url=None, filepath=None, size=None
    ):  # https://www.cleverbot.com/conv/202202041647/WYDS891QFL_Hello-who-are-you
        options = webdriver.ChromeOptions()
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Experimental cleverbot block bypassing options
        options.add_experimental_option("useAutomationExtension", False)

        # Normal options
        if size:
            options.add_argument(size)
        else:
            options.add_argument("window-size=950,1420")
        options.add_argument("window-position=-10,0")
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\chromedriver.exe",
            chrome_options=options,
        )
        if self.width and self.height:
            self.driver.set_window_size(self.width, self.height)
        if self.x and self.y:
            self.driver.set_window_position(self.x, self.y, windowHandle="current")

        # Experimental cleverbot block bypassing options
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
            """
            },
        )
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {
                "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36"
            },
        )

        try:
            self.driver.get(url)
            return True
        except:
            traceback.print_exc()
            return False

    def getURL(self, url):
        try:
            self.driver.get(url)
            return True
        except AttributeError:
            return False

    def exposeURL(self):
        return self.driver.current_url

    def isAlive(self):
        try:
            assert self.driver.current_url
        except:
            traceback.print_exc()
            return False
        else:
            return True

    def refresh(self):
        self.driver.refresh()

    def back(self):
        self.driver.back()

    def forward(self):
        self.driver.forward()

    def tabNum(self):
        return len(self.driver.window_handles)

    def switchTabs(self, tab):
        self.driver.switch_to.window(self.driver.window_handles[tab])

    def bringToFront(self):
        self.driver.switch_to.window(self.driver.current_window_handle)

    def fixPos(self):
        self.width, self.height = self.driver.get_window_size().values()
        self.x = self.driver.get_window_position(windowHandle="current").get("x")
        self.y = self.driver.get_window_position(windowHandle="current").get("y")
        # print(self.width, self.height, self.x, self.y,)

    def tearDown(self):
        try:
            # self.driver.execute_script('window.close("")') # close specific tab
            # self.driver.close() # close current tab
            self.driver.quit()  # close browser
        except AttributeError:
            traceback.print_exc()

    def getCleverbotStatic(self):
        output = []
        try:
            content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            content = content.find_elements(By.TAG_NAME, "span")

            for message in content:
                # print(message.get_attribute('class'))
                if message.get_attribute("class") == "bot":
                    output.append(["bot", message.text])
                    # print('bot: ' + message.text)
                elif message.get_attribute("class") == "user":
                    output.append(["customer", message.text])
                    # print('user: ' + message.text)
            # print(output)
        except:
            traceback.print_exc()
        else:
            return output

    def getCleverbotLive(self):
        output = []
        if self.driver is not None:
            try:
                content = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "conversationcontainer"))
                )
                content = content.find_elements(By.TAG_NAME, "span")

                for message in content:
                    # print(message.get_attribute('class'))
                    if message.get_attribute("class") == "bot":
                        output.append(["bot", message.text])
                        # print('bot: ' + message.text)
                    elif message.get_attribute("class") == "user":
                        output.append(["customer", message.text])
                        # print('user: ' + message.text)
                # print(output)
            except:
                traceback.print_exc()
                time.sleep(1)
            else:
                return output

    def clickCleverbotAgree(self):
        try:
            WebDriverWait(self.driver, 15).until(
                # EC.element_to_be_clickable((By.ID, 'noteb'))
                EC.element_to_be_clickable((By.ID, "noteb"))
            )
            element = self.driver.find_element(By.XPATH, '//*[@id="noteb"]/form/input')
            element.click()
        except:
            traceback.print_exc()

    def setCleverbotLive(self, input):
        try:
            WebDriverWait(self.driver, 10).until(
                # EC.presence_of_element_located((By.NAME, 'stimulus'))
                EC.element_to_be_clickable((By.NAME, "stimulus"))
            )
            # self.driver.find_element(By.NAME, 'stimulus').clear()
            self.driver.find_element(By.NAME, "stimulus").send_keys(input)
            self.driver.find_element(By.NAME, "stimulus").send_keys("\ue007")
        except:
            traceback.print_exc()

    def prebufferAutoTab(self, questions):
        # self.driver.execute_script('window.open("https://www.cleverbot.com/")')
        for question in questions:
            if self.driver is None:
                return False
            # Ask Question
            self.setCleverbotLive(question)
            time.sleep(0.05)
            checking = True
            while checking:
                output = self.getCleverbotLive()
                # If bot has responded, sleep and ask next question
                if output[-1] != question:
                    checking = False
                    # print('checking')
                    time.sleep(5)
