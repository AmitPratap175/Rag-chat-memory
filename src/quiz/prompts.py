QUESTION_GENERATION_PROMPT = """
You are an expert CAT/XAT VARC author. Given this passage (between triple backticks), generate a JSON object with [RC, para-summary, para-jumble, vocab, critical reasoning] following the EXACT schema below. Make language and distractors exam-grade: close, plausible, and sometimes indistinguishable without deep reading. Indicate difficulty (1-10) and which questions should be marked 'very-hard'. Always include answer and explanation and cite the sentences from the passage that support the answer using offsets.

**Passage:**
```
{passage_text}
```

**JSON Schema:**
```json
{
  "source": "<source url>",
  "source_meta": {"title":"", "author":"", "publish_date":"YYYY-MM-DD"},
  "passage_id": "<uuid>",
  "passage_text": "...",
  "questions": [
    {
      "id": "<uuid>",
      "type": "RC" | "VOCAB" | "PARA_SUM" | "PARA_JUMBLE" | "ODD_ONE_OUT" | "INFERENCE" | "STRENGTHEN" | "WEAKEN" | "TITLE" | "PARA_ORDER",
      "difficulty": 8,
      "difficulty_label": "very-hard",
      "question_text": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "correct_option": "B",
      "explanation": "...",
      "supporting_offsets": [{"start":int,"end":int,"snippet":"..."}],
      "topic_tags": ["economy","migration"],
      "generator_meta": {"model":"gpt-5-thinking-mini","prompt_version":"v1.0"}
    }
  ]
}
```

**Instructions:**
1.  Generate a variety of question types suitable for the passage.
2.  Ensure the difficulty level is appropriate for CAT/XAT exams.
3.  Provide a concise explanation for the correct answer and why the other options are incorrect.
4.  The JSON output must be valid and adhere strictly to the provided schema.
"""
