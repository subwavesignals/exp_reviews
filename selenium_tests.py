import unittest
from selenium import webdriver
import time


HOME_URL = "http://localhost:5000"

class SeleniumTests(unittest.TestCase):
    """Tests for functionality or server and JS functions"""

    def setUp(self):
        self.browser = webdriver.Chrome()

    def tearDown(self):
        self.browser.quit()

    def wait_for_page_load(self, timeout=30):
        old_page = self.find_element_by_tag_name('html')
        yield
        WebDriverWait(self, timeout).until(staleness_of(old_page))

    # def test_index(self):
    #     """Tests for index.html"""

    #     self.browser.get(HOME_URL)
    #     self.assertEqual(self.browser.title, 'EXP Reviews')

    def test_homelink(self):

        self.browser.get(HOME_URL + '/users/1')
        self.browser.wait_for_page_load(15)
        homelink = self.browser.find_element_by_class_name("navbar-brand")

        homelink.click()

        self.browser.wait_for_page_load(15)
        self.assertEqual(self.browser.title, 'EXP Reviews')

    def test_login(self):

        self.browser.get(HOME_URL + '/login')

        username = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        btn = self.browser.find_element_by_name("signin")

        username.send_keys("pandatoast")
        password.send_keys("booleanbear")
        btn.click()

        self.browser.wait_for_page_load(15)
        self.assertIn(self.browser.page_source, "Logged in")
        self.assertEqual(self.browser.title, 'EXP Reviews')

if __name__ == "__main__":
    unittest.main()