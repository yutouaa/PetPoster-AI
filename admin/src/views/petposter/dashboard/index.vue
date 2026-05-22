<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue';
import { useEcharts } from '@/hooks/common/echarts';
import { fetchPetPosterDashboard } from '@/service/api';

defineOptions({ name: 'PetposterDashboard' });

function createEmptyDashboard(): Api.PetPoster.DashboardMetrics {
  return {
    userCount: 0,
    templateCount: 0,
    generationCount: 0,
    todayGenerationCount: 0,
    todayRevenue: 0,
    todayCost: 0,
    failureRate: 0,
    successRate: 0,
    activeUserCount: 0,
    styleDistribution: [],
    statusDistribution: [],
    generationTrend: [],
    userPortrait: {
      activeUserCount: 0,
      newUserCount: 0,
      repeatUserCount: 0,
      anonymousCount: 0,
      highValueUserCount: 0
    },
    topTemplates: [],
    recentTasks: [],
    taskDuration: { avg: 0, p50: 0, p95: 0, sampleSize: 0 },
    failureTypeDistribution: [],
    retryEffectiveness: { attempted: 0, succeeded: 0, rate: 0 },
    revenueTrend: [],
    consumptionPerUser: 0,
    recentTimeouts24h: 0,
    periodComparison: null,
    days: 7
  };
}

const loading = ref(false);
const dashboard = ref<Api.PetPoster.DashboardMetrics>(createEmptyDashboard());

const statusLabelMap: Record<string, string> = {
  pending: '待处理',
  processing: '生成中',
  success: '成功',
  failed: '失败'
};

const overviewMetrics = computed(() => [
  {
    label: '用户总数',
    value: formatInt(dashboard.value.userCount),
    desc: `活跃 ${formatInt(dashboard.value.activeUserCount)}`,
    icon: 'material-symbols:groups-rounded',
    tone: 'blue'
  },
  {
    label: '模板数量',
    value: formatInt(dashboard.value.templateCount),
    desc: `Top ${dashboard.value.topTemplates[0]?.name || '暂无'}`,
    icon: 'material-symbols:dashboard-customize-rounded',
    tone: 'green'
  },
  {
    label: '生成总数',
    value: formatInt(dashboard.value.generationCount),
    desc: `今日 ${formatInt(dashboard.value.todayGenerationCount)}`,
    icon: 'material-symbols:auto-awesome-rounded',
    tone: 'purple'
  },
  {
    label: '成功率',
    value: formatPercent(dashboard.value.successRate),
    desc: `失败率 ${formatPercent(dashboard.value.failureRate)}`,
    icon: 'material-symbols:verified-rounded',
    tone: 'cyan'
  },
  {
    label: '今日成本',
    value: formatCurrency(dashboard.value.todayCost),
    desc: `收入 ${formatCurrency(dashboard.value.todayRevenue)}`,
    icon: 'material-symbols:payments-rounded',
    tone: 'orange'
  },
  {
    label: '高价值用户',
    value: formatInt(dashboard.value.userPortrait.highValueUserCount),
    desc: `复购 ${formatInt(dashboard.value.userPortrait.repeatUserCount)}`,
    icon: 'material-symbols:person-star-rounded',
    tone: 'red'
  }
]);

const portraitItems = computed(() => [
  { label: '活跃用户', value: dashboard.value.userPortrait.activeUserCount },
  { label: '新用户', value: dashboard.value.userPortrait.newUserCount },
  { label: '复购用户', value: dashboard.value.userPortrait.repeatUserCount },
  { label: '匿名任务', value: dashboard.value.userPortrait.anonymousCount },
  { label: '高价值用户', value: dashboard.value.userPortrait.highValueUserCount }
]);

const totalStyleUsage = computed(() => dashboard.value.styleDistribution.reduce((sum, item) => sum + item.value, 0));
const topStyle = computed(() => dashboard.value.styleDistribution[0]);
const topStyleShare = computed(() => {
  if (!topStyle.value || !totalStyleUsage.value) return 0;

  return Math.round((topStyle.value.value / totalStyleUsage.value) * 100);
});

