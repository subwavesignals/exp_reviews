import unittest
from selenium import webdriver


class SeleniumTests(unittest.TestCase):
    """Tests for functionality or server and JS functions"""

    def setUp(self):
        self.browser = webdriver.Firefox(executable_path='/usr/local/bin/geckodriver.exe')

    def tearDown(self):
        self.browser.quit()

    def test_index(self):
        """Tests for index.html"""

        self.browser.get('http://localhost:5000/')
        self.assertEqual(self.browser.title, 'EXP Reviews')git 

if __name__ == "__main__":
    unittest.main()