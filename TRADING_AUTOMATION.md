# Trading Automation Implementation - MEXC Futures

## Overview

Автоматизация Short/Long трейдинга на MEXC Futures с использованием элементов которые ты предоставил из DevTools (F12).

**Версия:** v0.2.7 (НЕ закоммичено - для тестирования)

---

## Реализованная функциональность

### 1. URL Generation (parse_token_url)
```python
Поддерживаемые форматы:
- Полный URL: https://www.mexc.com/ru-RU/futures/BTC_USDT?type=linear_swap&lang=ru-RU
- Тикер: BTC_USDT (автоматически формирует URL)
- Fallback: Если не распознан → BTC_USDT по умолчанию
```

### 2. Order Type Selection
```python
# Лимитный ордер:
text=Лимит → click()

# Маркет ордер:
text=Маркет → click()
```

### 3. Limit Price Input (только для Limit)
```python
Селектор: .ant-input[type="text"]
Действия:
1. clear_input_text() - очистить поле
2. type(limit_price) - ввести цену
```

### 4. Position Percentage Slider
```python
Селекторы по процентам:
- 25%: .ant-slider-v2-dot[style*="left: 25%"]
- 50%: .ant-slider-v2-dot[style*="left: 50%"]
- 75%: .ant-slider-v2-dot[style*="left: 75%"]
- 100%: .ant-slider-v2-dot[style*="left: 100%"]

Действие: click()
```

### 5. Execute Trade Button
```python
Лонг: text=Открыть Лонг
Шорт: text=Открыть Шорт

Подтверждение: text=Подтвердить
```

---

## Код Implementation

### ShortLongTradeThread (scraper_runner.py)

**Полный flow автоматизации:**

```python
class ShortLongTradeThread(QThread):
    def run(self):
        # 1. Создание браузера с профилем и прокси
        driver = Driver(profile=profile_name, proxy=proxy)

        # 2. Открытие страницы токена
        token_url = self.parse_token_url(token_link)
        driver.get(token_url)
        driver.sleep(3)  # Ждем загрузки

        # 3. Выбор типа ордера
        if zaliv_type == "Limit":
            driver.get_element_or_none('text=Лимит').click()

            # Ввод цены
            price_input = driver.get_element_or_none('.ant-input[type="text"]')
            price_input.clear_input_text()
            price_input.type(limit_price)
        else:
            driver.get_element_or_none('text=Маркет').click()

        # 4. Выбор процента позиции
        dot_selector = f'.ant-slider-v2-dot[style*="left: {position}%"]'
        driver.get_element_or_none(dot_selector).click()

        # 5. Выполнение сделки
        if mode == "long":
            driver.get_element_or_none('text=Открыть Лонг').click()
        else:
            driver.get_element_or_none('text=Открыть Шорт').click()

        # 6. Подтверждение (если появится диалог)
        confirm = driver.get_element_or_none('text=Подтвердить', wait=2)
        if confirm:
            confirm.click()
```

### Parallel Execution (main_window.py)

```python
def run_short_long_trade(mode, selected_rows, settings):
    # Запускает ПАРАЛЛЕЛЬНО для всех выбранных профилей
    for row in selected_rows:
        thread = ShortLongTradeThread(
            scraper_runner,
            profile_name,
            email,
            mode,  # "short" or "long"
            settings,  # {token_link, position_percent, zaliv_type, limit_price}
            headless=False
        )

        thread.start()  # Все потоки стартуют одновременно!
```

---

## Mapping элементов

### Элементы которые ты дал → Селекторы в коде:

| Твой HTML элемент | Селектор в коде | Действие |
|-------------------|-----------------|----------|
| `<span class="EntrustTabs_buttonTextOne__Jx1oT">Лимит</span>` | `text=Лимит` | `click()` |
| `<span>Маркет</span>` | `text=Маркет` | `click()` |
| `<input autocomplete="off" class="ant-input" type="text" value="">` | `.ant-input[type="text"]` | `clear_input_text()` + `type(price)` |
| `<span class="ant-slider-v2-dot" style="left: 25%;">` | `.ant-slider-v2-dot[style*="left: 25%"]` | `click()` |
| `<span class="ant-slider-v2-dot" style="left: 50%;">` | `.ant-slider-v2-dot[style*="left: 50%"]` | `click()` |
| `<span class="ant-slider-v2-dot" style="left: 75%;">` | `.ant-slider-v2-dot[style*="left: 75%"]` | `click()` |
| `<span class="ant-slider-v2-dot" style="left: 100%;">` | `.ant-slider-v2-dot[style*="left: 100%"]` | `click()` |
| `<div><div>Открыть Лонг</div></div>` | `text=Открыть Лонг` | `click()` |
| `<div><div>Открыть Шорт</div></div>` | `text=Открыть Шорт` | `click()` |

