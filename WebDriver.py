from selenium import webdriver
import selenium


class WebDriver:
    """
    This class provides a web driver for web requests.
    The driver should be only one at the same time, and can open multiple webpages.
    TODO: It should also be refreshed timely to avoid strange problems.
    Note this class is not thread-safe.
    """
    driver = None  # The web driver

    @staticmethod
    def new_driver():
        """
        Initializes and return a new driver.
        """
        # we need to use web-driver to open the webpage
        # The webpage got from requests is not complete
        # use a headless-chrome as webdriver
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')  # fix problems on non-graphics ubuntu server
        options.add_argument('--headless')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # try to find driver in PATH, if failed, then must exists in same folder
        try:
            driver = webdriver.Chrome(options=options)
        except selenium.common.exceptions.WebDriverException:
            driver = webdriver.Chrome('./chromedriver', options=options)
        return driver

    @staticmethod
    def get_driver():
        """
        Returns the driver. If the driver is not initialized, it will initialize it.
        """
        if WebDriver.driver is None:
            WebDriver.driver = WebDriver.new_driver()
        return WebDriver.driver

    @staticmethod
    def refresh_driver():
        """
        Close current driver and initialize a new one.
        Notice this operation costs a lot of time.
        """
        WebDriver.driver.close()
        WebDriver.driver = WebDriver.new_driver()
