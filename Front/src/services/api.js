import axios from "axios";

const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000" });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("infotech_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(error.response?.data?.detail || ({ 401: "Votre session a expiré. Veuillez vous reconnecter.", 403: "Vous n'avez pas les droits nécessaires.", 404: "Ressource introuvable.", 422: "Veuillez vérifier les informations saisies.", 500: "Une erreur est survenue sur le serveur." }[error.response?.status] || "Impossible de contacter le serveur.")))
);

export const authService = {
  login: (payload) => api.post("/api/auth/login", payload),
  register: (payload) => api.post("/api/auth/register", payload),
  me: () => api.get("/api/me"),
  updateProfile: (payload) => api.put("/api/me", payload),
  activate: (payload) => api.patch("/api/auth/activate", payload),
};
export const materialService = {
  list: () => api.get("/api/materiels"),
  create: (payload) => api.post("/api/admin/materiels", payload),
  update: (id, payload) => api.put(`/api/admin/materiels/${id}`, payload),
};
export const requestService = {
  mine: () => api.get("/api/requests/my"), create: (payload) => api.post("/api/requests", payload),
  all: () => api.get("/api/admin/requests"),
  pending: () => api.get("/api/admin/requests/pending"), approve: (id) => api.patch(`/api/admin/requests/${id}/approve`),
  reject: (id, payload) => api.patch(`/api/admin/requests/${id}/reject`, payload), returnMaterial: (id) => api.patch(`/api/admin/requests/${id}/return`),
};
export const notificationService = { list: () => api.get("/api/notifications"), unread: () => api.get("/api/notifications/unread-count"), read: (id) => api.patch(`/api/notifications/${id}/read`) };
export const userService = { create: (payload) => api.post("/api/admin/users", payload), list: () => api.get("/api/admin/users"), pending: () => api.get("/api/admin/users/pending"), get: (id) => api.get(`/api/admin/users/${id}`), update: (id, payload) => api.put(`/api/admin/users/${id}`, payload), approve: (id) => api.patch(`/api/admin/users/${id}/approve`), reject: (id) => api.patch(`/api/admin/users/${id}/reject`) };
export const auditService = { list: () => api.get("/api/admin/audit-logs") };
