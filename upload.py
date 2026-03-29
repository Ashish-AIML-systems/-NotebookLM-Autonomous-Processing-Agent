"""
NotebookLM Upload Flow Debugger
==============================

Purpose:
--------
Trace the complete "Add Source → Upload" flow.

Steps:
------
1. Open NotebookLM
2. Create notebook
3. Click "Add Source"
4. Click "Upload"
5. Detect file input elements

Outputs:
--------
- Debug screenshots (3 stages)
- Button dumps
- File input visibility

Use Case:
---------
Used to understand why file upload fails and locate hidden inputs.

Author: Ashish Sharma
"""
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

PROFILE_DIR    = Path(__file__).parent / ".notebooklm_profile"
NOTEBOOKLM_URL = "https://notebooklm.google.com"

async def dump_buttons(page, tag=""):
    print(f"\n─── BUTTONS [{tag}] ───────────────────────────")
    btns = await page.query_selector_all('button, div[role="menuitem"], li, [role="option"]')
    for i, b in enumerate(btns[:60]):
        try:
            txt  = (await b.inner_text()).strip().replace("\n", " ")
            aria = await b.get_attribute("aria-label") or ""
            box  = await b.bounding_box()
            vis  = await b.is_visible()
            pos  = f"({int(box['x'])},{int(box['y'])})" if box else "no-box"
            if vis and (txt or aria):
                print(f"  [{i:02d}] pos={pos:15s} text='{txt[:50]}' aria='{aria[:40]}'")
        except:
            pass
    inputs = await page.query_selector_all('input[type="file"]')
    print(f"  → file inputs visible: {len(inputs)}")

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

        # Click Create new notebook
        btn = await page.query_selector('[aria-label="Create new notebook"]')
        await btn.click(force=True)
        print("✅ Clicked Create new notebook")
        try:
            await page.wait_for_url("**/notebook**", timeout=20000)
        except:
            await page.wait_for_function(
                "() => document.body.innerText.toLowerCase().includes('add source')",
                timeout=20000
            )
        await asyncio.sleep(3)
        await page.screenshot(path="DEBUG_1_notebook_opened.png")
        print("📸 DEBUG_1_notebook_opened.png")

        # Click Add source
        add_btn = await page.query_selector('[aria-label="Add source"]')
        if not add_btn:
            for b in await page.query_selector_all('button'):
                txt = (await b.inner_text()).lower()
                if "add source" in txt:
                    add_btn = b
                    break
        await add_btn.click(force=True)
        print("✅ Clicked Add source")
        await asyncio.sleep(2)
        await page.screenshot(path="DEBUG_2_after_add_source.png")
        print("📸 DEBUG_2_after_add_source.png")
        await dump_buttons(page, "after Add Source click")

        # Click Upload
        upload_btn = None
        for b in await page.query_selector_all('button, div[role="menuitem"], li'):
            try:
                txt = (await b.inner_text()).lower().strip()
                if "upload" in txt and await b.is_visible():
                    upload_btn = b
                    print(f"  Found upload option: '{txt}'")
                    break
            except:
                pass

        if upload_btn:
            await upload_btn.click(force=True)
            print("✅ Clicked Upload option")
            await asyncio.sleep(2)
            await page.screenshot(path="DEBUG_3_after_upload_click.png")
            print("📸 DEBUG_3_after_upload_click.png")
            await dump_buttons(page, "after Upload click")

            # Check for file inputs NOW
            inputs = await page.query_selector_all('input[type="file"]')
            print(f"\n  → file inputs after upload click: {len(inputs)}")
            for i, inp in enumerate(inputs):
                vis    = await inp.is_visible()
                accept = await inp.get_attribute("accept") or ""
                print(f"     [{i}] visible={vis} accept='{accept}'")

        print("\n✅ Done. Check the 3 screenshots.")
        input("Press Enter to close...")
        await context.close()
        

asyncio.run(main())