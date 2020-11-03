from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest
import time
import os  # in order to upload file


class TestStringMethods(unittest.TestCase):

    def setUp(self):

        self.browser = webdriver.Chrome("chromedriver.exe")
        self.browser.get('https://multitrade.herokuapp.com/')

    def login(self): # initial login assist function

        self.browser.find_element_by_link_text("login").click()
        self.email_field = self.browser.find_element_by_name(
            'email')  # Find the email box
        time.sleep(1)
        self.email_field.send_keys('aricrachmany@gmail.com') # important the user should be exist
        self.pass_field = self.browser.find_element_by_name('pass')
        self.pass_field.send_keys('123123')

        self.button = self.browser.find_element_by_id("submit").click()
        time.sleep(2)
        assert(self.browser.current_url == 'https://multitrade.herokuapp.com/')

    def edit_presonal_details(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id('navbarDropdown').click()
        self.browser.find_element_by_link_text("personal details").click()
        time.sleep(1)
        self.state_field = self.browser.find_element_by_name('myState')
        self.state_field.clear()
        self.state_field.send_keys('H')
        self.state_field.send_keys(Keys.DOWN)
        self.state_field.send_keys(Keys.ENTER)
        self.phonePrefix_field = self.browser.find_element_by_name('phone1Prefix')
        self.phonePrefix_field.send_keys('055')
        self.phoneNum_field = self.browser.find_element_by_name('phoneNum')
        self.phoneNum_field.clear()
        self.phoneNum_field.send_keys('1234567')
        self.submit_field = self.browser.find_element_by_id("submit").click()


    def add_item(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id(
            'navbarDropdown').click()
        self.browser.find_element_by_link_text("my collection").click()
        time.sleep(1)
        self.browser.find_element_by_id("add item").click()
        time.sleep(1)
        self.itemName_field = self.browser.find_element_by_id('input name')
        self.itemName_field.send_keys("test item")
        self.itemDetails_field = self.browser.find_element_by_name(
            'itemDetails')
        self.itemDetails_field.send_keys('this is a test item')
        time.sleep(2)
        self.browser.find_element_by_id("image").send_keys(
            os.getcwd() + "/example.jpg")
        time.sleep(2)
        self.submit_field = self.browser.find_element_by_id("submit").click()
        time.sleep(2)
        assert(self.browser.current_url == 'https://multitrade.herokuapp.com/collection/')

    def delete_item(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id(
            'navbarDropdown').click()
        self.browser.find_element_by_link_text("my collection").click()
        time.sleep(1)
        self.browser.find_element_by_id("edit item").click()
        time.sleep(1)
        self.browser.find_element_by_id("delete item").click()
        time.sleep(1)

    def update_item(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id(
            'navbarDropdown').click()
        self.browser.find_element_by_link_text("my collection").click()
        time.sleep(1)
        self.browser.find_element_by_id("edit item").click()
        time.sleep(1)
        self.browser.find_element_by_id("input name").send_keys(" updated ")
        time.sleep(1)
        self.browser.find_element_by_id("update item").click()
        time.sleep(1)

    def create_tender(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id(
            'navbarDropdown').click()
        self.browser.find_element_by_link_text("create a tender").click()
        time.sleep(1)
        self.browser.find_element_by_id("input name").send_keys("test tender")
        time.sleep(1)
        self.browser.find_element_by_name("tenderDetails").send_keys("I am just a test tender")
        time.sleep(1)
        self.browser.find_element_by_id("datepicker").click() # open calendar
        time.sleep(1)
        self.browser.find_element_by_class_name('today').click() # pick today by class name
        time.sleep(1)
        self.browser.find_element_by_id("create tender").click()
        time.sleep(1)

    def join_tender(self):

        time.sleep(1)
        self.browser.find_element_by_id("select item").click()
        time.sleep(1)
        self.browser.find_element_by_id("clickable image").click()
        time.sleep(1)

    def edit_tender(self):

        time.sleep(1)
        self.browser.find_element_by_id("edit tender").click()
        time.sleep(1)
        self.browser.find_element_by_id("input name").send_keys(" new name")
        time.sleep(1)
        self.browser.find_element_by_id('edit tender submit').click()
        time.sleep(1)

    def delete_tender(self):

        time.sleep(1)
        self.openNavBar = self.browser.find_element_by_id(
            'navbarDropdown').click()
        self.browser.find_element_by_link_text("my own tenders").click()
        time.sleep(1)
        self.browser.find_element_by_id("delete tender").click()
        time.sleep(1)
        self.browser.find_element_by_id("delete permanently").click()
        time.sleep(1)

    def log_out(self):

        time.sleep(1)
        self.browser.find_element_by_link_text("log out").click()
        assert(self.browser.current_url == 'https://multitrade.herokuapp.com/')
        time.sleep(2)

    def path2(self):

        time.sleep(1)
        self.browser.find_element_by_link_text("About us").click()
        y = 0
        for timer in range(0,23): # scroll down in y Axis
            self.browser.execute_script("window.scrollTo(0, "+str(y)+")")
            y += 75
            time.sleep(0.3)

        time.sleep(1)
        self.browser.find_element_by_link_text("FQA").click()
        time.sleep(1)
        qeustions = self.browser.find_elements_by_class_name('accordion-toggle') # open question in FQA
        for questNum in range(0,4):
            qeustions[questNum].click()
            time.sleep(1)
        time.sleep(3)
        self.browser.find_element_by_link_text("Contact").click()
        time.sleep(1)
        self.browser.find_element_by_id("name").send_keys("Aric")
        time.sleep(1)
        self.browser.find_element_by_id("email").send_keys("aricrachmany@gmail.com")
        time.sleep(1)
        self.browser.find_element_by_id("subject").send_keys("Test subject")
        time.sleep(1)
        self.browser.find_element_by_id("message").send_keys("Test message")
        time.sleep(1)
        self.browser.find_element_by_class_name('update').click()
        time.sleep(1)

    def search(self):
        time.sleep(1)
        self.browser.find_element_by_name("search").send_keys("test tender")
        time.sleep(1)
        self.browser.find_element_by_class_name("searchBtn").click()
        time.sleep(1)
        self.browser.find_element_by_name("search").clear()
        time.sleep(1)
        self.browser.find_element_by_class_name("searchBtn").click()
        time.sleep(1)

    def home(self):
        time.sleep(1)
        self.browser.find_element_by_class_name("navbar-brand").click()




    def test_1(self):
        self.login()
        self.edit_presonal_details()
        self.add_item()
        self.update_item()
        self.create_tender()
        self.join_tender()
        self.edit_tender()
        # self.home()
        self.search()
        self.delete_tender()
        self.delete_item()
        self.log_out()
        self.path2()

if __name__ == '__main__':

    unittest.main()
