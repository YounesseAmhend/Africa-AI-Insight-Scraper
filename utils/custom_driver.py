import os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (ElementClickInterceptedException,
                                        ElementNotInteractableException,
                                        NoSuchElementException,
                                        StaleElementReferenceException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from settings import DEBUG_MODE


class CustomDriver:

    EDGE_DRIVER_PATH = "bin/msedgedriver.exe" if os.name == 'nt' else "bin/msedgedriver" # check if windows

    service = Service(EDGE_DRIVER_PATH)
    options = webdriver.EdgeOptions()
    
    if not DEBUG_MODE:
        options.add_argument('--headless')
        
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
    actions = ActionChains(driver)
    

    @staticmethod
    def get(url: str)-> None:
        __class__.driver.get(url, )

    @staticmethod
    def scroll_to_end(css_selector: str | None, timeout_s: float = DEFAULT_TIMEOUT_S) -> None:
        wait = __class__.wait
        if timeout_s != __class__.DEFAULT_TIMEOUT_S:
            wait = WebDriverWait(__class__.driver, timeout=timeout_s)
        print("Handling infinite scrolling...")

        while True:
            try:
                # Wait for the "Load More" button to appear

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

                # Scroll to the button and click it

                if css_selector is not None:
                    load_more_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                    )

                # Scroll to the button and click it
                load_more_button.click()

                # Wait for new content to load
                sleep(2)
            except Exception as e:
                print("No more 'Load More' button found or error:")
                break
            
    @staticmethod
    def handle_pagination(css_selector: str, timeout_s: float = DEFAULT_TIMEOUT_S, max_pages: int = 20) -> str:
        print("Handling pagination...")
        wait = __class__.wait
        
        if timeout_s != __class__.DEFAULT_TIMEOUT_S:
            wait = WebDriverWait(__class__.driver, timeout=timeout_s)
            
        html: str = ""
        page_count: int = 1
        while True:
            html += __class__.get_html()
            
            if page_count > 20:
                break

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

            
            try:
                # Wait for the "Next" button to appear
                print(f"Next Page {page_count + 1}")
                next_button = wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
                )

                # Scroll the button into view
                __class__.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                
                # Add a small delay to ensure the page is settled
                sleep(0.5)
                
                # Try JavaScript click first to avoid intercepted clicks
                try:
                    __class__.driver.execute_script("arguments[0].click();", next_button)
                except Exception:
                    # If JavaScript click fails, try moving to the element first
                    __class__.actions.move_to_element(next_button).click().perform()
                finally:
                    page_count += 1
                # Wait for new content to load
                sleep(2)
            except Exception as e:
                # print(f"No more 'Next' button found or error: {str(e)}")
                print(f"Error type: {type(e).__name__}")
                if isinstance(e, TimeoutException):
                    print("Timeout waiting for next button to be clickable")
                elif isinstance(e, ElementNotInteractableException):
                    print("Next button found but not clickable")
                elif isinstance(e, NoSuchElementException):
                    print("Next button element not found in the DOM")
                elif isinstance(e, StaleElementReferenceException):
                    print("Next button reference is stale (page may have changed)")
                elif isinstance(e, ElementClickInterceptedException):
                    print("Click was intercepted by another element")
                break
        return html
    
    @staticmethod
    def get_html() -> str:
        return __class__.driver.page_source
    
    @staticmethod
    def close():
        __class__.driver.quit()
