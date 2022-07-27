import time
import traceback
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common.exceptions import (ElementNotVisibleException,
                                        NoSuchElementException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Browser:
    def __init__(self):
        self.width = None
        self.height = None
        self.x = None
        self.y = None
        self.driver = None

    def setUp(
        self, url=None, size=None
    ):
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

    def get_url(self, url):
        try:
            self.driver.get(url)
            return True
        except AttributeError:
            return False

    def fixPos(self):
        self.width, self.height = self.driver.get_window_size().values()
        self.x = self.driver.get_window_position(windowHandle="current").get("x")
        self.y = self.driver.get_window_position(windowHandle="current").get("y")

    def tear_down(self):
        try:
            self.driver.quit()
        except AttributeError:
            traceback.print_exc()

    def get_cleverbot_static(self):
        output = []
        try:
            content = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "content"))
            )
            content = content.find_elements(By.TAG_NAME, "span")

            for message in content:
                if message.get_attribute("class") == "bot":
                    output.append(["bot", message.text])

                elif message.get_attribute("class") == "user":
                    output.append(["customer", message.text])
        except:
            traceback.print_exc()
        else:
            return output

    def get_cleverbot_live(self):
        output = []
        if self.driver is not None:
            try:
                content = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "conversationcontainer"))
                )
                content = content.find_elements(By.TAG_NAME, "span")

                for message in content:
                    if message.get_attribute("class") == "bot":
                        output.append(["bot", message.text])
                    elif message.get_attribute("class") == "user":
                        output.append(["customer", message.text])
            except:
                traceback.print_exc()
                time.sleep(1)
            else:
                return output

    def click_cleverbot_agree(self):
        try:
            WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.ID, "noteb"))
            )
            element = self.driver.find_element(By.XPATH, '//*[@id="noteb"]/form/input')
            element.click()
        except:
            traceback.print_exc()

    def set_cleverbot_live(self, text):
        try:
            WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.NAME, "stimulus"))
            )
            self.driver.find_element(By.NAME, "stimulus").send_keys(text)
            self.driver.find_element(By.NAME, "stimulus").send_keys("\ue007")
        except:
            traceback.print_exc()

    def prebuffer_auto_tab(self, questions):
        for question in questions:
            if self.driver is None:
                return False
            # Ask Question
            self.set_cleverbot_live(question)
            time.sleep(0.05)
            checking = True
            while checking:
                output = self.get_cleverbot_live()
                # If bot has responded, sleep and ask next question
                if output[-1] != question:
                    checking = False
                    # print('checking')
                    time.sleep(5)
