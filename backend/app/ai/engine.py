from typing import Dict, Any, List, Optional
from app.ai.base import QuestionContext, AnswerContext, QuestionEvaluationResult, OverallEvaluationResult
from app.ai.question_selector import AnswerAnalyzer
from app.ai.evaluators import TechnicalEvaluator, DomainEvaluator, ProblemSolvingEvaluator, BehavioralEvaluator, CommunicationEvaluator
from app.ai.field_registry import UniversalFieldRegistry
from app.models.entities import RecommendationType


class CompetencyScorer:
    """
    Computes overall score and field-aware competency rubrics.
    """
    def compute_overall(
        self,
        question_evaluations: List[QuestionEvaluationResult],
        weights: Dict[str, float],
        field_name: str = "Universal",
        target_role: Optional[str] = None
    ) -> OverallEvaluationResult:
        if not question_evaluations:
            return OverallEvaluationResult(
                relevance_score=0.0,
                technical_score=0.0,
                communication_score=0.0,
                completeness_score=0.0,
                problem_solving_score=0.0,
                behavioral_score=0.0,
                domain_score=0.0,
                overall_score=0.0,
                confidence_indicator=0.0,
                field_name=field_name,
                target_role=target_role,
                recommendation=RecommendationType.REJECT.value
            )

        n = len(question_evaluations)
        avg_rel = sum(q.relevance_score for q in question_evaluations) / n
        avg_tech = sum(q.technical_score for q in question_evaluations) / n
        avg_comm = sum(q.communication_score for q in question_evaluations) / n
        avg_comp = sum(q.completeness_score for q in question_evaluations) / n
        avg_prob = sum(q.problem_solving_score for q in question_evaluations) / n
        avg_beh = sum(q.behavioral_score for q in question_evaluations) / n
        avg_domain = sum(q.domain_score for q in question_evaluations) / n

        # Extract field default weights if not explicitly customized
        field_data = UniversalFieldRegistry.get_field_data(field_name) or {}
        default_w = field_data.get("scoring_weights", {"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15})

        w_tech = weights.get("technical", default_w.get("technical", 0.40))
        w_prob = weights.get("problem_solving", default_w.get("problem_solving", 0.30))
        w_comm = weights.get("communication", default_w.get("communication", 0.15))
        w_beh = weights.get("behavioral", default_w.get("behavioral", 0.15))

        total_weight = w_tech + w_prob + w_comm + w_beh or 1.0

        overall = (
            (avg_tech * w_tech) +
            (avg_prob * w_prob) +
            (avg_comm * w_comm) +
            (avg_beh * w_beh)
        ) / total_weight

        # Aggregate unique strengths, weaknesses, and missing topics
        all_strengths = []
        all_weaknesses = []
        all_missing = []

        for q in question_evaluations:
            all_strengths.extend(q.strengths)
            all_weaknesses.extend(q.weaknesses)
            all_missing.extend(q.missing_topics)

        unique_strengths = list(dict.fromkeys(all_strengths))[:6]
        unique_weaknesses = list(dict.fromkeys(all_weaknesses))[:6]
        unique_missing = list(dict.fromkeys(all_missing))[:8]

        # Field-Tailored Actionable Improvement Suggestions (कहाँ पर ज्यादा ध्यान की जरूरत है)
        improvement_suggestions = self._build_field_improvement_suggestions(
            field_name=field_name,
            target_role=target_role,
            technical_score=avg_tech,
            problem_solving_score=avg_prob,
            communication_score=avg_comm,
            missing_topics=unique_missing
        )

        # Recommendation logic
        if overall >= 85.0:
            rec = RecommendationType.STRONG_HIRE.value
        elif overall >= 72.0:
            rec = RecommendationType.HIRE.value
        elif overall >= 58.0:
            rec = RecommendationType.CONSIDER.value
        elif overall >= 40.0:
            rec = RecommendationType.REJECT.value
        else:
            rec = RecommendationType.STRONG_REJECT.value

        breakdown = [q.model_dump() for q in question_evaluations]

        return OverallEvaluationResult(
            relevance_score=round(avg_rel, 1),
            technical_score=round(avg_tech, 1),
            communication_score=round(avg_comm, 1),
            completeness_score=round(avg_comp, 1),
            problem_solving_score=round(avg_prob, 1),
            behavioral_score=round(avg_beh, 1),
            domain_score=round(avg_domain, 1),
            overall_score=round(overall, 1),
            confidence_indicator=0.92,
            field_name=field_name,
            target_role=target_role,
            strengths=unique_strengths,
            weaknesses=unique_weaknesses,
            missing_topics=unique_missing,
            improvement_suggestions=improvement_suggestions,
            question_breakdown=breakdown,
            recommendation=rec,
            engine_version="universal-v1.0"
        )

    def _build_field_improvement_suggestions(
        self,
        field_name: str,
        target_role: Optional[str],
        technical_score: float,
        problem_solving_score: float,
        communication_score: float,
        missing_topics: List[str]
    ) -> List[Dict[str, Any]]:
        suggestions = []
        role_str = target_role or f"{field_name} Practitioner"

        if technical_score < 75.0:
            suggestions.append({
                "area": f"{field_name} Core Methodologies",
                "priority": "HIGH",
                "description": f"Deepen fundamental domain rigor and standard analytical frameworks expected of a {role_str}."
            })

        if problem_solving_score < 75.0:
            suggestions.append({
                "area": "Trade-off & Scenario Analysis",
                "priority": "MEDIUM",
                "description": "Explicitly articulate edge-case handling, scalability trade-offs, and cost-vs-benefit considerations."
            })

        if communication_score < 75.0:
            suggestions.append({
                "area": "Structured Domain Communication",
                "priority": "MEDIUM",
                "description": "Use the STAR method (Situation -> Task -> Action -> Result) and explain complex concepts step-by-step."
            })

        for mt in missing_topics[:4]:
            if not mt.startswith("STAR-"):
                suggestions.append({
                    "area": f"Unaddressed Concept: {mt}",
                    "priority": "HIGH" if technical_score < 70 else "MEDIUM",
                    "description": f"Review key interview scenarios and standard practices related to {mt}."
                })

        if not suggestions:
            suggestions.append({
                "area": f"Advanced {field_name} Mastery",
                "priority": "LOW",
                "description": f"Maintain your strong foundation and explore emerging trends and leadership methodologies in {field_name}."
            })

        return suggestions


class AIInterviewEngine:
    """
    Universal Modular Internal AI Interview Engine.
    Evaluates questions and interviews across all professional fields.
    """
    def __init__(self, version: str = "universal-v1.0"):
        self.version = version
        self.analyzer = AnswerAnalyzer()
        self.tech_evaluator = TechnicalEvaluator()
        self.domain_evaluator = DomainEvaluator()
        self.prob_evaluator = ProblemSolvingEvaluator()
        self.beh_evaluator = BehavioralEvaluator()
        self.comm_evaluator = CommunicationEvaluator()
        self.scorer = CompetencyScorer()

    def evaluate_question(self, question: QuestionContext, answer: AnswerContext) -> QuestionEvaluationResult:
        analysis = self.analyzer.analyze(answer.answer_text)

        tech_res = self.tech_evaluator.evaluate(question, answer)
        domain_res = self.domain_evaluator.evaluate(question, answer)
        prob_res = self.prob_evaluator.evaluate(question, answer)
        beh_res = self.beh_evaluator.evaluate(question, answer)
        comm_res = self.comm_evaluator.evaluate(question, answer)

        word_count = analysis["word_count"]
        relevance = 85.0 if word_count > 25 else (word_count / 25.0) * 85.0
        relevance = min(100.0, max(10.0, relevance))

        # Completeness based on expected topics coverage
        covered = tech_res.get("detected_topics", [])
        completeness = round(min(100.0, max(15.0, (len(covered) / max(len(question.expected_topics), 1)) * 100)), 1)

        # Composite score adapting to question type
        q_type = question.question_type.upper()
        if q_type in ["TECHNICAL", "CODING", "SYSTEM_DESIGN"]:
            q_score = (tech_res["score"] * 0.45) + (prob_res["score"] * 0.30) + (domain_res["domain_score"] * 0.15) + (comm_res["score"] * 0.10)
        elif q_type in ["BEHAVIORAL", "HR", "SITUATIONAL"]:
            q_score = (beh_res["score"] * 0.50) + (comm_res["score"] * 0.30) + (relevance * 0.20)
        elif q_type in ["PROBLEM_SOLVING", "CASE_STUDY"]:
            q_score = (prob_res["score"] * 0.45) + (domain_res["domain_score"] * 0.25) + (tech_res["score"] * 0.15) + (comm_res["score"] * 0.15)
        else:
            q_score = (tech_res["score"] * 0.35) + (domain_res["domain_score"] * 0.25) + (beh_res["score"] * 0.20) + (comm_res["score"] * 0.20)

        strengths = list(dict.fromkeys(tech_res["strengths"] + beh_res["strengths"] + comm_res["strengths"]))
        weaknesses = list(dict.fromkeys(tech_res["weaknesses"] + beh_res["weaknesses"] + comm_res["weaknesses"]))
        detected_topics = list(dict.fromkeys(tech_res.get("detected_topics", []) + beh_res.get("detected_topics", [])))
        missing_topics = list(dict.fromkeys(tech_res.get("missing_topics", []) + beh_res.get("missing_topics", [])))
        positive_indicators = list(dict.fromkeys(tech_res.get("positive_indicators", []) + beh_res.get("positive_indicators", []) + comm_res.get("positive_indicators", [])))
        negative_indicators = list(dict.fromkeys(tech_res.get("negative_indicators", []) + beh_res.get("negative_indicators", []) + comm_res.get("negative_indicators", [])))

        if q_type in ["BEHAVIORAL", "HR", "SITUATIONAL"]:
            explanation = beh_res.get("explanation", "")
        else:
            explanation = tech_res.get("explanation", "")

        feedback = (
            f"Candidate scored {round(q_score, 1)}/100 on {question.category}. "
            f"Domain depth: {tech_res['score']}%, Problem solving: {prob_res['score']}%, Communication: {comm_res['score']}%."
        )

        return QuestionEvaluationResult(
            question_id=question.question_id,
            score=round(q_score, 1),
            relevance_score=round(relevance, 1),
            technical_score=round(tech_res["score"], 1),
            completeness_score=round(completeness, 1),
            communication_score=round(comm_res["score"], 1),
            problem_solving_score=round(prob_res["score"], 1),
            behavioral_score=round(beh_res["score"], 1),
            domain_score=round(domain_res["domain_score"], 1),
            detected_topics=detected_topics,
            missing_topics=missing_topics,
            positive_indicators=positive_indicators,
            negative_indicators=negative_indicators,
            strengths=strengths,
            weaknesses=weaknesses,
            feedback=feedback,
            explanation=explanation
        )

    def evaluate_interview(
        self,
        questions: List[QuestionContext],
        answers: List[AnswerContext],
        weights: Dict[str, float],
        field_name: str = "Universal",
        target_role: Optional[str] = None
    ) -> OverallEvaluationResult:
        answers_dict = {a.question_id: a for a in answers}
        question_evals = []

        for q in questions:
            ans = answers_dict.get(q.question_id, AnswerContext(question_id=q.question_id, answer_text="No answer submitted."))
            q_eval = self.evaluate_question(q, ans)
            question_evals.append(q_eval)

        return self.scorer.compute_overall(question_evals, weights, field_name=field_name, target_role=target_role)
