"""Command line interface for the AI-HW-Guider MVP."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

from .session import GuidanceSession
from .syllabus import Syllabus


DEFAULT_SYLLABUS = {
    "course": "HIST-204",
    "assignment": "Industrial Revolution Research Essay",
    "points": [
        {
            "identifier": "thesis",
            "description": "Clear thesis statement connecting industrialization to social change",
            "keywords": ["thesis", "argument", "claim"],
            "conceptual_help": "Define a single arguable claim that links industrialization with a specific social impact.",
        },
        {
            "identifier": "evidence",
            "description": "Primary and secondary evidence integration",
            "keywords": ["evidence", "source", "citation"],
            "conceptual_help": "Differentiate between primary and secondary sources and cite at least one of each.",
        },
        {
            "identifier": "context",
            "description": "Historical context and timeline",
            "keywords": ["context", "timeline", "background"],
            "conceptual_help": "Outline key events or dates that frame your argument before analysing them.",
        },
        {
            "identifier": "analysis",
            "description": "Analytical explanation of cause and effect",
            "keywords": ["analysis", "cause", "effect"],
            "conceptual_help": "Connect evidence to your thesis by explaining why each piece matters.",
        },
    ],
}


def load_syllabus(path: str | None) -> Syllabus:
    if path is None:
        return Syllabus.from_dict(DEFAULT_SYLLABUS)
    data = json.loads(Path(path).read_text())
    return Syllabus.from_dict(data)


def format_feedback(feedback: Iterable) -> str:
    lines = []
    for item in feedback:
        prefix = {
            "supportive": "✅",
            "caution": "⚠️",
            "boundary": "⛔",
        }.get(getattr(item, "tone", "supportive"), "✅")
        related = f" (syllabus: {', '.join(item.related_points)})" if item.related_points else ""
        lines.append(f"{prefix} {item.message}{related}")
    return "\n".join(lines)


def interactive_loop(session: GuidanceSession) -> None:
    print("AI-HW-Guider MVP")
    print("This assistant will guide you through your assignment without completing it.")
    print("Type 'exit' to finish the session.\n")

    while True:
        student_input = input("Describe your current progress or questions> ")
        if student_input.strip().lower() in {"exit", "quit"}:
            break

        interaction = session.record_student_input(student_input)
        feedback_text = format_feedback(interaction.feedback)
        if feedback_text:
            print("\nGuidance:")
            print(feedback_text)

        prompts = session.brainstorming_suggestions(student_input)
        if prompts:
            print("\nBrainstorm prompts to explore:")
            for prompt in prompts:
                print(f"- {prompt}")

        print()

    summary = session.build_summary()
    print("Session summary:")
    for identifier, covered in summary.coverage_map.items():
        status = "covered" if covered else "needs attention"
        print(f"- {identifier}: {status}")

    print("\nHighlights:")
    for highlight in summary.highlights:
        print(f"* {highlight}")

    print("\nSession citation:")
    print(summary.to_citation())


def run(syllabus_path: str | None = None) -> None:
    syllabus = load_syllabus(syllabus_path)
    session = GuidanceSession(syllabus)
    interactive_loop(session)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else None
    run(path)
