<script setup lang="ts">
import { computed, watch } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

defineOptions({ name: 'StatsDrawer' });

const props = defineProps<{
  visible: boolean;
  loading: boolean;
  template: Api.PetPoster.Template | null;
  stats: Api.PetPoster.TemplateStats | null;
}>();

const emit = defineEmits<{ (e: 'update:visible', v: boolean): void }>();

const appStore = useAppStore();

const innerVisible = computed({
  get: () => props.visible,
  set: v => emit('update:visible', v)
});

function formatMs(ms: number) {
  if (!ms) return '-';
  if (ms < 1000) return `${ms} ms`;
  return `${(ms / 1000).toFixed(1)} s`;
}

const { domRef, updateOptions } = useEcharts(() => ({
  tooltip: { trigger: 'axis' },
  animationDuration: 400,
  animationEasing: 'cubicOut',
  grid: { top: 24, right: 16, bottom: 28, left: 36, containLabel: true },
  xAxis: { type: 'category', data: [] as string[] },
  yAxis: { type: 'value' },
  series: [
    {
      name: $t('page.petposter.templateStats.usageCount'),
      type: 'line',
      smooth: true,
      areaStyle: { opacity: 0.2 },
      color: '#409eff',
      data: [] as number[]
    },
    {
      name: $t('page.petposter.templateStats.successCount'),
      type: 'line',
      smooth: true,
      color: '#67c23a',
      data: [] as number[]
    }
  ]
}));

function refresh() {
  if (!props.stats) return;
  updateOptions(opts => {
    opts.xAxis.data = props.stats!.recent30d.map(r => r.date.slice(5));
    opts.series[0].data = props.stats!.recent30d.map(r => r.count);
    opts.series[1].data = props.stats!.recent30d.map(r => r.success);
    return opts;
  });
}

watch(() => props.stats, refresh, { immediate: true });
watch(() => appStore.locale, refresh);
</script>

<template>
  <ElDrawer
    v-model="innerVisible"
    :title="template ? `${template.name} - ${$t('page.petposter.templateStats.drawerTitle')}` : $t('page.petposter.templateStats.drawerTitle')"
    direction="rtl"
    size="520px"
    destroy-on-close
  >
    <div v-loading="loading" class="flex-col gap-16px">
      <ElDescriptions v-if="stats" :column="2" border>
        <ElDescriptionsItem :label="$t('page.petposter.templateStats.usageCount')">{{ stats.usageCount }}</ElDescriptionsItem>
        <ElDescriptionsItem :label="$t('page.petposter.templateStats.successCount')">{{ stats.successCount }}</ElDescriptionsItem>
        <ElDescriptionsItem :label="$t('page.petposter.templateStats.failedCount')">{{ stats.failedCount }}</ElDescriptionsItem>
        <ElDescriptionsItem :label="$t('page.petposter.templateStats.successRate')">{{ stats.successRate }}%</ElDescriptionsItem>
        <ElDescriptionsItem :label="$t('page.petposter.templateStats.avgDuration')" :span="2">{{ formatMs(stats.avgDurationMs) }}</ElDescriptionsItem>
      </ElDescriptions>

      <ElCard shadow="never">
        <template #header>
          <span class="text-14px font-bold">{{ $t('page.petposter.templateStats.last30Days') }}</span>
        </template>
        <div ref="domRef" class="h-280px"></div>
        <div v-if="stats && stats.recent30d.length === 0" class="py-24px text-center text-gray-400">
          {{ $t('page.petposter.templateStats.noUsage') }}
        </div>
      </ElCard>
    </div>
  </ElDrawer>
</template>
