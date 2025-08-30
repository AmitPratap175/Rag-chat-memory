import json
import re

class JsonToLatexConverter:
    def __init__(self, data):
        """
        data: list of dicts or dict
        """
        if isinstance(data, dict):
            self.data = [data]
        elif isinstance(data, list):
            self.data = data
        else:
            raise ValueError("Input must be a dict or list of dicts")

    @staticmethod
    def latex_escape(text):
        # LaTeX special characters:
        replacements = {
            '\\': r'\textbackslash ',
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }
        # Do tilde and caret first as they use more than 1 char
        text = re.sub(r'~', replacements['~'], text)
        text = re.sub(r'\^', replacements['^'], text)
        # Then all other characters
        for char, esc in replacements.items():
            if char not in ['~', '^']:
                text = text.replace(char, esc)
        return text

    def process_options(self, options):
        options_latex = ""
        for key in sorted(options.keys()):
            value = self.latex_escape(options[key])
            options_latex += f"    \\item {value}\n"
        return options_latex

    def process_images(self, image_urls):
        images_latex = ""
        for url in image_urls:
            images_latex += f"\\includegraphics[width=0.7\\textwidth]{{{self.latex_escape(url)}}}\n"
        return images_latex

    def problem_to_latex(self, problem):
        q_num = self.latex_escape(str(problem.get("question_number", "")))
        q_text = self.latex_escape(problem.get("question_text", ""))
        options = problem.get("options", {})
        solution = self.latex_escape(problem.get("solution", ""))
        instructions = self.latex_escape(problem.get("instructions", ""))
        subject = self.latex_escape(problem.get("subject", ""))
        image_urls = problem.get("image_urls", [])

        latex = (
f"\\newpage\n"
f"\\begin{{problem}}{{}}{{}}\n"
f"% Subject: {subject}\n"
f"\\textbf{{Instructions}}\n\n"
f"{instructions}\n\n"
f"\\vspace{{1em}}\n"
f"\\textbf{{Question {q_num}}}\n\n"
f"{q_text}\n\n"
f"\\begin{{enumerate}}[label=\\Alph*.]\n"
f"{self.process_options(options)}"
f"\\end{{enumerate}}\n"
f"\\vspace{{1em}}\n"
f"\\textbf{{Solution:}}\n\n"
f"{solution}\n\n"
f"{self.process_images(image_urls)}"
f"\\end{{problem}}\n"
        )
        return latex

    def convert(self):
        latex_blocks = [self.problem_to_latex(problem) for problem in self.data]
        return "\n".join(latex_blocks)

    def write_to_file(self, filename):
        latex_code = self.convert()
        with open(filename, "w", encoding="utf-8") as f:
            f.write(latex_code)


# Example usage:
with open("varc_question_bank.json", "r") as file:
    json_array = json.load(file)

converter = JsonToLatexConverter(json_array)
converter.write_to_file("VARC.tex")

