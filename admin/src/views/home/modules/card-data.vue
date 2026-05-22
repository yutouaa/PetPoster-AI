<script setup lang="ts">
import { computed } from 'vue';
import { createReusableTemplate } from '@vueuse/core';
import { $t } from '@/locales';

defineOptions({ name: 'CardData' });

const props = defineProps<{
  dashboard: Api.PetPoster.DashboardMetrics | null;
}>();

interface CardData {
  key: string;
  title: string;
  value: number;
  unit: string;
  suffix?: string;
  delta?: number | null;
  decimals?: number;
  color: { start: string; end: string };
  icon: string;
}

function formatMs(ms: number) {
  if (!ms) return 0;
  return Math.round(ms / 100) / 10; // seconds with 1 decimal
}

const cardData = computed<CardData[]>(() => {
  const d = props.dashboard;
  const comparison = d?.periodComparison;
  return [
    {
      key: 'visitCount',
      title: $t('page.home.visitCount'),
      value: d?.userCount || 0,
      unit: '',
      color: { start: '#ec4786', end: '#b955a4' },
      icon: 'ant-design:bar-chart-outlined'
    },
    {
      key: 'generations',
      title: $t('page.home.downloadCount'),
      value: d?.generationCount || 0,
      unit: '',
      delta: comparison?.generationsPct ?? null,
      color: { start: '#56cdf3', end: '#719de3' },
      icon: 'carbon:document-download'
    },
    {
      key: 'duration',
      title: $t('page.home.taskDurationP50'),
      value: formatMs(d?.taskDuration?.p50 || 0),
      unit: '',
      suffix: 's',
      decimals: 1,
      color: { start: '#865ec0', end: '#5144b4' },
      icon: 'ant-design:clock-circle-outlined'
    },
    {
      key: 'timeouts',
      title: $t('page.home.timeouts24h'),
      value: d?.recentTimeouts24h || 0,
      unit: '',
      color: { start: '#fcbc25', end: '#f68057' },
      icon: 'ant-design:warning-outlined'
    }
  ];
});

interface GradientBgProps {
  gradientColor: string;
}

const [DefineGradientBg, GradientBg] = createReusableTemplate<GradientBgProps>();

function getGradientColor(color: CardData['color']) {
  return `linear-gradient(to bottom right, ${color.start}, ${color.end})`;
}

function deltaClass(delta: number | null | undefined) {
  if (delta == null) return 'opacity-60';
  return delta >= 0 ? 'text-green-200' : 'text-red-200';
}

function deltaIcon(delta: number | null | undefined) {
  if (delta == null) return 'ant-design:minus-outlined';
  return delta >= 0 ? 'ant-design:arrow-up-outlined' : 'ant-design:arrow-down-outlined';
}
</script>

<template>
  <ElCard class="card-wrapper">
    <DefineGradientBg v-slot="{ $slots, gradientColor }">
      <div class="rd-8px px-16px pb-4px pt-8px text-white" :style="{ backgroundImage: gradientColor }">
        <component :is="$slots.default" />
      </div>
    </DefineGradientBg>
    <ElRow :gutter="16">
      <ElCol v-for="item in cardData" :key="item.key" :lg="6" :md="12" :sm="24" class="my-8px kpi-col">
        <GradientBg :gradient-color="getGradientColor(item.color)" class="flex-1">
          <div class="flex items-center justify-between">
            <h3 class="text-16px">{{ item.title }}</h3>
            <span v-if="item.delta !== undefined" :class="deltaClass(item.delta)" class="flex items-center text-12px">
              <SvgIcon :icon="deltaIcon(item.delta)" class="mr-2px" />
              <span>{{ item.delta == null ? '-' : `${Math.abs(item.delta)}%` }}</span>
            </span>
          </div>
          <div class="flex items-end justify-between pt-12px">
            <SvgIcon :icon="item.icon" class="text-32px" />
            <div class="flex items-baseline">
              <CountTo
                :prefix="item.unit"
                :start-value="1"
                :end-value="item.value"
                :decimals="item.decimals ?? 0"
                class="text-30px text-white dark:text-dark"
              />
              <span v-if="item.suffix" class="ml-2px text-14px">{{ item.suffix }}</span>
            </div>
          </div>
        </GradientBg>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped>
@keyframes kpi-enter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kpi-col {
  animation: kpi-enter 0.4s ease both;
}

.kpi-col:nth-child(1) {
  animation-delay: 0ms;
}

.kpi-col:nth-child(2) {
  animation-delay: 80ms;
}

.kpi-col:nth-child(3) {
  animation-delay: 160ms;
}

.kpi-col:nth-child(4) {
  animation-delay: 240ms;
}
</style>
