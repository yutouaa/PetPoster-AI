<script setup lang="ts">
import { watch } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

defineOptions({ name: 'PieChart' });

const props = defineProps<{
  statusDistribution: Api.PetPoster.ChartItem[];
}>();

const appStore = useAppStore();

const statusColorMap: Record<string, string> = {
  success: '#67c23a',
  failed: '#f56c6c',
  processing: '#e6a23c',
  pending: '#409eff'
};

const { domRef, updateOptions } = useEcharts(() => ({
  tooltip: {
    trigger: 'item'
  },
  animationDuration: 400,
  animationEasing: 'cubicOut',
  animationDelay: (idx: number) => idx * 30,
  legend: {
    bottom: '1%',
    left: 'center',
    itemStyle: {
      borderWidth: 0
    }
  },
  series: [
    {
      color: ['#67c23a', '#f56c6c', '#e6a23c', '#409eff'],
      name: $t('page.home.schedule'),
      type: 'pie',
      radius: ['45%', '75%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 10,
        borderColor: '#fff',
        borderWidth: 1
      },
      label: {
        show: false,
        position: 'center'
      },
      emphasis: {
        label: {
          show: true,
          fontSize: '12'
        }
      },
      labelLine: {
        show: false
      },
      data: [] as { name: string; value: number; itemStyle?: { color: string } }[]
    }
  ]
}));

const statusLabelMap: Record<string, string> = {
  pending: '待处理',
  processing: '生成中',
  success: '成功',
  failed: '失败'
};

function refreshChart() {
  updateOptions(opts => {
    opts.series[0].data = props.statusDistribution.map(item => ({
      name: statusLabelMap[item.name] || item.name,
      value: item.value,
      itemStyle: { color: statusColorMap[item.name] || '#909399' }
    }));
    return opts;
  });
}

function updateLocale() {
  updateOptions((opts, factory) => {
    const originOpts = factory();
    opts.series[0].name = originOpts.series[0].name;
    return opts;
  });
}

watch(() => props.statusDistribution, refreshChart, { immediate: true });

watch(
  () => appStore.locale,
  () => {
    updateLocale();
  }
);
</script>

<template>
  <ElCard class="card-wrapper">
    <div ref="domRef" class="h-360px overflow-hidden"></div>
  </ElCard>
</template>

<style scoped></style>
