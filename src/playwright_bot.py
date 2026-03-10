from playwright.sync_api import sync_playwright
import time
import random
import os

CHAT_URL = "https://chatgpt.com/"


class ChatGPTBot:
    def __init__(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(
            headless=False,
            args=[
                "--start-maximized",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        storage_state_path = "storage_state.json"

        # 🔐 Використання збереженої сесії
        if os.path.exists(storage_state_path):
            self.context = self.browser.new_context(
                storage_state=storage_state_path,
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            print("🔐 Використовую збережену сесію")
        else:
            self.context = self.browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            )
            print("⚠️ Сесія не знайдена — потрібно увійти вручну")

        self.page = self.context.new_page()

        self.page.goto(CHAT_URL, wait_until="domcontentloaded", timeout=60000)
        time.sleep(random.uniform(3, 5))

        # 🔑 Перевірка логіну
        if (
            "login" in self.page.url.lower()
            or self.page.locator("button:has-text('Log in')").count() > 0
        ):
            print("👉 Увійди в ChatGPT вручну і натисни Enter тут...")
            input()

        # 💾 Зберігаємо сесію
        self.context.storage_state(path=storage_state_path)

        print("✅ ChatGPT готовий")

    def send_prompt(self, prompt: str):
        """Стабільна вставка тексту без .type() (без таймаутів)"""

        selectors = [
            'div#prompt-textarea[contenteditable="true"]',
            'div.ProseMirror[contenteditable="true"]',
            'div[role="textbox"][contenteditable="true"]',
            'textarea'
        ]

        textarea = None

        for attempt in range(3):
            for sel in selectors:
                try:
                    el = self.page.locator(sel).first
                    el.wait_for(state="visible", timeout=10000)

                    if el.is_visible():
                        textarea = el
                        break
                except:
                    continue

            if textarea:
                break
            time.sleep(1)

        if not textarea:
            self.page.screenshot(path="error_no_input.png")
            raise Exception("❌ Поле вводу не знайдено (див. error_no_input.png)")

        try:
            textarea.click()
            time.sleep(0.3)

            # 🧹 очистка
            self.page.keyboard.press("Control+A")
            self.page.keyboard.press("Backspace")

            time.sleep(0.3)

            # ⚡ вставка без лагів
            textarea.fill(prompt)

            time.sleep(0.3)

            # 🚀 відправка
            self.page.keyboard.press("Enter")

            print("📤 Prompt відправлено")

        except Exception as e:
            self.page.screenshot(path="error_send.png")
            raise Exception(f"❌ Помилка при відправці: {e}")

    def get_response(self):
        try:
            self.page.wait_for_selector(
                "[data-message-author-role='assistant']",
                timeout=60000
            )
        except:
            print("⚠️ Відповідь не з'явилась")
            return ""

        # ⏳ чекаємо поки перестане генеруватись
        for _ in range(120):
            time.sleep(1)
            if self.page.locator("button[aria-label='Stop streaming']").count() == 0:
                break

        time.sleep(random.uniform(1.5, 2.5))

        messages = self.page.locator("[data-message-author-role='assistant']")

        if messages.count() == 0:
            return ""

        last_message = messages.last
        text = last_message.inner_text().strip()

        print(f"📥 Отримано відповідь ({len(text)} символів)")
        return text

    def close(self):
        try:
            self.context.close()
            self.browser.close()
            self.playwright.stop()
            print("🛑 Браузер закрито")
        except Exception as e:
            print(f"Помилка при закритті: {e}")