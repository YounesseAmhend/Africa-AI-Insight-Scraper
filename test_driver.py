import logging
import sys
from time import sleep
from utils.custom_driver import CustomDriver

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def test_driver():
    """Test if the WebDriver initializes and navigates correctly"""
    driver = None
    try:
        logger.info("Initializing driver...")
        driver = CustomDriver()
        
        if driver.driver is None:
            logger.error("Driver initialization failed - driver.driver is None")
            return False
            
        logger.info("Navigating to Google...")
        driver.get("https://www.google.com")
        sleep(2)
        
        title = driver.driver.title
        logger.info(f"Page title: {title}")
        
        html = driver.get_html()
        logger.info(f"HTML content length: {len(html)}")
        
        return True
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False
    finally:
        if driver:
            logger.info("Quitting driver...")
            driver.quit()

if __name__ == "__main__":
    success = test_driver()
    sys.exit(0 if success else 1) 