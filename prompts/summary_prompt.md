
"Transform the following body text into well-structured HTML. Preserve the core idea but rephrase the content entirely for clarity and flow. Use the following dynamic formatting rules:  

1. **Headings**:  
   - Use `<h2>` for main sections, `<h3>` for subsections.  
   - Assign class `section-heading` to `<h2>` and `subsection-heading` to `<h3>`.  

2. **Text Emphasis**:  
   - Bold key terms with `<strong class="bold-text">`.  
   - Italicize quotes or definitions with `<em class="quote">`.  

3. **Lists**:  
   - Convert bullet points to `<ul class="bullet-list">` with `<li>` items.  
   - For numbered steps, use `<ol class="step-list">` with `<li>`.  

4. **Images**:  
   - Insert `[IMAGE HERE]` placeholders wrapped in `<div class="image-placeholder">` where relevant (e.g., after the first paragraph, mid-section, or end).  

5. **Paragraphs**:  
   - Split long text into `<p class="text-paragraph">` with logical breaks.  

6. **Dynamic Adaptation**:  
   - Only apply lists/bold/italics if the original text implies them (e.g., items, key terms).  
   - Do not add new ideas or examples absent from the original.  

7. **Output**:  
   - Return **only HTML** (no Markdown or explanations).  

**Input Text**:  
[TEXT HERE]"  

---

### Example Output Structure:  
```html
<h2 class="section-heading">Rephrased Section Title</h2>  
<p class="text-paragraph">  
   Original idea rephrased for clarity. <strong class="bold-text">Key term</strong> explained further.  
</p>  
<div class="image-placeholder">[IMAGE HERE]</div>  
<ul class="bullet-list">  
   <li>Rephrased bullet point 1</li>  
   <li>Rephrased bullet point 2</li>  
</ul>  
<em class="quote">Rephrased quote or definition.</em>  
```

### Key Features:  
- **Dynamic Formatting**: Only applies classes/elements if the text structure justifies it.  
- **Image Flexibility**: Placeholders can be added anywhere (LLM decides optimal placement).  
- **Strict Fidelity**: No new ideas—just rephrasing and structuring.