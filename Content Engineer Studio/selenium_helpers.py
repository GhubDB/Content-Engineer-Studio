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

    def setUp(self, url=None, filepath=None): #https://www.cleverbot.com/conv/202202041647/WYDS891QFL_Hello-who-are-you
        options = webdriver.ChromeOptions()
        options.add_argument('--enable-extensions')
        self.driver = webdriver.Chrome(
            executable_path="C:\Program Files (x86)\chromedriver.exe", chrome_options=options)
        self.driver.get(url)

    def cleverbot(self):
        page = Executors(self.driver)
        return page.__get__()
        # mainPage.search_text_element = 'pycon'
        # mainPage.click_go_button()

    def dearDown(self):
        self.driver.close()



class Executors(object):
    def __init__(self, driver):
        self.driver = driver

    def __set__(self, obj, value):
        driver = obj.driver
        WebDriverWait(driver, 10).until(
            lambda driver: driver.find_element_by_name(self.locator))
        driver.find_element_by_name(self.locator).clear()
        driver.find_element_by_name(self.locator).send_keys(value)

    def __get__(self):
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

    def clickByName(self, ID):
        element = self.driver.find_element(By.NAME, ID)
        element.click()

if __name__ == '__main__':
    cleverbot_driver = MainDriver()
    cleverbot_driver.setUp()
    cleverbot_driver.cleverbot()