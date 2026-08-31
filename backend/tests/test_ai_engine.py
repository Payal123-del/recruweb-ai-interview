import pytest
from app.ai.base import QuestionContext, AnswerContext
from app.ai.engine import AIInterviewEngine


def test_internal_ai_evaluation_scoring():
    engine = AIInterviewEngine(version="internal-v1")
    
    question = QuestionContext(
        question_id="q1",
        question_text="Explain Forward vs Inverse Kinematics in a 6-DOF robotic manipulator.",
        category="Kinematics",
        question_type="TECHNICAL",
        difficulty="HARD",
        skills=["Kinematics", "Jacobian", "Manipulator"],
        expected_topics=["forward kinematics", "inverse kinematics", "jacobian", "singularities"]
    )

    # Strong technical response
    good_answer = AnswerContext(
        question_id="q1",
        answer_text=(
            "In a 6-DOF robotic manipulator, Forward Kinematics computes the end-effector pose from joint angles, "
            "whereas Inverse Kinematics calculates the required joint configurations for a target pose. "
            "IK often has multiple solutions and potential singularities where the Jacobian matrix loses rank. "
            "To handle singularities, we use damped least squares or pseudo-inverse methods."
        ),
        duration_seconds=95.0
    )

    eval_result = engine.evaluate_question(question, good_answer)
    assert eval_result.technical_score >= 80.0
    assert eval_result.relevance_score >= 80.0
    assert len(eval_result.strengths) > 0

    # Weak response
    weak_answer = AnswerContext(
        question_id="q1",
        answer_text="Um, kinematics is about moving the robot arm around with motors.",
        duration_seconds=10.0
    )

    weak_result = engine.evaluate_question(question, weak_answer)
    assert weak_result.technical_score < 60.0
    assert len(weak_result.weaknesses) > 0
