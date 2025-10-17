"""Syllabus representation and parsing utilities for AI-HW-Guider."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SyllabusPoint:
    """Represents a single point or requirement from the syllabus."""

    identifier: str
    description: str
    keywords: List[str] = field(default_factory=list)
    conceptual_help: str | None = None

    def matches(self, text: str) -> bool:
        """Return True when the provided text touches on this syllabus point."""
        normalized = text.lower()
        return any(keyword in normalized for keyword in self.keywords)


@dataclass
class Syllabus:
    """Container for all syllabus points relevant to an assignment."""

    course: str
    assignment: str
    points: Dict[str, SyllabusPoint]

    @classmethod
    def from_dict(cls, payload: Dict) -> "Syllabus":
        points = {
            item["identifier"]: SyllabusPoint(
                identifier=item["identifier"],
                description=item["description"],
                keywords=item.get("keywords", []),
                conceptual_help=item.get("conceptual_help"),
            )
            for item in payload["points"]
        }
        return cls(course=payload["course"], assignment=payload["assignment"], points=points)

    def coverage(self, text: str) -> Dict[str, bool]:
        """Return a mapping of syllabus identifiers to coverage booleans."""
        return {identifier: point.matches(text) for identifier, point in self.points.items()}

    def uncovered_points(self, text: str) -> List[SyllabusPoint]:
        """Return points not yet covered by the provided text."""
        return [point for point in self.points.values() if not point.matches(text)]
