"""Session management for the AI-HW-Guider MVP."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict

from .guidance import GuidanceEngine, Feedback
from .syllabus import Syllabus


@dataclass
class Interaction:
    """Represents a single exchange between the student and the tool."""

    timestamp: datetime
    student_input: str
    feedback: List[Feedback]


@dataclass
class SessionSummary:
    """Structured output summarising a session."""

    course: str
    assignment: str
    coverage_map: Dict[str, bool]
    highlights: List[str]
    guardrail_triggered: bool

    def to_citation(self) -> str:
        """Produce a summary citation for the student's records."""
        coverage = ", ".join(
            f"{identifier}:{'Y' if covered else 'N'}" for identifier, covered in self.coverage_map.items()
        )
        highlight_text = " | ".join(self.highlights)
        guardrail = "guardrail-engaged" if self.guardrail_triggered else "no-guardrail"
        return f"AI-HW-Guider session citation [{self.course} - {self.assignment}] coverage({coverage}) notes({highlight_text}) {guardrail}."


class GuidanceSession:
    """Orchestrates a session between the student and the guidance engine."""

    def __init__(self, syllabus: Syllabus):
        self.syllabus = syllabus
        self.engine = GuidanceEngine(syllabus)
        self.interactions: List[Interaction] = []
        self.guardrail_triggered = False

    def record_student_input(self, text: str) -> Interaction:
        """Process student input, generating feedback while enforcing guardrails."""
        guardrail_feedback = self.engine.guardrails(text)
        feedback: List[Feedback]
        if guardrail_feedback:
            self.guardrail_triggered = True
            feedback = [guardrail_feedback]
        else:
            assessment = self.engine.assess_submission(text)
            conceptual_support = self.engine.offer_conceptual_support(text)
            misalignments = self.engine.detect_misalignment(text)
            feedback = assessment + conceptual_support + misalignments

        interaction = Interaction(timestamp=datetime.utcnow(), student_input=text, feedback=feedback)
        self.interactions.append(interaction)
        return interaction

    def brainstorming_suggestions(self, text: str) -> List[str]:
        """Return brainstorming prompts based on the latest student input."""
        return self.engine.brainstorm_prompts(text)

    def build_summary(self) -> SessionSummary:
        """Compile a summary of the session for student records."""
        if not self.interactions:
            coverage_map = {identifier: False for identifier in self.syllabus.points}
            highlights = ["Session ended without student input."]
        else:
            latest = self.interactions[-1]
            coverage_map = self.syllabus.coverage(latest.student_input)
            highlights = []
            for interaction in self.interactions:
                for item in interaction.feedback:
                    highlights.append(item.message)

        return SessionSummary(
            course=self.syllabus.course,
            assignment=self.syllabus.assignment,
            coverage_map=coverage_map,
            highlights=highlights,
            guardrail_triggered=self.guardrail_triggered,
        )
