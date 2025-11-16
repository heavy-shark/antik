# Short/Long Trading UI - v0.2.6

## Feature: Interactive Trading Settings for Short/Long Modes

Added comprehensive UI for configuring Short and Long trading operations with reactive controls and validation.

---

## UI Components

### 1. Trading Settings Section (Conditional)
**Visibility:** Shows only when "Short" or "Long" mode is selected
**Location:** Between Operation Mode and Logs sections

### 2. Token Link Input
- **Label:** "Token Link:"
- **Type:** Text input (QLineEdit)
- **Purpose:** Enter token contract address or trading link
- **Validation:** Required field
- **Placeholder:** "Enter token contract address or link..."

### 3. Position in % Dropdown
- **Label:** "Position in %:"
- **Type:** Dropdown (QComboBox)
- **Options:** 25%, 50%, 75%, 100%, Custom
- **Reactive Behavior:**
  - When "Custom" selected → Shows custom input field
  - Other options → Hides custom input field
- **Validation:** Must be number between 0-100

### 4. Custom Position Input (Conditional)
- **Type:** Text input (QLineEdit)
- **Visibility:** Only when "Custom" selected in dropdown
- **Purpose:** Enter custom position percentage
- **Placeholder:** "Enter custom %..."
- **Auto-focus:** Gets focus when shown
- **Auto-clear:** Clears when hidden

### 5. Type of Zaliv Selector
- **Label:** "Type of Zaliv:"
- **Type:** Radio buttons
- **Options:**
  - Market (default)
  - Limit
- **Reactive Behavior:**
  - Market selected → Hides limit price input
  - Limit selected → Shows limit price input

### 6. Limit Price Input (Conditional)
- **Label:** "Limit Price:"
- **Type:** Text input (QLineEdit)
- **Visibility:** Only when "Limit" radio button selected
- **Purpose:** Enter limit order price
- **Placeholder:** "Enter limit price..."
- **Validation:** Must be number > 0
- **Auto-focus:** Gets focus when shown
- **Auto-clear:** Clears when hidden

---

## Reactive Logic Flow

### Mode Selection → Section Visibility
```python
User selects Operation Mode:
├─ Manual → Hide Trading Settings ❌
├─ Login → Hide Trading Settings ❌
├─ Short → Show Trading Settings ✅ (title: "Short Trading Settings")
├─ Long → Show Trading Settings ✅ (title: "Long Trading Settings")
├─ Balance → Hide Trading Settings ❌
└─ RK → Hide Trading Settings ❌
```

### Position Dropdown → Custom Input
```python
User selects Position:
├─ 25% → Hide custom input, use "25"
├─ 50% → Hide custom input, use "50"
├─ 75% → Hide custom input, use "75"
├─ 100% → Hide custom input, use "100"
└─ Custom → Show custom input, get user value
```

### Zaliv Type → Limit Price
```python
User selects Type:
├─ Market → Hide limit price input
└─ Limit → Show limit price input + label
```

---

## Implementation Details

### Functions Added

**1. create_short_long_settings_section()**
```python
def create_short_long_settings_section(self):
    """Create Short/Long mode settings section"""
    # Creates all UI elements:
    # - Token Link input
    # - Position dropdown + custom input
    # - Market/Limit radio buttons
    # - Limit price input
    # Sets up reactive connections
```

**2. on_operation_mode_changed(button)**
```python
def on_operation_mode_changed(self, button):
    """Handle operation mode change - show/hide Short/Long settings"""
    mode = button.property("mode")
    if mode in ["short", "long"]:
        self.short_long_section.show()
        # Update title: "Short Trading Settings" or "Long Trading Settings"
    else:
        self.short_long_section.hide()
```

**3. on_position_dropdown_changed(text)**
```python
def on_position_dropdown_changed(self, text):
    """Show/hide custom position input based on dropdown selection"""
    if text == "Custom":
        self.custom_position_input.show()
        self.custom_position_input.setFocus()
    else:
        self.custom_position_input.hide()
        self.custom_position_input.clear()
```

**4. on_zaliv_type_changed(button)**
```python
def on_zaliv_type_changed(self, button):
    """Show/hide limit price input based on Market/Limit selection"""
    if button == self.limit_radio:
        self.limit_price_label.show()
        self.limit_price_input.show()
        self.limit_price_input.setFocus()
    else:
        self.limit_price_label.hide()
        self.limit_price_input.hide()
        self.limit_price_input.clear()
```

**5. get_short_long_settings()**
```python
def get_short_long_settings(self):
    """Get current Short/Long trading settings"""
    return {
        'token_link': str,
        'position_percent': str,
        'zaliv_type': "Market" | "Limit",
        'limit_price': str (empty if Market)
    }
```

**6. validate_short_long_settings()**
```python
def validate_short_long_settings(self):
    """Validate Short/Long settings before execution"""
    # Validates:
    # - Token link not empty
    # - Position is valid number 0-100
    # - Limit price valid if Limit type selected
    # Shows QMessageBox warnings for errors
    # Returns: bool (True if valid)
```

**7. run_short_long_trade(mode, selected_rows, settings)**
```python
def run_short_long_trade(self, mode, selected_rows, settings):
    """Execute Short/Long trading operation (placeholder)"""
    # Logs configuration
    # TODO: Implement actual trading logic
```

---

## User Workflow

