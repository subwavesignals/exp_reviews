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

    # def test_index(self):
    #     """Tests for index.html"""

    #     self.browser.get(HOME_URL)
    #     self.assertEqual(self.browser.title, 'EXP Reviews')

    def test_homelink(self):

        self.browser.get(HOME_URL + '/users/1')
        homelink = self.browser.find_element_by_class_name("navbar-brand")

        homelink.click()

        self.browser.implicitly_wait(5)
        self.assertEqual(self.browser.title, 'EXP Reviews')

    def test_login(self):

        self.browser.get(HOME_URL + '/login')

        username = self.browser.find_element_by_name("username")
        password = self.browser.find_element_by_name("password")
        btn = self.browser.find_element_by_name("signin")

        username.send_keys("pandatoast")
        password.send_keys("booleanbear")
        btn.click()

        self.browser.implicitly_wait(5)
        self.assertIn(self.browser.page_source, "Logged in")
        self.assertEqual(self.browser.title, 'EXP Reviews')

if __name__ == "__main__":
    unittest.main()