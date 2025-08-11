import re
from pathlib import Path
from src.settings import settings

class MarkdownCleaner:
    def __init__(self):
        self.input_dir = Path(settings.SCRAPED_DIR)
        self.output_dir = Path(settings.DOCUMENTS_DIR)

        # Old pattern from original code (fixed escaping)
        self.old_pattern = re.compile(
            r"(?:(?:\*\*Instruction(?: for set(?: \d+)?)?\s*:?\*\*"
            r"|\*\*Instructions\*\*"
            r"|Directions for the next[\s\S]*?(?=#### Question)"
            r"|#### Question\s+\d+)"
            r"[\s\S]*?correct\s*answer\s*[:\-]*\s*\*{1,2}.*?\*{1,2})",
            flags=re.IGNORECASE
        )

        # Pattern for standard Q&A blocks
        self.new_pattern = re.compile(
            r"(?:(?:\*\*Instructions?\*\*[\s\S]*?)(?=\n\*\*Question)|"
            r"\*\*Question\s*\d+\s*:\*\*[\s\S]*?(?=\n(?=\*\*Question|\Z)))",
            flags=re.IGNORECASE
        )

        # Pattern for long-form narrative with question link and solution
        self.narrative_pattern = re.compile(
            r"(?:Instructions\s+[\s\S]*?)"                       # starts with Instructions
            r"(?:\[\s*Question\s*\d+\]\(https?:\/\/[^\)]+\)[\s\S]*?)"  # question link
            r"(?:Solution\s+[\s\S]*?)(?=\n(?=Instructions|\Z))", # until next block or EOF
            flags=re.IGNORECASE
        )

    async def extract_qa_blocks(self, text: str) -> str:

        text = re.split(r"##### Login to your Cracku account", text, 1)[0]
        # Collect matches from all patterns
        matches = (
            self.old_pattern.findall(text)
            + self.new_pattern.findall(text)
            + self.narrative_pattern.findall(text)
        )

        seen = set()
        cleaned_blocks = []
        for match in matches:
            # Convert [Question XX] or [Question XX](url) into ## Question XX
            match = re.sub(r"\[\s*Question\s*(\d+)\s*\](?:\([^\)]*\))?", r"## Question \1", match)

            # Remove external links but keep image links
            match = re.sub(r"\[(?!.*?\]\(.*?\.(?:png|jpg|jpeg|gif)\))([^\]]+)\]\([^\)]+\)", r"\1", match)

            # Remove standalone !
            match = re.sub(r"(?<!\w)!(?!\w)", "", match)

            match = match.strip()
            if match and match not in seen:
                seen.add(match)
                cleaned_blocks.append(match)

        return "\n\n".join(cleaned_blocks)

    async def process_files(self, raw_text, file_name) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        try:
            cleaned_text = await self.extract_qa_blocks(raw_text)
            output_file = self.output_dir / f"{file_name}_cleaned.md"
            with output_file.open('w', encoding='utf-8') as out_f:
                out_f.write(cleaned_text)
            print(f"[✔] Extracted Q&A: {file_name} → {output_file.name}")
            return cleaned_text
        except Exception as e:
            print(f"[✘] Failed to process {file_name}: {e}")
            return None
