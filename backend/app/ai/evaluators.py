import re
from typing import Dict, Any, List, Set, Optional
from app.ai.base import BaseEvaluator, QuestionContext, AnswerContext


class DomainEvaluator(BaseEvaluator):
    """
    Field-aware domain evaluator.
    Validates field-specific terminology, domain models, and professional jargon
    across engineering, data science, finance, marketing, HR, medicine, law, and management.
    """
    FIELD_DOMAIN_LEXICONS = {
        "data science": ["feature engineering", "cross validation", "bias variance", "loss function", "p-value", "overfitting", "regularization", "roc-auc", "hyperparameter", "pipeline"],
        "machine learning": ["gradient descent", "backpropagation", "convolutional", "transformer", "attention mechanism", "batch norm", "dropout", "latent space", "embeddings"],
        "software engineering": ["time complexity", "space complexity", "concurrency", "scalability", "caching", "database indexing", "clean architecture", "unit test", "asynchronous"],
        "robotics": ["forward kinematics", "inverse kinematics", "jacobian", "kalman filter", "slam", "ros2", "odometry", "trajectory planning", "state estimation", "actuator"],
        "finance": ["discounted cash flow", "wacc", "ebitda", "npv", "irr", "liquidity", "working capital", "beta", "capital structure", "valuation multiple", "balance sheet"],
        "marketing": ["customer acquisition cost", "lifetime value", "funnel conversion", "roas", "attribution model", "click through rate", "segmentation", "a/b test", "churn"],
        "human resources": ["competency matrix", "performance appraisal", "labor compliance", "pip", "mediation", "retention", "talent pipeline", "onboarding", "culture add"],
        "mechanical engineering": ["finite element", "stress strain", "yield strength", "heat transfer", "fluid dynamics", "tolerances", "machining", "dfm", "fatigue life"],
        "cybersecurity": ["threat actor", "cve", "zero trust", "least privilege", "encryption at rest", "soc", "siem", "privilege escalation", "lateral movement"]
    }

    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        answer_text_lower = (answer.answer_text or "").lower()
        field_key = question.field_name.lower().strip() if question.field_name else "general"

        lexicon = self.FIELD_DOMAIN_LEXICONS.get(field_key, [
            "framework", "methodology", "best practices", "analysis", "optimization", "metrics", "risk", "validation", "execution"
        ])

        matched_domain_terms = [term for term in lexicon if term in answer_text_lower]
        domain_ratio = len(matched_domain_terms) / max(len(lexicon[:5]), 1)
        domain_score = min(100.0, max(15.0, round(domain_ratio * 95.0 + 15.0, 1)))

        return {
            "domain_score": domain_score,
            "matched_domain_terms": matched_domain_terms,
            "field_name": question.field_name
        }


class TechnicalEvaluator(BaseEvaluator):
    """
    Evaluates technical concept coverage, depth, and rubric compliance across any field.
    """
    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        answer_text = answer.answer_text or ""
        answer_text_lower = answer_text.lower()
        expected = [t.strip() for t in question.expected_topics if t.strip()]
        skills = [s.strip() for s in question.skills if s.strip()]

        covered_topics: List[str] = []
        missing_topics: List[str] = []
        positive_indicators: List[str] = []
        negative_indicators: List[str] = []

        for topic in expected:
            topic_lower = topic.lower()
            words = topic_lower.split()
            if topic_lower in answer_text_lower or all(w in answer_text_lower for w in words):
                covered_topics.append(topic)
                positive_indicators.append(f"Addressed core concept: '{topic}'")
            else:
                missing_topics.append(topic)
                negative_indicators.append(f"Omitted concept: '{topic}'")

        covered_skills = [s for s in skills if s.lower() in answer_text_lower]
        for sk in covered_skills:
            positive_indicators.append(f"Applied domain skill: '{sk}'")

        topic_ratio = len(covered_topics) / max(len(expected), 1) if expected else 0.8
        skill_ratio = len(covered_skills) / max(len(skills), 1) if skills else 0.8

        word_count = len(answer_text.split())
        length_factor = min(1.0, max(0.2, word_count / 70.0))

        technical_score = round(((topic_ratio * 0.60) + (skill_ratio * 0.25) + (length_factor * 0.15)) * 100, 1)
        technical_score = min(100.0, max(10.0, technical_score))

        strengths = []
        if covered_topics:
            strengths.append(f"Demonstrated solid understanding of {len(covered_topics)} key concepts ({', '.join(covered_topics[:3])}).")
        if covered_skills:
            strengths.append(f"Referenced relevant industry frameworks ({', '.join(covered_skills[:3])}).")
        if word_count >= 50:
            strengths.append("Provided detailed domain reasoning with clear structural flow.")

        weaknesses = []
        if missing_topics:
            weaknesses.append(f"Did not adequately address: {', '.join(missing_topics[:3])}.")
        if word_count < 25:
            weaknesses.append("Response was brief and lacked procedural or mathematical elaboration.")
            negative_indicators.append("Answer length below expected depth for senior assessment.")

        if covered_topics and missing_topics:
            explanation = (
                f"Candidate demonstrated good domain awareness by explaining {', '.join(covered_topics[:2])}, "
                f"but missed essential principles regarding {', '.join(missing_topics[:2])}."
            )
        elif covered_topics:
            explanation = f"Comprehensive response thoroughly addressing key requirements: {', '.join(covered_topics[:3])}."
        else:
            explanation = f"Response lacked core technical depth. Expected coverage of: {', '.join(expected[:3]) if expected else 'key domain fundamentals'}."

        return {
            "score": technical_score,
            "covered_topics": covered_topics,
            "detected_topics": covered_topics,
            "missing_topics": missing_topics,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "explanation": explanation
        }


