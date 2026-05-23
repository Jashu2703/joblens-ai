import axios from "axios";

const API_URL = "https://joblens-ai-production.up.railway.app";
const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  register: (data) => api.post("/api/auth/register", data),
  login: (data) => api.post("/api/auth/login", data),
};

export const resumeAPI = {
  upload: (file) => {
    const form = new FormData();
    form.append("file", file);
    return api.post("/api/resume/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
  },
  list: () => api.get("/api/resume/"),
  get: (id) => api.get(`/api/resume/${id}`),
  delete: (id) => api.delete(`/api/resume/${id}`),
};

export const jobsAPI = {
  list: (params) => api.get("/api/jobs/", { params }),
  stats: () => api.get("/api/jobs/stats"),
  seedNow: () => api.post("/api/jobs/seed/now"),
};

export const analyzeAPI = {
  ats: (data) => api.post("/api/analyze/ats", data),
  gaps: (data) => api.post("/api/analyze/gaps", data),
  matchRoles: (data) => api.post("/api/analyze/match-roles", data),
  full: (data) => api.post("/api/analyze/full", data),
  history: () => api.get("/api/analyze/history"),
};

export const interviewAPI = {
  generate: (data) => api.post("/api/interview/generate", data),
  tips: () => api.get("/api/interview/tips"),
};

export default api;
