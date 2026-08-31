import re
from typing import Dict, Any, List, Optional
from app.ai.field_registry import UniversalFieldRegistry


class FieldDetectionEngine:
    """
    Modular Universal Field Detection Engine.
    Analyzes candidate profile/resume text, explicit skills, experience history,
    and job descriptions to generate an internal ranked list of recommended career fields.
    Zero external LLM API dependency.
    """

    def __init__(self):
        self.fields_registry = UniversalFieldRegistry.DEFAULT_FIELDS

    def detect_fields(
        self,
        resume_text: Optional[str] = None,
        skills: Optional[List[str]] = None,
        job_title: Optional[str] = None,
        job_description: Optional[str] = None,
        education: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Computes relevance scores across all registered professional fields
        using multi-factor tokenization and keyword alignment.
        """
        combined_text = " ".join(filter(None, [
            resume_text or "",
            " ".join(skills or []),
            job_title or "",
            job_description or "",
            education or ""
        ])).lower()

        # Tokenize words and 2-word phrases
        words = set(re.findall(r"\b[a-z0-9_\-\.#+]+\b", combined_text))
        phrases = set()
        raw_words = re.findall(r"\b[a-z0-9_\-\.#+]+\b", combined_text)
        for i in range(len(raw_words) - 1):
            phrases.add(f"{raw_words[i]} {raw_words[i+1]}")

        scored_fields = []

        for field_name, meta in self.fields_registry.items():
            field_score = 0.0
            matched_skills = []

            # 1. Skill overlap (Weight: 5.0 per match)
            for skill in meta.get("skills", []):
                s_clean = skill.lower().strip()
                if s_clean in combined_text or s_clean in words or s_clean in phrases:
                    field_score += 5.0
                    matched_skills.append(skill)

            # 2. Role title alignment (Weight: 8.0 per match)
            matched_roles = []
            for role in meta.get("roles", []):
                r_clean = role.lower().strip()
                if r_clean in combined_text:
                    field_score += 8.0
                    matched_roles.append(role)

            # 3. Direct field name mention (Weight: 6.0)
            if field_name.lower() in combined_text:
                field_score += 6.0

            # Normalize score into an internal ranking confidence (0.10 to 0.96)
            if field_score > 0:
                raw_confidence = min(0.96, 0.40 + (field_score / 45.0) * 0.56)
                confidence = round(raw_confidence, 2)
            else:
                confidence = 0.15

            if matched_skills or matched_roles or field_score > 0:
                scored_fields.append({
                    "field": field_name,
                    "confidence": confidence,
                    "matched_skills": list(dict.fromkeys(matched_skills)),
                    "suggested_roles": meta.get("roles", [])[:4],
                    "category": meta.get("category", "General"),
                    "icon": meta.get("icon", "Briefcase"),
                    "reasoning": f"Detected {len(matched_skills)} core skills ({', '.join(matched_skills[:3]) if matched_skills else 'profile alignment'}) matching {field_name} competencies."
                })

        # Sort by confidence descending
        scored_fields.sort(key=lambda x: x["confidence"], reverse=True)

        # Fallback if no strong match detected (e.g. blank profile)
        if not scored_fields:
            default_recommendations = ["Software Engineering", "Data Science", "Marketing", "Finance", "Human Resources"]
            for f in default_recommendations:
                meta = self.fields_registry.get(f, {})
                scored_fields.append({
                    "field": f,
                    "confidence": 0.50,
                    "matched_skills": meta.get("skills", [])[:2],
                    "suggested_roles": meta.get("roles", [])[:3],
                    "category": meta.get("category", "General"),
                    "icon": meta.get("icon", "Briefcase"),
                    "reasoning": f"Standard foundation track in {f}."
                })

        return scored_fields[:6]
