<script setup lang="ts">
import { computed } from 'vue';
import { useAppStore } from '@/store/modules/app';
import { useAuthStore } from '@/store/modules/auth';
import { $t } from '@/locales';

defineOptions({ name: 'HeaderBanner' });

const props = defineProps<{
  dashboard: Api.PetPoster.DashboardMetrics | null;
}>();

const appStore = useAppStore();
const authStore = useAuthStore();

const gap = computed(() => (appStore.isMobile ? 0 : 16));

interface StatisticData {
  id: number;
  title: string;
  value: number;
}

const pendingCount = computed(() => {
  if (!props.dashboard) return 0;
  const item = props.dashboard.statusDistribution.find(s => s.name === 'pending');
  return item?.value || 0;
});

const statisticData = computed<StatisticData[]>(() => [
  { id: 0, title: $t('page.home.projectCount'), value: props.dashboard?.templateCount || 0 },
  { id: 1, title: $t('page.home.todo'), value: pendingCount.value },
  { id: 2, title: $t('page.home.message'), value: props.dashboard?.todayGenerationCount || 0 }
]);
</script>

<template>
  <ElCard class="card-wrapper">
    <ElRow :gutter="gap" class="px-8px">
      <ElCol :md="18" :sm="24">
        <div class="flex-y-center">
          <div class="size-72px shrink-0 overflow-hidden rd-1/2 flex-center bg-primary/10">
            <SvgIcon icon="material-symbols:pets" class="text-36px text-primary" />
          </div>
          <div class="pl-12px">
            <h3 class="text-18px font-semibold">
              {{ $t('page.home.greeting', { userName: authStore.userInfo.userName }) }}
            </h3>
            <p class="text-#999 leading-30px">{{ $t('page.home.weatherDesc') }}</p>
          </div>
        </div>
      </ElCol>
      <ElCol :md="6" :sm="24">
        <ElSpace direction="horizontal" class="w-full justify-end" :size="24">
          <ElStatistic v-for="item in statisticData" :key="item.id" class="whitespace-nowrap" v-bind="item" />
        </ElSpace>
      </ElCol>
    </ElRow>
  </ElCard>
</template>

<style scoped></style>
