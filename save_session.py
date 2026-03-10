from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()

    page = context.new_page()
    page.goto("https://chat.openai.com")

    input("👉 Залогінься і натисни Enter...")

    context.storage_state(path="storage_state.json")

    print("✅ Session saved!")

    browser.close()