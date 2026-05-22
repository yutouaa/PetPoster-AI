<script setup lang="ts">
import { $t } from '@/locales';

defineOptions({ name: 'ProjectNews' });

const props = defineProps<{
  recentTasks: Api.PetPoster.RecentTask[];
}>();

const statusLabelMap: Record<string, string> = {
  pending: '待处理',
  processing: '生成中',
  success: '成功',
  failed: '失败'
};

const statusTypeMap: Record<string, 'success' | 'warning' | 'info' | 'primary' | 'danger'> = {
  pending: 'info',
  processing: 'warning',
  success: 'success',
  failed: 'danger'
};
</script>

<template>
  <ElCard class="card-wrapper">
    <template #header>
      <ElRow>
        <ElCol :span="18">{{ $t('page.home.projectNews.title') }}</ElCol>
        <ElCol :span="6" class="text-right">
          <RouterLink class="text-primary" to="/petposter/generations">
            {{ $t('page.home.projectNews.moreNews') }}
          </RouterLink>
        </ElCol>
      </ElRow>
    </template>
    <ElTimeline>
      <ElTimelineItem v-for="item in props.recentTasks" :key="item.id" :timestamp="item.createdAt" placement="top">
        <ElSpace>
          <div class="size-36px shrink-0 overflow-hidden rd-1/2 flex-center bg-primary/10">
            <SvgIcon icon="material-symbols:pets" class="text-18px text-primary" />
          </div>
          <p>
            {{ item.templateName }}
            <ElTag size="small" :type="statusTypeMap[item.status] || 'info'" class="ml-8px">
              {{ statusLabelMap[item.status] || item.status }}
            </ElTag>
          </p>
        </ElSpace>
      </ElTimelineItem>
    </ElTimeline>
    <ElEmpty v-if="props.recentTasks.length === 0" :image-size="80" description="暂无任务记录" />
  </ElCard>
</template>

<style scoped></style>
