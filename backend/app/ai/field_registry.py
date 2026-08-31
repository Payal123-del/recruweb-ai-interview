from typing import Dict, Any, List, Optional


class UniversalFieldRegistry:
    """
    Centralized, extensible metadata registry for all professional career fields,
    their associated roles, core skills, adaptive interview types, and scoring rubrics.
    Supports dynamic additions without code modification.
    """

    DEFAULT_FIELDS: Dict[str, Dict[str, Any]] = {
        "Data Science": {
            "category": "Data & AI",
            "icon": "Database",
            "description": "Statistical modeling, predictive analytics, data manipulation, and actionable business insights.",
            "roles": ["Data Scientist", "Lead Data Scientist", "Data Analyst", "Machine Learning Scientist", "BI Analyst"],
            "skills": ["Python", "SQL", "Statistics", "Machine Learning", "Pandas", "Scikit-Learn", "Data Visualization", "Hypothesis Testing", "A/B Testing", "R"],
            "interview_types": ["Technical", "Statistics & Modeling", "SQL & Querying", "Case Study", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15},
            "competencies": ["Statistical Rigor", "Data Manipulation", "Model Validation", "Business Acumen", "Communication"]
        },
        "Software Engineering": {
            "category": "Engineering & Tech",
            "icon": "Code2",
            "description": "Full-stack development, software architecture, distributed systems, algorithms, and clean code practices.",
            "roles": ["Software Engineer", "Frontend Developer", "Backend Developer", "Full Stack Developer", "System Architect", "Tech Lead"],
            "skills": ["Data Structures", "Algorithms", "System Design", "Python", "JavaScript", "TypeScript", "C++", "Java", "REST APIs", "Microservices", "Docker", "SQL"],
            "interview_types": ["Coding & DSA", "System Design", "Technical Architecture", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Algorithmic Problem Solving", "System Architecture", "Code Quality & Patterns", "Debugging & Trade-offs", "Collaboration"]
        },
        "Machine Learning": {
            "category": "Data & AI",
            "icon": "Brain",
            "description": "Deep learning, neural networks, computer vision, NLP, MLOps, and model deployment pipelines.",
            "roles": ["ML Engineer", "Deep Learning Engineer", "NLP Engineer", "Computer Vision Engineer", "MLOps Engineer"],
            "skills": ["PyTorch", "TensorFlow", "Deep Learning", "Transformers", "Model Optimization", "Feature Engineering", "MLOps", "Python", "CUDA", "Model Evaluation"],
            "interview_types": ["ML Theory", "Deep Learning Architecture", "System Design for ML", "Case Study", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Model Architecture", "Mathematical Understanding", "Production Scalability", "Performance Tuning", "Evaluation Discipline"]
        },
        "Robotics": {
            "category": "Engineering & Tech",
            "icon": "Bot",
            "description": "Autonomous navigation, kinematic controls, sensor fusion, SLAM, ROS2, and embedded hardware integration.",
            "roles": ["Robotics Software Engineer", "SLAM & Navigation Specialist", "Controls Engineer", "Robotics Perception Engineer", "Embedded Robotics Developer"],
            "skills": ["ROS2", "C++", "Kinematics", "SLAM", "Kalman Filtering", "Control Systems", "Motion Planning", "Computer Vision", "Real-Time OS", "Simulation"],
            "interview_types": ["Technical Controls & Kinematics", "SLAM & Navigation", "Real-Time Systems", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.25, "communication": 0.15, "behavioral": 0.15},
            "competencies": ["Kinematic & Dynamic Analysis", "State Estimation & SLAM", "Embedded Determinism", "System Safety", "Problem Solving"]
        },
        "Cybersecurity": {
            "category": "Security & Infra",
            "icon": "Shield",
            "description": "Threat modeling, penetration testing, network security, incident response, SIEM, and vulnerability analysis.",
            "roles": ["Security Analyst", "Penetration Tester", "SOC Engineer", "Application Security Specialist", "Chief Information Security Officer (CISO)"],
            "skills": ["Threat Modeling", "Penetration Testing", "Network Protocols", "SIEM", "Incident Response", "Cryptography", "Vulnerability Assessment", "OWASP Top 10", "Firewalls"],
            "interview_types": ["Security Scenario", "Threat Modeling", "Incident Response Walkthrough", "Ethical Hacking", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.35, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Threat Surface Identification", "Vulnerability Remediation", "Security Incident Handling", "Risk Assessment", "Clarity Under Pressure"]
        },
        "Cloud Computing & DevOps": {
            "category": "Security & Infra",
            "icon": "Cloud",
            "description": "Infrastructure as Code, Kubernetes orchestration, CI/CD automation, cloud architecture, and observability.",
            "roles": ["DevOps Engineer", "Cloud Architect", "Site Reliability Engineer (SRE)", "Platform Engineer"],
            "skills": ["AWS", "Kubernetes", "Docker", "Terraform", "CI/CD", "Linux", "Prometheus", "Grafana", "Ansible", "Helm", "Microservices"],
            "interview_types": ["Infrastructure Design", "CI/CD Pipelines", "Incident Debugging / SRE", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Infrastructure Architecture", "Automation & Reliability", "Troubleshooting & Postmortems", "Scalability Optimization", "Communication"]
        },
        "Mechanical Engineering": {
            "category": "Core Engineering",
            "icon": "Wrench",
            "description": "CAD design, thermodynamics, structural finite element analysis (FEA), fluid dynamics, and manufacturing.",
            "roles": ["Mechanical Design Engineer", "Structural Analyst", "Thermal Engineer", "Manufacturing Engineer", "Automotive Systems Engineer"],
            "skills": ["SolidWorks", "CAD", "FEA Analysis", "Thermodynamics", "Fluid Mechanics", "Material Science", "GD&T", "DFM / DFA", "Heat Transfer"],
            "interview_types": ["Core Mechanical Design", "Thermodynamics & Fluids", "Manufacturing (DFM)", "Case Study", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["CAD & Geometric Dimensioning", "Stress & Thermal Analysis", "Manufacturing Feasibility", "Failure Mode Analysis", "Technical Precision"]
        },
        "Finance": {
            "category": "Business & Finance",
            "icon": "TrendingUp",
            "description": "Financial modeling, valuation analysis, corporate finance, DCF analysis, budgeting, and risk mitigation.",
            "roles": ["Financial Analyst", "Investment Banking Analyst", "Corporate Finance Specialist", "Portfolio Manager", "Risk Analyst"],
            "skills": ["Financial Modeling", "Valuation (DCF/Comps)", "Excel Modeling", "Accounting Principles", "Corporate Finance", "Portfolio Risk", "Budgeting", "Cash Flow Analysis"],
            "interview_types": ["Financial Valuation", "Corporate Finance Modeling", "Quantitative Analysis", "Case Study", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Valuation & Modeling Rigor", "Accounting & Statement Analysis", "Market & Risk Perspective", "Quantitative Reasoning", "Executive Presentation"]
        },
        "Marketing": {
            "category": "Business & Marketing",
            "icon": "Megaphone",
            "description": "Digital growth marketing, brand strategy, conversion rate optimization (CRO), SEO/SEM, and performance analytics.",
            "roles": ["Digital Marketing Manager", "Growth Marketer", "Brand Strategist", "Content Marketing Lead", "Product Marketing Manager (PMM)"],
            "skills": ["Growth Strategy", "Conversion Rate Optimization", "SEO / SEM", "Google Analytics", "Paid Acquisition (PPC)", "Customer Acquisition Cost (CAC)", "Email Marketing", "Brand Positioning"],
            "interview_types": ["Marketing Campaign Strategy", "Growth Analytics & ROI", "Brand Positioning Case", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.30, "communication": 0.25, "behavioral": 0.10},
            "competencies": ["Campaign Strategy & Vision", "Analytics & Data-Driven CRO", "Creative Value Proposition", "Audience Empathy", "Articulate Pitching"]
        },
        "Human Resources": {
            "category": "Human Resources",
            "icon": "Users",
            "description": "Talent acquisition, employee relations, HR policy compliance, organizational design, and performance management.",
            "roles": ["HR Generalist", "Talent Acquisition Lead", "HR Business Partner (HRBP)", "Compensation & Benefits Specialist", "People Operations Director"],
            "skills": ["Talent Acquisition", "Employee Relations", "HR Policies & Labor Law", "Performance Appraisals", "Conflict Resolution", "Diversity & Inclusion", "Onboarding", "Retention Strategy"],
            "interview_types": ["HR Policy & Labor Law", "Conflict Resolution & Relations", "Talent Strategy", "Situational Judgment", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.30, "problem_solving": 0.30, "communication": 0.25, "behavioral": 0.15},
            "competencies": ["Policy & Legal Compliance", "Conflict Mediation", "Empathy & Active Listening", "Strategic People Operations", "Ethical Judgment"]
        },
        "Product Management": {
            "category": "Business & Product",
            "icon": "Layers",
            "description": "Product roadmap prioritization, user journey definition, KPI tracking, feature trade-offs, and stakeholder alignment.",
            "roles": ["Associate Product Manager", "Technical Product Manager", "Senior Product Manager", "Group Product Manager", "Head of Product"],
            "skills": ["Product Roadmap", "User Empathy & Wireframing", "PRD Writing", "KPI & OKR Definition", "A/B Testing", "Agile & Scrum", "Prioritization Frameworks (RICE)", "Market Research"],
            "interview_types": ["Product Sense & Design", "Execution & Metrics", "Technical Trade-offs", "Leadership & Influence", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.30, "problem_solving": 0.35, "communication": 0.20, "behavioral": 0.15},
            "competencies": ["Customer Centricity & Product Sense", "Metric & Data-Driven Thinking", "Prioritization & Trade-offs", "Cross-Functional Influence", "Strategic Clarity"]
        },
        "Civil Engineering": {
            "category": "Core Engineering",
            "icon": "Building",
            "description": "Structural analysis, geotechnical evaluation, concrete/steel design, transportation engineering, and project scheduling.",
            "roles": ["Structural Engineer", "Civil Site Engineer", "Transportation Planner", "Geotechnical Engineer", "Construction Project Manager"],
            "skills": ["AutoCAD", "ETABS / SAP2000", "Structural Mechanics", "Concrete & Steel Design", "Soil Mechanics", "Project Estimation", "Building Codes", "Hydrology"],
            "interview_types": ["Structural Calculations", "Geotechnical & Site Planning", "Project Management & Codes", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Structural Rigor", "Code Compliance & Safety", "Site Feasibility", "Material Understanding", "Problem Solving"]
        },
        "Electrical Engineering": {
            "category": "Core Engineering",
            "icon": "Zap",
            "description": "Circuit analysis, power systems, PCB layout, signal processing, microcontroller firmware, and embedded hardware.",
            "roles": ["Electrical Design Engineer", "Power Systems Engineer", "PCB Layout Specialist", "Embedded Firmware Developer", "FPGA Engineer"],
            "skills": ["Circuit Simulation (SPICE)", "PCB Design (Altium/KiCad)", "Power Electronics", "Signal Processing", "Microcontrollers", "Verilog/VHDL", "Oscilloscopes & Lab Testing", "EMC / EMI Compliance"],
            "interview_types": ["Circuit Analysis", "Power & Electronics Design", "Signal & Embedded Hardware", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Circuit Fundamentals", "PCB & Power Electronics", "Debugging & Signal Integrity", "Safety & Standards", "Analytical Thinking"]
        },
        "Healthcare & Medicine": {
            "category": "Healthcare & Life Sciences",
            "icon": "HeartPulse",
            "description": "Clinical diagnosis, medical protocols, healthcare operations, patient triage, and pharmacology basics.",
            "roles": ["Clinical Research Associate", "Healthcare Administrator", "Medical Science Liaison", "Biomedical Specialist", "Nursing Supervisor"],
            "skills": ["Clinical Protocols", "Patient Assessment", "HIPAA Compliance", "Medical Terminology", "Pharmacology", "Healthcare Informatics", "Diagnostic Workflow", "Emergency Triage"],
            "interview_types": ["Clinical Scenarios", "Medical Ethics & Protocols", "Healthcare Operations", "Situational Judgment", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Diagnostic Precision", "Ethics & Patient Safety", "Regulatory Compliance", "Crisis Management", "Empathetic Communication"]
        },
        "Legal & Compliance": {
            "category": "Legal & Corporate",
            "icon": "Scale",
            "description": "Contract negotiation, regulatory compliance, intellectual property, corporate governance, and risk mitigation.",
            "roles": ["Corporate Counsel", "Legal Analyst", "Compliance Officer", "IP / Patent Specialist", "Contract Manager"],
            "skills": ["Contract Law", "Regulatory Compliance", "Intellectual Property", "Litigation Risk", "Corporate Governance", "Legal Research", "Due Diligence", "Statutory Interpretation"],
            "interview_types": ["Contract Analysis", "Regulatory Compliance Scenarios", "Statutory Interpretation", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Legal Precedent & Analysis", "Risk Assessment & Mitigation", "Contractual Drafting", "Ethical Integrity", "Persuasive Argumentation"]
        },
        "Biotechnology & Life Sciences": {
            "category": "Healthcare & Life Sciences",
            "icon": "Dna",
            "description": "Bioinformatics, molecular biology, genomics, fermentation, assay design, and pharmaceutical chemistry.",
            "roles": ["Bioinformatics Scientist", "Molecular Biologist", "Assay Development Scientist", "Bioprocess Engineer", "Genomics Analyst"],
            "skills": ["PCR & Gel Electrophoresis", "Bioinformatics (BLAST/Biopython)", "Genomic Sequencing", "Cell Culture", "Assay Validation", "CRISPR / Gene Editing", "Biostatistics"],
            "interview_types": ["Molecular Protocols", "Bioinformatics & Genomic Analysis", "Assay Design Case", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Experimental Design", "Bioinformatics Computation", "Data Validation & Controls", "Scientific Communication", "Quality Assurance"]
        },
        "Consulting & Business Strategy": {
            "category": "Business & Strategy",
            "icon": "Briefcase",
            "description": "Market entry analysis, corporate restructuring, profitability diagnosis, M&A due diligence, and executive presentations.",
            "roles": ["Management Consultant", "Strategy Analyst", "Operations Consultant", "Senior Associate", "Engagement Manager"],
            "skills": ["Case Interview Frameworks", "Market Sizing & Estimation", "Profitability Diagnosis", "Financial Analysis", "Executive Communication", "Data Synthesis", "Slide Structuring"],
            "interview_types": ["Business Case Study", "Market Sizing & Estimation", "Strategy & Structuring", "Leadership & Communication", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.30, "problem_solving": 0.40, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Structured Problem Solving", "Analytical Rigor", "Hypothesis-Driven Synthesis", "Client Communication", "Composure & Adaptability"]
        },
        "UI/UX & Product Design": {
            "category": "Design & Creative",
            "icon": "Palette",
            "description": "User research, wireframing, design systems, usability testing, Figma prototyping, and user journey mapping.",
            "roles": ["UI/UX Designer", "Product Designer", "User Researcher", "Design Systems Lead"],
            "skills": ["Figma", "Design Systems", "User Research", "Wireframing", "Prototyping", "Usability Testing", "Information Architecture"],
            "interview_types": ["Design Portfolio Walkthrough", "Product Sense & Wireframing", "Critique & Systems Design", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.35, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["User Centricity", "Design Craft & Visual Hierarchy", "Systems Thinking", "Research Translation", "Cross-Functional Collaboration"]
        },
        "QA & Test Automation Engineering": {
            "category": "Engineering & Tech",
            "icon": "CheckSquare",
            "description": "Test automation frameworks, performance testing, CI/CD test gates, API testing, and bug lifecycle triage.",
            "roles": ["QA Automation Engineer", "SDET", "Performance Test Engineer", "Manual QA Lead"],
            "skills": ["Selenium", "Cypress", "Playwright", "Postman", "JUnit / PyTest", "CI/CD Gates", "Load Testing (JMeter)", "Bug Tracking"],
            "interview_types": ["Automation Framework Design", "Test Strategy & Edge Cases", "API & Performance Testing", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Test Architecture", "Edge-Case Detection", "Automation Efficiency", "Root-Cause Analysis", "Quality Advocacy"]
        },
        "Mobile App Development": {
            "category": "Engineering & Tech",
            "icon": "Smartphone",
            "description": "Native and cross-platform mobile apps for iOS and Android, offline caching, push notifications, and store deployment.",
            "roles": ["iOS Engineer", "Android Engineer", "React Native Developer", "Flutter Developer"],
            "skills": ["Swift / SwiftUI", "Kotlin / Jetpack Compose", "React Native", "Flutter", "App Store Guidelines", "Mobile Architecture (MVVM/Clean)", "Local DB (Room/CoreData)"],
            "interview_types": ["Mobile Architecture", "UI & Memory Management", "Platform Nuances", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Mobile System Design", "Memory & Performance", "UI Responsiveness", "Platform Lifecycle", "Clean Architecture"]
        },
        "Aerospace & Aeronautical Engineering": {
            "category": "Core Engineering",
            "icon": "Plane",
            "description": "Aerodynamics, propulsion systems, flight mechanics, orbital dynamics, structural composites, and avionics.",
            "roles": ["Aerospace Engineer", "Aerodynamics Specialist", "Propulsion Engineer", "Avionics Systems Engineer", "Flight Test Engineer"],
            "skills": ["Aerodynamics (CFD)", "Propulsion Systems", "Orbital Mechanics", "Flight Dynamics & Control", "Composite Structures", "MATLAB / Simulink"],
            "interview_types": ["Aerodynamic Analysis", "Propulsion & Thermal Trade-offs", "Flight Controls Case", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Flight Physics & Mechanics", "Thermodynamics & Propulsion", "Safety & Redundancy", "Analytical Precision", "Problem Solving"]
        },
        "Chemical Engineering": {
            "category": "Core Engineering",
            "icon": "FlaskConical",
            "description": "Reaction kinetics, process simulation, mass and heat transfer, separation processes, and plant safety.",
            "roles": ["Process Engineer", "Chemical Plant Manager", "R&D Chemist", "Refinery Operations Specialist"],
            "skills": ["Aspen Plus / HYSYS", "Reaction Kinetics", "Mass & Heat Transfer", "Distillation & Separation", "P&ID Diagrams", "Process Safety Management (HAZOP)"],
            "interview_types": ["Process Flow Design", "Thermodynamics & Kinetics", "Safety & Plant Operations", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Thermodynamic Rigor", "Process Optimization", "Safety Compliance", "Mass Balances", "Analytical Reasoning"]
        },
        "Supply Chain & Operations": {
            "category": "Business & Operations",
            "icon": "Truck",
            "description": "Inventory optimization, demand forecasting, logistics routing, procurement strategy, and warehouse automation.",
            "roles": ["Supply Chain Manager", "Logistics Coordinator", "Procurement Specialist", "Demand Planner", "Operations Lead"],
            "skills": ["Demand Forecasting", "Inventory Management (EOQ/Safety Stock)", "ERP Systems (SAP)", "Procurement Negotiation", "Warehouse Management (WMS)", "Lean / Six Sigma"],
            "interview_types": ["Supply Chain Optimization Case", "Procurement & Negotiation", "Logistics & Bottleneck Triage", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.35, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Cost & Routing Optimization", "Risk Mitigation & Buffers", "Analytical Forecasting", "Supplier Negotiation", "Execution Speed"]
        },
        "Sales Engineering & Tech Solutions": {
            "category": "Business & Sales",
            "icon": "Presentation",
            "description": "B2B SaaS product demos, RFP responses, architectural scoping, technical objection handling, and enterprise proofs of concept.",
            "roles": ["Solutions Architect", "Sales Engineer", "Technical Account Manager", "Pre-Sales Consultant"],
            "skills": ["Technical Discovery", "Product Demos", "RFP Scoping", "Cloud Architecture", "Objection Handling", "Executive Stakeholder Engagement"],
            "interview_types": ["Technical Discovery Roleplay", "Product Demo Presentation", "Architectural Scoping", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.30, "communication": 0.25, "behavioral": 0.10},
            "competencies": ["Value Proposition Delivery", "Technical Discovery Acumen", "Active Listening", "Architectural Feasibility", "Trust Building"]
        },
        "Accounting & Taxation": {
            "category": "Business & Finance",
            "icon": "Calculator",
            "description": "General ledger, GAAP/IFRS standards, corporate taxation, internal controls, auditing, and financial reporting.",
            "roles": ["Certified Public Accountant (CPA)", "Senior Auditor", "Tax Consultant", "Staff Accountant", "Controller"],
            "skills": ["GAAP / IFRS", "Tax Compliance", "Financial Auditing", "General Ledger", "Reconciliations", "ERP Accounting (QuickBooks/NetSuite)"],
            "interview_types": ["Accounting Standards Case", "Audit Risk Walkthrough", "Tax Planning & Compliance", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Statutory GAAP Precision", "Internal Controls & Audit", "Tax Optimization", "Reconciliation Accuracy", "Ethical Integrity"]
        },
        "Environmental Science & Sustainability": {
            "category": "Science & Environment",
            "icon": "Leaf",
            "description": "Carbon footprint accounting, ESG reporting, renewable energy systems, environmental impact assessments (EIA).",
            "roles": ["Sustainability Consultant", "Environmental Analyst", "ESG Reporting Specialist", "Renewable Energy Project Lead"],
            "skills": ["Carbon Accounting (GHG Protocol)", "ESG Metrics", "Environmental Impact Assessment", "Lifecycle Analysis (LCA)", "Renewable Systems (Solar/Wind)"],
            "interview_types": ["ESG Frameworks", "Carbon Reduction Strategy", "Environmental Compliance", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.35, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Carbon Methodology", "Regulatory Standards", "Data Integrity in ESG", "Impact Assessment", "Stakeholder Advocacy"]
        },
        "Journalism & Content Strategy": {
            "category": "Media & Communications",
            "icon": "Newspaper",
            "description": "Investigative reporting, multi-platform storytelling, editorial guidelines, copy editing, SEO content planning.",
            "roles": ["Investigative Journalist", "Content Strategist", "Editorial Lead", "Technical Writer", "Communications Specialist"],
            "skills": ["Fact-Checking & Sourcing", "Editorial Copywriting", "Content Strategy", "SEO Content Architecture", "Interview Techniques", "Multimedia Storytelling"],
            "interview_types": ["Editorial Writing Case", "Investigative Sourcing Scenario", "Content Strategy & SEO", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.30, "problem_solving": 0.30, "communication": 0.30, "behavioral": 0.10},
            "competencies": ["Narrative Clarity & Framing", "Fact Rigor & Source Verification", "Audience Engagement", "Ethical Journalism", "Concise Delivery"]
        },
        "Psychology & Behavioral Science": {
            "category": "Social Sciences",
            "icon": "HeartHandshake",
            "description": "Cognitive psychology, clinical counseling, psychometric assessment, behavioral economics, and research methodology.",
            "roles": ["Behavioral Researcher", "Organizational Psychologist", "Clinical Counselor", "UX Researcher (Behavioral)"],
            "skills": ["Psychometric Testing", "Cognitive Behavioral Frameworks", "Experimental Design", "SPSS / R Analysis", "Qualitative Coding", "Ethical Human Subjects"],
            "interview_types": ["Research Methodology & Ethics", "Behavioral Diagnosis & Case", "Psychometric Measurement", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.35, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Empirical Research Rigor", "Active Empathy & Listening", "Behavioral Diagnostics", "Ethical Responsibility", "Analytical Synthesis"]
        },
        "Artificial Intelligence Research": {
            "category": "Data & AI",
            "icon": "Cpu",
            "description": "Foundation models, reinforcement learning, transformer architectures, alignment, and novel neural networks.",
            "roles": ["AI Research Scientist", "Postdoctoral AI Fellow", "Algorithm Scientist", "Applied AI Lead"],
            "skills": ["PyTorch", "Reinforcement Learning (PPO/DPO)", "Diffusion Models", "Transformers", "Mathematical Proofs", "LaTeX / Papers", "CUDA Optimization"],
            "interview_types": ["AI Theory & Proofs", "Model Architecture Design", "Empirical Paper Defense", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.50, "problem_solving": 0.30, "communication": 0.10, "behavioral": 0.10},
            "competencies": ["Theoretical Depth", "Empirical Rigor", "Mathematical Formulation", "Scientific Communication", "Novel Synthesis"]
        },
        "Investment Banking & Private Equity": {
            "category": "Business & Finance",
            "icon": "Coins",
            "description": "Leveraged buyouts (LBO), merger & acquisition (M&A) advisory, debt restructuring, and pitchbook presentations.",
            "roles": ["M&A Analyst", "Private Equity Associate", "Investment Banking Associate", "Deal Lead"],
            "skills": ["LBO Modeling", "M&A Accretion / Dilution", "DCF Modeling", "Due Diligence", "Pitchbook Creation", "Debt Capital Markets"],
            "interview_types": ["LBO Modeling Test", "M&A Case Analysis", "Valuation Defense", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["LBO & Valuation Precision", "Deal Structure Feasibility", "Stress Testing Models", "Executive Gravitas", "Quantitative Stamina"]
        },
        "Biomedical Engineering": {
            "category": "Healthcare & Life Sciences",
            "icon": "Activity",
            "description": "Medical device design, biocompatible materials, physiological signal processing, and FDA 510(k) regulatory submissions.",
            "roles": ["Biomedical Device Engineer", "Clinical Systems Specialist", "Bio-Instrumentation Lead", "Regulatory Affairs Specialist"],
            "skills": ["Medical Device ISO 13485", "FDA 510(k) Submissions", "Biosensors & EMG/ECG", "Biocompatible Polymers", "Biomechanics (OpenSim)", "LabVIEW"],
            "interview_types": ["Device Design & Safety Risk (FMEA)", "Regulatory Standards Walkthrough", "Signal Processing Case", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Device Safety & Risk (FMEA)", "Regulatory Protocol Precision", "Biocompatibility & Materials", "Signal Integrity", "Analytical Problem Solving"]
        },
        "Digital Media & Video Production": {
            "category": "Media & Creative",
            "icon": "Video",
            "description": "Cinematography, audio engineering, post-production color grading, storytelling, and digital broadcast pipelines.",
            "roles": ["Creative Director", "Video Producer", "Motion Graphics Designer", "Audio Engineer"],
            "skills": ["Premiere Pro", "After Effects", "DaVinci Resolve", "Color Grading", "Audio Mixing (Pro Tools)", "Lighting & Composition", "Storyboarding"],
            "interview_types": ["Portfolio Review", "Production Workflow Case", "Creative Direction Challenge", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.30, "communication": 0.25, "behavioral": 0.10},
            "competencies": ["Visual Storytelling", "Post-Production Craft", "Creative Direction", "Timeline Management", "Client Collaboration"]
        },
        "Instructional Design & EdTech": {
            "category": "Education & Learning",
            "icon": "GraduationCap",
            "description": "Pedagogical design, curriculum frameworks, learning management systems (LMS), and gamified learning evaluation.",
            "roles": ["Instructional Designer", "Learning Experience Designer (LXD)", "Curriculum Developer", "Corporate Training Lead"],
            "skills": ["ADDIE Model", "Bloom's Taxonomy", "Articulate Storyline", "LMS Administration", "Curriculum Mapping", "Formative & Summative Assessment"],
            "interview_types": ["Curriculum Design Case", "Pedagogical Frameworks", "Assessment Strategy", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.35, "problem_solving": 0.35, "communication": 0.20, "behavioral": 0.10},
            "competencies": ["Pedagogical Theory & ADDIE", "Curriculum Scaffolding", "Learner Empathy", "Measurable Learning Outcomes", "Presentation Clarity"]
        },
        "Architecture & Spatial Design": {
            "category": "Core Engineering",
            "icon": "Compass",
            "description": "Architectural drafting, building information modeling (BIM), urban zoning codes, parametric modeling, and spatial aesthetics.",
            "roles": ["Project Architect", "BIM Coordinator", "Urban Designer", "Interior Architect", "Architectural Drafter"],
            "skills": ["Revit / BIM", "Rhino / Grasshopper", "AutoCAD", "Building Codes & Zoning", "Sustainable Design (LEED)", "Parametric Modeling", "Rendering (V-Ray/Lumion)"],
            "interview_types": ["Portfolio Critique", "BIM Modeling & Coordination Case", "Zoning & Environmental Analysis", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.45, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.10},
            "competencies": ["Spatial Hierarchy & Aesthetics", "BIM & Constructability", "Zoning & Environmental Compliance", "Design Communication", "Problem Solving"]
        }


    }

    @classmethod
    def get_all_fields(cls) -> List[Dict[str, Any]]:
        """Returns structured list of all registered professional fields."""
        fields_list = []
        for name, data in cls.DEFAULT_FIELDS.items():
            fields_list.append({
                "name": name,
                "slug": name.lower().replace(" & ", "-").replace(" ", "-"),
                "category": data.get("category", "General"),
                "icon": data.get("icon", "Briefcase"),
                "description": data.get("description", ""),
                "roles": data.get("roles", []),
                "skills": data.get("skills", []),
                "interview_types": data.get("interview_types", ["Technical", "Behavioral", "Mixed"]),
                "scoring_weights": data.get("scoring_weights", {"technical": 0.4, "problem_solving": 0.3, "communication": 0.15, "behavioral": 0.15}),
                "competencies": data.get("competencies", ["Technical Competency", "Problem Solving", "Communication", "Behavioral"])
            })
        return fields_list

    @classmethod
    def get_field_data(cls, field_name: str) -> Optional[Dict[str, Any]]:
        """Finds field data by name or slug (case-insensitive fuzzy match)."""
        clean_target = field_name.strip().lower()
        for name, data in cls.DEFAULT_FIELDS.items():
            if name.lower() == clean_target or name.lower().replace(" ", "-") == clean_target:
                return {
                    "name": name,
                    "slug": name.lower().replace(" & ", "-").replace(" ", "-"),
                    **data
                }
        return None

    @classmethod
    def register_custom_field(cls, field_name: str, category: str = "Custom Field", description: str = "", roles: List[str] = None, skills: List[str] = None) -> Dict[str, Any]:
        """Dynamically adds a custom field so candidates can prepare for any niche or emerging domain."""
        clean_name = field_name.strip()
        custom_data = {
            "category": category or "Emerging Field",
            "icon": "Sparkles",
            "description": description or f"Universal professional assessment for {clean_name}.",
            "roles": roles or [f"{clean_name} Specialist", f"{clean_name} Consultant", f"Senior {clean_name} Engineer"],
            "skills": skills or [clean_name, "Analysis", "Domain Knowledge", "Problem Solving", "Communication"],
            "interview_types": ["Technical", "Domain Specific", "Problem Solving", "Behavioral", "Mixed"],
            "scoring_weights": {"technical": 0.40, "problem_solving": 0.30, "communication": 0.15, "behavioral": 0.15},
            "competencies": ["Domain Knowledge", "Problem Solving", "Communication", "Role Readiness"]
        }
        cls.DEFAULT_FIELDS[clean_name] = custom_data
        return {"name": clean_name, **custom_data}
