"""Guidance and assessment logic for the AI-HW-Guider MVP."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from .syllabus import Syllabus, SyllabusPoint


@dataclass
class Feedback:
    """Represents feedback provided to the student during a session."""

    message: str
    related_points: List[str] = field(default_factory=list)
    tone: str = "supportive"


class GuidanceEngine:
    """Provides assessments, guidance, and brainstorming prompts."""

    def __init__(self, syllabus: Syllabus):
        self.syllabus = syllabus

    def assess_submission(self, submission: str) -> List[Feedback]:
        """Analyse the student's current work and return actionable feedback."""
        coverage = self.syllabus.coverage(submission)
        uncovered = [self.syllabus.points[key] for key, covered in coverage.items() if not covered]

        feedback: List[Feedback] = []
        for point, covered in coverage.items():
            if covered:
                feedback.append(
                    Feedback(
                        message=(
                            f"Great work incorporating syllabus point '{point}'. "
                            "Keep elaborating on the evidence and connections."
                        ),
                        related_points=[point],
                    )
                )

        for point in uncovered:
            feedback.append(
                Feedback(
                    message=(
                        f"It looks like you haven't addressed '{point.identifier}' yet. "
                        "Consider how this requirement fits into your current draft."
                    ),
                    related_points=[point.identifier],
                )
            )

        if not uncovered:
            feedback.append(
                Feedback(
                    message=(
                        "You've referenced every syllabus point! Focus now on clarity, "
                        "supporting evidence, and consistent reasoning."
                    )
                )
            )

        return feedback

    def offer_conceptual_support(self, submission: str) -> List[Feedback]:
        """Surface conceptual reminders without solving the assignment."""
        reminders: List[Feedback] = []
        for point in self.syllabus.uncovered_points(submission):
            if point.conceptual_help:
                reminders.append(
                    Feedback(
                        message=(
                            f"Concept check for '{point.identifier}': {point.conceptual_help} "
                            "Reflect on how this concept applies to your scenario."
                        ),
                        related_points=[point.identifier],
                    )
                )
        return reminders

    def brainstorm_prompts(self, submission: str) -> List[str]:
        """Generate brainstorming prompts tailored to uncovered syllabus points."""
        prompts = []
        for point in self.syllabus.uncovered_points(submission):
            prompts.append(
                (
                    f"What real-world example or citation could reinforce '{point.identifier}'?\n"
                    f"How might you explain {point.description.lower()} in your own words?"
                )
            )
        if not prompts:
            prompts.append(
                "Brainstorm enhancement: identify potential counterarguments or alternative"
                " perspectives you can acknowledge without solving the assignment."
            )
        return prompts

    def detect_misalignment(self, submission: str) -> List[Feedback]:
        """Highlight potential misalignments with the syllabus expectations."""
        misalignments: List[Feedback] = []
        coverage = self.syllabus.coverage(submission)
        for identifier, covered in coverage.items():
            if covered:
                point = self.syllabus.points[identifier]
                if sum(submission.lower().count(keyword) for keyword in point.keywords) < 2:
                    misalignments.append(
                        Feedback(
                            message=(
                                f"Double-check how thoroughly you treated '{identifier}'. "
                                "Try adding supporting details or citations without giving a full answer."
                            ),
                            related_points=[identifier],
                            tone="caution",
                        )
                    )
        return misalignments

    def guardrails(self, student_request: str) -> Feedback | None:
        """Detect attempts to solicit completed solutions and politely refuse."""
        disallowed_markers = [
            "complete solution",
            "do my homework",
            "write the answer",
            "full answer",
            "solve this for me",
            "give me the solution",
        ]
        normalized = student_request.lower()
        if any(marker in normalized for marker in disallowed_markers):
            return Feedback(
                message=(
                    "I'm here to guide and support your own work. Let's break the task into "
                    "steps you can tackle—what part would you like to think through next?"
                ),
                tone="boundary",
            )
        return None
