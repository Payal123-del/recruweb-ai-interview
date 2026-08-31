import logging
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.security import get_password_hash
from app.models.entities import (
    Base, Company, User, Job, Candidate, Question, Interview, Invitation,
    InterviewQuestion, Answer, Evaluation, QuestionEvaluation, Report, Dataset, DatasetVersion,
    ModelVersion, SystemSetting, UserRoleType, CompanyStatus, JobStatus,
    CandidateStatus, InterviewStatus, InterviewType, DifficultyLevel,
    QuestionType, RecommendationType
)

logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    # 1. Create Super Admin if not exists
    super_admin_email = "admin@ardhnarishwar.ai"
    result = await db.execute(select(User).where(User.email == super_admin_email))
    super_admin = result.scalars().first()

    if not super_admin:
        super_admin = User(
            email=super_admin_email,
            hashed_password=get_password_hash("AdminSecurePassword123!"),
            full_name="Ardhnarishwar Platform Director",
            role=UserRoleType.SUPER_ADMIN.value,
            is_active=True,
            is_superuser=True
        )
        db.add(super_admin)
        await db.flush()

    # 2. Seed AI Datasets and Models
    ds_check = (await db.execute(select(Dataset))).scalars().first()
    if not ds_check:
        ds1 = Dataset(
            name="Robotics Core Competencies v1.0",
            category="Question Dataset",
            description="Curated question dataset for autonomous systems, kinematics, ROS2, and control loops.",
            current_version="v1.0",
            records_count=150,
            status="ACTIVE"
        )
        db.add(ds1)
        await db.flush()

        v1 = DatasetVersion(
            dataset_id=ds1.id,
            version_tag="v1.0",
            records_count=150,
            validation_status="PASSED",
            validation_summary={"validated_by": "System", "passed_checks": 150}
        )
        db.add(v1)

        model1 = ModelVersion(
            name="Deterministic-NLP-Rubric-v1",
            version_tag="internal-v1",
            model_type="Deterministic-NLP-Rubric",
            status="PRODUCTION",
            metrics={"precision": 0.94, "recall": 0.91, "f1_score": 0.925, "latency_ms": 42}
        )
        db.add(model1)

    # 2.1 Seed Universal Professional Fields
    from app.models.entities import Field, FieldRole, FieldSkill
    from app.ai.field_registry import UniversalFieldRegistry

    f_check = (await db.execute(select(Field))).scalars().first()
    if not f_check:
        for f_data in UniversalFieldRegistry.get_all_fields():
            new_f = Field(
                name=f_data["name"],
                slug=f_data["slug"],
                category=f_data.get("category", "General"),
                icon=f_data.get("icon", "Briefcase"),
                description=f_data.get("description", ""),
                is_active=True,
                is_custom=False
            )
            db.add(new_f)
            await db.flush()

            for r_name in f_data.get("roles", []):
                db.add(FieldRole(field_id=new_f.id, role_name=r_name))

            for s_name in f_data.get("skills", []):
                db.add(FieldSkill(field_id=new_f.id, skill_name=s_name))
        await db.flush()

    # 3. Seed Universal Multi-Field Question Bank
    q_check = (await db.execute(select(Question).where(Question.tenant_id == None))).scalars().first()
    if not q_check:
        global_questions = [
            # Data Science Questions
            Question(
                field_name="Data Science",
                role_name="Data Scientist",
                category="Machine Learning & Modeling",
                question_text="Explain the bias-variance tradeoff. How do regularization techniques like L1 (Lasso) and L2 (Ridge) prevent overfitting in high-dimensional datasets?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Machine Learning", "Statistics", "Python"],
                expected_topics=["bias variance", "overfitting", "regularization", "l1 lasso", "l2 ridge", "loss function"],
                time_limit_seconds=150
            ),
            Question(
                field_name="Data Science",
                role_name="Data Scientist",
                category="Statistics & Experimentation",
                question_text="How do you design an A/B test with statistical power calculations? Describe how you mitigate sample ratio mismatch (SRM) and p-hacking.",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["Statistics", "A/B Testing", "Hypothesis Testing"],
                expected_topics=["statistical power", "sample size", "p-value", "significance level", "srm", "minimum detectable effect"],
                time_limit_seconds=180
            ),
            # Software Engineering Questions
            Question(
                field_name="Software Engineering",
                role_name="Software Engineer",
                category="System Design & Architecture",
                question_text="How would you design a distributed caching layer using Redis to handle cache stampede and ensure eventual consistency with an SQL primary database?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["System Design", "Distributed Systems", "SQL"],
                expected_topics=["caching", "cache stampede", "redis", "eventual consistency", "ttl", "write-through"],
                time_limit_seconds=180
            ),
            Question(
                field_name="Software Engineering",
                role_name="Software Engineer",
                category="Algorithms & Data Structures",
                question_text="Explain the time and space complexity differences between BFS and DFS. In what production scenarios is one preferred over the other?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Algorithms", "Data Structures", "Problem Solving"],
                expected_topics=["time complexity", "space complexity", "bfs", "dfs", "queue", "stack", "shortest path"],
                time_limit_seconds=150
            ),
            # Marketing Questions
            Question(
                field_name="Marketing",
                role_name="Digital Marketing Manager",
                category="Growth & Conversion Optimization",
                question_text="Walk through your methodology for reducing Customer Acquisition Cost (CAC) while scaling paid acquisition across Google and Meta ad channels. How do you measure Blended ROAS?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Growth Strategy", "Paid Acquisition (PPC)", "Conversion Rate Optimization"],
                expected_topics=["customer acquisition cost", "cac", "ltv", "roas", "funnel", "a/b testing", "attribution"],
                time_limit_seconds=150
            ),
            # Finance Questions
            Question(
                field_name="Finance",
                role_name="Financial Analyst",
                category="Corporate Valuation & Modeling",
                question_text="Explain step-by-step how to build a Discounted Cash Flow (DCF) model. How do you calculate Weighted Average Cost of Capital (WACC) and terminal value?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["Financial Modeling", "Valuation (DCF/Comps)", "Corporate Finance"],
                expected_topics=["discounted cash flow", "wacc", "free cash flow", "terminal value", "discount rate", "enterprise value"],
                time_limit_seconds=180
            ),
            # Human Resources Questions
            Question(
                field_name="Human Resources",
                role_name="HR Business Partner (HRBP)",
                category="Employee Relations & Conflict",
                question_text="How do you handle a sensitive workplace conflict where a high-performing engineer is reported for toxic interpersonal behavior by team members? Describe your resolution framework.",
                question_type=QuestionType.BEHAVIORAL.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Conflict Resolution", "Employee Relations", "HR Policies & Labor Law"],
                expected_topics=["fact-finding", "impartial investigation", "mediation", "documentation", "performance plan", "culture"],
                time_limit_seconds=150
            ),
            # Mechanical Engineering Questions
            Question(
                field_name="Mechanical Engineering",
                role_name="Mechanical Design Engineer",
                category="CAD & Structural Design",
                question_text="How do you apply Geometric Dimensioning & Tolerancing (GD&T) datums and Design for Manufacturing (DFM) principles when designing an injection-molded or CNC-machined enclosure?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["GD&T", "DFM / DFA", "CAD", "SolidWorks"],
                expected_topics=["gd&t", "datums", "tolerances", "draft angles", "wall thickness", "dfm", "cnc"],
                time_limit_seconds=180
            ),
            # Robotics Questions
            Question(
                field_name="Robotics",
                role_name="Robotics Software Engineer",
                category="Robotics Kinematics",
                question_text="Explain the difference between Forward Kinematics (FK) and Inverse Kinematics (IK) for a 6-DOF robotic manipulator, and discuss how you handle kinematic singularities.",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["Kinematics", "Robotics Manipulation", "Linear Algebra"],
                expected_topics=["forward kinematics", "inverse kinematics", "jacobian", "singularities", "damped least squares"],
                time_limit_seconds=180
            ),
            Question(
                field_name="Robotics",
                role_name="Robotics Software Engineer",
                category="Autonomous Navigation & SLAM",
                question_text="How does an Extended Kalman Filter (EKF) fuse wheel odometry, IMU, and LiDAR sensor data in a ROS2 robot_localization pipeline?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.HARD.value,
                skills=["ROS2", "SLAM", "State Estimation", "EKF"],
                expected_topics=["extended kalman filter", "imu", "odometry", "lidar", "covariance", "ros2"],
                time_limit_seconds=180
            ),
            # Cybersecurity Questions
            Question(
                field_name="Cybersecurity",
                role_name="Security Analyst",
                category="Threat Modeling & Architecture",
                question_text="Explain the core principles of Zero Trust Architecture. How do you implement micro-segmentation and least-privilege access across cloud infrastructure?",
                question_type=QuestionType.TECHNICAL.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Threat Modeling", "OWASP Top 10", "Network Protocols"],
                expected_topics=["zero trust", "least privilege", "micro-segmentation", "iam", "authentication", "encryption"],
                time_limit_seconds=150
            ),
            # Universal Communication / Leadership Question
            Question(
                field_name="Universal",
                role_name="General",
                category="Communication & Leadership",
                question_text="Tell me about a time when a critical project deadline was at risk due to unforeseen roadblocks. How did you realign priorities and communicate effectively with stakeholders?",
                question_type=QuestionType.COMMUNICATION.value,
                difficulty=DifficultyLevel.MEDIUM.value,
                skills=["Clear Communication", "Stakeholder Management", "Crisis Management"],
                expected_topics=["situation", "task", "proactive communication", "prioritization", "outcome", "lessons"],
                time_limit_seconds=120
            )
        ]
        for gq in global_questions:
            db.add(gq)
        await db.flush()


    # 4. Seed Company 1: Apex Robotics Inc
    apex_check = (await db.execute(select(Company).where(Company.slug == "apex-robotics"))).scalars().first()
    if not apex_check:
        apex = Company(
            name="Apex Robotics Inc",
            slug="apex-robotics",
            email="admin@apexrobotics.io",
            industry="Autonomous Mobile Robots (AMR)",
            website="https://apexrobotics.io",
            country="United States",
            timezone="America/Los_Angeles",
            status=CompanyStatus.ACTIVE.value,
            subscription_plan="ENTERPRISE"
        )
        db.add(apex)
        await db.flush()

        apex_admin = User(
            tenant_id=apex.id,
            email="recruiter@apexrobotics.io",
            hashed_password=get_password_hash("ApexSecurePass2026!"),
            full_name="Elena Rostova (Lead Recruiter)",
            role=UserRoleType.COMPANY_ADMIN.value,
            is_active=True
        )
        db.add(apex_admin)
        await db.flush()

        # Job 1
        job1 = Job(
            tenant_id=apex.id,
            title="Senior Autonomous Navigation Engineer (ROS2 / SLAM)",
            department="Perception & Autonomy",
            description="Lead the design and deployment of SLAM and Nav2 navigation stacks for heavy industrial AMRs.",
            location="San Francisco, CA (Hybrid)",
            employment_type="Full-time",
            experience_level="Senior",
            required_skills=["ROS2", "Nav2", "C++", "SLAM", "EKF", "LiDAR"],
            preferred_skills=["CUDA", "Docker", "Python"],
            salary_range="$165,000 - $210,000",
            status=JobStatus.PUBLISHED.value,
            created_by=apex_admin.id
        )
        db.add(job1)
        await db.flush()

        # Candidate 1
        cand1 = Candidate(
            tenant_id=apex.id,
            name="Dr. Marcus Vance",
            email="marcus.vance@stanford.alumni.edu",
            phone="+1 (415) 890-1234",
            skills=["ROS2", "Nav2", "C++", "Kalman Filtering", "Cartographer SLAM"],
            experience_years=6.5,
            education="Ph.D. in Robotics - Stanford University",
            status=CandidateStatus.SHORTLISTED.value
        )
        db.add(cand1)
        await db.flush()

        # Interview 1 (Completed with AI evaluation & Report)
        int1 = Interview(
            tenant_id=apex.id,
            job_id=job1.id,
            candidate_id=cand1.id,
            title="Senior Navigation Engineer AI Screening Round",
            interview_type=InterviewType.TECHNICAL.value,
            difficulty=DifficultyLevel.HARD.value,
            num_questions=3,
            time_limit_minutes=45,
            status=InterviewStatus.COMPLETED.value,
            started_at=datetime.now(timezone.utc) - timedelta(days=1),
            completed_at=datetime.now(timezone.utc) - timedelta(days=1, hours=-1)
        )
        db.add(int1)
        await db.flush()

        # Invitation 1
        inv1 = Invitation(
            tenant_id=apex.id,
            interview_id=int1.id,
            candidate_email=cand1.email,
            secure_token="apex-demo-token-marcus-vance-2026",
            is_used=True,
            expires_at=datetime.now(timezone.utc) + timedelta(days=6)
        )
        db.add(inv1)

        # Evaluation 1
        eval1 = Evaluation(
            tenant_id=apex.id,
            interview_id=int1.id,
            evaluation_status="COMPLETED",
            relevance_score=94.0,
            technical_score=91.5,
            communication_score=88.0,
            completeness_score=92.0,
            problem_solving_score=89.0,
            behavioral_score=86.0,
            overall_score=89.5,
            confidence_indicator=0.95,
            strengths=[
                "Exceptional depth in Extended Kalman Filter formulations and covariance tuning.",
                "Demonstrated rigorous understanding of ROS2 lifecycle nodes and deterministic timing.",
                "Articulate and structured communication under pressure."
            ],
            weaknesses=[
                "Could have elaborated more on fail-safe recovery behaviors when LiDAR returns high noise."
            ],
            missing_topics=["Innovation gating edge cases"],
            recommendation=RecommendationType.STRONG_HIRE.value,
            engine_version="internal-v1"
        )
        db.add(eval1)
        await db.flush()

        # Seed Question Evaluations for eval1
        existing_qs = (await db.execute(select(Question).order_by(Question.created_at))).scalars().all()
        q1_id = existing_qs[0].id if len(existing_qs) > 0 else "q1"
        q2_id = existing_qs[1].id if len(existing_qs) > 1 else "q2"
        q3_id = existing_qs[2].id if len(existing_qs) > 2 else "q3"

        qe1 = QuestionEvaluation(
            tenant_id=apex.id,
            evaluation_id=eval1.id,
            question_id=q1_id,
            score=93.5,
            relevance_score=95.0,
            technical_score=94.0,
            completeness_score=92.0,
            communication_score=90.0,
            problem_solving_score=92.0,
            behavioral_score=85.0,
            detected_topics=["Forward Kinematics", "Inverse Kinematics", "Jacobian Matrix", "Damped Least Squares"],
            missing_topics=["Null space projection optimization"],
            positive_indicators=["Identified core concept: 'Jacobian Matrix'", "Applied skill competency: 'Kinematics'"],
            negative_indicators=["Omitted minor topic: 'Null space projection'"],
            strengths=["Thorough derivation of DH parameters and singularity mitigation via Levenberg-Marquardt regularization."],
            weaknesses=["Could have discussed null space redundancy resolution in 7+ DOF arms."],
            explanation="Candidate demonstrated comprehensive mastery of kinematics and Jacobian inversion under singular configurations."
        )
        qe2 = QuestionEvaluation(
            tenant_id=apex.id,
            evaluation_id=eval1.id,
            question_id=q2_id,
            score=91.0,
            relevance_score=92.0,
            technical_score=93.0,
            completeness_score=90.0,
            communication_score=88.0,
            problem_solving_score=90.0,
            behavioral_score=82.0,
            detected_topics=["Extended Kalman Filter", "IMU", "Odometry", "Sensor Fusion", "robot_localization"],
            missing_topics=["Dynamic covariance adaptation"],
            positive_indicators=["Identified core concept: 'Extended Kalman Filter'", "Applied skill competency: 'ROS2'"],
            negative_indicators=["Omitted topic: 'Dynamic covariance adaptation'"],
            strengths=["Detailed architectural explanation of EKF sensor fusion and covariance propagation in ROS2."],
            weaknesses=["Did not elaborate on lidar slip detection."],
            explanation="Clear explanation of multi-sensor fusion balancing high-frequency IMU and low-frequency LiDAR drift correction."
        )
        qe3 = QuestionEvaluation(
            tenant_id=apex.id,
            evaluation_id=eval1.id,
            question_id=q3_id,
            score=84.0,
            relevance_score=90.0,
            technical_score=86.0,
            completeness_score=82.0,
            communication_score=85.0,
            problem_solving_score=84.0,
            behavioral_score=80.0,
            detected_topics=["Priority Inversion", "Priority Inheritance", "SCHED_FIFO", "mlockall"],
            missing_topics=["Memory pool pre-allocation"],
            positive_indicators=["Identified core concept: 'Priority Inheritance'", "Applied skill competency: 'Real-time C++'"],
            negative_indicators=["Omitted topic: 'Memory pool pre-allocation'"],
            strengths=["Solid knowledge of RT-PREEMPT kernel tuning and priority inheritance mutex protocols."],
            weaknesses=["Omitted heap allocation avoidance strategies in inner loops."],
            explanation="Accurate implementation details for deterministic real-time control loops with minimal jitter."
        )
        db.add_all([qe1, qe2, qe3])

        # Report 1
        rep1 = Report(
            tenant_id=apex.id,
            interview_id=int1.id,
            candidate_id=cand1.id,
            recruiter_decision="SHORTLISTED",
            recruiter_notes="Candidate demonstrated top 5% domain knowledge in SLAM and ROS2 lifecycle architectures. Highly recommended for executive panel round.",
            is_published_to_candidate=True
        )
        db.add(rep1)

        # Candidate 2 (Invited, pending)
        cand2 = Candidate(
            tenant_id=apex.id,
            name="Sarah Lin",
            email="sarah.lin@robotics.dev",
            phone="+1 (510) 678-9012",
            skills=["Python", "ROS2", "Control Loops", "PID"],
            experience_years=3.0,
            education="M.S. Robotics - CMU",
            status=CandidateStatus.INTERVIEW_SCHEDULED.value
        )
        db.add(cand2)
        await db.flush()

        int2 = Interview(
            tenant_id=apex.id,
            job_id=job1.id,
            candidate_id=cand2.id,
            title="Autonomy Engineer Technical Assessment",
            interview_type=InterviewType.TECHNICAL.value,
            difficulty=DifficultyLevel.MEDIUM.value,
            num_questions=3,
            time_limit_minutes=45,
            status=InterviewStatus.PENDING.value
        )
        db.add(int2)
        await db.flush()

        inv2 = Invitation(
            tenant_id=apex.id,
            interview_id=int2.id,
            candidate_email=cand2.email,
            secure_token="apex-interview-token-sarah-lin-789",
            is_used=False,
            expires_at=datetime.now(timezone.utc) + timedelta(days=5)
        )
        db.add(inv2)

    # 5. Seed Company 2: Boston Cybernetics
    boston_check = (await db.execute(select(Company).where(Company.slug == "boston-cybernetics"))).scalars().first()
    if not boston_check:
        boston = Company(
            name="Boston Cybernetics",
            slug="boston-cybernetics",
            email="admin@bostoncyber.com",
            industry="Humanoid Robotics & Quadruped Systems",
            website="https://bostoncyber.com",
            country="United States",
            timezone="America/New_York",
            status=CompanyStatus.ACTIVE.value,
            subscription_plan="ENTERPRISE"
        )
        db.add(boston)
        await db.flush()

        boston_admin = User(
            tenant_id=boston.id,
            email="recruiter@bostoncyber.com",
            hashed_password=get_password_hash("BostonSecurePass2026!"),
            full_name="David Chen (VP of Talent)",
            role=UserRoleType.COMPANY_ADMIN.value,
            is_active=True
        )
        db.add(boston_admin)
        await db.flush()

        job2 = Job(
            tenant_id=boston.id,
            title="Dynamic Bipedal Locomotion & Controls Engineer",
            department="Controls & Dynamics",
            description="Develop MPC and whole-body control algorithms for humanoid balance and agile locomotion.",
            location="Boston, MA (On-site)",
            employment_type="Full-time",
            experience_level="Lead / Principal",
            required_skills=["Model Predictive Control (MPC)", "Dynamics", "C++", "Whole Body Control", "Pinocchio"],
            preferred_skills=["MuJoCo", "Reinforcement Learning"],
            salary_range="$180,000 - $240,000",
            status=JobStatus.PUBLISHED.value,
            created_by=boston_admin.id
        )
        db.add(job2)
        await db.flush()

    await db.commit()
    logger.info("Database initialized and development seed data loaded successfully.")
