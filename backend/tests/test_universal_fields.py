import pytest
from app.ai.field_registry import UniversalFieldRegistry
from app.ai.field_detector import FieldDetectionEngine
from app.ai.question_selector import UniversalQuestionEngine, AnswerAnalyzer
from app.ai.evaluators import TechnicalEvaluator, DomainEvaluator, ProblemSolvingEvaluator, BehavioralEvaluator, CommunicationEvaluator
from app.ai.engine import AIInterviewEngine, CompetencyScorer
from app.ai.base import QuestionContext, AnswerContext


def test_universal_field_registry_defaults():
    fields = UniversalFieldRegistry.get_all_fields()
    assert len(fields) >= 30

    names = {f["name"] for f in fields}
    assert "Data Science" in names
    assert "Software Engineering" in names
    assert "Marketing" in names
    assert "Finance" in names
    assert "Human Resources" in names
    assert "Mechanical Engineering" in names
    assert "Robotics" in names
    assert "Cybersecurity" in names


def test_custom_field_dynamic_registration():
    custom_name = "Quantum Machine Learning"
    registered = UniversalFieldRegistry.register_custom_field(
        field_name=custom_name,
        category="Emerging Tech",
        roles=["Quantum ML Researcher", "Quantum Algorithm Engineer"],
        skills=["Qiskit", "Pennylane", "Variational Circuits"]
    )
    assert registered["name"] == custom_name
    assert "Quantum ML Researcher" in registered["roles"]

    retrieved = UniversalFieldRegistry.get_field_data(custom_name)
    assert retrieved is not None
    assert retrieved["name"] == custom_name


def test_field_detection_nlp_ranking():
    detector = FieldDetectionEngine()

    # Test candidate with data science background
    ds_results = detector.detect_fields(
        resume_text="Senior Machine Learning Specialist with 5 years experience in Python, Pandas, Scikit-Learn, Feature Engineering, and ROC-AUC optimization.",
        skills=["Python", "Machine Learning", "Statistics"],
        job_title="Data Scientist"
    )
    assert len(ds_results) > 0
    top_fields = [r["field"] for r in ds_results[:3]]
    assert "Data Science" in top_fields or "Machine Learning" in top_fields
    assert ds_results[0]["confidence"] > 0.5

    # Test candidate with finance background
    fin_results = detector.detect_fields(
        resume_text="Investment banking analyst skilled in DCF valuation, EBITDA multiples, financial modeling, and capital structure analysis.",
        skills=["Financial Modeling", "Corporate Finance", "Valuation"]
    )
    assert len(fin_results) > 0
    assert "Finance" in [r["field"] for r in fin_results[:2]]


def test_universal_question_engine_selection():
    q_engine = UniversalQuestionEngine()

    sample_questions = [
        {
            "id": "q1",
            "field_name": "Data Science",
            "role_name": "Data Scientist",
            "category": "ML Modeling",
            "question_text": "Explain bias variance trade-off in machine learning.",
            "question_type": "TECHNICAL",
            "difficulty": "MEDIUM",
            "skills": ["Machine Learning", "Python"],
            "expected_topics": ["bias variance", "overfitting"],
            "time_limit_seconds": 150
        },
        {
            "id": "q2",
            "field_name": "Marketing",
            "role_name": "Growth Lead",
            "category": "Paid Media",
            "question_text": "How do you optimize CAC and ROAS on Google Ads?",
            "question_type": "TECHNICAL",
            "difficulty": "MEDIUM",
            "skills": ["Paid Acquisition", "Analytics"],
            "expected_topics": ["cac", "roas", "funnel"],
            "time_limit_seconds": 150
        },
        {
            "id": "q3",
            "field_name": "Software Engineering",
            "role_name": "Backend Engineer",
            "category": "Architecture",
            "question_text": "Design a distributed caching system using Redis.",
            "question_type": "TECHNICAL",
            "difficulty": "HARD",
            "skills": ["Distributed Systems", "Redis"],
            "expected_topics": ["caching", "redis", "ttl"],
            "time_limit_seconds": 180
        }
    ]

    # Select Data Science questions
    selected_ds = q_engine.select_questions(
        available_questions=sample_questions,
        field_name="Data Science",
        role_name="Data Scientist",
        count=1
    )
    assert len(selected_ds) == 1
    assert selected_ds[0]["id"] == "q1"

    # Select Marketing questions
    selected_mkt = q_engine.select_questions(
        available_questions=sample_questions,
        field_name="Marketing",
        role_name="Growth Lead",
        count=1
    )
    assert len(selected_mkt) == 1
    assert selected_mkt[0]["id"] == "q2"


def test_ai_interview_engine_universal_evaluation():
    engine = AIInterviewEngine()

    q_ctx = QuestionContext(
        question_id="ds_q1",
        question_text="Explain bias variance tradeoff and how L1/L2 regularization prevents overfitting.",
        category="Machine Learning Modeling",
        question_type="TECHNICAL",
        difficulty="MEDIUM",
        field_name="Data Science",
        role_name="Data Scientist",
        skills=["Machine Learning", "Statistics", "Python"],
        expected_topics=["bias variance", "overfitting", "regularization", "loss function"]
    )

    ans_ctx = AnswerContext(
        question_id="ds_q1",
        answer_text="The bias variance tradeoff balances underfitting and overfitting. High bias leads to underfitting while high variance fits noise. We use regularization such as L1 Lasso and L2 Ridge which adds a penalty to the loss function to shrink coefficients and prevent overfitting.",
        duration_seconds=75.0
    )

    eval_result = engine.evaluate_question(q_ctx, ans_ctx)

    assert eval_result.score > 60.0
    assert eval_result.technical_score > 60.0
    assert len(eval_result.detected_topics) > 0
    assert len(eval_result.strengths) > 0

    # Overall interview evaluation
    overall = engine.evaluate_interview(
        questions=[q_ctx],
        answers=[ans_ctx],
        weights={"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15},
        field_name="Data Science",
        target_role="Data Scientist"
    )

    assert overall.overall_score > 60.0
    assert overall.field_name == "Data Science"
    assert overall.target_role == "Data Scientist"
    assert len(overall.improvement_suggestions) > 0
