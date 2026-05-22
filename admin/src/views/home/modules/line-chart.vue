<script setup lang="ts">
import { watch } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useEcharts } from '@/hooks/common/echarts';
import { $t } from '@/locales';

defineOptions({ name: 'LineChart' });

const props = defineProps<{
  trend: Api.PetPoster.TrendItem[];
  revenue?: Api.PetPoster.RevenueTrendItem[];
}>();

const appStore = useAppStore();

const { domRef, updateOptions } = useEcharts(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      label: {
        backgroundColor: '#6a7985'
      }
    }
  },
  animationDuration: 400,
  animationEasing: 'cubicOut',
  legend: {
    data: [$t('page.home.downloadCount'), $t('page.home.registerCount'), $t('page.home.revenue')]
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    containLabel: true
  },
  xAxis: {
    type: 'category',
    boundaryGap: false,
    data: [] as string[]
  },
  yAxis: {
    type: 'value'
  },
  series: [
    {
      color: '#8e9dff',
      name: $t('page.home.downloadCount'),
      type: 'line',
      smooth: true,
      stack: 'Total',
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0.25,
              color: '#8e9dff'
            },
            {
              offset: 1,
              color: '#fff'
            }
          ]
        }
      },
      emphasis: {
        focus: 'series'
      },
      data: [] as number[]
    },
    {
      color: '#26deca',
      name: $t('page.home.registerCount'),
      type: 'line',
      smooth: true,
      stack: 'Total',
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            {
              offset: 0.25,
              color: '#26deca'
            },
            {
              offset: 1,
              color: '#fff'
            }
          ]
        }
      },
      emphasis: {
        focus: 'series'
      },
      data: [] as number[]
    },
    {
      color: '#f59e0b',
      name: $t('page.home.revenue'),
      type: 'line',
      smooth: true,
      emphasis: {
        focus: 'series'
      },
      data: [] as number[]
    }
  ]
}));

function refreshChart() {
  updateOptions(opts => {
    opts.xAxis.data = props.trend.map(item => item.date);
    opts.series[0].data = props.trend.map(item => item.count);
    opts.series[1].data = props.trend.map(item => item.success);
    const revenueMap = new Map((props.revenue || []).map(r => [r.date, r.amount]));
    opts.series[2].data = props.trend.map(item => revenueMap.get(item.date) ?? 0);
    return opts;
  });
}

function updateLocale() {
  updateOptions((opts, factory) => {
    const originOpts = factory();
    opts.legend.data = originOpts.legend.data;
    opts.series[0].name = originOpts.series[0].name;
    opts.series[1].name = originOpts.series[1].name;
    opts.series[2].name = originOpts.series[2].name;
    return opts;
  });
}

watch(() => props.trend, refreshChart, { immediate: true });
watch(() => props.revenue, refreshChart);

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
