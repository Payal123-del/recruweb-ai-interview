const API_BASE = "/api/v1";

export interface StandardResponse<T> {
  success: boolean;
  message: string;
  data: T;
  error?: string;
}

export class ApiClient {
  private static isRefreshing = false;

  private static getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("ardhnarishwar_token");
  }

  private static getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("ardhnarishwar_refresh_token");
  }

  public static setToken(token: string, refreshToken?: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("ardhnarishwar_token", token);
      if (refreshToken) {
        localStorage.setItem("ardhnarishwar_refresh_token", refreshToken);
      }
    }
  }

  public static setTokens(accessToken: string, refreshToken: string) {
    if (typeof window !== "undefined") {
      localStorage.setItem("ardhnarishwar_token", accessToken);
      localStorage.setItem("ardhnarishwar_refresh_token", refreshToken);
    }
  }

  public static clearToken() {
    if (typeof window !== "undefined") {
      localStorage.removeItem("ardhnarishwar_token");
      localStorage.removeItem("ardhnarishwar_refresh_token");
      localStorage.removeItem("ardhnarishwar_user");
    }
  }

  public static async refreshToken(): Promise<string | null> {
    const rfToken = this.getRefreshToken();
    if (!rfToken) return null;

    try {
      const res = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: rfToken }),
      });

      if (!res.ok) {
        this.clearToken();
        return null;
      }

      const data = await res.json();
      if (data.success && data.data?.access_token) {
        this.setTokens(data.data.access_token, data.data.refresh_token || rfToken);
        return data.data.access_token;
      }
      return null;
    } catch {
      this.clearToken();
      return null;
    }
  }

  public static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<StandardResponse<T>> {
    let token = this.getToken();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    let res = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle 401 Unauthorized with automatic refresh-token rotation
    if (res.status === 401 && !endpoint.includes("/auth/login") && !endpoint.includes("/auth/refresh")) {
      if (!this.isRefreshing) {
        this.isRefreshing = true;
        const newToken = await this.refreshToken();
        this.isRefreshing = false;

        if (newToken) {
          headers["Authorization"] = `Bearer ${newToken}`;
          res = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
          });
        }
      }
    }

    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.message || data.detail || "An error occurred with the request");
    }
    return data;
  }

  // Auth Endpoints
  static async login(email: string, password: string) {
    return this.request<{ access_token: string; refresh_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  }

  static async getProfile() {
    return this.request<any>("/auth/me");
  }

  static async logout() {
    try {
      await this.request<any>("/auth/logout", { method: "POST" });
    } catch {}
    this.clearToken();
  }

  // Company Endpoints
  static async getCompanyCurrent() {
    return this.request<any>("/companies/current");
  }

  static async getCompanyStats() {
    return this.request<any>("/companies/current/stats");
  }

  static async getJobs() {
    return this.request<any[]>("/jobs");
  }

  static async createJob(payload: any) {
    return this.request<any>("/jobs", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getCandidates() {
    return this.request<any[]>("/candidates");
  }

  static async createCandidate(payload: any) {
    return this.request<any>("/candidates", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getInterviews() {
    return this.request<any[]>("/interviews");
  }

  static async createInterview(payload: any) {
    return this.request<any>("/interviews", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getQuestions() {
    return this.request<any[]>("/questions");
  }

  static async createQuestion(payload: any) {
    return this.request<any>("/questions", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getReports() {
    return this.request<any[]>("/reports");
  }

  static async updateReportDecision(reportId: string, decision: string, notes?: string) {
    return this.request<any>(`/reports/${reportId}/decision`, {
      method: "PATCH",
      body: JSON.stringify({ decision, notes }),
    });
  }

  static async getCompanyAnalytics() {
    return this.request<any>("/analytics/overview");
  }

  // Super Admin Endpoints
  static async getSuperAdminAnalytics() {
    return this.request<any>("/admin/analytics");
  }

  static async getAdminCompanies() {
    return this.request<any[]>("/admin/companies");
  }

  static async createAdminCompany(payload: any) {
    return this.request<any>("/admin/companies", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async getDatasets() {
    return this.request<any[]>("/datasets");
  }

  static async getModelVersions() {
    return this.request<any[]>("/models/versions");
  }

  static async getAuditLogs() {
    return this.request<any[]>("/audit-logs");
  }

  // Public Candidate Interview
  static async verifyCandidateToken(secureToken: string) {
    const res = await fetch(`${API_BASE}/interviews/verify/${secureToken}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || data.detail || "Invalid or expired interview token");
    }
    return data;
  }

  static async submitCandidateAnswers(secureToken: string, answers: any[]) {
    const res = await fetch(`${API_BASE}/interviews/submit/${secureToken}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(answers),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || data.detail || "Submission failed");
    }
    return data;
  }

  static async getInterviewStatus(secureToken: string) {
    const res = await fetch(`${API_BASE}/interviews/status/${secureToken}`);
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || data.detail || "Failed to fetch status");
    }
    return data;
  }

  static async getDetailedEvaluation(interviewId: string) {
    return this.request<any>(`/evaluations/${interviewId}/detailed`);
  }

  // Universal Professional Field APIs
  static async getFields(search?: string, category?: string) {
    const params = new URLSearchParams();
    if (search) params.append("search", search);
    if (category) params.append("category", category);
    const qs = params.toString() ? `?${params.toString()}` : "";
    const res = await fetch(`${API_BASE}/fields${qs}`);
    const data = await res.json();
    return data;
  }

  static async getFieldDetails(fieldName: string) {
    const res = await fetch(`${API_BASE}/fields/${encodeURIComponent(fieldName)}`);
    const data = await res.json();
    return data;
  }

  static async createField(payload: { name: string; category?: string; description?: string; icon?: string; roles?: string[]; skills?: string[] }) {
    return this.request<any>("/fields", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  static async detectFields(profileData: { resume_text?: string; skills?: string[]; job_title?: string; job_description?: string; education?: string }) {
    const res = await fetch(`${API_BASE}/fields/detect`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(profileData),
    });
    const data = await res.json();
    return data;
  }

  static async configureCustomInterview(secureToken: string, payload: {
    field_name: string;
    target_role?: string;
    interview_type?: string;
    difficulty?: string;
    is_adaptive?: boolean;
    experience_level?: string;
    focus_skills?: string[];
    num_questions?: number;
  }) {
    const res = await fetch(`${API_BASE}/interviews/configure-custom/${secureToken}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.message || data.detail || "Failed to configure interview");
    }
    return data;
  }
}

