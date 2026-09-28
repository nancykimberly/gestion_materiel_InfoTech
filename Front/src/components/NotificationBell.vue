<script setup>
import { onMounted, ref } from "vue";
import { notificationService } from "../services/api";
const count = ref(0); onMounted(async () => { try { count.value = (await notificationService.unread()).data.count; } catch {} });
</script>
<template><RouterLink to="/notifications" class="btn btn-ghost btn-circle btn-sm" aria-label="Notifications"><span class="indicator"><span>🔔</span><span v-if="count" class="badge badge-xs badge-error indicator-item">{{ count > 9 ? "9+" : count }}</span></span></RouterLink></template>
