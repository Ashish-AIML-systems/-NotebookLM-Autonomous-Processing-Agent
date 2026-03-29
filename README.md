# 🤖 NotebookLM Autonomous Processing Agent

> **An autonomous AI agent that takes your PDFs → uploads to NotebookLM → triggers all Studio outputs in one shot. No manual clicking.**

---

## 🧠 What This Does

You drop a PDF. The agent opens NotebookLM, creates a notebook, waits for you to upload, then automatically fires every Studio feature — Audio Overview, Video Overview, Mind Map, Slide Deck, Flashcards, Infographic, and Data Table — back to back without any manual interaction.

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Ashish-AIML-systems/NotebookLM-Autonomous-Processing-Agent.git
cd NotebookLM-Autonomous-Processing-Agent

# 2. Install dependencies
pip install playwright
playwright install chrome

# 3. Run the agent
python agent.py
```

On first run, it will open Chrome and ask you to log into your Google account. After that, the session is saved and reused automatically.

---

## 🗂️ Project Structure

```
NotebookLM-Autonomous-Processing-Agent/
│
├── agent.py              # Main automation agent — runs the full pipeline
├── mapper.py             # Utility: maps UI element coordinates on screen
├── debug.py              # Utility: lists all buttons, inputs, links on page
├── upload_debug.py       # Utility: traces the file upload flow
│
├── .notebooklm_profile/  # Persistent Chrome session (auto-created, gitignored)
└── README.md
```

---

## 🎯 Studio Features Automated

| Feature | Status | Notes |
|---|---|---|
| 🎧 Audio Overview | ✅ Auto | No popup — fires instantly |
| 🎥 Video Overview | ✅ Auto | Opens popup → clicks Generate |
| 🧠 Mind Map | ✅ Auto | Opens popup → clicks Generate |
| 📑 Slide Deck | ✅ Auto | Opens popup → clicks Generate |
| 🃏 Flashcards | ✅ Auto | Opens popup → clicks Generate |
| 📊 Infographic | ✅ Auto | Opens popup → clicks Generate |
| 📋 Data Table | ✅ Auto | Opens popup → clicks Generate |
| ❌ Quiz | Skipped | — |
| ❌ Reports | Skipped | — |

---

## 🏗️ How It Works

```
You run agent.py
       ↓
Opens NotebookLM in Chrome
       ↓
Creates a new notebook
       ↓
Waits for your "yes" in terminal  ← you upload PDF manually here
       ↓
Scans DOM for each Studio button by text
       ↓
Clicks button → handles popup → clicks Generate → closes popup
       ↓
Moves to next feature immediately (no waiting for generation)
       ↓
All 7 features generating in background ✅
```

---

## 🧪 Interaction Engine

NotebookLM uses a React-based UI where standard Selenium-style selectors often fail. This agent uses a **3-layer hybrid click system**:

1. **DOM Text Scan** — searches all elements for matching `innerText` or `aria-label`
2. **JavaScript Click** — triggers `.click()` directly via `page.evaluate()`
3. **Coordinate Fallback** — uses mapped (x, y) pixel coordinates as last resort

This approach handles nested divs, non-standard buttons, and dynamically rendered UI components.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.10+ | Core scripting |
| Playwright (async) | Browser automation |
| AsyncIO | Async flow control |
| JavaScript (injected) | DOM interaction |
| Google Chrome | Browser engine |
| Google NotebookLM | AI document processing |

---

## 🧰 Dev Utilities

### `mapper.py`
Run this to get the exact screen coordinates of any UI element. Used to build the coordinate fallback system.

### `debug.py`
Lists all visible buttons, inputs, and links on the current page. Useful when NotebookLM updates its UI and elements change.

### `upload_debug.py`
Traces the file upload flow — detects hidden `<input type="file">` elements and their triggers.

---

## 🚧 Known Limitations

- File upload is still manual (you upload in browser, then type `yes`)
- Coordinate fallback may break if screen resolution or zoom changes
- NotebookLM UI updates can affect text-matching (just update the task names in `TASKS` list)
- Generation time varies — the agent moves on immediately, outputs complete in background

---

## 🔮 Roadmap

- [ ] Fully automated file upload via hidden input injection
- [ ] Auto-download of all generated outputs
- [ ] Batch mode: process a folder of PDFs one by one
- [ ] Progress dashboard in terminal
- [ ] RAG pipeline integration (feed outputs into a retrieval system)

---

## 👨‍💻 Author

**Ashish Sharma**
B.Tech AI/ML Engineering — BMSIT Bangalore
Building AI systems that automate real workflows.

[GitHub](https://github.com/Ashish-AIML-systems) · [LinkedIn](https://www.linkedin.com/in/ashish-sharma-0b8121357)

---

## 📌 Disclaimer

This project is for educational and research purposes only. NotebookLM is a product of Google. UI changes on their end may require updates to this agent.
