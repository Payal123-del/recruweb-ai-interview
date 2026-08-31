import re
from typing import List, Dict, Any, Set, Optional


class UniversalQuestionEngine:
    """
    Universal Question Engine for any professional field.
    Selects balanced questions matching field, target role, focus skills,
    experience level, and adaptive difficulty without duplicates.
    """

    def select_questions(
        self,
        available_questions: List[Dict[str, Any]],
        field_name: str = "Universal",
        role_name: Optional[str] = None,
        interview_type: str = "TECHNICAL",
        focus_skills: Optional[List[str]] = None,
        difficulty: str = "MEDIUM",
        experience_level: str = "Mid-Level",
        count: int = 5,
        exclude_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        exclude_set = set(exclude_ids or [])
        scored_candidates = []
        skills_set = {s.lower().strip() for s in (focus_skills or [])}
        target_field = field_name.lower().strip()
        target_role = (role_name or "").lower().strip()
        target_diff = difficulty.upper()

        for q in available_questions:
            q_id = q.get("id")
            if q_id in exclude_set:
                continue

            score = 0.0

            # 1. Field matching (Primary filter)
            q_field = str(q.get("field_name", "")).lower().strip()
            if q_field == target_field or q_field == "universal" or not q_field:
                score += 30.0
            elif target_field in q_field or q_field in target_field:
                score += 20.0
            else:
                # Different field - lower priority
                score -= 10.0

            # 2. Role matching
            q_role = str(q.get("role_name", "")).lower().strip()
            if target_role and q_role:
                if target_role == q_role:
                    score += 25.0
                elif any(word in q_role for word in target_role.split() if len(word) > 3):
                    score += 15.0

            # 3. Focus Skills overlap
            q_skills = {s.lower().strip() for s in q.get("skills", [])}
            if skills_set:
                overlap = len(skills_set.intersection(q_skills))
                score += overlap * 12.0

            # 4. Difficulty alignment
            q_diff = str(q.get("difficulty", "")).upper()
            if target_diff == "ADAPTIVE":
                # For adaptive mode, start with medium difficulty
                if q_diff == "MEDIUM":
                    score += 15.0
            elif q_diff == target_diff:
                score += 15.0
            elif (target_diff == "HARD" and q_diff == "EXPERT") or (target_diff == "MEDIUM" and q_diff == "HARD"):
                score += 8.0

            # 5. Interview type alignment
            q_type = str(q.get("question_type", "")).upper()
            if interview_type.upper() in ["MIXED", "ALL"]:
                score += 10.0
            elif q_type == interview_type.upper() or (interview_type.upper() == "TECHNICAL" and q_type in ["TECHNICAL", "PROBLEM_SOLVING"]):
                score += 15.0

            scored_candidates.append((score, q))

        # Sort by relevance score descending
        scored_candidates.sort(key=lambda x: x[0], reverse=True)

        selected = [q for _, q in scored_candidates[:count]]

        # Fallback if insufficient questions exist in DB for niche/custom fields
        if len(selected) < count:
            selected.extend(self._generate_field_fallback_questions(
                field_name=field_name,
                role_name=role_name or f"{field_name} Specialist",
                skills=focus_skills or [field_name],
                needed=count - len(selected)
            ))

        return selected[:count]

    def _generate_field_fallback_questions(
        self,
        field_name: str,
        role_name: str,
        skills: List[str],
        needed: int
    ) -> List[Dict[str, Any]]:
        """Synthesizes realistic, professional interview questions for any custom or new field."""
        skill_str = ", ".join(skills[:3]) if skills else field_name
        templates = [
            {
                "category": f"{field_name} Fundamentals",
                "question_text": f"Explain the core methodologies, standard tools, and fundamental principles you apply as a {role_name} when working with {skill_str}.",
                "question_type": "TECHNICAL",
                "difficulty": "MEDIUM",
                "skills": skills[:3] or [field_name],
                "expected_topics": ["methodology", "best practices", "workflow", "tools", "verification"],
                "time_limit_seconds": 150
            },
            {
                "category": f"{field_name} Problem Solving",
                "question_text": f"Walk me through a complex scenario or technical challenge in {field_name} where you had to evaluate trade-offs between performance, quality, and time constraints.",
                "question_type": "PROBLEM_SOLVING",
                "difficulty": "HARD",
                "skills": ["Problem Solving", "Trade-offs", field_name],
                "expected_topics": ["problem statement", "evaluation of alternatives", "trade-offs", "solution", "quantified impact"],
                "time_limit_seconds": 180
            },
            {
                "category": f"{field_name} Architecture & Strategy",
                "question_text": f"How do you design, structure, and scale a production-grade workflow or system in {field_name} while mitigating edge cases and failure modes?",
                "question_type": "TECHNICAL",
                "difficulty": "HARD",
                "skills": ["Architecture", "System Design", field_name],
                "expected_topics": ["scalability", "edge cases", "risk mitigation", "monitoring", "architecture"],
                "time_limit_seconds": 180
            },
            {
                "category": "Behavioral & Stakeholder Alignment",
                "question_text": f"Describe a situation in your {field_name} experience where you had to convey complex domain concepts to cross-functional stakeholders who lacked technical background.",
                "question_type": "COMMUNICATION",
                "difficulty": "MEDIUM",
                "skills": ["Communication", "Stakeholder Management"],
                "expected_topics": ["situation", "simplification", "stakeholder empathy", "outcome", "alignment"],
                "time_limit_seconds": 120
            }
        ]
        return templates[:needed]

    def get_adaptive_followup(
        self,
        question: Dict[str, Any],
        answer_score: float,
        missing_topics: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Selects a deterministic relational follow-up question based on candidate's answer quality.
        """
        followup_rules = question.get("followup_rules", [])
        if followup_rules:
            for rule in followup_rules:
                min_s = rule.get("min_score", 0.0)
                max_s = rule.get("max_score", 100.0)
                if min_s <= answer_score <= max_s:
                    return {
                        "question_text": rule.get("followup_text"),
                        "category": "Adaptive Deep Dive",
                        "question_type": question.get("question_type", "TECHNICAL"),
                        "time_limit_seconds": 90
                    }

        # Dynamic follow-up if missing core concepts
        if answer_score < 65.0 and missing_topics:
            mt = missing_topics[0]
            return {
                "question_text": f"You mentioned key aspects, but could you elaborate specifically on how you incorporate '{mt}' into your approach?",
                "category": "Adaptive Clarification",
                "question_type": question.get("question_type", "TECHNICAL"),
                "time_limit_seconds": 90
            }
        return None


class AnswerAnalyzer:
    """
    Tokenizes answers, extracts keywords, measures text structure, length density, and clarity.
    """
    STOP_WORDS: Set[str] = {
        "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
        "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
        "by", "could", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
        "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
        "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
        "more", "most", "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only",
        "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same", "she",
        "should", "so", "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves",
        "then", "there", "these", "they", "this", "those", "through", "to", "too", "under", "until",
        "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
        "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
    }

    FILLER_WORDS: Set[str] = {
        "um", "uh", "like", "you know", "basically", "actually", "literally", "sort of", "kind of"
    }

    def analyze(self, text: str) -> Dict[str, Any]:
        cleaned = text.lower().strip()
        words = re.findall(r"\b[a-zA-Z0-9_\-\./+#]+\b", cleaned)
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        filtered_words = [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
        filler_count = sum(text.lower().count(fw) for fw in self.FILLER_WORDS)

        word_count = len(words)
        unique_word_count = len(set(filtered_words))
        lexical_richness = (unique_word_count / max(len(filtered_words), 1)) * 100

        return {
            "word_count": word_count,
            "sentence_count": len(sentences),
            "meaningful_words": filtered_words,
            "filler_count": filler_count,
            "lexical_richness": min(100.0, lexical_richness),
            "cleaned_text": cleaned
        }


# Backwards compatibility alias
QuestionSelector = UniversalQuestionEngine

