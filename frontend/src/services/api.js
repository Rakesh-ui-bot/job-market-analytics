import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const getJobs = async (params = {}) => {
  const res = await api.get('/jobs', { params });
  return res.data;
};

export const getJobById = async (id) => {
  const res = await api.get(`/jobs/${id}`);
  return res.data;
};

export const uploadCsv = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/jobs/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return res.data;
};

export const analyzeSkillGap = async (targetRole, userSkills) => {
  const res = await api.post('/analytics/skill-gap', {
    target_role: targetRole,
    user_skills: userSkills,
  });
  return res.data;
};

export const getOverview = async (params = {}) => {
  const res = await api.get('/analytics/overview', { params });
  return res.data;
};

export const getTopSkills = async (limit = 15) => {
  const res = await api.get('/analytics/skills', { params: { limit } });
  return res.data;
};

export const getSkillDetail = async (skill, currency = 'USD') => {
  const res = await api.get('/analytics/skill-detail', { params: { skill, currency } });
  return res.data;
};

export const getRoleDetail = async (role, currency = 'USD') => {
  const res = await api.get('/analytics/role-detail', { params: { role, currency } });
  return res.data;
};

export const getSkillsByRole = async (role = '', limit = 10) => {
  const res = await api.get('/analytics/skills-by-role', { params: { role, limit } });
  return res.data;
};

export const getSkillsByLocation = async (location = '', limit = 10) => {
  const res = await api.get('/analytics/skills-by-location', { params: { location, limit } });
  return res.data;
};

export const getRoles = async (limit = 10) => {
  const res = await api.get('/analytics/roles', { params: { limit } });
  return res.data;
};

export const getLocations = async (limit = 15) => {
  const res = await api.get('/analytics/locations', { params: { limit } });
  return res.data;
};

export const getSalaryAnalytics = async (currency = 'USD') => {
  const res = await api.get('/analytics/salary', { params: { currency } });
  return res.data;
};

export const getExperienceAnalytics = async () => {
  const res = await api.get('/analytics/experience');
  return res.data;
};

export const getRemoteAnalytics = async () => {
  const res = await api.get('/analytics/remote');
  return res.data;
};

export default api;
