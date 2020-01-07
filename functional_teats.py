from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self) -> None:
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        self.browser.quit()

    def test_can_start_a_list_and_retrieve_it_later(self):
        # open homepage
        self.browser.get("http://localhost:8000")

        # page title and head have to-do list
        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name('h1').text
        self.assertIn('To-Do', header_text)

        # enter a to-do item
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertEqual(inputbox.get_attribute('placeholder'), 'Enter a to-do item')

        # type a item
        inputbox.send_keys('Buy peacock feathers')

        # hit enter, the page updates, the page list that item in a to-do list table
        inputbox.send_keys(Keys.ENTER)

        table = self.browser.find_element_by_id('id_list_table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertTrue(any(rows.text == '1: Buy peacock feathers' for row in rows),
                        'New to-do item did not appear in table')

        # an other input box
        self.fail('Finish the test!')
        [...]


if __name__ == '__main__':
    unittest.main(warnings='ignore')
