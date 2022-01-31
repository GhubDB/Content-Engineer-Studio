import unittest
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import page


class PythonOrgSerach(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome("C:\Program Files (x86)\chromedriver.exe")
        self.driver.get('http://www.python.org')



    def test_search_python(self):
        mainPage = page.MainPage(self.driver)
        assert mainPage.is_title_matches()
        mainPage.search_text_element = 'pycon'
        mainPage.click_go_button()
        search_result_page = page.SearchResultPage(self.driver)
        assert search_result_page.is_results_found()

    def dearDown(self):
        self.driver.close()


if __name__ == '__main__':
    unittest.main()