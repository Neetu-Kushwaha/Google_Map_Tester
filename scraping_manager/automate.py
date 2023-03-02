import os
import sys
import time
import logging
import zipfile
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager, ChromeType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service

current_file = os.path.basename(__file__)

# Diable web driver manager logs
logger_webdriver = logging.getLogger("webdriver_manager")
logger_webdriver.setLevel(logging.ERROR)

logger_selenium = logging.getLogger("selenium")
logger_selenium.setLevel(logging.ERROR)


class WebScraping:
    """
    Class to manage and configure web browser
    """

    def __init__(
            self, web_page="", headless=False, time_out=0,
            proxy_server="", proxy_port="", proxy_user="", proxy_pass="",
            chrome_folder="", user_agent=False, capabilities=False,
            download_folder="", extensions=[], incognito=False, experimentals=True,
            start_killing=False):
        """
        Constructor of the class
        """

        self.basetime = 1

        # variables of class
        self.__headless = headless
        self.__current_dir = os.path.dirname(__file__)
        self.__web_page = web_page
        self.__proxy_server = proxy_server
        self.__proxy_port = proxy_port
        self.__proxy_user = proxy_user
        self.__proxy_pass = proxy_pass
        self.__pluginfile = 'proxy_auth_plugin.zip'
        self.__chrome_folder = chrome_folder
        self.__user_agent = user_agent
        self.__capabilities = capabilities
        self.__download_folder = download_folder
        self.__extensions = extensions
        self.__incognito = incognito
        self.__experimentals = experimentals

        # Kill chrome from CMD in donwows
        if start_killing:
            command = 'taskkill /IM "chrome.exe" /F'
            os.system(command)

        # Create and instance of the web browser
        self.__set_browser_instance()

        # Get current file name
        self.current_file = os.path.basename(__file__)

        # Set time out
        if time_out > 0:
            self.driver.set_page_load_timeout(time_out)

        if self.__web_page:
            self.set_page(self.__web_page)

    def __set_browser_instance(self):
        """
        Open and configure browser
        """

        # Disable logs
        os.environ['WDM_LOG_LEVEL'] = '0'
        os.environ['WDM_PRINT_FIRST_LINE'] = 'False'

        # Configure browser
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--start-maximized')
        options.add_argument('--output=/dev/null')
        options.add_argument('--log-level=3')
        options.add_argument("--disable-notifications")
        options.add_argument("disable-infobars")
        options.add_argument("--safebrowsing-disable-download-protection")

        # Experimentals
        if self.__experimentals:
            options.add_experimental_option('excludeSwitches', ['enable-logging', "enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

        if self.__headless:
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--headless")

        # Set proxy without autentication
        if (self.__proxy_server and self.__proxy_port
                and not self.__proxy_user and not self.__proxy_pass):
            proxy = f"{self.__proxy_server}:{self.__proxy_port}"
            options.add_argument(f"--proxy-server={proxy}")

        # Set proxy with autentification
        if (self.__proxy_server and self.__proxy_port
                and self.__proxy_user and self.__proxy_pass):
            self.__create_proxy_extesion()
            options.add_extension(self.__pluginfile)

        # Set chrome folder
        if self.__chrome_folder:
            options.add_argument(f"--user-data-dir={self.__chrome_folder}")

        # Set default user agent
        if self.__user_agent:
            options.add_argument(
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')

        if self.__capabilities:
            capabilities = DesiredCapabilities.CHROME
            capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        else:
            capabilities = None

        if self.__download_folder:
            prefs = {"download.default_directory": f"{self.__download_folder}",
                     "download.prompt_for_download": "false",
                     'profile.default_content_setting_values.automatic_downloads': 1,
                     'profile.default_content_settings.popups': 0,
                     "download.directory_upgrade": True,
                     "plugins.always_open_pdf_externally": True,
                     "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                     'download.extensions_to_open': 'xml',
                     'safebrowsing.enabled': True
                     }

            options.add_experimental_option("prefs", prefs)

        if self.__extensions:
            for extension in self.__extensions:
                options.add_extension(extension)

        if self.__incognito:
            options.add_argument("--incognito")

        if self.__experimentals:
            options.add_argument("--disable-blink-features=AutomationControlled")

        # Set configuration to  and create instance
        # chromedriver = ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.GOOGLE).install()),
                                       options=options,
                                       service_log_path=None,
                                       desired_capabilities=capabilities)

    def __create_proxy_extesion(self):
        """Create a proxy chrome extension"""

        # plugin data
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (self.__proxy_server, self.__proxy_port, self.__proxy_user, self.__proxy_pass)

        # Compress file
        with zipfile.ZipFile(self.__pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)

    def get_attrib(self, selector, attrib_name):
        """
        Return the class value from specific element in the page
        """

        try:
            elem = self.driver.find_element(By.XPATH, selector)
            return elem.get_attribute(attrib_name)
        except Exception as err:
            return None

    def get_attribs(self, selector, attrib_name):
        """
        Return the attributes value from specific element in the page
        """

        attributes = []
        elems = self.driver.find_elements(By.XPATH, selector)

        for elem in elems:

            try:
                attribute = elem.get_attribute(attrib_name)
                attributes.append(attribute)
            except Exception as err:
                attributes.append("NA")
                continue
        return attributes

    def get_elems(self, selector):
        """
        Return a list of specific element in the page
        """

        elems = self.driver.find_elements(By.XPATH, selector)
        return elems

    def get_browser(self):
        """
        Return the current instance of web browser
        """

        return self.driver

    def end_browser(self):
        """
        End current instance of web browser
        """

        self.driver.quit()

    def send_data(self, selector, data):
        """
        Send data to specific input fill
        """

        elem = self.driver.find_element(By.XPATH, selector)
        elem.send_keys(data)

    def click(self, selector):
        """
        Send click to specific element in the page
        """

        elem = self.driver.find_element(By.XPATH, selector)
        elem.click()

    def get_elems(self, selector):
        """
        Return a list of specific element in the page
        """

        elems = self.driver.find_elements(By.XPATH, selector)
        return elems

    def check_exists_by_xpath(self, selector):
        """
        Check whether specific element in the page exist by xpath or not
        """

        try:
            self.driver.find_element(By.XPATH, selector)
        except NoSuchElementException:
            return False
        return True

    def go_back(self):
        """
        go back to the previous page
        """

        self.driver.execute_script("history.go(-1)")
        # self.driver.back()

    def visibility_by_element_located_and_click_js(self, selector, timeout=10):
        """
         Send click with js, for hidden elements
         """

        element = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, selector)))
        self.driver.execute_script("arguments[0].click();", element)

    def wait(self, timeout=10):
        """
        Wait until timeout
        """
        WebDriverWait(driver=self.driver, timeout=300)

    def get_text(self, selector):
        """
        Return text for specific element in the page
        """

        try:
            elem = self.driver.find_element(By.XPATH, selector)
            return elem.text
        except Exception as err:
            # print (err)
            return None

    def get_texts(self, selector):
        """
        Return a list of text for specific selector
        """

        texts = []

        elems = self.driver.find_elements(By.XPATH, selector)

        for elem in elems:
            try:
                texts.append(elem.text)
            except Exception as err:
                texts.append("NA")
                continue

        return texts

    def visibility_by_element_located(self, selector, timeout=10):
        """
        Wait until the element is located
        """
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, selector)))

    def element_to_be_clickable(self, selector, timeout=10):
        """
         wait until the element is located and clickable and  then Send click to specific element in the page
        """
        elem = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.XPATH, selector)))
        elem.click()

    def set_page(self, web_page, time_out=0, break_time_out=False):
        """
        Update the web page in browser
        """

        try:

            self.__web_page = web_page

            # Save time out when is greader than 0
            if time_out > 0:
                self.driver.set_page_load_timeout(time_out)

            self.driver.get(self.__web_page)

        # Catch error in load page
        except TimeoutException:

            # Raise error
            if break_time_out:
                raise Exception(f"Time out to load page: {web_page}")

            # Ignore error
            else:
                self.driver.execute_script("window.stop();")

    def visibility_by_element_located_click(self, selector, timeout=10):
        """
         wait until the element is located and then Send click to specific element in the page
        """
        try:
            button = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, selector)))
            button.click()
            return True
        except Exception as err:
            # print (err)
            return False

    def element_to_be_clickable_by_css(self, selector, timeout=10):
        """
         wait until the element is located and clickable and then Send click to specific element in the page
        """
        elem = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        elem.click()

    def visibility_by_element_located_by_css(self, selector, timeout=10):
        """
        Wait until the element is located
        """
        WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))

    def get_elem_by_css(self, selector):
        """
        Return a list of specific element in the page
        """

        elem = self.driver.find_element(By.CSS_SELECTOR, selector)
        return elem

    def get_elem_by_css_class_name(self, selector):
        """
        Return a list of specific element in the page
        """

        elem = self.driver.find_element(By.CLASS_NAME, selector)
        return elem

    def get_elements_by_css_class_name(self, selector):
        """
        Return a list of specific element in the page
        """

        elems = self.driver.find_elements(By.CLASS_NAME, selector)
        return elems







