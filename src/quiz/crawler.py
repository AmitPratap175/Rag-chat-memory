import asyncio
import os
import hashlib
import regex as re
from urllib.parse import urldefrag, urlparse
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from pathlib import Path

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    MemoryAdaptiveDispatcher
)
from src.settings import settings
from src.ingestion.markdown_cleaner import MarkdownCleaner
from src.chatbot.modules.memory.long_term.vector_store import get_vector_store
import uuid
from datetime import datetime

from . import schemas
from .generator import generate_questions_for_passage

class SeleniumCleaner:
    """
    Cleans text content extracted via Selenium, handling inconsistent newlines
    and formatting issues while extracting Q&A blocks similar to MarkdownCleaner.
    """
    def __init__(self):
        self.output_dir = Path(settings.DOCUMENTS_DIR)
        
        # Enhanced regex patterns for text content (not markdown)
        self.qa_block_pattern = re.compile(
            r"(?:(?:Instruction(?:\s+for\s+set(?:\s+\d+)?)?\s*:?"
            r"|Directions\s+for\s+the\s+next[\s\S]*?(?=Question)"
            r"|Question\s+\d+)"
            r"[\s\S]*?correct\s*answer\s*[:\-]*\s*.*?)",
            flags=re.IGNORECASE | re.MULTILINE
        )
        
        # Pattern to match numbered questions
        self.question_pattern = re.compile(
            r"(\d+\.?\s+.*?(?=\d+\.|$))",
            flags=re.DOTALL | re.MULTILINE
        )

    async def normalize_whitespace(self, text: str) -> str:
        """Clean up inconsistent newlines and whitespace."""
        if not text:
            return ""
        
        # Replace multiple consecutive newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple consecutive spaces with single space
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove trailing whitespace from each line
        lines = text.split('\n')
        cleaned_lines = [line.rstrip() for line in lines]
        
        # Remove empty lines at start and end, but preserve structure
        while cleaned_lines and not cleaned_lines[0].strip():
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1].strip():
            cleaned_lines.pop()
            
        # Join back with consistent newlines
        text = '\n'.join(cleaned_lines)
        
        # Ensure proper spacing around questions
        text = re.sub(r'\n(\d+\.\s)', r'\n\n\1', text)
        
        # Fix spacing around "correct answer" sections
        text = re.sub(r'(\w)\s*correct\s*answer', r'\1\n\nCorrect Answer', text, flags=re.IGNORECASE)
        
        return text.strip()

    async def extract_qa_blocks(self, text: str) -> str:
        """Extract Q&A blocks from cleaned text."""
        # First normalize whitespace
        text = await self.normalize_whitespace(text)
        
        # Try to extract using Q&A pattern first
        matches = self.qa_block_pattern.findall(text)
        if matches:
            cleaned_blocks = []
            for match in matches:
                # Remove standalone exclamation marks
                cleaned = re.sub(r'(?<!\w)!(?!\w)', '', match)
                # Additional cleaning for text format
                cleaned = await self.normalize_whitespace(cleaned)
                if cleaned.strip():
                    cleaned_blocks.append(cleaned.strip())
            
            if cleaned_blocks:
                return "\n\n---\n\n".join(cleaned_blocks)
        
        # Fallback: try to extract by numbered questions
        questions = []
        lines = text.split('\n')
        current_question = []
        in_question = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_question:
                    current_question.append('')
                continue
                
            # Check if this line starts a new question
            if re.match(r'^\d+\.?\s+', line):
                # Save previous question
                if current_question and in_question:
                    question_text = '\n'.join(current_question).strip()
                    if question_text:
                        questions.append(question_text)
                
                # Start new question
                current_question = [line]
                in_question = True
            elif in_question:
                current_question.append(line)
                
                # Check if we've reached the end of this question
                if re.search(r'correct\s*answer|solution|answer.*choice', line, re.IGNORECASE):
                    question_text = '\n'.join(current_question).strip()
                    if question_text:
                        questions.append(question_text)
                    current_question = []
                    in_question = False
        
        # Don't forget the last question
        if current_question and in_question:
            question_text = '\n'.join(current_question).strip()
            if question_text:
                questions.append(question_text)
        
        if questions:
            return "\n\n---\n\n".join(questions)
        
        # Ultimate fallback: return normalized text
        return text

    async def convert_to_markdown_style(self, text: str) -> str:
        """Convert cleaned text to a markdown-like format."""
        if not text:
            return ""
        
        # Split into sections
        sections = text.split("---")
        markdown_sections = []
        
        for i, section in enumerate(sections, 1):
            section = section.strip()
            if not section:
                continue
                
            lines = section.split('\n')
            markdown_lines = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    markdown_lines.append('')
                    continue
                
                # Convert numbered questions to markdown headers
                if re.match(r'^\d+\.?\s+', line):
                    question_num = re.match(r'^(\d+)\.?\s+', line).group(1)
                    question_text = re.sub(r'^\d+\.?\s+', '', line)
                    markdown_lines.append(f"## Question {question_num}")
                    markdown_lines.append('')
                    markdown_lines.append(question_text)
                # Convert answer choices to bullet points
                elif re.match(r'^[A-E]\)\s*', line):
                    choice = re.sub(r'^([A-E])\)\s*', r'- **\1)** ', line)
                    markdown_lines.append(choice)
                # Convert correct answer sections
                elif re.search(r'correct\s*answer', line, re.IGNORECASE):
                    markdown_lines.append('')
                    markdown_lines.append('**Correct Answer:**')
                    answer_text = re.sub(r'correct\s*answer[:\-]*\s*', '', line, flags=re.IGNORECASE)
                    if answer_text.strip():
                        markdown_lines.append(answer_text.strip())
                else:
                    markdown_lines.append(line)
            
            if markdown_lines:
                markdown_sections.append('\n'.join(markdown_lines))
        
        return '\n\n---\n\n'.join(markdown_sections)

    async def process_selenium_content(self, raw_text: str, file_name: str, convert_to_markdown: bool = True) -> str:
        """
        Process Selenium-extracted content with comprehensive cleaning.
        
        Args:
            raw_text: Raw text from Selenium
            file_name: Base filename for saving
            convert_to_markdown: Whether to convert to markdown-style format
            
        Returns:
            Cleaned text content
        """
        try:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            
            if not raw_text or not raw_text.strip():
                print(f"[SELENIUM CLEANER] No content to process for {file_name}")
                return ""
            
            # Extract Q&A blocks
            cleaned_text = await self.extract_qa_blocks(raw_text)
            
            # Convert to markdown-style if requested
            if convert_to_markdown:
                cleaned_text = await self.convert_to_markdown_style(cleaned_text)
            
            # Save cleaned content
            if cleaned_text.strip():
                base_name = file_name.replace('.txt', '').replace('.html', '')
                output_file = self.output_dir / f"{base_name}_cleaned.md"
                
                with output_file.open('w', encoding='utf-8') as out_f:
                    out_f.write(cleaned_text)
                
                print(f"[SELENIUM CLEANER] ✔ Cleaned and saved: {file_name} → {output_file.name}")
                print(f"[SELENIUM CLEANER] Content length: {len(raw_text)} → {len(cleaned_text)} chars")
                
                return cleaned_text
            else:
                print(f"[SELENIUM CLEANER] ⚠ No Q&A content extracted from {file_name}")
                return ""
                
        except Exception as e:
            print(f"[SELENIUM CLEANER] ✘ Failed to process {file_name}: {e}")
            return ""

