import time
from django.test import LiveServerTestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import unittest

MAX_WAIT = 3


# class NewVisitorTest(LiveServerTestCase):
class NewVisitorTest(StaticLiveServerTestCase):

    def setUp(self) -> None:
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)

    def tearDown(self) -> None:
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()
        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    def test_can_start_a_list_and_retrieve_it_later_for_one_user(self):
        # open homepage
        self.browser.get(self.live_server_url)

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

        # to do item show on her list
        self.wait_for_row_in_list_table('1: Buy peacock feathers')

        # add another in input box
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Use peacock feathers to make a fly')
        inputbox.send_keys(Keys.ENTER)

        # the page updated again, and show both items on her list
        self.wait_for_row_in_list_table('1: Buy peacock feathers')
        self.wait_for_row_in_list_table('2: Use peacock feathers to make a fly')

    def test_multiple_users_can_start_lists_at_different_urls(self):
        # Edith starts a new to-do list
        self.browser.get(self.live_server_url)
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy peacook feathers')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy peacook feathers')

        # she notices that her list has a unique url
        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, '/lists/.+')

        # Now a new user, Francis, come along to the site.

        ## We use a new browser session to make sure that no information
        ## of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Chrome()

        # Francis visits the home page. There is no sign of Edith's list
        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacook feathers', page_text)
        self.assertNotIn('make a fly', page_text)

        # Francis starts a new list by entering a new item
        inputbox = self.browser.find_element_by_id('id_new_item')
        inputbox.send_keys('Buy milk')
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Buy milk')

        # Francis get his own unique URL
        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, '/lists/.+')
        self.assertNotEqual(edith_list_url, francis_list_url)

        # Again, there is no trace of Edith's list
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertNotIn('Buy peacook feathers', page_text)
        self.assertIn('Buy milk', page_text)

    def test_layout_and_styling(self):
        # Edith go to the home page
        self.browser.get(self.live_server_url)
        self.browser.set_window_size(1024, 768)

        time.sleep(2)
        # she notices the input box is nearly entered
        inputbox = self.browser.find_element_by_id('id_new_item')
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=10)
        inputbox.send_keys('testing\n')
        inputbox = self.browser.find_element_by_id('id_new_item')

        time.sleep(2)
        self.assertAlmostEqual(inputbox.location['x'] + inputbox.size['width'] / 2, 512, delta=10)