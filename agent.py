"""
NotebookLM Studio Automation Agent
=================================

This script automates the Studio features in NotebookLM after manual file upload.

Workflow:
1. Opens NotebookLM
2. Creates a new notebook
3. User uploads file manually
4. After confirmation, agent clicks all Studio features:
   - Audio Overview (auto-start)
   - Video Overview (Generate required)
   - Slide Deck
   - Mind Map
   - Flashcards
   - Infographic
   - Data Table

Notes:
- Skips Quiz and Reports
- Uses DOM-based text matching (robust against UI changes)
- Designed for fullscreen Chrome session

Author: Ashish Sharma
"""

import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR = Path(__file__).parent / ".notebooklm_profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com"

# Studio tasks (case-insensitive match)
TASKS = [
    "Audio Overview",
    "Video Overview",
    "Slide deck",
    "Mind Map",
    "Flashcards",
    "Infographic",
    "Data table",
]


async def click_by_text(page, keyword, wait=2):
    """
    Click any visible element by matching text or aria-label.

    Args:
        page: Playwright page
        keyword: text to search
        wait: delay after click
    """
    clicked = await page.evaluate("""(kw) => {
        const all = [...document.querySelectorAll('*')];
        for (const el of all) {
            const txt = (el.innerText || '').toLowerCase().trim();
            const aria = (el.getAttribute('aria-label') || '').toLowerCase();
            if (txt === kw || txt.startsWith(kw) || aria.includes(kw)) {
                const r = el.getBoundingClientRect();
                if (r.width > 10 && r.height > 10) {
                    el.scrollIntoView({block: 'center'});
                    el.click();
                    return true;
                }
            }
        }
        return false;
    }""", keyword.lower())

    print(f"{'✅' if clicked else '❌'} Click → {keyword}")
    await asyncio.sleep(wait)
    return clicked


async def click_generate_in_popup(page):
    """
    Click 'Generate' button inside popup panels.
    Required for Video, Mind Map, etc.
    """
    for _ in range(8):
        clicked = await page.evaluate("""() => {
            for (const b of document.querySelectorAll('button')) {
                if ((b.innerText || '').toLowerCase().trim() === 'generate') {
                    b.scrollIntoView({block: 'center'});
                    b.click();
                    return true;
                }
            }
            return false;
        }""")
        if clicked:
            print("⚡ Generate clicked")
            return True
        await asyncio.sleep(1)

    print("⚠️ Generate not found")
    return False


async def close_popup(page):
    """Close popup using Close button or Escape key."""
    closed = await page.evaluate("""() => {
        for (const b of document.querySelectorAll('button')) {
            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
            const txt = (b.innerText || '').toLowerCase();
            if (aria.includes('close') || txt.includes('close')) {
                b.click();
                return true;
            }
        }
        return false;
    }""")

    if not closed:
        await page.keyboard.press('Escape')

    await asyncio.sleep(2)


async def handle_task(page, task):
    """
    Handle a single Studio feature.

    Audio:
        - Starts automatically
    Others:
        - Open panel → click Generate → close
    """
    print(f"\n🔹 {task}")

    ok = await click_by_text(page, task)
    if not ok:
        return

    if task.lower() == "audio overview":
        print("🎧 Audio auto-starts")
        await asyncio.sleep(2)
        return

    await asyncio.sleep(1)
    await click_generate_in_popup(page)
    await asyncio.sleep(3)
    await close_popup(page)


async def run_agent():
    """Main automation flow"""
    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else await context.new_page()

        print("🌐 Opening NotebookLM...")
        await page.goto(NOTEBOOKLM_URL)
        await asyncio.sleep(6)

        print("📓 Creating new notebook...")
        await click_by_text(page, "new notebook", wait=6)

        print("\n👉 Upload your file manually")
        while input("Type 'yes' when ready: ").strip().lower() != "yes":
            pass

        print("\n🚀 Running Studio automation...\n")

        for task in TASKS:
            await handle_task(page, task)

        print("\n🎉 All tasks triggered!")

        input("\nPress Enter to close...")
        await context.close()


if __name__ == "__main__":
    asyncio.run(run_agent())