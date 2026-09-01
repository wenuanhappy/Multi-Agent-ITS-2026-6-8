"""
Student Diagnostic Module
Tracks student progress, identifies weak areas, and recommends
adjusted difficulty levels for the Socratic tutor.

适配说明（Multi-Agent-ITS / CrewAI 版）：
  · SymPy 符号诊断核心逻辑
  · 本模块纯 stdlib，无跨包 import，无需改路径
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


class DifficultyLevel(str, Enum):
    """Enum for difficulty levels."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


@dataclass
class StudentState:
    """Represents the current state of a student."""
    level: str = DifficultyLevel.INTERMEDIATE
    consecutive_correct: int = 0
    consecutive_wrong: int = 0
    weak_areas: List[str] = field(default_factory=list)
    strong_areas: List[str] = field(default_factory=list)
    total_interactions: int = 0
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict:
        """Convert state to dictionary."""
        return asdict(self)


class StudentDiagnostic:
    """
    Diagnostic module for tracking and analyzing student progress.
    Manages student state and provides recommendations for tutoring.
    """

    def __init__(self):
        """Initialize the diagnostic module with default student state."""
        self.state = StudentState()
        self._interaction_history = []

    def update(self, is_correct: bool, topic_node_id: str, error_type: Optional[str] = None) -> None:
        """
        Update student state based on their answer.

        Args:
            is_correct: Whether the student's answer was correct
            topic_node_id: The ID of the knowledge node being assessed
            error_type: Type of error if incorrect (e.g., "conceptual", "computational", "careless")
        """
        self.state.total_interactions += 1
        self._interaction_history.append({
            "timestamp": datetime.now().isoformat(),
            "is_correct": is_correct,
            "topic_node_id": topic_node_id,
            "error_type": error_type,
            "difficulty_level": self.state.level
        })

        if is_correct:
            self.state.consecutive_correct += 1
            self.state.consecutive_wrong = 0

            # Add to strong areas if not already there
            if topic_node_id not in self.state.strong_areas:
                self.state.strong_areas.append(topic_node_id)

            # Remove from weak areas if in there
            if topic_node_id in self.state.weak_areas:
                self.state.weak_areas.remove(topic_node_id)

            # Level up if 2 consecutive correct and not already advanced
            if self.state.consecutive_correct >= 2 and self.state.level != DifficultyLevel.ADVANCED:
                self.state.level = self._level_up()
                self.state.consecutive_correct = 0

        else:
            self.state.consecutive_wrong += 1
            self.state.consecutive_correct = 0

            # Add to weak areas if not already there
            if topic_node_id not in self.state.weak_areas:
                self.state.weak_areas.append(topic_node_id)

            # Remove from strong areas if the error suggests deeper misunderstanding
            if error_type in ["conceptual", "fundamental"] and topic_node_id in self.state.strong_areas:
                self.state.strong_areas.remove(topic_node_id)

            # Level down if 2 consecutive wrong and not already beginner
            if self.state.consecutive_wrong >= 2 and self.state.level != DifficultyLevel.BEGINNER:
                self.state.level = self._level_down()
                self.state.consecutive_wrong = 0

        self.state.last_updated = datetime.now().isoformat()

    def _level_up(self) -> str:
        """
        Promote student to next difficulty level.

        Returns:
            New difficulty level
        """
        if self.state.level == DifficultyLevel.BEGINNER:
            return DifficultyLevel.INTERMEDIATE
        elif self.state.level == DifficultyLevel.INTERMEDIATE:
            return DifficultyLevel.ADVANCED
        return DifficultyLevel.ADVANCED

    def _level_down(self) -> str:
        """
        Demote student to previous difficulty level.

        Returns:
            New difficulty level
        """
        if self.state.level == DifficultyLevel.ADVANCED:
            return DifficultyLevel.INTERMEDIATE
        elif self.state.level == DifficultyLevel.INTERMEDIATE:
            return DifficultyLevel.BEGINNER
        return DifficultyLevel.BEGINNER

    def get_recommendation(self) -> Dict:
        """
        Get tutoring recommendation based on current student state.

        Returns:
            Dictionary with keys:
                - recommended_difficulty: str
                - suggested_topics: list[str] (topics to focus on)
                - should_show_animation: bool
                - prerequisite_review: list[str] (topics to review if needed)
                - encouragement_message: str
        """
        recommendation = {
            "recommended_difficulty": self.state.level,
            "suggested_topics": [],
            "should_show_animation": False,
            "prerequisite_review": [],
            "encouragement_message": ""
        }

        # If weak areas exist, prioritize them
        if self.state.weak_areas:
            recommendation["suggested_topics"] = self.state.weak_areas[:3]

        # If multiple consecutive errors, suggest animation support and review
        if self.state.consecutive_wrong >= 1 and self.state.weak_areas:
            recommendation["should_show_animation"] = True
            recommendation["prerequisite_review"] = self.state.weak_areas[:2]
            recommendation["encouragement_message"] = "看起来这个概念有点困难。让我们一起分解它，并用动画帮助理解。"

        # If on a winning streak, encourage continuation
        if self.state.consecutive_correct >= 2:
            recommendation["encouragement_message"] = "很好！你正在取得进展。让我们继续挑战更复杂的问题。"

        # If just leveled up, celebrate
        if self.state.consecutive_correct == 0 and self.state.level == DifficultyLevel.ADVANCED:
            recommendation["encouragement_message"] = "恭喜！你已经达到高级水平。现在让我们处理更复杂的问题。"

        # If recent level down, be supportive
        if self.state.consecutive_wrong == 0 and self.state.level == DifficultyLevel.BEGINNER:
            recommendation["encouragement_message"] = "没关系，我们会回到基础知识。让我们一步步来。"

        return recommendation

    def get_state_summary(self) -> str:
        """
        Generate a text summary of student state for injection into LLM prompt.

        Returns:
            Formatted string describing student's current state
        """
        level_name = {
            DifficultyLevel.BEGINNER: "初级",
            DifficultyLevel.INTERMEDIATE: "中级",
            DifficultyLevel.ADVANCED: "高级"
        }.get(self.state.level, "中级")

        summary_parts = [
            f"当前学生水平：{level_name}",
            f"总互动次数：{self.state.total_interactions}",
            f"连续正确：{self.state.consecutive_correct}次",
            f"连续错误：{self.state.consecutive_wrong}次"
        ]

        if self.state.strong_areas:
            summary_parts.append(f"掌握很好的领域：{', '.join(self.state.strong_areas)}")

        if self.state.weak_areas:
            summary_parts.append(f"需要加强的领域：{', '.join(self.state.weak_areas)}")

        # Add contextual guidance
        if self.state.consecutive_wrong >= 2:
            summary_parts.append("学生最近遇到困难，建议放慢步伐，提供更小的步骤。")
        elif self.state.consecutive_correct >= 2:
            summary_parts.append("学生表现很好，可以增加难度或提出更复杂的问题。")

        return "\n".join(summary_parts)

    def get_state(self) -> Dict:
        """
        Get the current student state as a dictionary.

        Returns:
            Dictionary representation of student state
        """
        return self.state.to_dict()

    def reset_state(self) -> None:
        """Reset student state to defaults (for new sessions or testing)."""
        self.state = StudentState()
        self._interaction_history = []

    def get_interaction_history(self) -> List[Dict]:
        """
        Get the complete interaction history.

        Returns:
            List of interaction records
        """
        return self._interaction_history.copy()

    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics from interaction history.

        Returns:
            Dictionary with metrics like:
                - success_rate: float (0-1)
                - total_interactions: int
                - avg_consecutive_correct: float
                - error_type_breakdown: dict
        """
        if not self._interaction_history:
            return {
                "success_rate": 0.0,
                "total_interactions": 0,
                "avg_consecutive_correct": 0.0,
                "error_type_breakdown": {}
            }

        total = len(self._interaction_history)
        correct = sum(1 for h in self._interaction_history if h["is_correct"])
        success_rate = correct / total if total > 0 else 0.0

        # Calculate error type breakdown
        error_types = {}
        for record in self._interaction_history:
            if not record["is_correct"] and record["error_type"]:
                error_types[record["error_type"]] = error_types.get(record["error_type"], 0) + 1

        return {
            "success_rate": success_rate,
            "total_interactions": total,
            "correct_answers": correct,
            "incorrect_answers": total - correct,
            "avg_consecutive_correct": self.state.consecutive_correct,
            "error_type_breakdown": error_types
        }

    def should_review_prerequisites(self) -> bool:
        """
        Determine if student should review prerequisites.

        Returns:
            True if student has multiple weak areas or recent failures
        """
        return len(self.state.weak_areas) >= 2 or self.state.consecutive_wrong >= 2

    def get_next_recommended_topic(self) -> Optional[str]:
        """
        Get the next recommended topic to study.

        Returns:
            Topic node ID to study next, or None if no recommendation
        """
        # Prioritize weak areas
        if self.state.weak_areas:
            return self.state.weak_areas[0]

        # If no weak areas, suggest advancing in strong areas
        if self.state.strong_areas:
            return f"advanced_{self.state.strong_areas[0]}"

        return None
