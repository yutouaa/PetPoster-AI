<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({ name: 'DurationStats' });

const props = defineProps<{
  duration: Api.PetPoster.TaskDuration | undefined;
}>();

function formatMs(ms: number) {
  if (!ms) return '-';
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

const items = computed(() => [
  { label: $t('page.home.durationAvg'), value: props.duration?.avg ?? 0 },
  { label: 'P50', value: props.duration?.p50 ?? 0 },
  { label: 'P95', value: props.duration?.p95 ?? 0 }
]);

const sampleSize = computed(() => props.duration?.sampleSize ?? 0);
const maxValue = computed(() => Math.max(...items.value.map(i => i.value), 1));
</script>

<template>
  <ElCard class="card-wrapper h-full" shadow="never">
    <template #header>
      <div class="flex items-center justify-between">
        <span class="text-16px font-bold">{{ $t('page.home.taskDuration') }}</span>
        <span class="text-12px text-gray-400">{{ $t('page.home.sampleSize', { count: sampleSize }) }}</span>
      </div>
    </template>
    <div v-if="sampleSize === 0" class="py-32px text-center text-gray-400">
      {{ $t('common.noData') }}
    </div>
    <div v-else class="flex-col gap-16px">
      <div v-for="item in items" :key="item.label" class="flex-col gap-4px duration-item">
        <div class="flex items-center justify-between">
          <span class="text-14px text-gray-500">{{ item.label }}</span>
          <span class="text-16px font-semibold">{{ formatMs(item.value) }}</span>
        </div>
        <div class="h-6px overflow-hidden rd-full bg-gray-100 dark:bg-gray-800">
          <div
            class="h-full rd-full bg-primary transition-all duration-500"
            :style="{ width: `${(item.value / maxValue) * 100}%` }"
          ></div>
        </div>
      </div>
    </div>
  </ElCard>
</template>

<style scoped>
@keyframes duration-item-enter {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.duration-item {
  animation: duration-item-enter 0.4s ease both;
}

.duration-item:nth-child(1) {
  animation-delay: 0ms;
}

.duration-item:nth-child(2) {
  animation-delay: 120ms;
}

.duration-item:nth-child(3) {
  animation-delay: 240ms;
}
</style>