### Scenario 1: Short Trade with Market Order
```
1. User selects "Short" mode
   → Trading Settings section appears with title "Short Trading Settings"

2. User enters token link: "0x1234abcd..."
   → Token field populated

3. User selects "75%" from dropdown
   → Position set to 75%

4. User keeps "Market" selected (default)
   → Limit price input remains hidden

5. User clicks "Open Selected"
   → Validation passes
   → Settings logged:
     📊 Trading Configuration:
        Token Link: 0x1234abcd...
        Position: 75%
        Order Type: Market
   → Trade execution initiated (placeholder)
```

### Scenario 2: Long Trade with Limit Order
```
1. User selects "Long" mode
   → Trading Settings section appears with title "Long Trading Settings"

2. User enters token link: "https://dexscreener.com/..."
   → Token field populated

3. User selects "Custom" from dropdown
   → Custom input field appears and gets focus

4. User enters "35" in custom field
   → Position set to 35%

5. User selects "Limit" radio button
   → Limit price label and input appear

6. User enters "0.00015" in limit price
   → Limit price set

7. User clicks "Open Selected"
   → Validation passes
   → Settings logged:
     📊 Trading Configuration:
        Token Link: https://dexscreener.com/...
        Position: 35%
        Order Type: Limit
        Limit Price: 0.00015
   → Trade execution initiated (placeholder)
```

### Scenario 3: Validation Errors
```
1. User selects "Short" mode
2. User clicks "Open Selected" without entering token
   → Warning: "Please enter a token link or contract address"

3. User enters token, selects "Custom", leaves % empty
   → Warning: "Please enter a position percentage"

4. User enters "150" in custom %
   → Warning: "Position percentage must be between 0 and 100"

5. User enters "50", selects "Limit", leaves price empty
   → Warning: "Please enter a limit price"

6. User enters "-10" in limit price
   → Warning: "Limit price must be greater than 0"
```

---

## Styling

All elements follow the existing dark blue theme:
- Background: #132f4c
- Border: #1e4976
- Text: #ffffff
- Labels: #90caf9 (light blue)
- Title: #64b5f6 (bright blue)
- Focus border: #2196f3

---

## State Management

### Instance Variables
```python
self.short_long_section         # Main container widget
self.token_link_input          # QLineEdit for token
self.position_dropdown         # QComboBox for position %
self.custom_position_input     # QLineEdit for custom %
self.zaliv_group               # QButtonGroup for Market/Limit
self.market_radio              # QRadioButton for Market
self.limit_radio               # QRadioButton for Limit
self.limit_price_label         # QLabel for limit price
self.limit_price_input         # QLineEdit for limit price
```

### Signal Connections
```python
# Operation mode change
self.operation_group.buttonClicked.connect(on_operation_mode_changed)

# Position dropdown change
self.position_dropdown.currentTextChanged.connect(on_position_dropdown_changed)

# Zaliv type change
self.zaliv_group.buttonClicked.connect(on_zaliv_type_changed)
```

---

## Integration with Existing Code

### Modified: open_selected_profiles()
```python
# Before:
elif operation_mode in ["short", "long", ...]:
    self.log("Mode not implemented")
    QMessageBox.information("Coming Soon")

# After:
elif operation_mode in ["short", "long"]:
    # Validate settings
    if not self.validate_short_long_settings():
        return

    # Get settings
    settings = self.get_short_long_settings()

    # Log configuration
    self.log("Trading Configuration:")
    ...

    # Execute
    self.run_short_long_trade(operation_mode, selected_rows, settings)
```

---

## Future Implementation (TODO)

The `run_short_long_trade()` function is currently a placeholder. Future implementation should:

1. Open browser for each profile (using ManualBrowserThread)
2. Navigate to trading platform
3. Find token by address/link
4. Calculate position size based on percentage
5. Select Market or Limit order type
6. If Limit: Set limit price
7. Execute trade
8. Monitor execution status
9. Update profile status in table
10. Log results

---

## Testing Checklist

✅ **Mode Switching**
- Manual → Settings hidden
- Login → Settings hidden
- Short → Settings shown with "Short Trading Settings"
- Long → Settings shown with "Long Trading Settings"
- Balance → Settings hidden
- RK → Settings hidden

✅ **Position Dropdown**
- 25% → Custom input hidden
- 50% → Custom input hidden
- 75% → Custom input hidden
- 100% → Custom input hidden
- Custom → Custom input shown and focused

✅ **Zaliv Type**
- Market → Limit price hidden
- Limit → Limit price shown and focused

✅ **Validation**
- Empty token → Warning shown
- Empty position → Warning shown
- Invalid position (0, -10, 150) → Warning shown
- Limit without price → Warning shown
- Invalid limit price (0, -5) → Warning shown
- Valid inputs → Validation passes

✅ **Settings Retrieval**
- Token link captured correctly
- Position % captured (from dropdown or custom)
- Zaliv type captured (Market/Limit)
- Limit price captured when applicable

✅ **Logging**
- Configuration logged before execution
- All settings displayed in logs
- Clear indication of operation type

---

## Code Statistics

**Lines Added:** ~270
- create_short_long_settings_section(): ~160 lines
- Event handlers: ~50 lines
- Validation: ~40 lines
- Integration: ~20 lines

**Files Modified:**
- botasaurus_app/main_window.py

**New Functions:** 7
**Modified Functions:** 1

---

## Conclusion

This implementation provides a complete, reactive UI for Short/Long trading configuration with:

✅ Clean, intuitive interface
✅ Reactive show/hide logic
✅ Comprehensive validation
✅ Consistent styling
✅ Easy integration with future trading logic
✅ Professional UX

The UI is fully functional and ready for backend trading implementation.

---

**Implementation Date**: 2025-11-16
**Version**: v0.2.6
**Status**: ✅ Complete and Ready
**Next Step**: Implement actual trading logic in run_short_long_trade()