def url_to_filename(url: str, default="page", ext=".md") -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")

    if path:
        base = path.split("/")[-1]
    else:
        base = parsed.netloc.replace(".", "_")

    base = re.sub(r"\W+", "_", base).strip("_")

    if not base:
        base = hashlib.md5(url.encode()).hexdigest()

    return f"{base}{ext}"

def normalize_url(url):
    return urldefrag(url)[0]

def setup_selenium_driver():
    """Setup Chrome driver with optimal settings for scraping."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def expand_and_extract_with_selenium(url: str, max_clicks: int = 50) -> tuple:
    """
    Uses Selenium to expand "Load more" content and extract both HTML and text content.
    Returns (html_content, text_content, final_url, click_count)
    """
    print(f"[SELENIUM] Starting content expansion and extraction for {url}")
    
    driver = None
    try:
        driver = setup_selenium_driver()
        
        # Navigate to the page
        print(f"[SELENIUM] Loading page: {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)
        
        # Count initial questions
        def count_questions():
            try:
                strategies = [
                    (By.CSS_SELECTOR, '[class*="question"]'),
                    (By.CSS_SELECTOR, '.card'),
                    (By.CSS_SELECTOR, '[id*="question"]'),
                    (By.TAG_NAME, 'article')
                ]
                
                counts = []
                for by, selector in strategies:
                    try:
                        elements = driver.find_elements(by, selector)
                        counts.append(len(elements))
                    except:
                        counts.append(0)
                
                page_height = driver.execute_script("return document.body.scrollHeight")
                return max(counts + [page_height // 1000])
            except:
                return 0
        
        initial_count = count_questions()
        print(f"[SELENIUM] Initial content count: {initial_count}")
        
        # Expand "Load more" content
        clicks = 0
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while clicks < max_clicks and consecutive_failures < max_consecutive_failures:
            try:
                # Scroll to bottom
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                # Find load more button
                button = None
                try:
                    button = driver.find_element(By.ID, "load_more_questions")
                    print(f"[SELENIUM] Found button by ID")
                except NoSuchElementException:
                    try:
                        button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, 
                                "//button[contains(text(), 'Load more') and contains(text(), 'Probability') and contains(text(), 'Combinatorics')]"
                            ))
                        )
                        print(f"[SELENIUM] Found button by text")
                    except TimeoutException:
                        try:
                            button = driver.find_element(By.XPATH, "//button[contains(text(), 'Load more')]")
                            print(f"[SELENIUM] Found generic load more button")
                        except NoSuchElementException:
                            print(f"[SELENIUM] No load more button found after {clicks} clicks")
                            break
                
                if not button or not button.is_enabled() or not button.is_displayed():
                    print(f"[SELENIUM] Button is disabled or hidden, stopping")
                    break
                
                before_count = count_questions()
                
                # Click button
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)
                
                print(f"[SELENIUM] Clicking load more button (click {clicks + 1}/{max_clicks})")
                
                click_success = False
                try:
                    button.click()
                    click_success = True
                except Exception as e:
                    try:
                        driver.execute_script("arguments[0].click();", button)
                        click_success = True
                    except Exception as e2:
                        print(f"[SELENIUM] All click methods failed: {e2}")
                
                if not click_success:
                    consecutive_failures += 1
                    continue
                
                # Wait and check for new content
                time.sleep(2)
                
                content_grew = False
                for poll in range(10):
                    current_count = count_questions()
                    if current_count > before_count:
                        content_grew = True
                        break
                    time.sleep(0.8)
                
                if content_grew:
                    clicks += 1
                    consecutive_failures = 0
                    time.sleep(1.5)
                else:
                    consecutive_failures += 1
                    
            except Exception as e:
                print(f"[SELENIUM] Error in expansion loop: {e}")
                consecutive_failures += 1
                time.sleep(2)
        
        # Expand answers/solutions
        print(f"[SELENIUM] Expanding answer content...")
        answer_expansion_clicks = 0
        
        try:
            # Find and click show answer/solution buttons
            answer_buttons = driver.find_elements(By.XPATH, "//button[contains(text(), 'Show') or contains(text(), 'View') or contains(text(), 'Answer') or contains(text(), 'Solution')]")
            for button in answer_buttons:
                try:
                    if button.is_displayed() and button.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                        time.sleep(0.2)
                        button.click()
                        answer_expansion_clicks += 1
                        time.sleep(0.3)
                except:
                    continue
        except Exception as e:
            print(f"[SELENIUM] Error expanding answers: {e}")
        
        print(f"[SELENIUM] Expanded {answer_expansion_clicks} answers/solutions")
        
        # Final scroll and wait
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        # Extract content with enhanced text cleaning
        html_content = driver.page_source
        
        # Extract clean text content with better structure preservation
        text_content = driver.execute_script("""
            // Remove unwanted elements
            var unwanted = document.querySelectorAll('script, style, nav, header, footer, .advertisement, .ads, .social-share');
            unwanted.forEach(function(el) { el.remove(); });
            
            // Get main content area
            var mainContent = document.querySelector('main, .main-content, .content, .container, #main-content, .question-container');
            if (!mainContent) {
                mainContent = document.body;
            }
            
            // Extract text with better formatting
            var textContent = '';
            var elements = mainContent.querySelectorAll('*');
            
            for (var i = 0; i < elements.length; i++) {
                var el = elements[i];
                if (el.children.length === 0) { // Only text nodes
                    var text = el.innerText || el.textContent || '';
                    if (text.trim()) {
                        // Preserve question structure
                        if (el.tagName === 'H1' || el.tagName === 'H2' || el.tagName === 'H3') {
                            textContent += '\\n\\n' + text.trim() + '\\n';
                        } else if (el.className && el.className.includes('question')) {
                            textContent += '\\n\\n' + text.trim() + '\\n';
                        } else {
                            textContent += text.trim() + '\\n';
                        }
                    }
                }
            }
            
            return textContent;
        """)
        
        final_count = count_questions()
        final_url = driver.current_url
        
        print(f"[SELENIUM] Extraction complete.")
        print(f"[SELENIUM] Content stats: Initial: {initial_count}, Final: {final_count}")
        print(f"[SELENIUM] Load more clicks: {clicks}, Answer expansion clicks: {answer_expansion_clicks}")
        print(f"[SELENIUM] Content lengths: HTML: {len(html_content)} chars, Text: {len(text_content)} chars")
        
        return html_content, text_content, final_url, clicks
        
    except Exception as e:
        print(f"[SELENIUM] Error during content extraction: {e}")
        return "", "", url, 0
        
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass

def get_click_expansion_actions():
    """
    Returns Crawl4AI actions for content expansion (show answers, etc.)
    """
    return [
        {
            "type": "script",
            "script": """
                async () => {
                    const delay = ms => new Promise(res => setTimeout(res, ms));
                    const maxLoops = 40;
                    const matchRegexes = [
                        /show\\s*answer/i,
                        /show\\s*answers/i,
                        /view\\s*answer/i,
                        /view\\s*solution/i,
                        /show\\s*solution/i,
                        /see\\s*answer/i,
                        /reveal\\s*answer/i,
                        /solution/i,
                        /expand/i
                    ];
                    
                    function isVisible(el) {
                        try {
                            const rc = el.getBoundingClientRect();
                            const style = window.getComputedStyle(el);
                            return rc.width > 0 && rc.height > 0 && 
                                   style.display !== 'none' && 
                                   style.visibility !== 'hidden';
                        } catch (e) {
                            return false;
                        }
                    }

                    function textOf(el) {
                        try {
                            return (el.innerText || el.textContent || '').trim();
                        } catch (e) {
                            return '';
                        }
                    }

                    async function tryClick(el) {
                        try {
                            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            await delay(300);
                            el.click();
                            return true;
                        } catch (e) {
                            try {
                                el.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                                return true;
                            } catch (ee) {
                                return false;
                            }
                        }
                    }

                    console.log('[CRAWL4AI EXPANSION] Starting content expansion...');
                    let totalClicks = 0;
                    
                    for (let loop = 0; loop < maxLoops; loop++) {
                        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                        await delay(700);

                        let clickedAny = false;
                        const candidates = Array.from(document.querySelectorAll('button, a, span, div, p'));

                        for (const el of candidates) {
                            if (!isVisible(el)) continue;
                            const txt = textOf(el);
                            if (!txt) continue;
                            
                            for (const rx of matchRegexes) {
                                if (rx.test(txt)) {
                                    const ok = await tryClick(el);
                                    if (ok) {
                                        clickedAny = true;
                                        totalClicks++;
                                        console.log(`[CRAWL4AI EXPANSION] Revealed: "${txt.substring(0, 50)}"`);
                                    }
                                    await delay(300);
                                    break;
                                }
                            }
                        }

                        if (!clickedAny) break;
                        await delay(600);
                    }
                    
                    console.log(`[CRAWL4AI EXPANSION] Completed. Total reveals: ${totalClicks}`);
                    
                    // Final scroll
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                    await delay(1500);
                }
            """
        }
    ]

def compare_content_extraction(selenium_content: str, crawl4ai_content: str, url: str):
    """Compare the content extracted by Selenium vs Crawl4AI and log the differences."""
    selenium_len = len(selenium_content)
    crawl4ai_len = len(crawl4ai_content)
    
    print(f"\n[COMPARISON] Content comparison for {url}")
    print(f"[COMPARISON] Selenium content length: {selenium_len:,} characters")
    print(f"[COMPARISON] Crawl4AI content length: {crawl4ai_len:,} characters")
    
    if selenium_len > crawl4ai_len:
        difference = selenium_len - crawl4ai_len
        percentage = (difference / crawl4ai_len) * 100 if crawl4ai_len > 0 else 0
        print(f"[COMPARISON] Selenium extracted {difference:,} more characters ({percentage:.1f}% more)")
    elif crawl4ai_len > selenium_len:
        difference = crawl4ai_len - selenium_len
        percentage = (difference / selenium_len) * 100 if selenium_len > 0 else 0
        print(f"[COMPARISON] Crawl4AI extracted {difference:,} more characters ({percentage:.1f}% more)")
    else:
        print(f"[COMPARISON] Both tools extracted the same amount of content")
    
    # Quick content similarity check
    selenium_words = set(selenium_content.lower().split())
    crawl4ai_words = set(crawl4ai_content.lower().split())
    
    common_words = selenium_words.intersection(crawl4ai_words)
    unique_selenium = selenium_words - crawl4ai_words
    unique_crawl4ai = crawl4ai_words - selenium_words
    
    if selenium_words and crawl4ai_words:
        similarity = len(common_words) / max(len(selenium_words), len(crawl4ai_words))
        print(f"[COMPARISON] Content similarity: {similarity:.2%}")
        print(f"[COMPARISON] Unique to Selenium: {len(unique_selenium)} words")
        print(f"[COMPARISON] Unique to Crawl4AI: {len(unique_crawl4ai)} words")
    
    print(f"[COMPARISON] Analysis complete\n")

async def crawl_urls(crawl_request: schemas.CrawlRequest):
    browser_config = BrowserConfig(headless=True, verbose=False)
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        stream=False
    )
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=10
    )

    scraped_dir = settings.SCRAPED_DIR
    documents_dir = settings.DOCUMENTS_DIR
    os.makedirs(scraped_dir, exist_ok=True)
    os.makedirs(documents_dir, exist_ok=True)

    # Initialize cleaners
    markdown_cleaner = MarkdownCleaner()
    selenium_cleaner = SeleniumCleaner()
    vector_store = get_vector_store()
    all_processed_contents = []

    async with AsyncWebCrawler(config=browser_config) as crawler:
        if crawl_request.crawl_mode == "single":
            for url in crawl_request.urls:
                selenium_html = ""
                selenium_text = ""
                selenium_clicks = 0
                crawl4ai_markdown = ""
                
                try:
                    # PHASE 1: Extract with Selenium (includes load more expansion)
                    print(f"[INFO] Starting Selenium extraction for {url}")
                    selenium_html, selenium_text, expanded_url, selenium_clicks = expand_and_extract_with_selenium(url)
                    
                    # PHASE 2: Extract with Crawl4AI (after selenium expansion, use same URL)
                    print(f"[INFO] Starting Crawl4AI extraction for {expanded_url}")
                    result = await crawler.arun(
                        url=expanded_url,
                        config=run_config,
                        actions=get_click_expansion_actions()
                    )
                    
                    if result and result.success:
                        crawl4ai_markdown = result.markdown or ""
                        print(f"[INFO] Crawl4AI extraction completed")
                    else:
                        print(f"[ERROR] Crawl4AI extraction failed: {result.error_message if result else 'Unknown error'}")
                        # Continue with Selenium content only
                        
                except Exception as e:
                    print(f"[ERROR] Exception during extraction process for {url}: {e}")
                    continue

                # Compare the extractions if both succeeded
                if selenium_text and crawl4ai_markdown:
                    compare_content_extraction(selenium_text, crawl4ai_markdown, url)

                # Process and save both extractions
                base_filename = url_to_filename(url, ext="")
                
                # Save and clean Selenium content
                if selenium_text:
                    try:
                        # Save raw Selenium content
                        selenium_html_path = os.path.join(scraped_dir, f"{base_filename}_selenium.html")
                        with open(selenium_html_path, "w", encoding="utf-8") as f:
                            f.write(selenium_html)
                        
                        selenium_text_path = os.path.join(scraped_dir, f"{base_filename}_selenium.txt")
                        with open(selenium_text_path, "w", encoding="utf-8") as f:
                            f.write(selenium_text)
                        
                        print(f"[INFO] Saved raw Selenium content: {selenium_html_path}, {selenium_text_path}")
                        
                        # Clean Selenium content and save _cleaned version
                        cleaned_selenium_text = await selenium_cleaner.process_selenium_content(
                            selenium_text, 
                            f"{base_filename}_selenium",
                            convert_to_markdown=True
                        )
                        
                        if cleaned_selenium_text:
                            all_processed_contents.append((cleaned_selenium_text, f"{url}_selenium", "selenium"))
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to process Selenium content: {e}")

                # Save and clean Crawl4AI content
                if crawl4ai_markdown:
                    try:
                        # Save raw Crawl4AI content
                        crawl4ai_md_path = os.path.join(scraped_dir, f"{base_filename}_crawl4ai.md")
                        with open(crawl4ai_md_path, "w", encoding="utf-8") as f:
                            f.write(crawl4ai_markdown)
                        
                        print(f"[INFO] Saved raw Crawl4AI content: {crawl4ai_md_path}")
                        
                        # Clean Crawl4AI content and save _cleaned version
                        cleaned_crawl4ai_text = await markdown_cleaner.process_files(
                            crawl4ai_markdown, 
                            f"{base_filename}_crawl4ai"
                        )
                        
                        if cleaned_crawl4ai_text:
                            all_processed_contents.append((cleaned_crawl4ai_text, f"{url}_crawl4ai", "crawl4ai"))
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to process Crawl4AI content: {e}")

                # Store both cleaned contents in vector database
                for content, source_id, extraction_method in all_processed_contents:
                    if not content:
                        continue
                        
                    try:
                        metadata = {
                            "id": str(uuid.uuid4()),
                            "source": url,
                            "extraction_method": extraction_method,
                            "document_name": f"{base_filename}_{extraction_method}",
                            "timestamp": datetime.now().isoformat(),
                            "selenium_clicks": selenium_clicks if extraction_method == "selenium" else 0
                        }
                        vector_store.store_memory(text=content, metadata=metadata)
                        print(f"[INFO] Stored cleaned {extraction_method} content in vector store")
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to store {extraction_method} content: {e}")

        else:  # Recursive mode - simplified for this example
            print(f"[INFO] Recursive mode - using hybrid approach")
            visited = set()
            current_urls = set([normalize_url(u) for u in crawl_request.urls])

            for depth in range(3):
                urls_to_crawl = [normalize_url(url) for url in current_urls if normalize_url(url) not in visited]

                if not urls_to_crawl:
                    break

                print(f"[INFO] Recursive crawling at depth {depth}, processing {len(urls_to_crawl)} URLs")
                
                for url in urls_to_crawl:
                    visited.add(normalize_url(url))
                    
                    try:
                        if 'cracku.in' in url.lower():
                            # Use selenium + cleaning for cracku.in URLs
                            _, selenium_text, expanded_url, clicks = expand_and_extract_with_selenium(url)
                            if selenium_text:
                                base_filename = url_to_filename(url, ext="")
                                cleaned_text = await selenium_cleaner.process_selenium_content(
                                    selenium_text, 
                                    f"{base_filename}_selenium_recursive"
                                )
                                if cleaned_text:
                                    all_processed_contents.append((cleaned_text, url, "selenium"))
                            
                            # Also try crawl4ai on the expanded URL
                            result = await crawler.arun(
                                url=expanded_url,
                                config=run_config,
                                actions=get_click_expansion_actions()
                            )
                        else:
                            result = await crawler.arun(
                                url=url,
                                config=run_config
                            )

                        if result and result.success:
                            markdown = result.markdown or ""
                            try:
                                cleaned_text = await markdown_cleaner.clean_text(markdown)
                                if cleaned_text:
                                    all_processed_contents.append((cleaned_text, result.url, "crawl4ai"))
                                
                                # Save files
                                safe_filename = url_to_filename(result.url, ext=".md")
                                file_path = os.path.join(scraped_dir, safe_filename)
                                with open(file_path, "w", encoding="utf-8") as f:
                                    f.write(markdown)

                                metadata = {
                                    "id": str(uuid.uuid4()),
                                    "source": result.url,
                                    "extraction_method": "crawl4ai",
                                    "document_name": safe_filename,
                                    "timestamp": datetime.now().isoformat(),
                                    "crawl_depth": depth
                                }
                                vector_store.store_memory(text=cleaned_text, metadata=metadata)
                                
                            except Exception as e:
                                print(f"[ERROR] Failed to process content from {result.url}: {e}")
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to crawl {url}: {e}")

    # Generate questions from all processed contents
    print(f"[INFO] Generating questions for {len(all_processed_contents)} processed contents...")
    successful_generations = 0
    
    for cleaned_text, source_id, extraction_method in all_processed_contents:
        try:
            generate_questions_for_passage(cleaned_text, source_id)
            successful_generations += 1
            print(f"[INFO] Generated questions for {source_id} ({extraction_method})")
        except Exception as e:
            print(f"[ERROR] Failed to generate questions for {source_id}: {e}")

    return {
        "message": "Enhanced dual extraction with comprehensive cleaning completed successfully",
        "contents_processed": len(all_processed_contents),
        "questions_generated": successful_generations,
        "extraction_methods_used": list(set([method for _, _, method in all_processed_contents])),
        "files_saved": {
            "raw_selenium": f"*_selenium.html, *_selenium.txt",
            "raw_crawl4ai": f"*_crawl4ai.md", 
            "cleaned_selenium": f"*_selenium_cleaned.md",
            "cleaned_crawl4ai": f"*_crawl4ai_cleaned.md"
        }
    }

if __name__ == "__main__":
    from types import SimpleNamespace
    crawl_request = SimpleNamespace(
        crawl_mode="single",
        urls=["https://cracku.in/cat-probability-combinatorics-questions"]
    )
    asyncio.run(crawl_urls(crawl_request))
