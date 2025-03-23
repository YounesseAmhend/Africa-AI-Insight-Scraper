import logging
import os
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,  # Exception when a click is intercepted by another element
    ElementNotInteractableException,    # Exception when an element cannot be interacted with
    NoSuchElementException,             # Exception when an element is not found in the DOM
    StaleElementReferenceException,     # Exception when an element reference is no longer valid
    TimeoutException,                   # Exception when a wait times out
)
from selenium.webdriver.common.action_chains import ActionChains  # For complex mouse and keyboard actions
from selenium.webdriver.common.by import By                       # For locating elements
from selenium.webdriver.edge.service import Service               # Edge WebDriver service
from selenium.webdriver.support import expected_conditions as EC  # Conditions to wait for
from selenium.webdriver.support.ui import WebDriverWait           # For waiting for conditions

from settings import DEBUG_MODE                           # Import debug mode flag from settings
from utils.infinite_scrolling_iterator import InfiniteScrollIterator  # Iterator for infinite scrolling
from utils.pagination_iterator import PaginationIterator             # Iterator for pagination


# ================================================================================================
# CUSTOM WEBDRIVER CLASS DEFINITION
# ================================================================================================
class CustomDriver:
    """
    CustomDriver is a wrapper around Selenium WebDriver with specialized methods
    for web scraping, particularly handling different pagination mechanisms.
    
    This class provides:
    1. Anti-detection mechanisms to avoid being blocked by websites
    2. Methods to handle traditional pagination (clicking "next" buttons)
    3. Methods to handle infinite scrolling with optional "load more" buttons
    4. Utility methods for retrieving page content
    5. Proper resource cleanup
    
    Data Flow:
    1. Initialize EdgeDriver with anti-detection and performance optimizations
    2. Navigate to target URLs
    3. Extract content either through pagination or infinite scrolling
    4. Return consolidated HTML content for further processing
    5. Clean up resources when done
    """

    # Default timeout in seconds for waiting operations
    DEFAULT_TIMEOUT_S = 2.5

    # ================================================================================================
    # INITIALIZATION
    # ================================================================================================
    def __init__(self) -> None:
        """
        Initialize the CustomDriver with anti-detection mechanisms and performance optimizations.
        
        Steps:
        1. Configure the Edge WebDriver path based on the operating system
        2. Set up Edge options with anti-detection and performance optimizations
        3. Initialize the Edge WebDriver with these options
        4. Apply additional anti-detection JavaScript
        5. Set up WebDriverWait and ActionChains instances for later use
        """
        # Determine the path to the Edge WebDriver executable based on the operating system
        EDGE_DRIVER_PATH = (
            "bin/msedgedriver.exe" if os.name == "nt" else "bin/msedgedriver"
        )  # Windows uses .exe extension, Unix systems don't
        
        # Initialize the Edge WebDriver service
        self.service = Service(EDGE_DRIVER_PATH)
        
        # Initialize Edge options for configuring the browser
        self.options = webdriver.EdgeOptions()

        # Only run in headless mode (no visible browser window) if not in debug mode
        if not DEBUG_MODE:
            self.options.add_argument("--headless")  # No visible browser window

        # ================================================================================================
        # ANTI-DETECTION CONFIGURATION
        # ================================================================================================
        # Add arguments and options to prevent websites from detecting automation
        self.options.add_argument("--disable-blink-features=AutomationControlled")  # Disable automation flag
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])  # Hide automation flag
        self.options.add_experimental_option("useAutomationExtension", False)  # Disable automation extension

        # ================================================================================================
        # PERFORMANCE OPTIMIZATION
        # ================================================================================================
        # Add arguments to improve performance and stability
        self.options.add_argument("--disable-extensions")  # Disable browser extensions for faster loading
        self.options.add_argument("--disable-gpu")  # Disable GPU acceleration (often helps in headless mode)
        self.options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
        self.options.add_argument("--disable-browser-side-navigation")  # Disable browser side navigation
        self.options.add_argument("--disable-infobars")  # Disable info bars that might affect scraping
        self.options.add_argument("--no-sandbox")  # Disable sandbox for better performance
        self.options.add_argument("--disable-features=NetworkService")  # Disable network service
        self.options.add_argument("--disable-features=VizDisplayCompositor")  # Disable compositor
        self.options.add_argument("--disable-software-rasterizer")  # Disable software rasterizer
        self.options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors

        # ================================================================================================
        # WEBDRIVER INITIALIZATION
        # ================================================================================================
        # Initialize the Edge WebDriver with configured service and options
        self.driver = webdriver.Edge(service=self.service, options=self.options)
        
        # Further anti-detection: modify navigator.webdriver property using CDP
        # This helps bypass more sophisticated detection mechanisms
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            },
        )

        # Initialize WebDriverWait for waiting operations with default timeout
        self.wait = WebDriverWait(self.driver, timeout=__class__.DEFAULT_TIMEOUT_S)
        
        # Initialize ActionChains for complex mouse and keyboard interactions
        self.actions = ActionChains(self.driver)

    # ================================================================================================
    # URL NAVIGATION
    # ================================================================================================
    def get(self, url: str) -> None:
        """
        Navigate to the specified URL using the WebDriver.
        
        Args:
            url (str): The URL to navigate to
            
        Data Flow:
            1. WebDriver receives the URL
            2. Browser navigates to the URL
            3. Execution continues once page is loaded (controlled by browser's default behavior)
        """
        # Navigate to the specified URL
        self.driver.get(
            url,
        )

    # ================================================================================================
    # INFINITE SCROLLING HANDLER
    # ================================================================================================
    def handle_infinite_scroll(
        self,
        css_selector: str | None,  # CSS selector for "load more" button (if any)
        timeout_s: float = DEFAULT_TIMEOUT_S,  # Timeout for waiting operations
        max_loads: int = 20,  # Maximum number of "load more" operations to perform
    ) -> str:
        """
        Handle websites with infinite scrolling, optionally with "load more" buttons.
        
        Args:
            css_selector (str | None): CSS selector for "load more" button, or None if pure scrolling
            timeout_s (float): Timeout in seconds for waiting operations
            max_loads (int): Maximum number of scroll/load operations to perform
            
        Returns:
            str: Concatenated HTML content from all loaded pages
            
        Data Flow:
            1. Create an InfiniteScrollIterator to handle scrolling and loading
            2. Iterate through the content loaded after each scroll/load operation
            3. Concatenate the HTML from each iteration
            4. Return the complete HTML for further processing
        """
        logging.debug("Handling infinite scrolling...")
        
        # Initialize empty string to store concatenated HTML
        html = ""
        
        # Create an iterator that will progressively load more content through scrolling
        # and optionally clicking "load more" buttons
        for page in InfiniteScrollIterator(
            self,  # Pass this CustomDriver instance
            css_selector,  # CSS selector for "load more" button (if any)
            timeout_s,  # Timeout for waiting operations
            max_loads,  # Maximum number of load operations
        ):
            # Concatenate the HTML from this iteration
            html += page

        # Return the complete HTML content
        return html

    # ================================================================================================
    # PAGINATION HANDLER
    # ================================================================================================
    def handle_pagination(
        self,
        css_selector: str,  # CSS selector for "next" button
        timeout_s: float = DEFAULT_TIMEOUT_S,  # Timeout for waiting operations
        max_pages: int = 20,  # Maximum number of pages to navigate through
    ) -> str:
        """
        Handle traditional pagination by clicking "next" buttons to navigate through pages.
        
        Args:
            css_selector (str): CSS selector for the "next" button
            timeout_s (float): Timeout in seconds for waiting operations
            max_pages (int): Maximum number of pages to navigate through
            
        Returns:
            str: Concatenated HTML content from all visited pages
            
        Data Flow:
            1. Create a PaginationIterator to handle clicking "next" buttons
            2. Iterate through each page loaded after clicking "next"
            3. Concatenate the HTML from each page
            4. Return the complete HTML for further processing
        """
        logging.debug("Handling pagination...")

        # Initialize empty string to store concatenated HTML
        html: str = ""

        # Create an iterator that will progressively navigate through pages
        # by clicking the "next" button
        for page in PaginationIterator(
            self,  # Pass this CustomDriver instance
            css_selector,  # CSS selector for the "next" button
            timeout_s,  # Timeout for waiting operations
            limit=max_pages,  # Maximum number of pages to navigate through
        ):
            # Concatenate the HTML from this page
            html += page

        # Return the complete HTML content
        return html

    # ================================================================================================
    # NEXT PAGE NAVIGATION
    # ================================================================================================
    def nextPage(
        self,
        css_selector: str,  # CSS selector for "next" button
        timeout_s: float = DEFAULT_TIMEOUT_S,  # Timeout for waiting operations
    ) -> None:
        """
        Navigate to the next page by clicking a "next" button.
        
        This method:
        1. Scrolls to the bottom of the page to ensure all content is loaded
        2. Waits for the "next" button to become clickable
        3. Scrolls the button into view
        4. Attempts to click the button using JavaScript or ActionChains
        5. Waits for the new page to load
        
        Args:
            css_selector (str): CSS selector for the "next" button
            timeout_s (float): Timeout in seconds for waiting operations
            
        Raises:
            StopIteration: When no more "next" button is found or other errors occur
            
        Data Flow:
            1. Scroll to bottom of current page to load all content
            2. Locate and attempt to click the "next" button
            3. Wait for new page content to load
            4. If any error occurs, raise StopIteration to signal end of pagination
        """
        # Create a WebDriverWait instance with the specified timeout
        # or use the default one if timeout matches the default
        wait = self.wait
        if timeout_s != self.DEFAULT_TIMEOUT_S:
            wait = WebDriverWait(self.driver, timeout=timeout_s)

        # ================================================================================================
        # SCROLL TO BOTTOM OF PAGE
        # ================================================================================================
        # Get the initial scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        # Scroll to the bottom of the page to ensure all content is loaded
        # Keep scrolling until we reach the true bottom (no more height increase)
        while True:
            # Scroll down to the bottom of the page
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            # Wait for content to load after scrolling
            sleep(0.5)
            # Get the new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            # If the height hasn't changed, we've reached the bottom
            if new_height == last_height:
                break
            # Update the last height for the next iteration
            last_height = new_height
            
        # Additional wait for smooth scrolling and to ensure page is fully loaded
        sleep(1)

        # ================================================================================================
        # NEXT BUTTON INTERACTION
        # ================================================================================================
        try:
            # Wait for the "Next" button to appear and become clickable
            next_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, css_selector))
            )

            # Scroll the button into view to ensure it's visible
            self.driver.execute_script(
                "arguments[0].scrollIntoView(true);", next_button
            )

            # Small delay to ensure the page is settled after scrolling
            sleep(0.5)

            # Try JavaScript click first (more reliable for some websites)
            try:
                # Execute JavaScript to click the button
                self.driver.execute_script("arguments[0].click();", next_button)
            except Exception:
                # If JavaScript click fails, try using ActionChains
                # This is a fallback for cases where JavaScript clicking doesn't work
                self.actions.move_to_element(next_button).click().perform()

            # Wait for new content to load after clicking
            sleep(2)

        # ================================================================================================
        # ERROR HANDLING
        # ================================================================================================
        except Exception as e:
            # Log detailed error information based on the exception type
            logging.error(f"Error type: {type(e).__name__}")
            
            # Provide specific error messages based on the type of exception
            if isinstance(e, TimeoutException):
                logging.error("Timeout waiting for next button to be clickable")
            elif isinstance(e, ElementNotInteractableException):
                logging.error("Next button found but not clickable")
            elif isinstance(e, NoSuchElementException):
                logging.error("Next button element not found in the DOM")
            elif isinstance(e, StaleElementReferenceException):
                logging.error("Next button reference is stale (page may have changed)")
            elif isinstance(e, ElementClickInterceptedException):
                logging.error("Click was intercepted by another element")

            # Signal the end of pagination by raising StopIteration
            # This will be caught by the PaginationIterator
            raise StopIteration

    # ================================================================================================
    # HTML CONTENT RETRIEVAL
    # ================================================================================================
    def get_html(self) -> str:
        """
        Get the current page source (HTML content) from the WebDriver.
        
        Returns:
            str: The HTML content of the current page
            
        Data Flow:
            1. Request page source from WebDriver
            2. Return raw HTML content
        """
        # Return the current page source (HTML content)
        return self.driver.page_source

    # ================================================================================================
    # RESOURCE CLEANUP - DESTRUCTOR
    # ================================================================================================
    def __del__(self):
        """
        Destructor method to ensure the driver is properly closed when the object is garbage collected.
        This helps prevent memory leaks and orphaned browser processes.
        
        Data Flow:
            1. Python garbage collector calls this method when the object is being destroyed
            2. Method attempts to quit the WebDriver to release resources
            3. Any errors during cleanup are printed to stderr
        """
        try:
            # Quit the WebDriver to close the browser and release resources
            self.driver.quit()
        except Exception as e:
            # Can't use logging here as it might be unavailable during garbage collection
            # So we use direct printing to stderr instead
            import sys
            print(f"Error during driver cleanup: {str(e)}", file=sys.stderr)

    # ================================================================================================
    # EXPLICIT RESOURCE CLEANUP METHOD
    # ================================================================================================
    def quit(self):
        """
        Explicitly quit the WebDriver to release resources.
        
        This method should be called when the driver is no longer needed,
        especially in scenarios where waiting for garbage collection is not desirable.
        
        Data Flow:
            1. Method is called explicitly by the user of this class
            2. WebDriver is quit, closing the browser and releasing resources
        """
        # Quit the WebDriver to close the browser and release resources
        self.driver.quit()