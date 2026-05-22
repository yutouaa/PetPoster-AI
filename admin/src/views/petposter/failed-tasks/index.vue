<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import { batchRetryTasks, fetchFailedTasksSummary } from '@/service/api';

defineOptions({ name: 'PetposterFailedTasks' });

const { t } = useI18n();

const loading = ref(false);
const summaryList = ref<Api.PetPoster.FailedTaskSummary[]>([]);
const total = ref(0);
const query = reactive({ page: 1, pageSize: 20 });
const selectedTaskIds = ref<number[]>([]);
const expandedUser = ref<string | null>(null);

async function loadData() {
  loading.value = true;
  try {
    const { data, error } = await fetchFailedTasksSummary({ page: query.page, pageSize: query.pageSize });
    if (!error && data) {
      summaryList.value = data.records;
      total.value = data.total;
    }
  } finally {
    loading.value = false;
  }
}

function toggleExpand(userId: string) {
  expandedUser.value = expandedUser.value === userId ? null : userId;
}

function getTasksForUser(userId: string): Api.PetPoster.FailedTaskSummary['tasks'] {
  const item = summaryList.value.find(s => s.userId === userId);
  return item?.tasks || [];
}

function handleSelectTask(taskId: number, checked: boolean) {
  if (checked) {
    selectedTaskIds.value.push(taskId);
  } else {
    selectedTaskIds.value = selectedTaskIds.value.filter(id => id !== taskId);
  }
}

function selectAllForUser(userId: string) {
  const tasks = getTasksForUser(userId);
  const ids = tasks.map(t => t.id);
  const allSelected = ids.every(id => selectedTaskIds.value.includes(id));
  if (allSelected) {
    selectedTaskIds.value = selectedTaskIds.value.filter(id => !ids.includes(id));
  } else {
    const newIds = ids.filter(id => !selectedTaskIds.value.includes(id));
    selectedTaskIds.value.push(...newIds);
  }
}

async function handleBatchRetry() {
  if (selectedTaskIds.value.length === 0) {
    ElMessage.warning(t('page.petposter.failedTasks.selectFirst'));
    return;
  }
  try {
    await ElMessageBox.confirm(
      t('page.petposter.failedTasks.confirmBatchRetry', { count: selectedTaskIds.value.length }),
      t('page.petposter.failedTasks.confirmBatchRetryTitle'),
      {
        confirmButtonText: t('page.petposter.failedTasks.confirmRetryBtn'),
        cancelButtonText: t('page.petposter.common.cancel'),
        type: 'info'
      }
    );
  } catch {
    return;
  }
  const { data, error } = await batchRetryTasks(selectedTaskIds.value);
  if (!error && data) {
    ElMessage.success(t('page.petposter.failedTasks.retrySuccess', { count: data.retried }));
    selectedTaskIds.value = [];
    loadData();
  } else if (error) {
    ElMessage.error(error.message || t('page.petposter.failedTasks.retryFailed'));
  }
}

function formatTime(value: string | null | undefined) {
  if (!value) return '-';
  return new Date(value).toLocaleString('zh-CN');
}

onMounted(loadData);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="page-wrapper">
    <ElCard class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">{{ $t('page.petposter.failedTasks.pageTitle') }}</div>
            <div class="card-subtitle">{{ $t('page.petposter.failedTasks.pageSubtitle') }}</div>
          </div>
          <div class="header-actions">
            <ElButton type="primary" :disabled="selectedTaskIds.length === 0" @click="handleBatchRetry">
              <SvgIcon icon="material-symbols:replay-rounded" class="mr-4px text-icon" />
              {{ $t('page.petposter.failedTasks.batchRetry') }} ({{ selectedTaskIds.length }})
            </ElButton>
            <ElButton @click="loadData">
              <SvgIcon icon="material-symbols:refresh-rounded" class="mr-4px text-icon" />
              {{ $t('page.petposter.common.refresh') }}
            </ElButton>
          </div>
        </div>
      </template>

      <ElTable v-loading="loading" :data="summaryList" stripe row-key="userId">
        <ElTableColumn prop="userId" :label="$t('page.petposter.failedTasks.user')" min-width="140" show-overflow-tooltip />
        <ElTableColumn prop="failedCount" :label="$t('page.petposter.failedTasks.failedCount')" width="100" align="center">
          <template #default="{ row }">
            <ElTag type="danger" size="small">{{ row.failedCount }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="totalTasks" :label="$t('page.petposter.failedTasks.totalTasks')" width="100" align="center" />
        <ElTableColumn :label="$t('page.petposter.failedTasks.lastFailedAt')" width="180">
          <template #default="{ row }">{{ formatTime(row.lastFailedAt) }}</template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.common.operations')" width="200" align="center">
          <template #default="{ row }">
            <ElButton link type="primary" size="small" @click="toggleExpand(row.userId)">
              {{ expandedUser === row.userId ? $t('page.petposter.failedTasks.collapse') : $t('page.petposter.failedTasks.viewDetails') }}
            </ElButton>
            <ElButton link type="success" size="small" @click="selectAllForUser(row.userId)">
              {{ $t('page.petposter.failedTasks.selectAll') }}
            </ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div v-if="expandedUser" class="expanded-section">
        <div class="expanded-title">
          {{ $t('page.petposter.failedTasks.detailsTitle', { userId: expandedUser }) }}
        </div>
        <ElTable :data="getTasksForUser(expandedUser)" size="small" stripe>
          <ElTableColumn width="50" align="center">
            <template #default="{ row }">
              <ElCheckbox
                :model-value="selectedTaskIds.includes(row.id)"
                @change="(val: any) => handleSelectTask(row.id, Boolean(val))"
              />
            </template>
          </ElTableColumn>
          <ElTableColumn prop="id" label="ID" width="72" align="center" />
          <ElTableColumn prop="errorMessage" :label="$t('page.petposter.failedTasks.errorMessage')" min-width="220" show-overflow-tooltip>
            <template #default="{ row }">
              <span class="error-text">{{ row.errorMessage || '-' }}</span>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="retryCount" :label="$t('page.petposter.failedTasks.retryCount')" width="90" align="center" />
          <ElTableColumn :label="$t('page.petposter.failedTasks.createdAt')" width="170">
            <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
          </ElTableColumn>
        </ElTable>
      </div>

      <div class="pagination-bar">
        <ElPagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </ElCard>
  </ElSpace>
</template>

<style scoped>
.header-actions {
  display: flex;
  gap: 8px;
}

.expanded-section {
  margin-top: 16px;
  padding: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-fill-color-lighter);
}

.expanded-title {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.error-text {
  color: var(--el-color-danger);
  font-size: 12px;
}
</style>