function formatInt(value: number) {
  return Number(value || 0).toLocaleString('zh-CN');
}

function formatCurrency(value: number) {
  return `¥${Number(value || 0).toLocaleString('zh-CN')}`;
}

function formatPercent(value: number) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function formatDateTime(value: string) {
  return value ? new Date(value).toLocaleString('zh-CN') : '-';
}

function getStatusLabel(status: string) {
  return statusLabelMap[status] || status || '未知';
}

function getStatusTagType(status: string): 'success' | 'warning' | 'info' | 'danger' | 'primary' {
  const map: Record<string, 'success' | 'warning' | 'info' | 'danger' | 'primary'> = {
    success: 'success',
    processing: 'warning',
    pending: 'info',
    failed: 'danger'
  };

  return map[status] || 'primary';
}

function buildTrendOption() {
  const trend = dashboard.value.generationTrend;

  return {
    color: ['#409eff', '#67c23a', '#f56c6c', '#d97757'],
    animationDuration: 400,
    animationEasing: 'cubicOut' as const,
    animationDelay: (idx: number) => idx * 20,
    tooltip: {
      trigger: 'axis' as const
    },
    legend: {
      top: 0,
      data: ['生成量', '成功', '失败', '成本']
    },
    grid: {
      top: 48,
      right: 24,
      bottom: 24,
      left: 36,
      containLabel: true
    },
    xAxis: {
      type: 'category' as const,
      boundaryGap: false,
      data: trend.map(item => item.date)
    },
    yAxis: [
      {
        type: 'value' as const,
        name: '任务'
      },
      {
        type: 'value' as const,
        name: '成本'
      }
    ],
    series: [
      {
        name: '生成量',
        type: 'line' as const,
        smooth: true,
        areaStyle: {},
        data: trend.map(item => item.count)
      },
      {
        name: '成功',
        type: 'bar' as const,
        barMaxWidth: 18,
        data: trend.map(item => item.success)
      },
      {
        name: '失败',
        type: 'bar' as const,
        barMaxWidth: 18,
        data: trend.map(item => item.failed)
      },
      {
        name: '成本',
        type: 'line' as const,
        smooth: true,
        yAxisIndex: 1,
        data: trend.map(item => item.cost)
      }
    ]
  };
}

function buildStyleOption() {
  return {
    color: ['#d97757', '#409eff', '#67c23a', '#e6a23c', '#8e9dff', '#26deca', '#f56c6c', '#909399'],
    animationDuration: 400,
    animationEasing: 'cubicOut' as const,
    animationDelay: (idx: number) => idx * 30,
    tooltip: {
      trigger: 'item' as const
    },
    legend: {
      bottom: 0,
      left: 'center' as const,
      type: 'scroll' as const
    },
    series: [
      {
        name: '风格使用',
        type: 'pie' as const,
        radius: ['45%', '72%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        itemStyle: {
          borderRadius: 6,
          borderColor: '#fff',
          borderWidth: 2
        },
        data: dashboard.value.styleDistribution
      }
    ]
  };
}

function buildStatusOption() {
  const statuses = dashboard.value.statusDistribution;

  return {
    color: ['#409eff'],
    animationDuration: 400,
    animationEasing: 'cubicOut' as const,
    animationDelay: (idx: number) => idx * 40,
    tooltip: {
      trigger: 'axis' as const
    },
    grid: {
      top: 24,
      right: 16,
      bottom: 28,
      left: 28,
      containLabel: true
    },
    xAxis: {
      type: 'category' as const,
      data: statuses.map(item => getStatusLabel(item.name))
    },
    yAxis: {
      type: 'value' as const
    },
    series: [
      {
        name: '任务数',
        type: 'bar' as const,
        barMaxWidth: 30,
        itemStyle: {
          borderRadius: [6, 6, 0, 0]
        },
        data: statuses.map(item => item.value)
      }
    ]
  };
}

