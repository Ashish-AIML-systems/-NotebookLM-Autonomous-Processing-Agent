"""
NotebookLM UI Mapper
====================

Purpose:
--------
Maps all clickable elements on NotebookLM UI and extracts:
- Coordinates (x, y)
- Text / label
- Tag & role

Features:
---------
- Works before and after notebook creation
- Helps debug UI automation failures
- Saves annotated screenshots

Use Case:
---------
Used to build coordinate fallback systems and understand UI structure.

Author: Ashish Sharma
"""

import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

DESKTOP      = Path.home() / "OneDrive" / "Desktop"
PROFILE_DIR  = Path(__file__).parent / ".notebooklm_profile"
OUTPUT_DIR   = DESKTOP / "NotebookLM_Output" / "_coord_maps"
NOTEBOOKLM_URL = "https://notebooklm.google.com"

def ts():
    return datetime.now().strftime("%H:%M:%S")

def log(msg):
    print(f"[{ts()}]  {msg}")


# ─────────────────────────────────────────────────────────────
# CORE MAPPER
# ─────────────────────────────────────────────────────────────
async def map_all_clickables(page, label):
    print(f"\n{'═'*70}")
    print(f"  MAP: {label}")
    print(f"{'═'*70}")

    elements = await page.evaluate("""() => {
        const results = [];
        const selectors = [
            'button',
            '[role="button"]',
            'a[href]',
            'input',
            '[tabindex="0"]',
            'mat-card',
            '[class*="card"]',
            'li',
            '[role="menuitem"]',
            '[role="option"]'
        ];

        const seen = new Set();

        for (const sel of selectors) {
            for (const el of document.querySelectorAll(sel)) {
                const rect = el.getBoundingClientRect();
                if (rect.width < 8 || rect.height < 8) continue;

                const style = window.getComputedStyle(el);
                if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0') continue;

                const x = Math.round(rect.left + rect.width / 2);
                const y = Math.round(rect.top + rect.height / 2);

                const key = `${x},${y}`;
                if (seen.has(key)) continue;
                seen.add(key);

                const text =
                    el.innerText ||
                    el.value ||
                    el.getAttribute('aria-label') ||
                    el.getAttribute('placeholder') ||
                    el.getAttribute('title') ||
                    "";

                const cleanText = text.trim().replace(/\\n/g, " ").slice(0, 60);
                if (!cleanText) continue;

                results.push({
                    x: x,
                    y: y,
                    w: Math.round(rect.width),
                    h: Math.round(rect.height),
                    tag: el.tagName.toLowerCase(),
                    role: el.getAttribute('role') || '',
                    type: el.getAttribute('type') || '',
                    text: cleanText
                });
            }
        }

        return results.sort((a, b) => a.y - b.y || a.x - b.x);
    }""")

    # ── PRINT CLEAN TABLE ──
    print(f"\n  {'#':<3} {'COORD':<14} {'SIZE':<10} {'TAG':<10} {'ROLE':<12} {'TEXT'}")
    print(f"  {'─'*3} {'─'*14} {'─'*10} {'─'*10} {'─'*12} {'─'*40}")

    for i, el in enumerate(elements, 1):
        coord = f"({el['x']},{el['y']})"
        size  = f"{el['w']}x{el['h']}"
        role  = el['role'][:10]
        text  = el['text'][:40]

        print(f"  {i:<3} {coord:<14} {size:<10} {el['tag']:<10} {role:<12} {text}")

    # ── DRAW VISUAL MARKERS ──
    await page.evaluate("""(elements) => {
        elements.forEach((el, i) => {

            const dot = document.createElement('div');
            dot.style.cssText = `
                position: fixed;
                left: ${el.x - 5}px;
                top: ${el.y - 5}px;
                width: 10px;
                height: 10px;
                background: red;
                border-radius: 50%;
                z-index: 999999;
                pointer-events: none;
            `;
            document.body.appendChild(dot);

            const label = document.createElement('div');
            label.style.cssText = `
                position: fixed;
                left: ${el.x + 8}px;
                top: ${el.y - 10}px;
                background: rgba(0,0,0,0.75);
                color: white;
                font-size: 9px;
                padding: 2px 4px;
                border-radius: 3px;
                z-index: 999999;
                pointer-events: none;
                max-width: 200px;
                overflow: hidden;
            `;
            label.innerText = `${i}. ${el.text.slice(0,25)}`;
            document.body.appendChild(label);
        });
    }""", elements)

    await asyncio.sleep(0.5)

    safe = label.replace(" ", "_")
    path = OUTPUT_DIR / f"MAP_{safe}.png"
    await page.screenshot(path=str(path))

    log(f"📸 Saved: {path}")
    print(f"\n  Total elements: {len(elements)}")

    return elements


# ─────────────────────────────────────────────────────────────
# MAIN FLOW
# ─────────────────────────────────────────────────────────────
async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "═"*70)
    print("  NotebookLM Smart Mapper")
    print("═"*70)

    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            channel="chrome",
            args=["--start-maximized"],
            no_viewport=True,
        )

        page = context.pages[0] if context.pages else await context.new_page()

        # ── STEP 1: HOMEPAGE ──
        log("Opening NotebookLM...")
        await page.goto(NOTEBOOKLM_URL)
        await asyncio.sleep(5)

        elements = await map_all_clickables(page, "01_HOMEPAGE")

        input("\n▶ Press ENTER to click New Notebook...")

        # ── STEP 2: CLICK NEW NOTEBOOK ──
        clicked = False
        for el in elements:
            if "new notebook" in el['text'].lower() or "create" in el['text'].lower():
                await page.mouse.click(el['x'], el['y'])
                log(f"Clicked → {el['text']}")
                clicked = True
                break

        if not clicked:
            log("⚠️ Could not auto-click — click manually")
            input("▶ Press ENTER after clicking...")

        await asyncio.sleep(6)

        # ── STEP 3: INSIDE NOTEBOOK UI ──
        await map_all_clickables(page, "02_NOTEBOOK_UI")

        print("\n🔥 Now you have BOTH:")
        print("• Homepage elements")
        print("• Notebook UI elements (Add Source, Studio, etc.)")

        input("\n▶ Press ENTER to exit...")
        await context.close()


if __name__ == "__main__":
    asyncio.run(main())