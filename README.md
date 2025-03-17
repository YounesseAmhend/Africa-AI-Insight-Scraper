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
    python main.py
    ```

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

### **Selectors**

- CSS selectors should be specific and descriptive
