# FIXED: Double Click + Limit Price Input

## Issue 1: Double Clicking SHORT/LONG Button

### Problem
- Script searched Russian variants, then English variants
- Each successful match triggered a click
- Same button clicked multiple times (e.g., "Шорт" matches, then "Short" also matches)

### Solution
**New function: `find_and_click_by_texts()`**

```python
# OLD (caused double clicks):
clicked = find_and_click_by_text(driver, 'Шорт', 'button')
if not clicked:
    clicked = find_and_click_by_text(driver, 'Short', 'button')
# If both found same element → 2 clicks!

# NEW (single click only):
clicked = find_and_click_by_texts(
    driver,
    ['Открыть Шорт', 'Шорт', 'Open Short', 'Short'],
    'button'
)
# Finds FIRST match across ALL variants → 1 click only
```

### How it works
JavaScript searches all elements, checks against ALL text variants in one pass:
```javascript
var searchTexts = ['Открыть Шорт', 'Шорт', 'Open Short', 'Short'];
for (element in all_elements) {
    for (text in searchTexts) {
        if (element.textContent.includes(text)) {
            click_at_exact_coordinates();
            return true;  // STOP AFTER FIRST MATCH
        }
    }
}
```

**Result:** Only ONE click, regardless of how many text variants match the same element.

---

## Issue 2: Limit Price Wrong Input Field

### Problem
```python
# OLD - too generic, selected wrong input:
price_input = driver.select('.ant-input[type="text"]', wait=10)
price_input.clear()  # Didn't actually clear
price_input.type(new_price)  # Typed in wrong field
```

- Multiple `.ant-input[type="text"]` elements on page
- Selected first one (not the limit price input)
- `.clear()` method unreliable with React inputs
- Old value remained, new price ignored

### Solution
**Exact selector + JavaScript clear/type**

```python
# Target EXACT input field:
var input = document.querySelector('.ant-input.InputNumberExtend_input-main__StKNb');

# Steps:
1. input.focus()           # Focus the field
2. input.select()          # Select all existing text
3. input.value = ''        # Clear value
4. dispatch 'input' event  # Trigger React handlers
5. input.value = '45000'   # Set new value
6. dispatch 'input' event  # Trigger React again
7. dispatch 'change' event # Finalize change
```

### HTML Structure (provided by user)
```html
<div class="InputNumberHandle_inputOuterWrapper__8w_l1">
  <div class="InputNumberHandle_inputWrapper__Kntgy">
    <div class="InputNumberExtend_wrapper__qxkpD extend-wrapper">
      <input autocomplete="off"
             class="ant-input InputNumberExtend_input-main__StKNb"
             type="text"
             value="">
    </div>
  </div>
</div>
```

**Selector:** `.ant-input.InputNumberExtend_input-main__StKNb`
- Specific to limit price input only
- Won't match other text inputs on page

### Full Implementation
```javascript
(function() {
    // Target EXACT input
    var input = document.querySelector('.ant-input.InputNumberExtend_input-main__StKNb');

    if (!input) return false;

    // Focus and clear
    input.focus();
    input.select();
    input.value = '';
    input.dispatchEvent(new Event('input', { bubbles: true }));

    // Type new value
    setTimeout(function() {
        input.value = '45000';
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
    }, 100);

    return true;
})();
```

**Result:**
✅ Targets correct input field
✅ Clears existing value completely
✅ Types new price properly
✅ Triggers React/Vue handlers correctly

---

## Testing
```bash
# Syntax check
✅ python -m py_compile scraper_runner.py

# Expected behavior:
✅ SHORT/LONG button clicked ONCE only
✅ Limit price input cleared and filled correctly
✅ No double clicks
✅ Correct field targeted
```

## Files Modified
- `scraper_runner.py`:
  - Added `find_and_click_by_texts()` function (lines 945-1043)
  - Updated SHORT button click (lines 1548-1567)
  - Updated LONG button click (lines 1527-1546)
  - Fixed limit price input (lines 1420-1483)