**Почему эти селекторы надежные:**
- `text=` - ищет по тексту, не зависит от CSS классов
- `[style*="left: X%"]` - ищет по style attribute, точный match
- `.ant-input[type="text"]` - стандартный класс Ant Design, стабильный

---

## Тестирование

### Подготовка:

1. **Запусти приложение**
2. **Импортируй профиль** (или используй существующий)
3. **Выбери режим Short или Long**

### Test Case 1: Short Trade с Market ордером

**Настройки UI:**
```
Token Link: BTC_USDT
Position: 50%
Type: Market
```

**Ожидаемый результат:**
```
1. Браузер откроется на https://www.mexc.com/ru-RU/futures/BTC_USDT?...
2. Выберет "Маркет"
3. Кликнет на 50% слайдер
4. Нажмет "Открыть Шорт"
5. Если появится подтверждение → кликнет "Подтвердить"
```

**Логи:**
```
🚀 Starting operation: SHORT
📊 Trading Configuration:
   Token Link: BTC_USDT
   Position: 50%
   Order Type: Market
📈 Starting SHORT trade for 1 profile(s)
▶️ Started short trade thread for: user@example.com
🔧 Initializing browser for trade: user@example.com
⏳ Creating browser instance...
🌐 Opening: https://www.mexc.com/ru-RU/futures/BTC_USDT?type=linear_swap&lang=ru-RU
📊 Selecting order type: Market
✓ Selected Market order type
📈 Selecting position: 50%
✓ Selected 50% position
🚀 Executing SHORT trade...
✓ Trade execution button clicked
✅ SHORT trade executed for: user@example.com
✅ SHORT trade completed for: user@example.com
```

### Test Case 2: Long Trade с Limit ордером

**Настройки UI:**
```
Token Link: ETH_USDT
Position: 75%
Type: Limit
Limit Price: 2500.50
```

**Ожидаемый результат:**
```
1. Браузер откроется на https://www.mexc.com/ru-RU/futures/ETH_USDT?...
2. Выберет "Лимит"
3. Очистит поле цены и введет "2500.50"
4. Кликнет на 75% слайдер
5. Нажмет "Открыть Лонг"
6. Если появится подтверждение → кликнет "Подтвердить"
```

**Логи:**
```
🚀 Starting operation: LONG
📊 Trading Configuration:
   Token Link: ETH_USDT
   Position: 75%
   Order Type: Limit
   Limit Price: 2500.50
📈 Starting LONG trade for 1 profile(s)
▶️ Started long trade thread for: user@example.com
🔧 Initializing browser for trade: user@example.com
🌐 Opening: https://www.mexc.com/ru-RU/futures/ETH_USDT?type=linear_swap&lang=ru-RU
📊 Selecting order type: Limit
✓ Selected Limit order type
💰 Entering limit price: 2500.50
✓ Limit price entered: 2500.50
📈 Selecting position: 75%
✓ Selected 75% position
🚀 Executing LONG trade...
✓ Trade execution button clicked
✅ LONG trade executed for: user@example.com
✅ LONG trade completed for: user@example.com
```

### Test Case 3: Полный URL

**Настройки UI:**
```
Token Link: https://www.mexc.com/ru-RU/futures/BTC_USDT?type=linear_swap&lang=ru-RU
Position: 100%
Type: Market
```

**Ожидаемый результат:**
```
Использует точный URL из Token Link (не модифицирует)
```

### Test Case 4: Параллельное выполнение (2+ профиля)

**Действия:**
```
1. Выбери 3 профиля
2. Short mode, BTC_USDT, 25%, Market
3. Нажми "Open Selected"
```

**Ожидаемый результат:**
```
Все 3 браузера откроются ОДНОВРЕМЕННО
Все 3 сделки выполнятся ПАРАЛЛЕЛЬНО
UI останется отзывчивым
```

---

## Возможные проблемы и решения

### Проблема 1: Не находит элемент "Лимит"

**Причины:**
- Страница не загрузилась
- Язык интерфейса не русский

**Решение:**
```python
# В parse_token_url() добавлен параметр lang=ru-RU
# Но если все еще не работает, проверь:
driver.sleep(5)  # Увеличь ожидание после get()

# Или используй английскую версию:
text=Limit (вместо text=Лимит)
```

### Проблема 2: Не находит price input

**Причины:**
- Несколько `.ant-input[type="text"]` на странице
- Нужно более специфичный селектор

**Решение:**
```python
# Вариант 1: Найти все и взять нужный
inputs = driver.get_elements('.ant-input[type="text"]')
price_input = inputs[0]  # или inputs[1], etc.

# Вариант 2: Более специфичный селектор (нужно инспектировать)
price_input = driver.get_element_or_none('.price-input input')

# Вариант 3: По placeholder
price_input = driver.get_element_or_none('input[placeholder*="Цена"]')
```

