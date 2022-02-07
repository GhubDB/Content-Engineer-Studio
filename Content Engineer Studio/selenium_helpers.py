from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from urllib.parse import urlencode
from bs4 import BeautifulSoup


class MainDriver():
    def __init__(self):
        pass


    def setUp(self, url=None, filepath=None, size=None): #https://www.cleverbot.com/conv/202202041647/WYDS891QFL_Hello-who-are-you
        options = webdriver.ChromeOptions()
        options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        # Experimental cleverbot block bypassing options
        options.add_experimental_option('useAutomationExtension', False)

        # Normal options
        if size:
            options.add_argument(size)
        else:
            options.add_argument("window-size=1000,1420")
        options.add_argument("window-position=0,0")
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\chromedriver.exe", chrome_options=options)

        # Experimental cleverbot block bypassing options
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
            })
        """
        })
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        
        self.driver.get(url)

    def tearDown(self):
        try:
            self.driver.close()
        except AttributeError:
            pass

    # def __set__(self, obj, value):
    #     driver = obj.driver
    #     WebDriverWait(driver, 10).until(
    #         lambda driver: driver.find_element_by_name(self.locator))
    #     driver.find_element_by_name(self.locator).clear()
    #     driver.find_element_by_name(self.locator).send_keys(value)

    def getCleverbotStatic(self):
        output = []
        content = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'content'))
        )
        content = content.find_elements(By.TAG_NAME, 'span')

        for message in content:
            # print(message.get_attribute('class'))
            if message.get_attribute('class') == 'bot':
                output.append(['bot', message.text])
                # print('bot: ' + message.text)
            elif message.get_attribute('class') == 'user':
                output.append(['customer', message.text])
                # print('user: ' + message.text)
        # print(output)
        return output


    def getCleverbotLive(self):
        output = []
        content = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'conversationcontainer'))
        )
        content = content.find_elements(By.TAG_NAME, 'span')

        for message in content:
            # print(message.get_attribute('class'))
            if message.get_attribute('class') == 'bot':
                output.append(['bot', message.text])
                # print('bot: ' + message.text)
            elif message.get_attribute('class') == 'user':
                output.append(['customer', message.text])
                # print('user: ' + message.text)
        # print(output)
        return output

    def setCleverbotLive(self, input):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'stimulus'))
        )
        self.driver.find_element(By.NAME, 'stimulus').clear()
        self.driver.find_element(By.NAME, 'stimulus').send_keys(input)
        self.driver.find_element(By.NAME, 'stimulus').send_keys(u'\ue007')

    def clickByName(self, ID):
        element = self.driver.find_element(By.NAME, ID)
        element.click()

# class Executors(object):
#     def __init__(self, driver):
#         self.driver = driver


if __name__ == '__main__':
    cleverbot_driver = MainDriver()
    cleverbot_driver.setUp()
    cleverbot_driver.cleverbot()