function buildPortraitOption() {
  const values = portraitItems.value.map(item => item.value);
  const maxValue = Math.max(...values, 5);

  return {
    color: ['#d97757'],
    animationDuration: 400,
    animationEasing: 'cubicOut' as const,
    tooltip: {},
    radar: {
      radius: '66%',
      indicator: portraitItems.value.map(item => ({
        name: item.label,
        max: maxValue
      }))
    },
    series: [
      {
        name: '用户画像',
        type: 'radar' as const,
        areaStyle: {
          opacity: 0.18
        },
        data: [
          {
            name: '用户画像',
            value: values
          }
        ]
      }
    ]
  };
}

const { domRef: trendRef, updateOptions: updateTrendOptions } = useEcharts(() => buildTrendOption(), {
  onRender: chart => chart.setOption(buildTrendOption())
});
const { domRef: styleRef, updateOptions: updateStyleOptions } = useEcharts(() => buildStyleOption(), {
  onRender: chart => chart.setOption(buildStyleOption())
});
const { domRef: statusRef, updateOptions: updateStatusOptions } = useEcharts(() => buildStatusOption(), {
  onRender: chart => chart.setOption(buildStatusOption())
});
const { domRef: portraitRef, updateOptions: updatePortraitOptions } = useEcharts(() => buildPortraitOption(), {
  onRender: chart => chart.setOption(buildPortraitOption())
});

function refreshCharts() {
  updateTrendOptions(() => buildTrendOption());
  updateStyleOptions(() => buildStyleOption());
  updateStatusOptions(() => buildStatusOption());
  updatePortraitOptions(() => buildPortraitOption());
}

