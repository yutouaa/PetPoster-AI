<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { fetchAuditLogs } from '@/service/api';

defineOptions({ name: 'PetposterAuditLog' });

useI18n();

const loading = ref(false);
const logs = ref<Api.PetPoster.AuditLog[]>([]);
const total = ref(0);
const query = reactive({ page: 1, pageSize: 20, action: '', resourceType: '', adminId: '' });

async function loadData() {
  loading.value = true;
  try {
    const params: Record<string, unknown> = { page: query.page, pageSize: query.pageSize };
    if (query.action) params.action = query.action;
    if (query.resourceType) params.resourceType = query.resourceType;
    if (query.adminId) params.adminId = query.adminId;
    const { data, error } = await fetchAuditLogs(params as Api.PetPoster.AuditLogListParams);
    if (!error && data) {
      logs.value = data.records;
      total.value = data.total;
    }
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  query.page = 1;
  loadData();
}

function handleReset() {
  query.action = '';
  query.resourceType = '';
  query.adminId = '';
  query.page = 1;
  loadData();
}

function actionLabel(action: string) {
  return action;
}

function resourceTypeLabel(type: string) {
  return type;
}

onMounted(loadData);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="page-wrapper">
    <ElCard class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">{{ $t('page.petposter.auditLog.pageTitle') }}</div>
            <div class="card-subtitle">{{ $t('page.petposter.auditLog.pageSubtitle') }}</div>
          </div>
        </div>
      </template>

      <div class="filter-bar">
        <ElInput
          v-model="query.adminId"
          :placeholder="$t('page.petposter.auditLog.adminIdPlaceholder')"
          clearable
          style="width: 160px"
        />
        <ElSelect v-model="query.action" :placeholder="$t('page.petposter.auditLog.filterAction')" clearable style="width: 160px">
          <ElOption label="create_template" value="create_template" />
          <ElOption label="update_template" value="update_template" />
          <ElOption label="delete_template" value="delete_template" />
          <ElOption label="create_provider" value="create_provider" />
          <ElOption label="delete_provider" value="delete_provider" />
          <ElOption label="toggle_provider" value="toggle_provider" />
          <ElOption label="batch_retry" value="batch_retry" />
          <ElOption label="adjust_quota" value="adjust_quota" />
        </ElSelect>
        <ElSelect v-model="query.resourceType" :placeholder="$t('page.petposter.auditLog.filterResourceType')" clearable style="width: 140px">
          <ElOption label="template" value="template" />
          <ElOption label="ai_provider" value="ai_provider" />
          <ElOption label="generation_task" value="generation_task" />
          <ElOption label="user_quota" value="user_quota" />
        </ElSelect>
        <ElButton type="primary" @click="handleSearch">{{ $t('page.petposter.common.confirm') }}</ElButton>
        <ElButton @click="handleReset">{{ $t('page.petposter.common.refresh') }}</ElButton>
      </div>

      <ElTable v-loading="loading" :data="logs" stripe row-key="id" style="margin-top: 16px">
        <ElTableColumn prop="id" label="ID" width="60" align="center" />
        <ElTableColumn prop="adminId" :label="$t('page.petposter.auditLog.adminId')" width="120" show-overflow-tooltip />
        <ElTableColumn :label="$t('page.petposter.auditLog.action')" width="130" align="center">
          <template #default="{ row }">
            <ElTag size="small">{{ actionLabel(row.action) }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.auditLog.resourceType')" width="110" align="center">
          <template #default="{ row }">
            {{ resourceTypeLabel(row.resourceType) }}
          </template>
        </ElTableColumn>
        <ElTableColumn prop="resourceId" :label="$t('page.petposter.auditLog.resourceId')" width="90" align="center" />
        <ElTableColumn prop="detail" :label="$t('page.petposter.auditLog.detail')" min-width="200" show-overflow-tooltip />
        <ElTableColumn prop="ipAddress" :label="$t('page.petposter.auditLog.ipAddress')" width="130" show-overflow-tooltip />
        <ElTableColumn prop="createdAt" :label="$t('page.petposter.auditLog.time')" min-width="170" show-overflow-tooltip />
      </ElTable>

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
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
