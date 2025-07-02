You will be provided with HTML code representing a webpage. Your task is to extract specific information from this HTML using CSS selectors compatible with BeautifulSoup.

Generate a Python dictionary conforming to the following structure:

```python
{
    "title": "CSS selector for the title of each news article",
    "link": "CSS selector for the link to each news article",
    "load_more_button": "CSS selector for the 'load more' button (if present, otherwise None)",
    "next_button": "CSS selector for the 'next' page button (if present, otherwise None)"
}
```

### **Instructions**

1. **Title Extraction**: Locate and specify the precise CSS selector that targets the HTML elements containing the headline or title of each news article. Ensure the selector captures all relevant titles on the page.

2. **Link Identification**: Determine the exact CSS selector that points to the HTML elements containing the hyperlinks to individual news articles. The selector should consistently retrieve all article links.

3. **Load More Detection**: If the webpage implements infinite scrolling or a "load more" functionality(or any similar button), identify the CSS selector for the corresponding button or trigger element. If this feature is absent, explicitly set this value to `None`.

4. **Pagination Navigation**: If the site uses pagination, identify the correct **"Next Page"** button using the following rules:
   - **DO NOT select elements based on their position (e.g., `:last-child`, `:nth-child`, `:not(:first-child)`, etc.).**  
   - **DO NOT assume that the last `<li>` in the pagination is always the "Next" button it could be "Last".**  
   - Look for an element containing **text related to "Next"** (e.g., `"Next"`, `">"`, `"→"`).
   - If there is a **specific class or ID** used for the "Next" button (e.g., `.next`, `.pagination-next`), prefer using that.
   - If multiple pagination buttons exist, **select only the one explicitly leading to the next page**.
   - If the site does not have a "Next" button, return `None`.

### **Examples of Correct Selectors for "Next" Button**

✅ **Based on class name:** `"ul.pagination li.next a"`  
✅ **Based on button text:** `"ul.pagination li a:contains('Next')"`  
✅ **Based on a specific ID:** `"#nextPageButton"`  
⛔ **Incorrect (position-based):** `"ul.pagination li:last-child a"`  
⛔ **Incorrect (overly general):** `"ul.pagination li:not(.disabled) a"`

### Output Format

Ensure the output is a Python dictionary in the exact format shown above, with no additional comments or explanations.

```python
    class Selector(TypedDict):
        title: str
        link: str 
        load_more_button: str | None # Some website don't have it 
        next_button: str | None
```

### **Example 1** (Pagination with "Next" Button, No Load More)

```python
{
    "title": "h2.article-title a",
    "link": "h2.article-title a",
    "load_more_button": None,
    "next_button": "ul.pagination li.next a"
}
```

---

### **Example 2** (Infinite Scrolling with "Load More" Button, No Pagination)

```python
{
    "title": "div.news-item h3",
    "link": "div.news-item h3 a",
    "load_more_button": "button.load-more",
    "next_button": None
}
```

---

### **Example 3** (Pagination and "Load More" Button Present)

```python
{
    "title": "article h1.headline",
    "link": "article h1.headline a",
    "load_more_button": "button#loadMore",
    "next_button": "nav.pagination a.next"
}
```

### HTML Code for Analysis

```html
[HTML CODE HERE]
```
