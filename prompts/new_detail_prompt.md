```python
{
    "author": {
        "name": "CSS selector for the author's name",
        "link": "CSS selector for the author's link (if present, otherwise None)"
    },
    "body": "CSS selector for the body of the content",
    "event_date": "CSS selector for the event date (if present, otherwise None)",
    "post_date": "CSS selector for the post date (if present, otherwise None)"
}
```

### Instructions

1. **Author Name**: Identify the CSS selector for the HTML elements containing the author's name.
2. **Author Link**: Identify the CSS selector for the HTML elements containing the author's link. If not present, set this to `None`.
3. **Body**: Identify the CSS selector for the HTML elements containing the body of the content.
4. **Event Date**: Identify the CSS selector for the HTML elements containing the event date. If not present, set this to `None`.
5. **Post Date**: Identify the CSS selector for the HTML elements containing the post date. If not present, set this to `None`.

### Output Format

Ensure the output is a Python dictionary in the exact format shown above, with no additional comments or explanations.

### Example Output

```python
{
    "author": {
        "name": "div.author span.name",
        "link": "div.author a.link"
    },
    "body": "div.content p",
    "event_date": "div.dates span.event",
    "post_date": "div.dates span.post"
}
```

### HTML Code for Analysis

```html
[HTML CODE HERE]
```
