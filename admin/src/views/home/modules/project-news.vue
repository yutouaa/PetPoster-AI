<script setup lang="ts">
import { computed } from 'vue';
import { $t } from '@/locales';

defineOptions({ name: 'ProjectNews' });

interface NewsItem {
  id: number;
  content: string;
  time: string;
}

const newses = computed<NewsItem[]>(() => [
  { id: 1, content: $t('page.home.projectNews.desc1'), time: '2025-05-10 14:30:00' },
  { id: 2, content: $t('page.home.projectNews.desc2'), time: '2025-05-12 09:15:22' },
  { id: 3, content: $t('page.home.projectNews.desc3'), time: '2025-05-13 16:42:18' },
  { id: 4, content: $t('page.home.projectNews.desc4'), time: '2025-05-15 11:20:45' },
  { id: 5, content: $t('page.home.projectNews.desc5'), time: '2025-05-16 18:05:33' }
]);
</script>

<template>
  <ElCard class="card-wrapper">
    <template #header>
      <ElRow>
        <ElCol :span="18">{{ $t('page.home.projectNews.title') }}</ElCol>
        <ElCol :span="6" class="text-right">
          <a class="text-primary" href="javascript:;">{{ $t('page.home.projectNews.moreNews') }}</a>
        </ElCol>
      </ElRow>
    </template>
    <ElTimeline>
      <ElTimelineItem v-for="item in newses" :key="item.id" :timestamp="item.time" placement="top">
        <ElSpace>
          <div class="size-36px shrink-0 overflow-hidden rd-1/2 flex-center bg-primary/10">
            <SvgIcon icon="material-symbols:pets" class="text-18px text-primary" />
          </div>
          <p>{{ item.content }}</p>
        </ElSpace>
      </ElTimelineItem>
    </ElTimeline>
  </ElCard>
</template>

<style scoped></style>