### Проблема 3: Слайдер dot не кликается

**Причины:**
- Style атрибут немного другой (25.0% вместо 25%)
- Dot скрыт или disabled

**Решение:**
```python
# Используй более гибкий селектор
dot_selector = f'.ant-slider-v2-dot[style*="{position}"]'

# Или найди все dots и кликни по индексу
dots = driver.get_elements('.ant-slider-v2-dot')
# 0 index = 25%, 1 = 50%, 2 = 75%, 3 = 100%
position_map = {"25": 0, "50": 1, "75": 2, "100": 3}
dots[position_map[position]].click()
```

### Проблема 4: Кнопка "Открыть Лонг" не находится

**Причины:**
- Кнопка disabled (недостаточно средств, неправильные параметры)
- Текст кнопки другой

**Решение:**
```python
# Проверь disabled state
button = driver.get_element_or_none('text=Открыть Лонг')
if button and not button.is_enabled():
    self.log_signal.emit("⚠️ Button is disabled - check balance/settings")

# Альтернативные селекторы:
button = driver.get_element_or_none('[class*="buy-button"]')
button = driver.get_element_or_none('[data-testid="open-long"]')
```

---

## Debugging Tips

### Включи headless=False (уже включено)
```python
# В ShortLongTradeThread всегда headless=False
# Поэтому ты видишь что происходит
```

### Добавь скриншоты на каждом шаге
```python
# В ShortLongTradeThread.run():
driver.get(token_url)
driver.save_screenshot('step1_page_loaded.png')

limit_tab.click()
driver.save_screenshot('step2_limit_selected.png')

position_dot.click()
driver.save_screenshot('step3_position_selected.png')
```

### Используй Playwright Inspector
```python
# Добавь в run() перед автоматизацией:
driver.page.pause()  # Откроет Playwright Inspector
# Можешь вручную инспектировать элементы
```

### Логируй все найденные элементы
```python
# В ShortLongTradeThread:
limit_tab = driver.get_element_or_none('text=Лимит', wait=3)
self.log_signal.emit(f"DEBUG: limit_tab found: {limit_tab is not None}")

if limit_tab:
    self.log_signal.emit(f"DEBUG: limit_tab text: {limit_tab.inner_text()}")
    self.log_signal.emit(f"DEBUG: limit_tab clickable: {limit_tab.is_enabled()}")
```

---

## Следующие шаги после тестирования

### Если работает ✅:
1. Проверь все сценарии (Short Market, Short Limit, Long Market, Long Limit)
2. Проверь параллельное выполнение (2+ профиля)
3. Проверь разные токены (BTC_USDT, ETH_USDT, etc.)
4. Скажи мне "все работает" → я закоммичу в git

### Если НЕ работает ❌:
1. Скопируй логи из приложения
2. Сделай скриншот страницы MEXC
3. Скопируй HTML проблемного элемента (F12 → ПКМ → Copy element)
4. Отправь мне → я исправлю селекторы

---

## Custom Percentage (TODO)

Сейчас Custom percentage fallback на 100%. Если нужно реализовать:

```python
# Найти input для ввода процента вручную
# (Нужно инспектировать - может быть рядом со слайдером)
amount_input = driver.get_element_or_none('input[placeholder*="Amount"]')
if amount_input:
    # Вычислить сумму = balance * (custom_percent / 100)
    # Или просто ввести процент если поле поддерживает
    amount_input.clear_input_text()
    amount_input.type(calculated_amount)
```

---

## Заметки

**Что НЕ делает автоматизация:**
- ❌ Не проверяет баланс (может быть недостаточно средств)
- ❌ Не ждет выполнения ордера (просто кликает кнопку)
- ❌ Не закрывает позицию автоматически
- ❌ Не обрабатывает ошибки биржи (недостаточная ликвидность, etc.)

**Что МОЖНО добавить:**
- ✅ Проверку баланса перед сделкой
- ✅ Ожидание подтверждения выполнения ордера
- ✅ Скриншот результата
- ✅ Уведомление в Telegram при выполнении
- ✅ Автоматическое закрытие позиции при достижении profit/loss

---

## Файлы изменены (НЕ закоммичено):

```
botasaurus_app/scraper_runner.py
- Добавлен ShortLongTradeThread класс (~190 строк)

botasaurus_app/main_window.py
- Добавлен импорт ShortLongTradeThread
- Добавлен self.active_trade_threads
- Обновлен run_short_long_trade() для использования потоков
- Добавлен on_trade_finished() callback
```

---

**Готов к тестированию! Попробуй и дай фидбек!** 🚀
