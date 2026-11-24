# Contributing to Complete List of AI

Thank you for helping keep the **Complete List of AI** accurate, comprehensive, and useful for everyone!

Please review the short guidelines below before opening an Issue or Pull Request.

---

## Inclusion Criteria

1. **Strict Zero-Duplicates Policy (`1 AI = 1 Row`):** Every AI product, foundation model family, or open-source project may appear **only once** across the entire `README.md` in its single best-fit category. Duplicate AI names, duplicate brands, and duplicate URLs are automatically rejected by CI.
2. **Active & Real AIs Only:** Every entry must be an existing, publicly accessible AI model, chatbot, creative generator, agent, industry AI, or open-source AI project.
3. **Direct Official URLs Only:** Links must point directly to the canonical product homepage, model page, or open-source repository (`https://...`). **No affiliate links, URL shorteners, or referral tracking parameters** (`?ref=`, `?utm_`, `?via=`) are permitted.
4. **Accurate Free Plan & Pricing Info:**
   * Only mark `Free Plan` as `Yes (...)` or `Free & Open-Source` when users can genuinely try or run the AI without paying upfront.
   * Always verify current monthly or usage pricing on the creator's official pricing page.
5. **Keep Statistics & Index Counts in Sync:** When adding or removing an AI row, update the matching counts in the top badge, `## Directory Statistics`, and `## Index` table, then verify with `python3 scripts/validate_list.py`.

---

## Table Row Format

Every category table in `README.md` uses the same 7 columns:

```markdown
| AI Name | Creator | What It Does & Key Features | Best For | Free Plan | Pricing | Platforms |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [Example AI](https://example.com) | Example Lab | Concise summary of what the AI does and its standout capabilities. | Top 2–3 practical use cases | Yes (Free daily credits) | Free · Pro `$15/mo` | Web, iOS, Android |
```

---

## How to Submit a Pull Request

1. Fork [Ajitjha3095/Ultimate-AI-Models-API-Directory](https://github.com/Ajitjha3095/Ultimate-AI-Models-API-Directory) and create a new branch (`git checkout -b add-ai-name`).
2. Add or update the entry in **`README.md`** under the most relevant category section.
3. Run the validation script locally to check Markdown table columns, global uniqueness, links, and section anchors:

```bash
python3 scripts/validate_list.py
```

4. Open a [Pull Request](https://github.com/Ajitjha3095/Ultimate-AI-Models-API-Directory/pulls) and include a link to the AI's official website or pricing page for quick review.
