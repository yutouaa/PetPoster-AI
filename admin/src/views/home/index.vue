<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { fetchPetPosterDashboard } from '@/service/api';
import { $t } from '@/locales';
import HeaderBanner from './modules/header-banner.vue';
import CardData from './modules/card-data.vue';
import LineChart from './modules/line-chart.vue';
import PieChart from './modules/pie-chart.vue';
import ProjectNews from './modules/project-news.vue';
import CreativityBanner from './modules/creativity-banner.vue';
import DurationStats from './modules/duration-stats.vue';
import FailureBreakdown from './modules/failure-breakdown.vue';

const appStore = useAppStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

const dashboard = ref<Api.PetPoster.DashboardMetrics | null>(null);
const filter = reactive({ days: 7, compare: false });
const loading = ref(false);

async function loadDashboard() {
  loading.value = true;
  try {
    const { data, error } = await fetchPetPosterDashboard({
      days: filter.days,
      compare: filter.compare
    });
    if (!error && data) {
      dashboard.value = data;
    }
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);
</script>

<template>
  <ElSpace v-loading="loading" direction="vertical" fill class="full-space pb-0" :size="0">
    <HeaderBanner class="mb-16px" :dashboard="dashboard" />

    <ElCard class="mb-16px" shadow="never">
      <div class="flex flex-wrap items-center justify-between gap-12px">
        <ElRadioGroup v-model="filter.days" size="default" @change="loadDashboard">
          <ElRadioButton :value="1">{{ $t('page.home.dateToday') }}</ElRadioButton>
          <ElRadioButton :value="7">{{ $t('page.home.date7d') }}</ElRadioButton>
          <ElRadioButton :value="30">{{ $t('page.home.date30d') }}</ElRadioButton>
        </ElRadioGroup>
        <div class="flex items-center gap-8px">
          <span class="text-14px text-gray-500">{{ $t('page.home.compareWithPrev') }}</span>
          <ElSwitch v-model="filter.compare" @change="loadDashboard" />
        </div>
      </div>
    </ElCard>

    <CardData class="mb-16px" :dashboard="dashboard" />

    <ElRow :gutter="gap" class="w-full">
      <ElCol :lg="14" :sm="24" class="mb-16px">
        <LineChart :trend="dashboard?.generationTrend || []" :revenue="dashboard?.revenueTrend || []" />
      </ElCol>
      <ElCol :lg="10" :sm="24" class="mb-16px">
        <PieChart :status-distribution="dashboard?.statusDistribution || []" />
      </ElCol>
    </ElRow>

    <ElRow :gutter="gap" class="w-full">
      <ElCol :lg="10" :sm="24" class="mb-16px">
        <DurationStats :duration="dashboard?.taskDuration" />
      </ElCol>
      <ElCol :lg="14" :sm="24" class="mb-16px">
        <FailureBreakdown
          :failures="dashboard?.failureTypeDistribution || []"
          :retry="dashboard?.retryEffectiveness"
        />
      </ElCol>
    </ElRow>

    <ElRow :gutter="gap">
      <ElCol :lg="14" :sm="24" class="mb-16px">
        <ProjectNews :recent-tasks="dashboard?.recentTasks || []" />
      </ElCol>
      <ElCol :lg="10" :sm="24" class="mb-16px">
        <CreativityBanner />
      </ElCol>
    </ElRow>
  </ElSpace>
</template>

<style scoped lang="scss">
.full-space {
  > :deep(.el-space__item) {
    width: 100%;
  }
}
</style>
