<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { fetchGenerationTasks, retryGenerationTask } from '@/service/api';

defineOptions({ name: 'PetposterGenerations' });

const loading = ref(false);
const tasks = ref<Api.PetPoster.GenerationTask[]>([]);
const total = ref(0);
const query = reactive({
  page: 1,
  pageSize: 20,
  status: ''
});

const statusOptions = [
  { label: '全部状态', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' }
];

const stats = computed(() => {
  const list = tasks.value;
  const successCount = list.filter(t => t.status === 'success').length;
  const failedCount = list.filter(t => t.status === 'failed').length;
  const processingCount = list.filter(t => t.status === 'processing' || t.status === 'pending').length;
  const totalCost = list.reduce((sum, t) => sum + (Number(t.cost) || 0), 0);
  return [
    { label: '当前页任务', value: list.length, icon: 'material-symbols:task-rounded', tone: 'blue' },
    { label: '成功', value: successCount, icon: 'material-symbols:check-circle-rounded', tone: 'green' },
    { label: '失败', value: failedCount, icon: 'material-symbols:error-rounded', tone: 'red' },
    { label: '进行中', value: processingCount, icon: 'material-symbols:pending-rounded', tone: 'orange' },
    { label: '页面成本', value: `¥${totalCost.toFixed(2)}`, icon: 'material-symbols:payments-rounded', tone: 'purple' }
  ];
});

const previewVisible = ref(false);
const previewUrl = ref('');

function statusText(status: string) {
  const map: Record<string, string> = {
    pending: '待处理',
    processing: '处理中',
    success: '成功',
    failed: '失败'
  };
  return map[status] || status;
}

function statusType(status: string) {
  const map: Record<string, 'info' | 'warning' | 'success' | 'danger'> = {
    pending: 'info',
    processing: 'warning',
    success: 'success',
    failed: 'danger'
  };
  return map[status] || 'info';
}

function formatTime(value: string | null | undefined) {
  if (!value) return '-';
  return new Date(value).toLocaleString('zh-CN');
}

function calcDuration(createdAt: string | null | undefined, completedAt: string | null | undefined) {
  if (!createdAt || !completedAt) return '-';
  const diff = new Date(completedAt).getTime() - new Date(createdAt).getTime();
  if (diff < 0) return '-';
  const seconds = Math.round(diff / 1000);
  if (seconds < 60) return `${seconds}s`;
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
}

function openPreview(url: string) {
  previewUrl.value = url;
  previewVisible.value = true;
}

async function loadTasks() {
  loading.value = true;
  try {
    const { data, error } = await fetchGenerationTasks({
      page: query.page,
      pageSize: query.pageSize,
      status: query.status || undefined
    });
    if (!error && data) {
      tasks.value = data.records;
      total.value = data.total;
    }
  } finally {
    loading.value = false;
  }
}

async function handleRetry(row: Api.PetPoster.GenerationTask) {
  await ElMessageBox.confirm(`确认重新生成任务 #${row.id}？`, '重新生成', {
    confirmButtonText: '确认',
    cancelButtonText: '取消',
    type: 'info'
  });
  const { error } = await retryGenerationTask(row.id);
  if (!error) {
    ElMessage.success('已重新提交生成任务');
    loadTasks();
  }
}

function handleSearch() {
  query.page = 1;
  loadTasks();
}

onMounted(loadTasks);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="generations-page">
    <ElCard class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">生成任务管理</div>
            <div class="card-subtitle">查看和管理所有 AI 海报生成任务</div>
          </div>
          <ElButton type="primary" @click="loadTasks">
            <SvgIcon icon="material-symbols:refresh-rounded" class="mr-4px text-icon" />
            刷新
          </ElButton>
        </div>
      </template>

      <div class="stat-strip">
        <div v-for="item in stats" :key="item.label" class="stat-item" :class="`stat-${item.tone}`">
          <div class="stat-icon">
            <SvgIcon :icon="item.icon" />
          </div>
          <div class="stat-text">
            <div class="stat-value">{{ item.value }}</div>
            <div class="stat-label">{{ item.label }}</div>
          </div>
        </div>
      </div>

      <div class="filter-bar">
        <ElSelect v-model="query.status" class="!w-160px" placeholder="全部状态" @change="handleSearch">
          <ElOption v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </ElSelect>
        <div class="filter-right">
          <span class="total-hint">共 {{ total }} 条记录</span>
        </div>
      </div>

      <ElTable v-loading="loading" :data="tasks" stripe row-key="id" class="task-table">
        <ElTableColumn prop="id" label="ID" width="72" align="center" />
        <ElTableColumn label="结果" width="80" align="center">
          <template #default="{ row }">
            <div v-if="row.resultImageUrl" class="result-thumb-wrap" @click="openPreview(row.resultImageUrl)">
              <ElImage :src="row.resultImageUrl" fit="cover" class="result-thumb" />
              <div class="thumb-overlay">
                <SvgIcon icon="material-symbols:zoom-in-rounded" />
              </div>
            </div>
            <span v-else class="no-image">-</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="templateName" label="模板" min-width="140" show-overflow-tooltip />
        <ElTableColumn prop="userId" label="用户" width="120" show-overflow-tooltip />
        <ElTableColumn label="状态" width="100" align="center">
          <template #default="{ row }">
            <ElTag :type="statusType(row.status)" size="small">{{ statusText(row.status) }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn label="耗时" width="90" align="center">
          <template #default="{ row }">
            {{ calcDuration(row.createdAt, row.completedAt) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="cost" label="成本" width="90" align="right">
          <template #default="{ row }">
            {{ row.cost ? `¥${Number(row.cost).toFixed(2)}` : '-' }}
          </template>
        </ElTableColumn>
        <ElTableColumn label="创建时间" width="170">
          <template #default="{ row }">{{ formatTime(row.createdAt) }}</template>
        </ElTableColumn>
        <ElTableColumn label="完成时间" width="170">
          <template #default="{ row }">{{ formatTime(row.completedAt) }}</template>
        </ElTableColumn>
        <ElTableColumn prop="errorMessage" label="失败原因" min-width="180" show-overflow-tooltip>
          <template #default="{ row }">
            <span v-if="row.errorMessage" class="error-text">{{ row.errorMessage }}</span>
            <span v-else>-</span>
          </template>
        </ElTableColumn>
        <ElTableColumn label="操作" width="110" fixed="right" align="center">
          <template #default="{ row }">
            <ElButton
              v-if="['failed', 'success'].includes(row.status)"
              link
              type="primary"
              size="small"
              @click="handleRetry(row)"
            >
              <SvgIcon icon="material-symbols:replay-rounded" class="mr-2px text-icon" />
              重试
            </ElButton>
            <span v-else class="no-action">-</span>
          </template>
        </ElTableColumn>
      </ElTable>

      <div class="pagination-bar">
        <ElPagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadTasks"
          @current-change="loadTasks"
        />
      </div>
    </ElCard>

    <ElDialog v-model="previewVisible" title="生成结果预览" width="520px" destroy-on-close>
      <div class="preview-body">
        <ElImage :src="previewUrl" fit="contain" class="preview-image" />
      </div>
    </ElDialog>
  </ElSpace>
</template>

<style scoped>
.generations-page {
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

.stat-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 12px 16px;
  min-width: 140px;
  flex: 1;
}

.stat-icon {
  display: grid;
  width: 36px;
  height: 36px;
  flex: none;
  place-items: center;
  border-radius: 8px;
  font-size: 20px;
}

.stat-blue .stat-icon {
  background: rgb(64 158 255 / 12%);
  color: #409eff;
}

.stat-green .stat-icon {
  background: rgb(103 194 58 / 12%);
  color: #67c23a;
}

.stat-red .stat-icon {
  background: rgb(245 108 108 / 12%);
  color: #f56c6c;
}

.stat-orange .stat-icon {
  background: rgb(230 162 60 / 12%);
  color: #e6a23c;
}

.stat-purple .stat-icon {
  background: rgb(142 157 255 / 14%);
  color: #8e9dff;
}

.stat-value {
  color: var(--el-text-color-primary);
  font-size: 18px;
  font-weight: 700;
  line-height: 1.2;
}

.stat-label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-top: 2px;
}

.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.filter-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.total-hint {
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.result-thumb-wrap {
  position: relative;
  width: 48px;
  height: 48px;
  margin: 0 auto;
  cursor: pointer;
  border-radius: 6px;
  overflow: hidden;
}

.result-thumb {
  width: 48px;
  height: 48px;
  border-radius: 6px;
}

.thumb-overlay {
  position: absolute;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgb(0 0 0 / 0%);
  color: #fff;
  font-size: 18px;
  opacity: 0;
  transition: all 0.2s ease;
}

.result-thumb-wrap:hover .thumb-overlay {
  background: rgb(0 0 0 / 40%);
  opacity: 1;
}

.no-image,
.no-action {
  color: var(--el-text-color-placeholder);
}

.error-text {
  color: var(--el-color-danger);
  font-size: 12px;
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.preview-body {
  display: flex;
  justify-content: center;
  padding: 8px;
}

.preview-image {
  max-width: 100%;
  max-height: 480px;
  border-radius: 8px;
}
</style>
