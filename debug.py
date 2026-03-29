"""
NotebookLM Debug Scanner
=======================

Purpose:
--------
Diagnose UI structure after opening a notebook.

Features:
---------
- Lists all buttons with:
    • text
    • aria-label
    • coordinates
    • visibility
- Detects file input elements
- Captures screenshot

Use Case:
---------
Helps identify:
- missing buttons
- hidden inputs
- UI rendering issues

Author: Ashish Sharma
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR    = Path(__file__).parent / ".notebooklm_profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com"

async def main():
    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            channel="chrome"
        )
        page = await context.new_page()
        await page.goto(NOTEBOOKLM_URL)
        await asyncio.sleep(5)

        # ── Step 1: click New Notebook ──────────────────
        btns = await page.query_selector_all('button')
        for b in btns:
            try:
                txt  = (await b.inner_text()).lower()
                aria = (await b.get_attribute("aria-label") or "").lower()
                if "new" in txt or "notebook" in txt or "create" in txt or "new" in aria:
                    await b.click(force=True)
                    print(f"✅ Clicked New Notebook: '{txt or aria}'")
                    break
            except:
                continue

        await asyncio.sleep(5)

        # ── Step 2: screenshot of current state ─────────
        await page.screenshot(path="DEBUG_AFTER_NEW_NOTEBOOK.png", full_page=True)
        print("📸 Screenshot saved → DEBUG_AFTER_NEW_NOTEBOOK.png")

        # ── Step 3: dump ALL buttons ─────────────────────
        print("\n─── ALL BUTTONS ───────────────────────────────")
        btns = await page.query_selector_all('button')
        for i, b in enumerate(btns):
            try:
                txt  = (await b.inner_text()).strip().replace("\n", " ")
                aria = await b.get_attribute("aria-label") or ""
                box  = await b.bounding_box()
                vis  = await b.is_visible()
                pos  = f"({int(box['x'])},{int(box['y'])})" if box else "no-box"
                print(f"  [{i:02d}] vis={vis} pos={pos:15s} text='{txt[:40]}' aria='{aria[:40]}'")
            except:
                pass

        # ── Step 4: dump all <input type=file> ──────────
        print("\n─── FILE INPUTS ────────────────────────────────")
        inputs = await page.query_selector_all('input[type="file"]')
        for i, inp in enumerate(inputs):
            try:
                vis    = await inp.is_visible()
                accept = await inp.get_attribute("accept") or ""
                print(f"  [{i}] visible={vis} accept='{accept}'")
            except:
                pass
        if not inputs:
            print("  (none found)")

        # ── Step 5: dump all links/anchors ──────────────
        print("\n─── LINKS / ANCHORS ────────────────────────────")
        anchors = await page.query_selector_all('a')
        for i, a in enumerate(anchors):
            try:
                txt  = (await a.inner_text()).strip().replace("\n", " ")
                href = await a.get_attribute("href") or ""
                vis  = await a.is_visible()
                if vis:
                    print(f"  [{i:02d}] text='{txt[:40]}' href='{href[:60]}'")
            except:
                pass

        # ── Step 6: anything with "upload" in any attr ──
        print("\n─── ELEMENTS WITH 'upload' ANYWHERE ────────────")
        els = await page.query_selector_all('[class*="upload"], [id*="upload"], [aria-label*="upload"], [data-testid*="upload"]')
        for i, el in enumerate(els):
            try:
                tag  = await el.evaluate("el => el.tagName")
                txt  = (await el.inner_text()).strip()[:60]
                aria = await el.get_attribute("aria-label") or ""
                cls  = await el.get_attribute("class") or ""
                print(f"  [{i}] <{tag}> text='{txt}' aria='{aria}' class='{cls[:60]}'")
            except:
                pass
        if not els:
            print("  (none found)")

        print("\n✅ Debug dump complete. Check the output above + DEBUG_AFTER_NEW_NOTEBOOK.png")
        input("Press Enter to close browser...")
        await context.close()

asyncio.run(main())