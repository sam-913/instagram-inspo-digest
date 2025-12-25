# 
# Instagram Inspo Digest ✨

An end-to-end automation pipeline that extracts inspirational quotes from visual content and generates ready-to-post Instagram quote cards using ethical, human-in-the-loop design.

---

## 🚀 What This Project Does

This system automates the **generation** of social media quote content while keeping **publishing human-controlled** to comply with platform policies.

Daily workflow:
1. Ingests image URLs (e.g., Pinterest feeds)
2. Extracts text via OCR
3. Applies ethical and duplication filters
4. Summarizes content into concise quotes
5. Renders multiple Instagram-ready cards using predefined templates

---

## 🧠 Why This Matters

Most social media automation projects either:
- Violate platform policies, or
- Stop at toy-level scripts

This project demonstrates a **production-minded hybrid automation model**:
> Automated content generation + human-approved publishing

This mirrors how real media, marketing, and AI-assisted content teams work.

---
![Project Plan](<img2.png>)
---

## 🏗 Architecture Overview

Image URLs
↓
OCR (Tesseract)
↓
Ethical Filter + Deduplication
↓
Text Summarization (Transformer)
↓
Digest Storage (SQLite)
↓
Visual Card Rendering (Pillow)


Automation & scheduling handled via **n8n**.

---

## 🖼 Output Example

Each run generates a daily *Editor Pack*:
- 4 quote options
- 2 visual templates (A/B)
- High-resolution PNGs (1080×1350)

These can be manually posted to Instagram or scheduled via approved tools.

---

## 🛠 Tech Stack

- **Backend:** FastAPI
- **OCR:** Tesseract
- **NLP:** HuggingFace Transformers
- **Image Rendering:** Pillow
- **Database:** SQLite
- **Automation:** n8n (Docker)
- **Language:** Python

---

## ▶️ How to Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload
```


Automation & scheduling handled via **n8n**.

---

## 🖼 Output Example

Each run generates a daily *Editor Pack*:
- 4 quote options
- 2 visual templates (A/B)
- High-resolution PNGs (1080×1350)

These can be manually posted to Instagram or scheduled via approved tools. Like this one:

![Example Quote](<img.png>)

---

## 🛠 Tech Stack

- **Backend:** FastAPI
- **OCR:** Tesseract
- **NLP:** HuggingFace Transformers
- **Image Rendering:** Pillow
- **Database:** SQLite
- **Automation:** n8n (Docker)
- **Language:** Python

---

## ▶️ How to Run Locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api:app --reload
```

## Create a digest:

```bash
curl -X POST http://127.0.0.1:8000/digest \
  -H "Content-Type: application/json" \
  -d '["IMAGE_URL_1", "IMAGE_URL_2"]'
```

## Render quote cards:

```bash
curl -X POST http://127.0.0.1:8000/render-cards \
  -H "Content-Type: application/json" \
  -d '{"digest_id": 1}'
```

## 📌 Future Extensions (Not Implemented)

- **Canva API integration**

- **Caption generation**

- **Engagement analytics**

- **Multi-language support**

---

### 👩‍💻 Author

**Samriddhi Sharma**  
Computer Science Engineer | Applied ML & Data Science  
Creative technologist exploring ethical AI + content automation

- 🌐 GitHub: https://github.com/sam-913/
- 💼 LinkedIn: https://www.linkedin.com/in/samriddhi-sharma-b312a5222/
- 🖋️ Medium: https://medium.com/@samriddhisharma.vis 

---

> _“Automation should amplify creativity — not replace judgment.”_
