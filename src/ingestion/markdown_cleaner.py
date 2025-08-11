import re
from pathlib import Path
from src.settings import settings

class MarkdownCleaner:
    def __init__(self):
        self.input_dir = Path(settings.SCRAPED_DIR)
        self.output_dir = Path(settings.DOCUMENTS_DIR)

        # --- Updated regex ---
        self.qa_block_pattern = re.compile(
            r"(?:(?:\*\*Instruction(?: for set(?: \d+)?)?\s*:?\*\*"
            r"|Directions for the next[\s\S]*?(?=#### Question)"
            r"|#### Question\s+\d+)"
            r"[\s\S]*?correct\s*answer\s*[:\-]*\s*\*{1,2}.*?\*{1,2})",
            flags=re.IGNORECASE
        )

    async def extract_qa_blocks(self, text: str) -> str:
        matches = self.qa_block_pattern.findall(text)
        cleaned_blocks = []

        for match in matches:
            # Remove standalone exclamation marks (surrounded by spaces or line breaks)
            cleaned = re.sub(r'(?<!\w)!(?!\w)', '', match)
            cleaned_blocks.append(cleaned.strip())

        return "\n\n".join(cleaned_blocks)

    async def process_files(self, raw_text, file_name) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # for md_file in self.input_dir.rglob('*.md'):
        try:
            # with md_file.open('r', encoding='utf-8') as f:
            #     raw_text = f.read()

            cleaned_text = await self.extract_qa_blocks(raw_text)

            output_file = self.output_dir / f"{file_name}_cleaned.md"
            with output_file.open('w', encoding='utf-8') as out_f:
                out_f.write(cleaned_text)

            print(f"[✔] Extracted Q&A: {file_name} → {output_file.name}")
            return cleaned_text

        except Exception as e:
            print(f"[✘] Failed to process {file_name}: {e}")
            return None
