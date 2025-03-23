import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI, status

from constants import *
from constants import SOURCES
from utils.contains_triggers import contains_triggers
from dtypes.author import Author
from settings import *
from utils.custom_driver import CustomDriver
from utils.trigger_file import TriggerFile

# ================================================================================================
# LOGGING CONFIGURATION
# ================================================================================================
# Set up comprehensive logging with output to both a file and console
# The log format includes timestamp, logger name, log level, and the actual message
# This enables tracking of the application's execution flow and debugging issues
logging.basicConfig(
    level=logging.INFO,  # Set the minimum logging level to INFO (can be changed to DEBUG for more verbose output)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Define the format of log messages
    handlers=[
        logging.FileHandler("scraper.log"),  # Output logs to a file named 'scraper.log'
        logging.StreamHandler()  # Additionally output logs to the console/stdout
    ],
)
# Create a logger instance specific to this module for more granular control
logger = logging.getLogger(__name__)

# ================================================================================================
# FASTAPI APPLICATION INITIALIZATION
# ================================================================================================
# Initialize the FastAPI framework with metadata about the application
# This creates the web server foundation that will handle HTTP requests
app = FastAPI(
    title="Africa-AI-Insight-Scraper",  # Title displayed in the auto-generated API documentation
    description="Web scraper for AI and Africa-related content",  # Description of the application's purpose
    version="1.0.0",  # Current version number of the application
)

# ================================================================================================
# TRIGGER FILES LOADING
# ================================================================================================
# Attempt to load the trigger files that contain words and phrases used for content filtering
# These files define what content should be considered relevant to AI or Africa topics
try:
    # Initialize TriggerFile objects for each category of triggers
    # Each TriggerFile object loads words/phrases from the specified file path
    ai_trigger_words = TriggerFile(AI_TRIGGER_WORDS_PATH)  # Words related to AI (e.g., "machine learning", "neural network")
    ai_trigger_phrases = TriggerFile(AI_TRIGGER_PHRASES_PATH)  # Phrases related to AI (e.g., "artificial intelligence technology")
    africa_trigger_words = TriggerFile(AFRICA_TRIGGER_WORDS_PATH)  # Words related to Africa (e.g., "Lagos", "Kenya")
    africa_trigger_phrases = TriggerFile(AFRICA_TRIGGER_PHRASES_PATH)  # Phrases related to Africa (e.g., "West African countries")

    # Extract the actual trigger content from each TriggerFile object
    # These lists will be used later to match against scraped content titles
    trigger_words_ai = ai_trigger_words.get()  # Get the list of AI-related words
    trigger_phrases_ai = ai_trigger_phrases.get()  # Get the list of AI-related phrases
    trigger_words_africa = africa_trigger_words.get()  # Get the list of Africa-related words
    trigger_phrases_africa = africa_trigger_phrases.get()  # Get the list of Africa-related phrases

    # Log the number of triggers loaded for transparency and debugging
    logger.info(f"Loaded {len(trigger_words_ai)} AI trigger words")  # Log count of AI words
    logger.info(f"Loaded {len(trigger_phrases_ai)} AI trigger phrases")  # Log count of AI phrases
    logger.info(f"Loaded {len(trigger_words_africa)} Africa trigger words")  # Log count of Africa words
    logger.info(f"Loaded {len(trigger_phrases_africa)} Africa trigger phrases")  # Log count of Africa phrases

# Handle any exceptions that might occur during trigger file loading
except Exception as e:
    # Log the error for debugging purposes
    logger.error(f"Error loading trigger files: {str(e)}")
    
    # Initialize empty lists as fallbacks if trigger files fail to load
    # This ensures the application doesn't crash but may result in no content being matched
    trigger_words_ai = []  # Empty fallback for AI words
    trigger_phrases_ai = []  # Empty fallback for AI phrases
    trigger_words_africa = []  # Empty fallback for Africa words
    trigger_phrases_africa = []  # Empty fallback for Africa phrases
    
    # In debug mode, re-raise the exception to break execution
    # This prevents silent failures during development
    if DEBUG_MODE:  # DEBUG_MODE is likely defined in settings.py
        raise e  # Re-raise the exception to halt execution

# ================================================================================================
# HTTP HEADERS CONFIGURATION
# ================================================================================================
# Define HTTP headers to be used in requests
# These headers help mimic a real browser request to avoid being blocked by websites
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    # The User-Agent header identifies the requester as a Chrome browser on Windows
    # This reduces the likelihood of being blocked by websites that restrict scraping
}

