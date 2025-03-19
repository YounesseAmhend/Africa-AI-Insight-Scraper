# **Africa AI Insight Scraper**  

A web scraper that extracts AI-related news and insights focused on Africa.  

## **Getting Started**  

### **1. Install Dependencies**  

Run the following command to install the required dependencies:  
    ```sh
    pip install -r requirements.txt
    ```  

### **2. Run the Application**  

Execute the following command to start the scraper:  
    ```sh
    python -m uvicorn main:app --reload
    ```

## **Requirements**

- Python 3.12

## **Naming Conventions**

### **Variables and Functions**

- Use snake_case for variable and function names (e.g., `trigger_words`, `get_data`)
- Boolean variables should be prefixed with "is_", "has_", etc. (e.g., `is_valid`)

### **Classes**

- Use PascalCase for class names (e.g., `Source`)
- TypedDict classes follow the same convention

### **Constants**

- Use UPPER_SNAKE_CASE for constants (e.g., `API_KEY`, `BASE_URL`)

### **Files**

- Use snake_case for file names (e.g., `main.py`, `source.py`)

### **Development Setup**

1. Install Pylance extension in VS Code
2. Enable type checking in VS Code settings:
   - Open settings (Ctrl+,)
   - Search for "python.analysis.typeCheckingMode"
   - Set it to "basic"

### **Selectors**

- CSS selectors should be specific and descriptive
- Use class and ID selectors when possible
- Avoid overly complex selectors that are brittle


## **Project Structure**

The project is organized into the following directories:

- **`.vscode`**: Contains VS Code specific configuration files.
- **`data`**: Stores scraped data organized by categories:
  - `africa`: Data related to African news/events
  - `ai`: Data related to artificial intelligence
- **`dtypes`**: Contains TypedDict definitions (dictionary types) for type hinting. Each file follows a naming convention where it contains a single TypedDict class that matches the file name (e.g., `author.py` contains the `Author` class, `selector.py` contains the `Selector` class):

- **`utils`**: Contains utility functions and helper modules

The TypedDict classes in the `dtypes` directory provide structured type definitions that help with type checking and code completion throughout the project.
