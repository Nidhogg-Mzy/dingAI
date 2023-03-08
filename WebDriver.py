from selenium import webdriver
from selenium.common.exceptions import WebDriverException, SessionNotCreatedException


class WebDriver:
    """
    This class provides a web driver for web requests.
    The driver should be only one at the same time, and can open multiple webpages.
    Note this class is not thread-safe.
    """
    driver = None  # The web driver

    @staticmethod
    def new_driver():
        """
        Initializes and return a new driver.
        Raise WebDriverCannotFoundException if none driver available can be found.
        """
        # we need to use web-driver to open the webpage
        # The webpage got from requests is not complete
        # use a headless-chrome as webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # fix problems on non-graphics ubuntu server
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # try to find driver in PATH, if failed, then find in same folder
        find_in_path = True
        try:
            WebDriver.driver = webdriver.Chrome(options=options)
        except (WebDriverException, SessionNotCreatedException):
            find_in_path = False

        if find_in_path:
            return WebDriver.driver

        try:
            WebDriver.driver = webdriver.Chrome('./chromedriver', options=options)
        except (WebDriverException, SessionNotCreatedException, FileNotFoundError) as e:
            raise WebDriverCannotFoundException from e

        return WebDriver.driver

    @staticmethod
    def get_driver():
        """
        Returns the driver. If the driver is not initialized, it will initialize it.
        """
        if WebDriver.driver is None:
            WebDriver.driver = WebDriver.new_driver()
        else:
            # webdriver may down after a period of time, create a new driver then
            try:
                WebDriver.driver.get("https://www.baidu.com")   # TODO: other checking methods?
            except WebDriverException:
                WebDriver.driver = WebDriver.new_driver()
        return WebDriver.driver


class WebDriverCannotFoundException(Exception):
    """
    This exception is raised when the chrome web driver cannot be found.
    """