# ================================================================================================
# ROOT ENDPOINT DEFINITION
# ================================================================================================
# Define the root endpoint (/) which will handle all scraping operations
# This is the main entry point for the application's functionality
@app.get("/")  # Register this function to handle HTTP GET requests to the root path (/)
def root():
    """
    Main endpoint that orchestrates the scraping process across all configured sources.
    
    Data Flow:
    1. Initialize an empty list to store all scraped results
    2. Iterate through each source defined in SOURCES constant
    3. For each source, scrape content according to its configuration
    4. Filter content based on AI and Africa-related triggers
    5. Collect all matching results
    6. Return the aggregated results as JSON
    
    Returns:
        list[dict]: A list of dictionaries containing scraped content information
                   (title, link, and author details for each matching article)
    """
    # Initialize an empty list to store all scraped results from all sources
    all_results: list[dict] = []
    
    # ================================================================================================
    # ITERATION THROUGH SOURCES
    # ================================================================================================
    # Process each source defined in the SOURCES constant (imported from constants.py)
    # Each source represents a different website to scrape with its own configuration
    for source in SOURCES:
        logging.debug(f"Processing source: {source['url']}")  # Log which source is being processed

        # Extract configuration details for the current source
        url = source["url"]  # The URL of the website to scrape
        trigger_ai = source["trigger_ai"]  # Boolean flag: should we filter for AI content?
        trigger_africa = source["trigger_africa"]  # Boolean flag: should we filter for Africa content?
        selector = source["selectors"]  # CSS selectors for finding elements on the page

        # Extract specific selectors for different elements
        # author_selector = selector["author"]  # Commented out - not currently used
        next_button_selector = selector["next_button"]  # Selector for pagination "next" button
        load_more_selector = selector["load_more_button"]  # Selector for "load more" button in infinite scrolling

        # ================================================================================================
        # WEB NAVIGATION AND HTML RETRIEVAL
        # ================================================================================================
        logging.debug(f"Navigating to URL: {url}")  # Log navigation action
        html: str = ""  # Initialize empty string to store HTML content
        
        # Initialize the custom web driver (likely a Selenium wrapper)
        # This driver handles browser automation for complex scraping scenarios
        driver = CustomDriver()
        
        try:
            # Navigate to the source URL
            driver.get(url)  # Open the webpage in the automated browser

            # Handle different pagination methods based on the source configuration
            if next_button_selector is None:
                # If no next button selector exists, use infinite scrolling technique
                logging.debug(
                    f"No pagination found. Using scroll to end with load_more_selector: {load_more_selector}"
                )
                # Scroll to the end of the page and click "load more" buttons if present
                # with a timeout of 10 seconds to prevent infinite waiting
                driver.handle_infinite_scroll(load_more_selector, timeout_s=10)
                html = driver.get_html()  # Get the fully loaded HTML content
            else:
                # If next button selector exists, use traditional pagination
                logging.debug(
                    f"Pagination found. Using next button selector: {next_button_selector}"
                )
                # Navigate through pages using the next button with a limit of 5 pages
                # and a timeout of 10 seconds per operation
                html = driver.handle_pagination(
                    next_button_selector, timeout_s=10, max_pages=5
                )
        except Exception as e:
            # Handle any exceptions during web navigation
            print(e)  # Print the exception (consider using logger.error instead)
            driver.quit()  # Ensure the driver is closed to prevent resource leaks
        
        # Clean up by removing the driver reference
        # This helps ensure the browser is properly closed
        del driver

        # ================================================================================================
        # HTML PARSING AND ELEMENT EXTRACTION
        # ================================================================================================
        logging.debug("Parsing HTML with BeautifulSoup")  # Log parsing action
        # Parse the HTML content using BeautifulSoup with the html.parser engine
        # This creates a navigable structure of the HTML document
        soup = BeautifulSoup(html, "html.parser")

        # Extract title elements using the configured CSS selector
        logging.debug(f"Selecting elements with selector: {selector['title']}")
        elements = soup.select(selector["title"])  # Select all elements matching the title selector
        logging.debug(f"Found {len(elements)} title elements")  # Log the number of titles found

        # Extract link elements using the configured CSS selector
        logging.debug(f"Selecting links with selector: {selector['link']}")
        links = soup.select(selector["link"])  # Select all elements matching the link selector
        logging.debug(f"Found {len(links)} link elements")  # Log the number of links found

        # Uncomment to verify that the number of titles matches the number of links
        # assert(len(links) == len(elements))

        # Initialize a list to store results from this specific source
        source_results = []
        logging.debug(f"Processing {len(elements)} elements")  # Log processing action

        # ================================================================================================
        # ELEMENT PROCESSING AND CONTENT FILTERING
        # ================================================================================================
        # Process each title element (and its corresponding link) found on the page
        for i, element in enumerate(elements):
            logging.debug(f"Processing element {i+1}/{len(elements)}")  # Log progress

            # Extract the text content of the title and remove whitespace
            title = element.get_text().strip()
            
            # Extract the href attribute from the corresponding link
            link = links[i].get("href")
            
            # Handle case where link might be a list (sometimes happens with long URLs)
            if isinstance(link, list):
                # Join all parts of the link back together
                link = "".join(link)  

            # ================================================================================================
            # RELATIVE LINK RESOLUTION
            # ================================================================================================
            # Check if the link is relative (starts with /) and convert it to absolute
            if link and link.startswith("/"):
                # Extract domain components from the source URL
                parsed_url = urlparse(url)
                # Construct the base URL (scheme + domain)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                # Create an absolute URL by combining base URL and relative path
                link = f"{base_url}{link}"

            # Log extracted content for debugging
            logging.debug(f"Title: {title}")
            logging.debug(f"Link: {link}")

            # ================================================================================================
            # TRIGGER MATCHING FOR AFRICA-RELATED CONTENT
            # ================================================================================================
            # Initialize flag for Africa-related content matching
            should_add_africa = False
            
            # Only check for Africa triggers if required by the source configuration
            if trigger_africa:
                logging.debug(f"Checking for Africa triggers in: {title}")

                # Use the contains_triggers utility to check if the title contains any
                # Africa-related trigger words or phrases
                should_add_africa = contains_triggers(
                    title,  # The title text to check
                    trigger_words_africa,  # List of Africa-related words to match
                    trigger_phrases_africa,  # List of Africa-related phrases to match
                )
                
                # Special case: explicit check for "africa" in the title
                if "africa" in title.lower():
                    logging.debug(f"Found Africa keyword in: {title}")

            # ================================================================================================
            # TRIGGER MATCHING FOR AI-RELATED CONTENT
            # ================================================================================================
            # Initialize flag for AI-related content matching
            should_add_ai = False
            
            # Only check for AI triggers if required by the source configuration
            if trigger_ai:
                logging.debug(f"Checking for AI triggers in: {title}")
                
                # Use the contains_triggers utility to check if the title contains any
                # AI-related trigger words or phrases
                should_add_ai = contains_triggers(
                    title,  # The title text to check
                    trigger_words_ai,  # List of AI-related words to match
                    trigger_phrases_ai,  # List of AI-related phrases to match
                )
                
                # Log if an AI trigger was found
                if should_add_ai:
                    logging.debug(f"Found AI trigger in: {title}")

            # ================================================================================================
            # CONTENT INCLUSION DECISION
            # ================================================================================================
            # Determine if this content should be included in results based on trigger matches
            # Content is included only if it matches ALL required trigger types for this source
            should_add = (
                should_add_ai == trigger_ai and should_add_africa == trigger_africa
            )
            # For example:
            # - If source requires AI (trigger_ai=True), then should_add_ai must be True
            # - If source requires Africa (trigger_africa=True), then should_add_africa must be True
            # - If source requires both, then both must be True
            # - If source requires neither, then both should be False
            
            logging.debug(f"Should add this result: {should_add}")  # Log the decision

            # ================================================================================================
            # CONTENT COLLECTION (IF MATCHING)
            # ================================================================================================
            # Only process content that matches the required triggers
            if should_add:
                # Skip entries with no link (can't fetch additional data)
                if link is None:
                    logging.debug("Skipping - link is None")
                    continue

                # ================================================================================================
                # AUTHOR INFORMATION RETRIEVAL (CURRENTLY DISABLED)
                # ================================================================================================
                # Fetch the full article page to extract author information
                logging.debug(f"Fetching author information from: {link}")
                author_response = requests.get(url=link, headers=HEADERS)
                author_soup = BeautifulSoup(author_response.text, "html.parser")

                # Initialize author as None (the author extraction code is commented out)
                author: Author | None = None

                # The following code block for author extraction is commented out
                # but would extract author name and link if uncommented
                #
                # if author_selector is not None:
                #     logging.debug(
                #         f"Looking for author with selector: {author_selector}"
                #     )
                #     author_name_element = author_soup.select_one(
                #         author_selector["name"]
                #     )
                #     author_link_selector = author_selector["link"]
                #     if author_link_selector:
                #         author_link_element = author_soup.select_one(
                #             author_link_selector
                #         )
                #
                #     author = {
                #         "name": (
                #             author_name_element.get_text()
                #             if author_name_element
                #             else "Unknown"
                #         ),
                #         "link": (
                #             str(author_link_element.get("href"))
                #             if author_link_element
                #             else None
                #         ),
                #     }
                #     logging.debug(f"Found author: {author['name']}")

                # ================================================================================================
                # ADDING MATCHED CONTENT TO RESULTS
                # ================================================================================================
                # Log that this content is being added to results
                logging.debug(f"Adding result: {title}")
                
                # Add the content details to the source-specific results list
                source_results.append(
                    {
                        "title": title,  # The article title
                        "link": link,    # The URL to the article
                        "author": author,  # Author information (currently None)
                    }
                )

        # ================================================================================================
        # AGGREGATING RESULTS FROM ALL SOURCES
        # ================================================================================================
        # Add the results from this source to the overall results collection
        logging.debug(f"Adding {len(source_results)} results from {url} to all_results")
        all_results.extend(source_results)  # Append all source results to the master list

    # ================================================================================================
    # FINAL RESULTS LOGGING AND RETURN
    # ================================================================================================
    # Log summary information about the total results found
    logging.debug(f"Total results found: {len(all_results)}")
    logging.debug(all_results)  # Log the full results data (may be verbose)
    
    # Return the collected results to the API caller
    # FastAPI will automatically convert this to JSON in the HTTP response
    return all_results