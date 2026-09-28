<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import AuthLayout from "../../layouts/AuthLayout.vue";
import { authService } from "../../services/api";
import { useAuthStore } from "../../stores/auth";

const form = reactive({ nom_complet: "", departement: "", poste: "", nouveau_mot_de_passe: "", confirmation: "" });
const error = ref(""); const loading = ref(false); const router = useRouter(); const auth = useAuthStore();
const submit = async () => { error.value = ""; if (form.nouveau_mot_de_passe !== form.confirmation) { error.value = "Les mots de passe ne correspondent pas."; return; } loading.value = true; try { const { confirmation, ...payload } = form; await authService.activate(payload); await auth.restore(); router.push(auth.isAdmin ? "/admin" : "/catalogue"); } catch (exception) { error.value = exception.message; } finally { loading.value = false; } };
</script>
<template><AuthLayout><h1 class="mt-8 text-3xl font-bold text-slate-800">Activez votre compte</h1><p class="mt-2 text-sm text-slate-500">Complétez votre profil et remplacez votre mot de passe temporaire.</p><form class="mt-7 grid gap-3" @submit.prevent="submit"><input v-model="form.nom_complet" class="input input-bordered" placeholder="Nom complet" required><input v-model="form.departement" class="input input-bordered" placeholder="Département" required><input v-model="form.poste" class="input input-bordered" placeholder="Poste" required><input v-model="form.nouveau_mot_de_passe" type="password" minlength="8" class="input input-bordered" placeholder="Nouveau mot de passe" required><input v-model="form.confirmation" type="password" class="input input-bordered" placeholder="Confirmez le mot de passe" required><p v-if="error" class="text-sm text-error">{{ error }}</p><button class="btn border-0 bg-[#17482d] text-white" :disabled="loading">{{ loading ? 'Activation…' : 'Activer mon compte' }}</button></form></AuthLayout></template>