async function loadDashboard() {
  loading.value = true;
  try {
    const { data, error } = await fetchPetPosterDashboard();
    if (!error && data) {
      dashboard.value = {
        ...createEmptyDashboard(),
        ...data,
        userPortrait: {
          ...createEmptyDashboard().userPortrait,
          ...data.userPortrait
        }
      };
      await nextTick();
      refreshCharts();
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="dashboard-page">
    <ElCard v-loading="loading" class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">PetPoster AI 数据概览</div>
            <div class="card-subtitle">用户、模板、生成质量和成本的核心指标</div>
          </div>
          <ElButton type="primary" @click="loadDashboard">
            <SvgIcon icon="material-symbols:refresh-rounded" class="mr-4px text-icon" />
            刷新
          </ElButton>
        </div>
      </template>

      <div class="metric-grid">
        <div v-for="item in overviewMetrics" :key="item.label" class="metric-card" :class="`metric-${item.tone}`">
          <div class="metric-icon">
            <SvgIcon :icon="item.icon" />
          </div>
          <div class="metric-content">
            <div class="metric-value">{{ item.value }}</div>
            <div class="metric-label">{{ item.label }}</div>
            <div class="metric-desc">{{ item.desc }}</div>
          </div>
        </div>
      </div>
    </ElCard>

    <ElRow :gutter="16">
      <ElCol :xs="24" :lg="16">
        <ElCard class="card-wrapper chart-card">
          <template #header>
            <div class="card-title">近 7 日生成趋势</div>
          </template>
          <div ref="trendRef" class="chart-large"></div>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :lg="8">
        <ElCard class="card-wrapper chart-card">
          <template #header>
            <div class="card-title">风格使用分析</div>
          </template>
          <div class="style-summary">
            <span>最常用风格</span>
            <strong>{{ topStyle?.name || '暂无数据' }}</strong>
            <ElProgress :percentage="topStyleShare" :stroke-width="10" />
          </div>
          <div ref="styleRef" class="chart-medium"></div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow :gutter="16">
      <ElCol :xs="24" :lg="10">
        <ElCard class="card-wrapper chart-card">
          <template #header>
            <div class="card-title">用户画像分析</div>
          </template>
          <div ref="portraitRef" class="chart-medium"></div>
          <div class="portrait-list">
            <div v-for="item in portraitItems" :key="item.label" class="portrait-item">
              <span>{{ item.label }}</span>
              <strong>{{ formatInt(item.value) }}</strong>
            </div>
          </div>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :lg="14">
        <ElCard class="card-wrapper chart-card">
          <template #header>
            <div class="card-title">任务状态分布</div>
          </template>
          <div ref="statusRef" class="chart-medium"></div>
        </ElCard>
      </ElCol>
    </ElRow>

    <ElRow :gutter="16">
      <ElCol :xs="24" :lg="12">
        <ElCard class="card-wrapper">
          <template #header>
            <div class="card-title">热门模板排行</div>
          </template>
          <ElTable :data="dashboard.topTemplates" height="320" stripe>
            <ElTableColumn type="index" label="#" width="54" />
            <ElTableColumn prop="name" label="模板" min-width="120" show-overflow-tooltip />
            <ElTableColumn prop="category" label="分类" width="100" show-overflow-tooltip />
            <ElTableColumn prop="count" label="生成量" width="90" align="right" />
            <ElTableColumn label="成功率" width="110" align="right">
              <template #default="{ row }">{{ formatPercent(row.successRate) }}</template>
            </ElTableColumn>
          </ElTable>
        </ElCard>
      </ElCol>
      <ElCol :xs="24" :lg="12">
        <ElCard class="card-wrapper">
          <template #header>
            <div class="card-title">最近生成任务</div>
          </template>
          <ElTable :data="dashboard.recentTasks" height="320" stripe>
            <ElTableColumn prop="id" label="ID" width="72" />
            <ElTableColumn prop="templateName" label="模板" min-width="130" show-overflow-tooltip />
            <ElTableColumn label="状态" width="90">
              <template #default="{ row }">
                <ElTag :type="getStatusTagType(row.status)" size="small">{{ getStatusLabel(row.status) }}</ElTag>
              </template>
            </ElTableColumn>
            <ElTableColumn prop="cost" label="成本" width="80" align="right" />
            <ElTableColumn label="创建时间" width="170">
              <template #default="{ row }">{{ formatDateTime(row.createdAt) }}</template>
            </ElTableColumn>
          </ElTable>
        </ElCard>
      </ElCol>
    </ElRow>
  </ElSpace>
</template>

<style scoped>
.dashboard-page {
  width: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.card-title {
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 700;
}

.card-subtitle {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.metric-card {
  display: flex;
  min-height: 112px;
  align-items: center;
  gap: 14px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 18px;
  background: var(--el-bg-color);
}

.metric-icon {
  display: grid;
  width: 44px;
  height: 44px;
  flex: none;
  place-items: center;
  border-radius: 8px;
  font-size: 24px;
}

.metric-blue .metric-icon {
  background: rgb(64 158 255 / 12%);
  color: #409eff;
}

.metric-green .metric-icon {
  background: rgb(103 194 58 / 12%);
  color: #67c23a;
}

.metric-purple .metric-icon {
  background: rgb(142 157 255 / 14%);
  color: #8e9dff;
}

.metric-cyan .metric-icon {
  background: rgb(38 222 202 / 14%);
  color: #26deca;
}

.metric-orange .metric-icon {
  background: rgb(217 119 87 / 14%);
  color: #d97757;
}

.metric-red .metric-icon {
  background: rgb(245 108 108 / 12%);
  color: #f56c6c;
}

.metric-value {
  color: var(--el-text-color-primary);
  font-size: 26px;
  font-weight: 800;
  line-height: 1.1;
}

.metric-label {
  margin-top: 8px;
  color: var(--el-text-color-primary);
  font-weight: 600;
}

.metric-desc {
  margin-top: 4px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-large {
  height: 360px;
}

.chart-medium {
  height: 280px;
}

.style-summary {
  display: grid;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.style-summary strong {
  color: var(--el-text-color-primary);
  font-size: 18px;
}

.portrait-list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.portrait-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 6px;
  padding: 10px 12px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.portrait-item strong {
  color: var(--el-text-color-primary);
}
</style>
