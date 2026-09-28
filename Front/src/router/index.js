import { createRouter, createWebHistory } from "vue-router";

import LoginView from "../views/auth/Login.vue";
import RegisterView from "../views/auth/Register.vue";
import Catalogue from "../views/user/Catalogue.vue";
import MesDemandes from "../views/user/MesDemandes.vue";
import Notifications from "../views/user/Notifications.vue";
import Dashboard from "../views/admin/Dashboard.vue";
import Utilisateurs from "../views/admin/Utilisateurs.vue";
import Materiels from "../views/admin/Materiels.vue";
import Demandes from "../views/admin/Demandes.vue";
import Audit from "../views/admin/Audit.vue";
import { useAuthStore } from "../stores/auth";

const routes = [
    {
        path: "/login",
        name: "login",
        component: LoginView,
    },
    {
        path: "/register",
        name: "register",
        component: RegisterView,
    },
    { path: "/", redirect: "/catalogue" },
    { path: "/catalogue", component: Catalogue, meta: { auth: true } },
    { path: "/demandes", component: MesDemandes, meta: { auth: true } },
    { path: "/notifications", component: Notifications, meta: { auth: true } },
    { path: "/admin", component: Dashboard, meta: { auth: true, admin: true } },
    { path: "/admin/utilisateurs", component: Utilisateurs, meta: { auth: true, admin: true } },
    { path: "/admin/materiels", component: Materiels, meta: { auth: true, admin: true } },
    { path: "/admin/demandes", component: Demandes, meta: { auth: true, admin: true } },
    { path: "/admin/audit", component: Audit, meta: { auth: true, admin: true } },
    { path: "/:pathMatch(.*)*", redirect: "/catalogue" },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.ready) await auth.restore();
  if (to.meta.auth && !auth.isAuthenticated) return "/login";
  if (to.meta.admin && !auth.isAdmin) return "/catalogue";
  if ((to.path === "/login" || to.path === "/register") && auth.isAuthenticated) return auth.isAdmin ? "/admin" : "/catalogue";
});

export default router;
