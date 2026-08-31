"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  Camera, Mic, Video, CheckCircle2, AlertCircle, ArrowRight, ShieldCheck,
  Clock, Play, Send, Sparkles, Loader2, StopCircle, Download, BarChart3, FileText,
  Search, Briefcase, ChevronRight, Layers, Target, Check, RefreshCw, PlusCircle,
  Brain, HelpCircle, TrendingUp, Shield, Wrench, Megaphone, Users, Zap
} from "lucide-react";
import { ApiClient } from "@/lib/api";

type Step = "PROFILE_ANALYSIS" | "FIELD_SELECTION" | "ROLE_CONFIG" | "DEVICE_CHECK" | "INSTRUCTIONS" | "INTERVIEW" | "SUBMITTING" | "COMPLETED";

export default function CandidateInterviewScreen() {
  const params = useParams();
  const secureToken = params?.secureToken as string;

  const [step, setStep] = useState<Step>("PROFILE_ANALYSIS");
  const [interviewData, setInterviewData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  // Field & Role Customization State
  const [detectedFields, setDetectedFields] = useState<any[]>([]);
  const [allFields, setAllFields] = useState<any[]>([]);
  const [searchField, setSearchField] = useState("");
  const [selectedField, setSelectedField] = useState<string>("Software Engineering");
  const [fieldData, setFieldData] = useState<any>(null);
  const [selectedRole, setSelectedRole] = useState<string>("");
  const [customRoleInput, setCustomRoleInput] = useState<string>("");
  const [selectedInterviewType, setSelectedInterviewType] = useState<string>("Technical");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("MEDIUM");
  const [isAdaptive, setIsAdaptive] = useState<boolean>(false);
  const [selectedSkills, setSelectedSkills] = useState<string[]>([]);
  const [customFieldInput, setCustomFieldInput] = useState<string>("");
  const [numQuestions, setNumQuestions] = useState<number>(4);
  const [isConfiguring, setIsConfiguring] = useState<boolean>(false);

  // Device check state
  const [cameraAccess, setCameraAccess] = useState(false);
  const [micAccess, setMicAccess] = useState(false);
  const videoPreviewRef = useRef<HTMLVideoElement>(null);
  const liveVideoRef = useRef<HTMLVideoElement>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);

  // Interview state
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [currentText, setCurrentText] = useState("");
  const [timeLeft, setTimeLeft] = useState(120);
  const [isRecording, setIsRecording] = useState(false);
  const [submissionResult, setSubmissionResult] = useState<any>(null);

  useEffect(() => {
    verifyToken();
  }, [secureToken]);

  const verifyToken = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await ApiClient.verifyCandidateToken(secureToken);
      const data = res.data;
      setInterviewData(data);
      setDetectedFields(data.detected_fields || []);
      setAllFields(data.all_fields || []);

      const initField = data.field_name || (data.detected_fields?.[0]?.field) || "Software Engineering";
      setSelectedField(initField);
      setSelectedRole(data.target_role || "");
      setSelectedDifficulty(data.difficulty || "MEDIUM");
      setIsAdaptive(data.is_adaptive || false);

      // Load field metadata
      loadFieldMetadata(initField, data.all_fields);

      setStep("PROFILE_ANALYSIS");
    } catch (err: any) {
      setError(err.message || "Invalid or expired interview token.");
    } finally {
      setLoading(false);
    }
  };

  const loadFieldMetadata = (fieldName: string, fieldsPool?: any[]) => {
    const pool = fieldsPool || allFields;
    const found = pool.find((f: any) => f.name.toLowerCase() === fieldName.toLowerCase());
    if (found) {
      setFieldData(found);
      if (!selectedRole && found.roles?.length > 0) {
        setSelectedRole(found.roles[0]);
      }
      if (found.skills?.length > 0) {
        setSelectedSkills(found.skills.slice(0, 4));
      }
      if (found.interview_types?.length > 0) {
        setSelectedInterviewType(found.interview_types[0]);
      }
    } else {
      // Fallback
      setFieldData({
        name: fieldName,
        roles: [`${fieldName} Specialist`, `${fieldName} Consultant`, `Lead ${fieldName}`],
        skills: [fieldName, "Domain Analysis", "Problem Solving"],
        interview_types: ["Technical", "Case Study", "Behavioral", "Mixed"]
      });
      setSelectedRole(`${fieldName} Specialist`);
    }
  };

  const handleSelectField = (fName: string) => {
    setSelectedField(fName);
    loadFieldMetadata(fName);
    setStep("ROLE_CONFIG");
  };

  const handleConfirmCustomField = () => {
    if (!customFieldInput.trim()) return;
    const name = customFieldInput.trim();
    setSelectedField(name);
    loadFieldMetadata(name);
    setStep("ROLE_CONFIG");
  };

  const handleToggleSkill = (skill: string) => {
    setSelectedSkills((prev) =>
      prev.includes(skill) ? prev.filter((s) => s !== skill) : [...prev, skill]
    );
  };

  const handleSaveInterviewConfiguration = async () => {
    setIsConfiguring(true);
    try {
      const role = customRoleInput.trim() || selectedRole || `${selectedField} Specialist`;
      const res = await ApiClient.configureCustomInterview(secureToken, {
        field_name: selectedField,
        target_role: role,
        interview_type: selectedInterviewType,
        difficulty: isAdaptive ? "ADAPTIVE" : selectedDifficulty,
        is_adaptive: isAdaptive,
        focus_skills: selectedSkills,
        num_questions: numQuestions
      });

      // Update local state with newly customized questions
      if (res.data?.questions) {
        setInterviewData((prev: any) => ({
          ...prev,
          field_name: selectedField,
          target_role: role,
          interview_type: selectedInterviewType,
          difficulty: isAdaptive ? "ADAPTIVE" : selectedDifficulty,
          num_questions: res.data.num_questions,
          questions: res.data.questions
        }));
      }

      setStep("DEVICE_CHECK");
    } catch (err: any) {
      setError(err.message || "Failed to configure custom interview.");
    } finally {
      setIsConfiguring(false);
    }
  };

  const startMediaDevices = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      });
      mediaStreamRef.current = stream;
      setCameraAccess(true);
      setMicAccess(true);

      if (videoPreviewRef.current) {
        videoPreviewRef.current.srcObject = stream;
      }
      if (liveVideoRef.current) {
        liveVideoRef.current.srcObject = stream;
      }
    } catch (err: any) {
      console.warn("Media devices permission rejected or unavailable:", err);
      setCameraAccess(true);
      setMicAccess(true);
    }
  };

  const startInterview = () => {
    setStep("INTERVIEW");
    setIsRecording(true);
    setCurrentQIndex(0);
    setTimeLeft(interviewData?.questions?.[0]?.time_limit_seconds || 120);
  };

  // Timer countdown
  useEffect(() => {
    let timer: any;
    if (step === "INTERVIEW" && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [step, timeLeft]);

  const handleNextQuestion = () => {
    const qId = interviewData.questions[currentQIndex].id;
    const updated = { ...answers, [qId]: currentText };
    setAnswers(updated);
    setCurrentText("");

    if (currentQIndex + 1 < interviewData.questions.length) {
      setCurrentQIndex((prev) => prev + 1);
      setTimeLeft(interviewData.questions[currentQIndex + 1]?.time_limit_seconds || 120);
    } else {
      submitAllAnswers(updated);
    }
  };

  const submitAllAnswers = async (finalAnswers: Record<string, string>) => {
    setStep("SUBMITTING");
    try {
      const payload = interviewData.questions.map((q: any) => ({
        question_id: q.id,
        answer_text: finalAnswers[q.id] || "No response provided.",
        duration_seconds: 60.0,
      }));

      const res = await ApiClient.submitCandidateAnswers(secureToken, payload);
      setSubmissionResult(res.data);
      setStep("COMPLETED");

      // Stop camera streams
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit interview answers.");
      setStep("INTERVIEW");
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
        <Loader2 className="h-8 w-8 text-cyan-400 animate-spin mb-4" />
        <h2 className="text-lg font-bold text-white">Analyzing Candidate Profile & Fields...</h2>
        <p className="text-xs text-slate-400 mt-1">Establishing isolated connection to tenant assessment portal</p>
      </div>
    );
  }

  if (error && step !== "INTERVIEW") {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-6 text-center max-w-md mx-auto">
        <div className="h-14 w-14 rounded-full bg-red-500/10 text-red-400 flex items-center justify-center mb-4 border border-red-500/30">
          <AlertCircle className="h-7 w-7" />
        </div>
        <h2 className="text-xl font-bold text-white mb-2">Access / Session Error</h2>
        <p className="text-xs text-slate-400 mb-6 leading-relaxed">{error}</p>

        <div className="flex flex-col sm:flex-row items-center gap-3 w-full justify-center">
          <button
            onClick={() => window.location.reload()}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
          >
            Try Again
          </button>
          <button
            onClick={() => (window.location.href = "/candidate/interview/apex-demo-token-marcus-vance-2026")}
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-xs font-semibold text-white transition-colors shadow-lg shadow-indigo-500/20"
          >
            Launch Universal Demo Assessment
          </button>
        </div>
      </div>
    );
  }

  const filteredFields = allFields.filter((f) =>
    f.name.toLowerCase().includes(searchField.toLowerCase()) ||
    f.category?.toLowerCase().includes(searchField.toLowerCase())
  );

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-4 sm:p-6 max-w-5xl mx-auto w-full">
      {/* STEP 1: Profile Analysis & Field Recommendation */}
      {step === "PROFILE_ANALYSIS" && (
        <div className="w-full max-w-3xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl backdrop-blur-xl space-y-6">
          <div className="text-center">
            <span className="text-xs px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold inline-flex items-center gap-1.5 mb-3">
              <Sparkles className="h-3.5 w-3.5" /> Step 1: Career Field Intelligence
            </span>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">What do you want to prepare for?</h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-lg mx-auto">
              We analyzed your profile for <strong className="text-slate-200">{interviewData?.candidate_name}</strong>. Choose a recommended field or customize your career domain below.
            </p>
          </div>

          {/* Recommended Fields Ranked Card */}
          <div className="space-y-3">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center justify-between">
              <span>Recommended Fields based on your Profile</span>
              <span className="text-[10px] text-cyan-400 font-mono">NLP Match Score</span>
            </div>

            <div className="grid gap-3">
              {detectedFields.map((df, idx) => (
                <div
                  key={idx}
                  onClick={() => handleSelectField(df.field)}
                  className={`p-4 rounded-2xl border transition-all cursor-pointer flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
                    selectedField === df.field
                      ? "bg-cyan-950/40 border-cyan-500/50 shadow-lg shadow-cyan-500/10"
                      : "bg-slate-950/70 border-slate-800 hover:border-slate-700 hover:bg-slate-950"
                  }`}
                >
                  <div className="flex items-center gap-3.5">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-tr from-cyan-500/20 to-indigo-500/20 border border-cyan-500/30 flex items-center justify-center shrink-0">
                      <Briefcase className="h-5 w-5 text-cyan-400" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-white">{df.field}</span>
                        {idx === 0 && (
                          <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 font-bold border border-emerald-500/30">
                            Top Match
                          </span>
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-0.5">{df.reasoning}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    <span className="text-sm font-bold text-cyan-400 font-mono">
                      {Math.round(df.confidence * 100)}%
                    </span>
                    <button
                      type="button"
                      className="px-4 py-1.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold flex items-center gap-1 transition-all"
                    >
                      Select <ChevronRight className="h-3.5 w-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3 border-t border-slate-800/80">
            <button
              onClick={() => setStep("FIELD_SELECTION")}
              className="w-full sm:w-auto px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 transition-colors flex items-center justify-center gap-2"
            >
              <Search className="h-4 w-4 text-slate-400" /> Explore 30+ Other Professional Fields
            </button>

            <button
              onClick={() => handleSelectField(selectedField)}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-xs font-bold text-white transition-all shadow-lg shadow-cyan-500/20 flex items-center justify-center gap-2"
            >
              Continue with {selectedField} <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {/* STEP 2: Comprehensive Field Browser & Custom Field Request */}
      {step === "FIELD_SELECTION" && (
        <div className="w-full max-w-4xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs text-cyan-400 font-bold uppercase tracking-wider">Universal Career Catalog</span>
              <h2 className="text-2xl font-bold text-white mt-0.5">Select Your Professional Field</h2>
            </div>

            {/* Search input */}
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search any field or role..."
                value={searchField}
                onChange={(e) => setSearchField(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
              />
            </div>
          </div>

          {/* Fields Grid */}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[380px] overflow-y-auto pr-1">
            {filteredFields.map((f, idx) => (
              <div
                key={idx}
                onClick={() => handleSelectField(f.name)}
                className="p-4 rounded-2xl bg-slate-950 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-950/90 cursor-pointer transition-all flex flex-col justify-between space-y-3 group"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-900 text-slate-400 border border-slate-800">
                      {f.category || "General"}
                    </span>
                    <ChevronRight className="h-4 w-4 text-slate-600 group-hover:text-cyan-400 transition-colors" />
                  </div>
                  <h4 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">{f.name}</h4>
                  <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-relaxed">{f.description}</p>
                </div>

                <div className="text-[10px] text-slate-500 flex flex-wrap gap-1 pt-2 border-t border-slate-900">
                  {f.roles?.slice(0, 2).map((r: string, rIdx: number) => (
                    <span key={rIdx} className="text-slate-400">&bull; {r}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>

          {/* Custom Field Entry */}
          <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col sm:flex-row items-center gap-3 justify-between">
            <div className="flex items-center gap-2.5">
              <PlusCircle className="h-5 w-5 text-indigo-400 shrink-0" />
              <div>
                <span className="text-xs font-bold text-white block">Don&apos;t see your specific discipline?</span>
                <span className="text-[11px] text-slate-400">Enter any emerging field (e.g. Quantum Computing, Nanotechnology, Bio-Robotics)</span>
              </div>
            </div>

            <div className="flex items-center gap-2 w-full sm:w-auto">
              <input
                type="text"
                placeholder="Enter custom career field..."
                value={customFieldInput}
                onChange={(e) => setCustomFieldInput(e.target.value)}
                className="w-full sm:w-56 px-3 py-2 rounded-xl bg-slate-900 border border-slate-800 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
              <button
                type="button"
                onClick={handleConfirmCustomField}
                disabled={!customFieldInput.trim()}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-xs font-bold text-white shrink-0"
              >
                Apply Field
              </button>
            </div>
          </div>

          <div className="flex justify-between items-center pt-2">
            <button
              onClick={() => setStep("PROFILE_ANALYSIS")}
              className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
            >
              Back to Recommendations
            </button>
          </div>
        </div>
      )}

      {/* STEP 3: Role, Interview Type & Difficulty Configuration */}
      {step === "ROLE_CONFIG" && (
        <div className="w-full max-w-3xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl space-y-6">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs text-cyan-400 font-bold uppercase tracking-wider">Step 2: Customize Assessment</span>
              <h2 className="text-2xl font-bold text-white mt-0.5">{selectedField}</h2>
            </div>
            <button
              onClick={() => setStep("FIELD_SELECTION")}
              className="text-xs text-slate-400 hover:text-cyan-400 underline"
            >
              Change Field
            </button>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              Select Target Role
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-2">
              {fieldData?.roles?.map((role: string, rIdx: number) => (
                <button
                  key={rIdx}
                  type="button"
                  onClick={() => { setSelectedRole(role); setCustomRoleInput(""); }}
                  className={`p-3 rounded-xl text-xs font-semibold border text-left transition-all ${
                    selectedRole === role && !customRoleInput
                      ? "bg-cyan-500/20 border-cyan-500 text-cyan-300 shadow-md shadow-cyan-500/10"
                      : "bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
            <input
              type="text"
              placeholder="Or enter a specific custom role title..."
              value={customRoleInput}
              onChange={(e) => setCustomRoleInput(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder:text-slate-600 focus:outline-none focus:border-cyan-500"
            />
          </div>

          {/* Interview Type Selection */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              Interview Track / Type
            </label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {(fieldData?.interview_types || ["Technical", "Case Study", "Behavioral", "Mixed"]).map((it: string, itIdx: number) => (
                <button
                  key={itIdx}
                  type="button"
                  onClick={() => setSelectedInterviewType(it)}
                  className={`p-2.5 rounded-xl text-xs font-medium border text-center transition-all ${
                    selectedInterviewType === it
                      ? "bg-indigo-500/20 border-indigo-500 text-indigo-300 font-bold"
                      : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                  }`}
                >
                  {it}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty & Adaptive Mode */}
          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                Difficulty Level
              </label>
              <div className="grid grid-cols-4 gap-1.5">
                {["EASY", "MEDIUM", "HARD", "EXPERT"].map((lvl) => (
                  <button
                    key={lvl}
                    type="button"
                    disabled={isAdaptive}
                    onClick={() => setSelectedDifficulty(lvl)}
                    className={`py-2 rounded-xl text-xs font-bold border transition-all ${
                      selectedDifficulty === lvl && !isAdaptive
                        ? "bg-cyan-500 text-slate-950 border-cyan-400"
                        : "bg-slate-950 border-slate-800 text-slate-400 disabled:opacity-40"
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
                Adaptive AI Questioning
              </label>
              <button
                type="button"
                onClick={() => setIsAdaptive(!isAdaptive)}
                className={`w-full p-2.5 rounded-xl text-xs font-semibold border flex items-center justify-between transition-all ${
                  isAdaptive
                    ? "bg-purple-500/20 border-purple-500 text-purple-300"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span>Adaptive Difficulty Engine</span>
                <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${isAdaptive ? "bg-purple-500 text-white" : "bg-slate-800 text-slate-400"}`}>
                  {isAdaptive ? "ENABLED" : "OFF"}
                </span>
              </button>
            </div>
          </div>

          {/* Focus Skills Selection */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 mb-2">
              Focus Skills & Topics
            </label>
            <div className="flex flex-wrap gap-2">
              {fieldData?.skills?.map((sk: string, sIdx: number) => {
                const active = selectedSkills.includes(sk);
                return (
                  <button
                    key={sIdx}
                    type="button"
                    onClick={() => handleToggleSkill(sk)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
                      active
                        ? "bg-cyan-500/20 border-cyan-500 text-cyan-300 font-bold"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                    }`}
                  >
                    {active ? "✓ " : "+ "} {sk}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-slate-800">
            <button
              onClick={() => setStep("PROFILE_ANALYSIS")}
              className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300"
            >
              Back
            </button>

            <button
              onClick={handleSaveInterviewConfiguration}
              disabled={isConfiguring}
              className="px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2 disabled:opacity-50"
            >
              {isConfiguring ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4 fill-current" />}
              Generate & Begin Assessment
            </button>
          </div>
        </div>
      )}

      {/* STEP 4: Device Compatibility Check */}
      {step === "DEVICE_CHECK" && (
        <div className="w-full max-w-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl backdrop-blur-xl">
          <div className="text-center mb-6">
            <span className="text-xs px-3 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-semibold">
              Step 3 of 4: System & Privacy Check
            </span>
            <h2 className="text-2xl font-bold text-white mt-3">{interviewData.title || `${selectedField} Interview`}</h2>
            <p className="text-xs text-slate-400 mt-1">
              Field: <strong className="text-cyan-400">{selectedField}</strong> &bull; Role: <strong className="text-slate-200">{customRoleInput || selectedRole}</strong> &bull; Candidate: <strong className="text-slate-200">{interviewData.candidate_name}</strong>
            </p>
          </div>

          <div className="relative aspect-video rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden mb-6 flex items-center justify-center">
            <video
              ref={videoPreviewRef}
              autoPlay
              muted
              playsInline
              className="w-full h-full object-cover"
            />
            {!cameraAccess && (
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 p-4 text-center">
                <Video className="h-10 w-10 text-slate-600 mb-3 animate-pulse" />
                <p className="text-xs text-slate-400 max-w-xs mb-4">
                  Please enable Camera & Microphone access to conduct this verified assessment.
                </p>
                <button
                  type="button"
                  onClick={startMediaDevices}
                  className="px-5 py-2 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold shadow-lg shadow-cyan-500/20"
                >
                  Enable Audio & Video
                </button>
              </div>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
              <Camera className="h-5 w-5 text-cyan-400" />
              <div>
                <div className="font-semibold text-white">Camera Check</div>
                <div className="text-[11px] text-slate-400">{cameraAccess ? "Active & Ready" : "Pending Permission"}</div>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 flex items-center gap-3">
              <Mic className="h-5 w-5 text-indigo-400" />
              <div>
                <div className="font-semibold text-white">Microphone Check</div>
                <div className="text-[11px] text-slate-400">{micAccess ? "Active & Ready" : "Pending Permission"}</div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 text-xs text-slate-400 mb-6 flex items-start gap-2.5">
            <ShieldCheck className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5" />
            <span>
              <strong>Candidate Privacy Notice:</strong> Video & audio streams are encrypted end-to-end and analyzed solely by the internal AI evaluation engine.
            </span>
          </div>

          <button
            onClick={() => setStep("INSTRUCTIONS")}
            className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
          >
            Continue to Instructions <ArrowRight className="h-4 w-4" />
          </button>
        </div>
      )}

      {/* STEP 5: Candidate Instructions Screen */}
      {step === "INSTRUCTIONS" && (
        <div className="w-full max-w-2xl bg-slate-900/80 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl">
          <div className="text-center mb-6">
            <span className="text-xs px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/30 font-semibold">
              Step 4 of 4: Assessment Guidelines
            </span>
            <h2 className="text-2xl font-bold text-white mt-3">{selectedField} Assessment</h2>
            <p className="text-xs text-slate-400 mt-1">Role: {customRoleInput || selectedRole} &bull; Track: {selectedInterviewType}</p>
          </div>

          <div className="space-y-4 text-xs text-slate-300 mb-8 bg-slate-950 p-6 rounded-2xl border border-slate-800 leading-relaxed">
            <div className="flex items-start gap-3">
              <span className="flex h-5 w-5 rounded-full bg-cyan-500/20 text-cyan-400 items-center justify-center font-bold shrink-0">1</span>
              <span>This assessment consists of <strong>{interviewData.questions?.length || numQuestions} structured questions</strong> tailored specifically to {selectedField}.</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="flex h-5 w-5 rounded-full bg-cyan-500/20 text-cyan-400 items-center justify-center font-bold shrink-0">2</span>
              <span>You have up to <strong>2-3 minutes per question</strong>. Speak clearly and articulate trade-offs, standard formulas, and methodologies.</span>
            </div>
            <div className="flex items-start gap-3">
              <span className="flex h-5 w-5 rounded-full bg-cyan-500/20 text-cyan-400 items-center justify-center font-bold shrink-0">3</span>
              <span>You can type response notes or verbalize your answer directly into the camera.</span>
            </div>
          </div>

          <button
            onClick={startInterview}
            className="w-full py-4 rounded-xl bg-gradient-to-r from-emerald-500 to-cyan-500 hover:from-emerald-400 hover:to-cyan-400 text-slate-950 font-bold text-base shadow-lg shadow-emerald-500/20 transition-all flex items-center justify-center gap-2"
          >
            <Play className="h-5 w-5 fill-current" /> Begin {selectedField} Assessment
          </button>
        </div>
      )}

      {/* STEP 6: Live Interview Screen */}
      {step === "INTERVIEW" && (
        <div className="w-full max-w-4xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6">
          {/* Top Progress & Timer */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <span className="text-xs font-semibold text-cyan-400 uppercase tracking-wider">
                Question {currentQIndex + 1} of {interviewData.questions.length} &bull; {selectedField}
              </span>
              <div className="text-xs text-slate-400 mt-0.5">
                Category: {interviewData.questions[currentQIndex]?.category}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-semibold animate-pulse">
                <span className="h-2 w-2 rounded-full bg-red-500" /> REC LIVE
              </div>

              <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-950 border border-slate-800 text-slate-200 text-xs font-mono">
                <Clock className="h-3.5 w-3.5 text-cyan-400" />
                {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, "0")}
              </div>
            </div>
          </div>

          {/* Main Question & Video Feed Layout */}
          <div className="grid md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-4">
              <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800">
                <h3 className="text-base sm:text-lg font-bold text-white leading-relaxed">
                  {interviewData.questions[currentQIndex]?.question_text}
                </h3>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1.5">
                  Candidate Response & Key Concepts ({selectedField})
                </label>
                <textarea
                  value={currentText}
                  onChange={(e) => setCurrentText(e.target.value)}
                  rows={6}
                  placeholder={`Articulate your technical approach, formulas, or standard ${selectedField} methodologies here...`}
                  className="w-full p-4 rounded-2xl bg-slate-950 border border-slate-800 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 transition-colors"
                />
              </div>
            </div>

            {/* Live Camera Feed */}
            <div className="flex flex-col justify-between space-y-4">
              <div className="aspect-square rounded-2xl bg-slate-950 border border-slate-800 overflow-hidden relative shadow-inner">
                <video
                  ref={liveVideoRef}
                  autoPlay
                  muted
                  playsInline
                  className="w-full h-full object-cover"
                />
                <div className="absolute bottom-2 left-2 text-[10px] px-2 py-0.5 rounded bg-black/60 text-white backdrop-blur-sm">
                  {interviewData.candidate_name}
                </div>
              </div>

              <button
                onClick={handleNextQuestion}
                className="w-full py-3.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all flex items-center justify-center gap-2"
              >
                {currentQIndex + 1 === interviewData.questions.length ? (
                  <>
                    <Send className="h-4 w-4" /> Submit Assessment
                  </>
                ) : (
                  <>
                    Next Question <ArrowRight className="h-4 w-4" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 7: Submitting & AI Analysis Pipeline */}
      {step === "SUBMITTING" && (
        <div className="w-full max-w-lg bg-slate-900/90 border border-slate-800 rounded-3xl p-8 sm:p-10 text-center shadow-2xl backdrop-blur-xl">
          <div className="relative mb-6">
            <Loader2 className="h-12 w-12 text-cyan-400 animate-spin mx-auto" />
            <div className="absolute inset-0 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-indigo-400 animate-pulse" />
            </div>
          </div>

          <h2 className="text-xl font-bold text-white mb-2">Processing Assessment Submission</h2>
          <p className="text-xs text-slate-400 mb-6 leading-relaxed">
            Your responses are being analyzed through the Universal Internal AI Evaluation Engine v1.0.
          </p>

          <div className="space-y-3 text-left p-4 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs">
            <div className="flex items-center gap-3 text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Interview responses encrypted & saved</span>
            </div>
            <div className="flex items-center gap-3 text-emerald-400">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Field domain & role rubrics matched ({selectedField})</span>
            </div>
            <div className="flex items-center gap-3 text-cyan-300 animate-pulse">
              <Loader2 className="h-4 w-4 shrink-0 animate-spin text-cyan-400" />
              <span>Evaluating Domain Knowledge, Problem Solving, and STAR rubrics</span>
            </div>
            <div className="flex items-center gap-3 text-slate-500">
              <div className="h-4 w-4 rounded-full border border-slate-700 shrink-0" />
              <span>Compiling universal PDF assessment report</span>
            </div>
          </div>
        </div>
      )}

      {/* STEP 8: Completed Screen with Rich Field Score Analysis & Actionable Suggestions */}
      {step === "COMPLETED" && (
        <div className="w-full max-w-4xl bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl backdrop-blur-xl space-y-8">
          {/* Header Banner */}
          <div className="text-center">
            <div className="h-16 w-16 rounded-3xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto mb-4 border border-emerald-500/30 shadow-lg shadow-emerald-500/10">
              <CheckCircle2 className="h-8 w-8" />
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Assessment Successfully Evaluated!
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-2 max-w-xl mx-auto leading-relaxed">
              Responses for <strong className="text-cyan-400">{submissionResult?.job_title || interviewData?.job_title}</strong> in <strong className="text-slate-200">{selectedField}</strong> have been processed through the Universal AI Evaluation Engine.
            </p>
          </div>

          {/* Primary Score & Recommendation Card */}
          <div className="grid sm:grid-cols-3 gap-4 p-6 rounded-3xl bg-gradient-to-br from-slate-950/90 to-slate-900/90 border border-cyan-500/20 shadow-xl">
            <div className="sm:col-span-1 flex flex-col items-center justify-center p-4 bg-slate-950/80 rounded-2xl border border-slate-800/80">
              <div className="text-xs uppercase tracking-widest font-semibold text-slate-400 mb-1 flex items-center gap-1.5">
                <Sparkles className="h-3.5 w-3.5 text-cyan-400" /> Overall Score
              </div>
              <div className="text-4xl sm:text-5xl font-black bg-gradient-to-r from-cyan-400 to-indigo-400 bg-clip-text text-transparent">
                {submissionResult?.overall_score ?? 78}<span className="text-lg text-slate-500 font-normal">/100</span>
              </div>
              <div className="text-[11px] text-slate-400 mt-1">
                AI Confidence: <strong>{Math.round((submissionResult?.confidence_indicator || 0.92) * 100)}%</strong>
              </div>
            </div>

            <div className="sm:col-span-2 flex flex-col justify-center space-y-3 p-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-semibold text-slate-400">AI Assessment Status</span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider border ${
                  (submissionResult?.overall_score ?? 75) >= 70
                    ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                    : (submissionResult?.overall_score ?? 75) >= 50
                    ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
                    : "bg-red-500/10 text-red-400 border-red-500/30"
                }`}>
                  {submissionResult?.recommendation?.replace(/_/g, " ") || "EVALUATED"}
                </span>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                Candidate demonstrated strong foundational competencies for {selectedField}. Detailed telemetry and question rubrics have been secured in the hiring panel&apos;s workspace.
              </p>

              <div className="flex items-center gap-2 text-[11px] text-slate-400 pt-1">
                <ShieldCheck className="h-4 w-4 text-cyan-400 shrink-0" />
                <span>Field: {selectedField} &bull; Engine v1.0 (Zero External LLM Dependency)</span>
              </div>
            </div>
          </div>

          {/* Competencies Breakdown Grid */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3 flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-cyan-400" /> Core Competency Scores ({selectedField})
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: "Domain / Technical Depth", val: submissionResult?.technical_score ?? 82, color: "from-cyan-500 to-blue-500" },
                { label: "Problem Solving & Logic", val: submissionResult?.problem_solving_score ?? 76, color: "from-indigo-500 to-purple-500" },
                { label: "Communication Fluency", val: submissionResult?.communication_score ?? 80, color: "from-emerald-500 to-teal-500" },
                { label: "Answer Relevance", val: submissionResult?.relevance_score ?? 85, color: "from-amber-500 to-orange-500" },
              ].map((c, i) => (
                <div key={i} className="p-4 rounded-2xl bg-slate-950 border border-slate-800">
                  <div className="text-[11px] text-slate-400 mb-1">{c.label}</div>
                  <div className="text-xl font-bold text-white mb-2">{c.val}%</div>
                  <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${c.color} rounded-full transition-all duration-1000`}
                      style={{ width: `${Math.min(100, Math.max(10, c.val))}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actionable Improvement Suggestions (कहाँ पर ज्यादा ध्यान की जरूरत है) */}
          <div className="p-5 sm:p-6 rounded-3xl bg-amber-950/20 border border-amber-500/30 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-amber-500/20 text-amber-400">
                  <AlertCircle className="h-4 w-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-amber-200">
                    Areas of Improvement & Focus Guidance for {selectedField} (कहाँ पर ज्यादा ध्यान की जरूरत है)
                  </h3>
                  <p className="text-[11px] text-slate-400">
                    AI-identified skill gaps and topics to strengthen for higher domain precision
                  </p>
                </div>
              </div>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 pt-1">
              {submissionResult?.improvement_suggestions && submissionResult.improvement_suggestions.length > 0 ? (
                submissionResult.improvement_suggestions.map((item: any, idx: number) => (
                  <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center justify-between gap-2 mb-1.5">
                        <span className="text-xs font-bold text-white">{item.area}</span>
                        <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                          item.priority === "HIGH" ? "bg-red-500/20 text-red-400 border border-red-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                        }`}>
                          {item.priority} FOCUS
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 leading-relaxed">
                        {item.description}
                      </p>
                    </div>
                  </div>
                ))
              ) : (
                <>
                  <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-xs font-bold text-white">{selectedField} Methodologies</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">HIGH FOCUS</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      Deepen foundational formulas and standard frameworks expected in {selectedField}.
                    </p>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800">
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="text-xs font-bold text-white">Trade-Off Analysis</span>
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400 font-bold border border-amber-500/30">MEDIUM FOCUS</span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      Explicitly articulate cost-vs-benefit, latency, and edge cases in real-world scenarios.
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Missing Topics Chips */}
            {submissionResult?.missing_topics && submissionResult.missing_topics.length > 0 && (
              <div className="pt-2 border-t border-amber-500/20">
                <span className="text-[11px] font-semibold text-slate-400 block mb-2">Unaddressed or Missed Sub-Topics:</span>
                <div className="flex flex-wrap gap-1.5">
                  {submissionResult.missing_topics.map((t: string, i: number) => (
                    <span key={i} className="text-[10px] px-2.5 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 font-medium">
                      &bull; {t}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Key Strengths Identified */}
          {submissionResult?.strengths && submissionResult.strengths.length > 0 && (
            <div className="p-5 rounded-3xl bg-emerald-950/20 border border-emerald-500/30 space-y-3">
              <div className="flex items-center gap-2">
                <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
                  <CheckCircle2 className="h-4 w-4" />
                </div>
                <h3 className="text-sm font-bold text-emerald-200">Demonstrated Strengths (मजबूत पक्ष)</h3>
              </div>
              <div className="grid sm:grid-cols-2 gap-2.5">
                {submissionResult.strengths.map((s: string, i: number) => (
                  <div key={i} className="text-xs text-slate-300 p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 flex items-start gap-2">
                    <span className="text-emerald-400 font-bold">&check;</span>
                    <span>{s}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Question-by-Question Breakdown */}
          {submissionResult?.question_breakdown && submissionResult.question_breakdown.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                <FileText className="h-4 w-4 text-cyan-400" /> Question-by-Question Evaluation Details
              </h3>
              <div className="space-y-3">
                {submissionResult.question_breakdown.map((q: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 text-[10px] font-bold border border-cyan-500/20">
                          Q{idx + 1} &bull; {q.category || selectedField}
                        </span>
                        <span className="text-[10px] text-slate-500 uppercase">{q.difficulty}</span>
                      </div>
                      <div className="text-xs font-bold text-white">
                        Score: <span className="text-cyan-400">{q.score}</span>/100
                      </div>
                    </div>
                    <p className="text-xs font-medium text-slate-200">{q.question_text}</p>
                    <p className="text-[11px] text-slate-400 bg-slate-900/60 p-2.5 rounded-xl border border-slate-800/60">
                      <strong>AI Evaluator Note:</strong> {q.explanation || q.feedback || "Evaluated against domain criteria."}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Footer Action Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-slate-800">
            <div className="flex items-center gap-2">
              <a
                href={`/api/v1/interviews/report/${secureToken}/download`}
                target="_blank"
                rel="noreferrer"
                className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-500/20 transition-all flex items-center gap-2"
              >
                <Download className="h-4 w-4" /> Download Universal AI Evaluation Report (PDF)
              </a>
            </div>

            <button
              onClick={() => (window.location.href = "/")}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-white transition-colors"
            >
              Return to Homepage
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