class ProblemSolvingEvaluator(BaseEvaluator):
    """
    Evaluates algorithmic logic, trade-off analysis, edge-case mitigation, and structured reasoning.
    """
    TRADE_OFF_KEYWORDS = [
        "trade-off", "tradeoff", "latency vs", "accuracy vs", "cost vs", "pros and cons",
        "alternative", "bottleneck", "mitigate", "fallback", "edge case", "fail-safe", "heuristic"
    ]

    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        text_lower = (answer.answer_text or "").lower()
        word_count = len(text_lower.split())

        trade_off_matches = [kw for kw in self.TRADE_OFF_KEYWORDS if kw in text_lower]
        has_structure = any(token in text_lower for token in ["firstly", "secondly", "step 1", "approach", "therefore", "in conclusion", "finally"])

        score = 65.0
        if trade_off_matches:
            score += min(20.0, len(trade_off_matches) * 10.0)
        if has_structure:
            score += 10.0
        if word_count > 60:
            score += 5.0

        diff_mult = {"EASY": 1.0, "MEDIUM": 1.05, "HARD": 1.15, "EXPERT": 1.25}.get(question.difficulty.upper(), 1.0)
        final_score = min(100.0, max(15.0, round(score * diff_mult, 1)))

        return {
            "score": final_score,
            "trade_off_matches": trade_off_matches,
            "has_structure": has_structure
        }


class BehavioralEvaluator(BaseEvaluator):
    """
    Evaluates STAR framework compliance (Situation, Task, Action, Result), conflict resolution, and leadership.
    """
    STAR_INDICATORS = {
        "situation": ["when", "during", "at my previous", "in a project", "situation", "context", "faced with"],
        "task": ["my responsibility", "tasked with", "objective", "goal", "challenge", "needed to"],
        "action": ["i implemented", "i designed", "i resolved", "i led", "i investigated", "i took action", "i created"],
        "result": ["as a result", "outcome", "resulting in", "achieved", "improved by", "reduced by", "successfully"]
    }

    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        answer_text = answer.answer_text or ""
        text_lower = answer_text.lower()
        star_coverage = {}

        for component, keywords in self.STAR_INDICATORS.items():
            star_coverage[component] = any(kw in text_lower for kw in keywords)

        star_score = sum(25 for val in star_coverage.values() if val)
        if star_score == 0 and len(text_lower.split()) > 40:
            star_score = 60.0

        strengths = []
        weaknesses = []

        if star_coverage.get("action"):
            strengths.append("Articulated specific personal ownership and actions taken.")
        if star_coverage.get("result"):
            strengths.append("Clearly highlighted the outcome and quantified business/engineering impact.")

        if not star_coverage.get("result"):
            weaknesses.append("Did not explicitly mention the measurable outcome or results achieved.")
        if not star_coverage.get("action"):
            weaknesses.append("Focused more on team dynamics rather than specific personal contributions.")

        explanation = f"STAR Method evaluation: {sum(1 for v in star_coverage.values() if v)} of 4 components identified."

        return {
            "score": min(100.0, max(15.0, round(star_score, 1))),
            "star_coverage": star_coverage,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "detected_topics": [f"STAR-{k.upper()}" for k, v in star_coverage.items() if v],
            "missing_topics": [f"STAR-{k.upper()}" for k, v in star_coverage.items() if not v],
            "positive_indicators": [f"STAR {k.upper()} element present" for k, v in star_coverage.items() if v],
            "negative_indicators": [f"STAR {k.upper()} element missing" for k, v in star_coverage.items() if not v],
            "explanation": explanation
        }


class CommunicationEvaluator(BaseEvaluator):
    """
    Evaluates speech fluency, vocabulary richness, sentence structure, and conciseness.
    """
    def evaluate(self, question: QuestionContext, answer: AnswerContext) -> Dict[str, Any]:
        text = answer.answer_text or ""
        words = re.findall(r"\b[a-zA-Z0-9_\-\./+#]+\b", text)
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]

        word_count = len(words)
        unique_words = len(set([w.lower() for w in words]))
        lexical_richness = (unique_words / max(word_count, 1)) * 100

        comm_score = 80.0
        if word_count < 20:
            comm_score = 45.0
        elif word_count < 40:
            comm_score = 65.0
        elif lexical_richness > 55.0:
            comm_score += 15.0

        strengths = []
        weaknesses = []

        if lexical_richness > 50.0 and word_count >= 40:
            strengths.append("High vocabulary variety and articulate structural phrasing.")
        if word_count < 25:
            weaknesses.append("Response was too succinct; needs more articulate detail.")

        return {
            "score": min(100.0, max(15.0, round(comm_score, 1))),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "lexical_richness": round(lexical_richness, 1)
        }
