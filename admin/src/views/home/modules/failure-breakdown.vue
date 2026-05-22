<script setup lang="ts">
import { computed, watch } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

defineOptions({ name: 'FailureBreakdown' });

const props = defineProps<{
  failures: Api.PetPoster.FailureTypeItem[];
  retry: Api.PetPoster.RetryEffectiveness | undefined;
}>();

const appStore = useAppStore();

type FailureTypeKey = 'timeout' | 'api_error' | 'rate_limit' | 'template_missing' | 'unknown';
const KNOWN_TYPES: readonly FailureTypeKey[] = ['timeout', 'api_error', 'rate_limit', 'template_missing', 'unknown'];

function labelFor(t: string) {
  if ((KNOWN_TYPES as readonly string[]).includes(t)) {
    return $t(`page.home.failureTypes.${t as FailureTypeKey}`);
  }
  return $t('page.home.failureTypes.unknown');
}

const { domRef, updateOptions } = useEcharts(() => ({
  tooltip: { trigger: 'item' },
  animationDuration: 400,
  animationEasing: 'cubicOut',
  animationDelay: (idx: number) => idx * 30,
  legend: { bottom: 0, left: 'center' },
  series: [
    {
      name: $t('page.home.failureType'),
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: { show: false },
      labelLine: { show: false },
      data: [] as { name: string; value: number }[]
    }
  ]
}));

const retryRate = computed(() => props.retry?.rate ?? 0);
const retryAttempted = computed(() => props.retry?.attempted ?? 0);
const retrySucceeded = computed(() => props.retry?.succeeded ?? 0);

function refresh() {
  updateOptions(opts => {
    opts.series[0].data = props.failures.map(f => ({ name: labelFor(f.type), value: f.count }));
    return opts;
  });
}

watch(() => props.failures, refresh, { immediate: true, deep: true });
watch(() => appStore.locale, refresh);
</script>

<template>
  <ElCard class="card-wrapper h-full" shadow="never">
    <template #header>
      <span class="text-16px font-bold">{{ $t('page.home.failureBreakdown') }}</span>
    </template>
    <div ref="domRef" class="h-220px overflow-hidden"></div>
    <ElDivider class="my-12px" />
    <div class="flex-col gap-8px">
      <div class="flex items-center justify-between">
        <span class="text-14px text-gray-500">{{ $t('page.home.retryEffectiveness') }}</span>
        <span class="text-14px font-semibold">{{ retrySucceeded }} / {{ retryAttempted }}</span>
      </div>
      <ElProgress
        :percentage="retryRate"
        :stroke-width="8"
        :show-text="true"
        :format="(v: number) => `${v}%`"
      />
    </div>
  </ElCard>
</template>
