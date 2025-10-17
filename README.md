# AI-HW-Guider MVP

AI-HW-Guider is a console-based prototype that helps students stay aligned with
assignment expectations while keeping ownership of their work. The assistant is
designed to:

- Track coverage of syllabus requirements.
- Provide formative feedback and conceptual nudges.
- Offer brainstorming prompts tailored to uncovered requirements.
- Flag misalignment and enforce guardrails that prevent it from writing full
  solutions.
- Generate a session citation summarising how the student used the tool.

## Getting started

```bash
python -m ai_hw_guider.cli
```

By default the tool loads a sample syllabus for a history essay. Supply your own
syllabus in JSON format with the `--` notation when invoking the module (see
below for the structure).

Example JSON structure:

```json
{
  "course": "COURSE-CODE",
  "assignment": "Assignment name",
  "points": [
    {
      "identifier": "unique-label",
      "description": "Short explanation of the requirement",
      "keywords": ["list", "of", "keywords"],
      "conceptual_help": "Optional conceptual reminder to display to students"
    }
  ]
}
```

Save the structure to `syllabus.json` and run the tool with:

```bash
python -m ai_hw_guider.cli syllabus.json
```

## How sessions work

1. The student describes their progress or questions in their own words.
2. The tool analyses coverage against the syllabus, identifies conceptual
   reminders, and highlights places where the answer may still be thin.
3. Brainstorming prompts nudge the student toward next steps without revealing
   completed solutions.
4. When the student exits, the tool prints a coverage summary and a citation for
   their records detailing how AI-HW-Guider supported the work.

This MVP keeps a simple keyword-based model for clarity. Future iterations could
integrate richer semantic analysis or link to institutional LMS APIs while
preserving the "student does the work" principle.
