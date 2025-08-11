QUESTION_GENERATION_PROMPT = """
You are an expert CAT/XAT VARC author. Given this passage (between triple backticks), generate a JSON object with [RC, para-summary, para-jumble, vocab, critical reasoning] following the EXACT schema below. Make language and distractors exam-grade: close, plausible, and sometimes indistinguishable without deep reading. Indicate difficulty (1-10) and which questions should be marked 'very-hard'. Always include answer and explanation and cite the sentences from the passage that support the answer using offsets.

**Passage:**
{passage_text}


**Instructions:**
1.  Generate a variety of question types suitable for the passage.
2.  Ensure the difficulty level is appropriate for CAT/XAT exams.
3.  Provide a concise explanation for the correct answer and why the other options are incorrect.
4.  The JSON output must be valid and adhere strictly to the provided schema.
"""