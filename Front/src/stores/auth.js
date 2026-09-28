import { defineStore } from "pinia";
import { authService } from "../services/api";

export const useAuthStore = defineStore("auth", {
  state: () => ({ token: localStorage.getItem("infotech_token"), user: JSON.parse(localStorage.getItem("infotech_user") || "null"), ready: false }),
  getters: { isAdmin: (state) => state.user?.role === "administrateur", isAuthenticated: (state) => Boolean(state.token) },
  actions: {
    async login(payload) { const { data } = await authService.login(payload); this.token = data.access_token; localStorage.setItem("infotech_token", data.access_token); await this.restore(); },
    async restore() { if (!this.token) { this.ready = true; return; } try { const { data } = await authService.me(); this.user = data; localStorage.setItem("infotech_user", JSON.stringify(data)); } catch { this.logout(); } finally { this.ready = true; } },
    logout() { this.token = null; this.user = null; this.ready = true; localStorage.removeItem("infotech_token"); localStorage.removeItem("infotech_user"); },
  },
});
