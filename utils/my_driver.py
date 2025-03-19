
import os
from time import sleep

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class MyDriver:
    
    EDGE_DRIVER_PATH = "bin/msedgedriver.exe" if os.name == 'nt' else "bin/msedgedriver" # check if windows
    
    service = Service(EDGE_DRIVER_PATH)
    options = webdriver.EdgeOptions()
    # options.add_argument('--headless')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Edge(service=service, options=options)
    driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
        'source': '''
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        '''
    }) 
    
    DEFAULT_TIMEOUT_S = 2.5
    wait = WebDriverWait(driver, timeout=DEFAULT_TIMEOUT_S)
    
    @staticmethod
    def get(url: str)-> None:
        __class__.driver.get(url, )
        
    @staticmethod
    def scroll_to_end(css_selector: str | None, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        wait = __class__.wait
        if timeout_s != __class__.DEFAULT_TIMEOUT_S:
            wait = WebDriverWait(__class__.driver, timeout=timeout_s)
            
        while True:
            try:
                # Wait for the "Load More" button to appear
                if css_selector is not None:
                    load_more_button =  wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))

                # Scroll to the button and click it
                last_height = __class__.driver.execute_script("return document.body.scrollHeight")
                while True:
                    # Scroll down to bottom
                    __class__.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # Wait to load page
                    sleep(1)
                    # Calculate new scroll height and compare with last scroll height
                    new_height = __class__.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                sleep(1)  # Smooth scrolling
                load_more_button.click()

                # Wait for new content to load
                sleep(2)
            except Exception as e:
                print("No more 'Load More' button found or error:", e)
                break
            
            
    @staticmethod
    def get_html() -> str:
        return __class__.driver.page_source

        