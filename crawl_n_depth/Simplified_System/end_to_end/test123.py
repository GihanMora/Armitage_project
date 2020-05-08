from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
from fake_useragent import UserAgent
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
def use_firefox():
    binary = FirefoxBinary('C://Program Files//Mozilla Firefox//firefox.exe')
    browser = webdriver.Firefox(firefox_binary=binary)
    # profile = webdriver.FirefoxProfile()
    # # profile.set_preference("browser.privatebrowsing.autostart", True)
    # binary = 'C://Program Files//Mozilla Firefox//firefox.exe'
    # options = Options()
    # options.binary_location = binary
    # # options.headless = True
    #
    # profile.update_preferences()
    # browser = webdriver.Firefox(firefox_options=options, firefox_profile=profile,
    #                             executable_path='F://Armitage_project//crawl_n_depth//utilities//geckodriver.exe')
    return browser

def get_browser():
    ua = UserAgent()
    # PROXY = proxy_generator()
    userAgent = ua.random #get a random user agent
    options = webdriver.ChromeOptions()  # use headless version of chrome to avoid getting blocked
    options.add_argument('headless')
    options.add_argument(f'user-agent={userAgent}')
    # options.add_argument("start-maximized")# // open Browser in maximized mode
    # options.add_argument("disable-infobars")# // disabling infobars
    # options.add_argument("--disable-extensions")# // disabling extensions
    # options.add_argument("--disable-gpu")# // applicable to windows os only
    # options.add_argument("--disable-dev-shm-usage")# // overcome limited resource problems
    # options.add_argument('--proxy-server=%s' % PROXY)
    browser = webdriver.Chrome(chrome_options=options,  # give the path to selenium executable
                                   # executable_path='F://Armitage_lead_generation_project//chromedriver.exe'
                                   executable_path='F://Armitage_project//crawl_n_depth//utilities//chromedriver.exe',
                                    service_args=["--verbose", "--log-path=D:\\qc1.log"]
                                   )
    return browser

browser = get_browser()
browser.get('https://www.dnb.com/business-directory/company-profiles.caltex_australia_petroleum_pty_ltd.0396ff68b22e2dc4efe23c599456ed68.html')
ps = browser.page_source
print(len(ps))
browser.quit()