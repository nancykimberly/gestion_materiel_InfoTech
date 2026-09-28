<script setup>
import { useRouter } from "vue-router";
import { useAuthStore } from "../stores/auth";
import NotificationBell from "./NotificationBell.vue";
const auth = useAuthStore(); const router = useRouter();
const logout = () => { auth.logout(); router.push("/login"); };
</script>
<template>
  <div class="bg-[#17482d] px-5 py-2 text-xs text-white"><div class="mx-auto flex max-w-7xl items-center justify-between"><span>Gestion du parc informatique</span><span class="hidden sm:block">Plateforme de gestion du matériel informatique</span><button class="underline" @click="logout">Déconnexion</button></div></div>
  <header class="border-b border-slate-100 bg-white"><nav class="navbar mx-auto min-h-18 max-w-7xl px-5"><RouterLink to="/catalogue" class="text-xl font-bold tracking-tight text-[#17482d]">◈ InfoTech</RouterLink><div class="ml-auto flex items-center gap-1 sm:gap-4"><RouterLink class="btn btn-ghost btn-sm" to="/catalogue">Catalogue</RouterLink><RouterLink class="btn btn-ghost btn-sm" to="/demandes">Mes demandes</RouterLink><RouterLink v-if="auth.isAdmin" class="btn btn-ghost btn-sm" to="/admin">Administration</RouterLink><NotificationBell /><span class="hidden text-sm font-medium text-slate-600 md:block">{{ auth.user?.nom_complet }}</span></div></nav></header>
</template>
