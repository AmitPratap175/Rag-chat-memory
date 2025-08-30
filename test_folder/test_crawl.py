# scrape_questions_textonly.py
# pip install crawl4ai beautifulsoup4

import asyncio
import json
import re
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from bs4 import BeautifulSoup, NavigableString, Tag


# --- Helpers -----------------------------------------------------------------
def _replace_tex_annotations(soup_fragment: BeautifulSoup) -> BeautifulSoup:
    """Replace LaTeX annotations with $...$ inline text."""
    for ann in soup_fragment.find_all('annotation', attrs={'encoding': 'application/x-tex'}):
        tex = ann.string or "".join(ann.strings)
        newnode = NavigableString(f"${tex.strip()}$")
        ann.replace_with(newnode)
    return soup_fragment


def _html_to_text(html_fragment: str) -> str:
    """Convert HTML to plain text (preserve math replacements)."""
    frag = BeautifulSoup(html_fragment, "html.parser")
    return frag.get_text(" ", strip=True)


def _label_for_number(n: int) -> str:
    return chr(ord('A') + n - 1) if n and n > 0 else str(n)


# --- Core parser -------------------------------------------------------------
def parse_card(card: Tag) -> Optional[Dict]:
    qdiv = card.select_one(".question-text")
    if not qdiv:
        return None

    qfrag = BeautifulSoup(qdiv.decode_contents(), "html.parser")
    _replace_tex_annotations(qfrag)
    question_text = _html_to_text(str(qfrag))

    options_box = card.select_one(".options-box")
    options_list: List[Dict] = []
    correct_answer_data = None
    data_qid = None

    if options_box:
        correct_answer_data = options_box.get("data-answer")
        data_qid = options_box.get("data-qid")

        for btn in options_box.select("button[data-option]"):
            opt_num = btn.get("data-option")
            try:
                opt_num_int = int(opt_num)
            except Exception:
                opt_num_int = None

            label = _label_for_number(opt_num_int) if opt_num_int else opt_num
            opt_content = btn.select_one(".option-content")
            opt_text = _html_to_text(opt_content.decode_contents()) if opt_content else _html_to_text(btn.decode_contents())

            options_list.append({
                "data_option": opt_num,
                "label": label,
                "option_text": opt_text,
                "is_correct": (opt_num == correct_answer_data) 
            })
    else:
        correct_data_class = card.select_one(".answer-box input[data-answer], .answer-box a[data-answer]")
        # print(correct_data_class)
        correct_answer_data = correct_data_class.get("data-answer")
        # print(correct_answer_data)

    # solution placeholder (if not dynamically loaded)
    solution = None
    badge = card.select_one("span.badge-success")
    if badge:
        parent = badge.find_parent()
        if parent:
            sol_text = _html_to_text(parent.decode_contents())
            solution = sol_text

    # --- Markdown output (no HTML) ---
    md_lines = []
    md_lines.append(f"### Question (qid: {data_qid})" if data_qid else "### Question")
    md_lines.append("")
    md_lines.append(question_text)
    md_lines.append("")

    if options_list:
        md_lines.append("**Options:**")
        for o in options_list:
            mark = " ✅" if o["is_correct"] else ""
            md_lines.append(f"- **{o['label']}**. {o['option_text']}{mark}")
    else:
        md_lines.append("**Options:** _none listed on page_")

    # Always show correct answer (even if no options exist)
    if correct_answer_data:
        md_lines.append("")
        md_lines.append(f"**Correct Answer:** {correct_answer_data}")

    if solution:
        md_lines.append("")
        md_lines.append("**Solution:**")
        md_lines.append(solution)

    return {
        "qid": data_qid,
        "question_text": question_text,
        "options": options_list,
        "correct_option_data": correct_answer_data,
        "solution_text": solution,
        "full_markdown": "\n".join(md_lines)
    }


# --- Main crawler ------------------------------------------------------------
async def scrape_url_textonly(url: str, out_basename: str = "output"):
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=BrowserConfig()) as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            raise RuntimeError(f"crawl4ai failed: {result.error_message}")

        soup = BeautifulSoup(result.html, "html.parser")
        cards = soup.select(".card")

        parsed_questions = []
        for card in cards:
            parsed = parse_card(card)
            if parsed:
                parsed_questions.append(parsed)

        output = {
            "url": url,
            "num_questions_found": len(parsed_questions),
            "questions": parsed_questions
        }

        # Save JSON (text only, no HTML)
        with open(f"{out_basename}.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        # Save Markdown
        with open(f"{out_basename}.md", "w", encoding="utf-8") as f:
            for q in parsed_questions:
                f.write(q["full_markdown"])
                f.write("\n\n---\n\n")

        print(f"Saved JSON -> {out_basename}.json")
        print(f"Saved Markdown -> {out_basename}.md")
        return output


def read_urls_from_file(filepath="urls.txt"):
    urls = []
    try:
        with open(filepath, "r") as f:
            for line in f:
                url = line.strip()
                if url:  # Add only non-empty lines
                    urls.append(url)
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        sys.exit(1)
    return urls


urls = read_urls_from_file()
for url in urls:
  # url="https://cracku.in/cat-2024-slot-2-quant-question-paper-solved"
  out ="/home/dspratap/Documents/GithubProjects/Rag-chat-memory/test_folder/docs/"+url.split("/")[-1]

  # Run the async scraping
  data = asyncio.run(scrape_url_textonly(url, out_basename=out))

