<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createAiProvider,
  deleteAiProvider,
  fetchAiProviders,
  toggleAiProviderActive,
  updateAiProvider
} from '@/service/api';

defineOptions({ name: 'PetposterAiProviders' });

const { t } = useI18n();

const loading = ref(false);
const providers = ref<Api.PetPoster.AiProvider[]>([]);
const total = ref(0);
const query = reactive({ page: 1, pageSize: 20 });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const form = reactive({
  name: '',
  base_url: '',
  api_key: '',
  model_name: '',
  timeout: 120,
  is_active: true,
  priority: 0
});

function resetForm() {
  form.name = '';
  form.base_url = '';
  form.api_key = '';
  form.model_name = '';
  form.timeout = 120;
  form.is_active = true;
  form.priority = 0;
}

async function loadData() {
  loading.value = true;
  try {
    const { data, error } = await fetchAiProviders({ page: query.page, pageSize: query.pageSize });
    if (!error && data) {
      providers.value = data.records;
      total.value = data.total;
    }
  } finally {
    loading.value = false;
  }
}

function handleAdd() {
  editingId.value = null;
  resetForm();
  dialogVisible.value = true;
}

function handleEdit(row: Api.PetPoster.AiProvider) {
  editingId.value = row.id;
  form.name = row.name;
  form.base_url = row.baseUrl;
  form.api_key = '';
  form.model_name = row.modelName;
  form.timeout = row.timeout;
  form.is_active = row.isActive;
  form.priority = row.priority;
  dialogVisible.value = true;
}

async function handleSubmit() {
  if (!form.name || !form.base_url || !form.model_name) {
    ElMessage.warning(t('page.petposter.aiProviders.apiKeyRequired'));
    return;
  }
  if (editingId.value) {
    const payload: Record<string, unknown> = { ...form };
    if (!payload.api_key) delete payload.api_key;
    const { error } = await updateAiProvider(editingId.value, payload as Partial<Api.PetPoster.AiProviderForm>);
    if (!error) {
      ElMessage.success(t('page.petposter.aiProviders.updateSuccess'));
      dialogVisible.value = false;
      loadData();
    } else {
      ElMessage.error(error.message || t('page.petposter.aiProviders.updateFailed'));
    }
  } else {
    if (!form.api_key) {
      ElMessage.warning(t('page.petposter.aiProviders.apiKeyRequired'));
      return;
    }
    const { error } = await createAiProvider(form);
    if (!error) {
      ElMessage.success(t('page.petposter.aiProviders.createSuccess'));
      dialogVisible.value = false;
      loadData();
    } else {
      ElMessage.error(error.message || t('page.petposter.aiProviders.createFailed'));
    }
  }
}

async function handleDelete(row: Api.PetPoster.AiProvider) {
  try {
    await ElMessageBox.confirm(
      t('page.petposter.aiProviders.confirmDelete', { name: row.name }),
      t('page.petposter.aiProviders.deleteConfirmTitle'),
      {
        confirmButtonText: t('page.petposter.common.confirm'),
        cancelButtonText: t('page.petposter.common.cancel'),
        type: 'warning'
      }
    );
  } catch {
    return;
  }
  const { error } = await deleteAiProvider(row.id);
  if (!error) {
    ElMessage.success(t('page.petposter.aiProviders.deleted'));
    loadData();
  } else {
    ElMessage.error(error.message || t('page.petposter.aiProviders.deleteFailed'));
  }
}

async function handleToggle(row: Api.PetPoster.AiProvider) {
  const { data, error } = await toggleAiProviderActive(row.id);
  if (!error && data) {
    ElMessage.success(data.isActive ? t('page.petposter.aiProviders.enabled') : t('page.petposter.aiProviders.disabled'));
    loadData();
  } else if (error) {
    ElMessage.error(error.message || t('page.petposter.aiProviders.toggleFailed'));
  }
}

onMounted(loadData);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="page-wrapper">
    <ElCard class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">{{ $t('page.petposter.aiProviders.pageTitle') }}</div>
            <div class="card-subtitle">{{ $t('page.petposter.aiProviders.pageSubtitle') }}</div>
          </div>
          <ElButton type="primary" @click="handleAdd">
            <SvgIcon icon="material-symbols:add-rounded" class="mr-4px text-icon" />
            {{ $t('page.petposter.aiProviders.addProvider') }}
          </ElButton>
        </div>
      </template>

      <ElTable v-loading="loading" :data="providers" stripe row-key="id">
        <ElTableColumn prop="id" label="ID" width="60" align="center" />
        <ElTableColumn prop="name" :label="$t('page.petposter.aiProviders.name')" min-width="120" show-overflow-tooltip />
        <ElTableColumn prop="baseUrl" :label="$t('page.petposter.aiProviders.baseUrl')" min-width="220" show-overflow-tooltip />
        <ElTableColumn prop="apiKey" :label="$t('page.petposter.aiProviders.apiKey')" min-width="140" show-overflow-tooltip />
        <ElTableColumn prop="modelName" :label="$t('page.petposter.aiProviders.modelName')" min-width="140" show-overflow-tooltip />
        <ElTableColumn prop="timeout" :label="$t('page.petposter.aiProviders.timeout')" width="90" align="center" />
        <ElTableColumn prop="priority" :label="$t('page.petposter.aiProviders.priority')" width="80" align="center" />
        <ElTableColumn :label="$t('page.petposter.aiProviders.isActive')" width="80" align="center">
          <template #default="{ row }">
            <ElTag :type="row.isActive ? 'success' : 'info'" size="small">
              {{ row.isActive ? $t('page.petposter.aiProviders.enableAction') : $t('page.petposter.aiProviders.disableAction') }}
            </ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.common.operations')" width="180" fixed="right" align="center">
          <template #default="{ row }">
            <ElButton link type="primary" size="small" @click="handleEdit(row)">
              {{ $t('page.petposter.aiProviders.dialogTitleEdit') }}
            </ElButton>
            <ElButton link :type="row.isActive ? 'warning' : 'success'" size="small" @click="handleToggle(row)">
              {{ row.isActive ? $t('page.petposter.aiProviders.disableAction') : $t('page.petposter.aiProviders.enableAction') }}
            </ElButton>
            <ElButton link type="danger" size="small" @click="handleDelete(row)">
              {{ $t('page.petposter.aiProviders.deleteConfirmTitle') }}
            </ElButton>
          </template>
        </ElTableColumn>
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

    <ElDialog
      v-model="dialogVisible"
      :title="editingId ? $t('page.petposter.aiProviders.dialogTitleEdit') : $t('page.petposter.aiProviders.dialogTitleAdd')"
      width="520px"
      destroy-on-close
    >
      <ElForm :model="form" label-width="100px">
        <ElFormItem :label="$t('page.petposter.aiProviders.name')" required>
          <ElInput v-model="form.name" placeholder="RightCode / OpenAI" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.baseUrl')" required>
          <ElInput v-model="form.base_url" placeholder="https://api.example.com/v1" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.apiKey')" :required="!editingId">
          <ElInput
            v-model="form.api_key"
            type="password"
            show-password
            :placeholder="editingId ? $t('page.petposter.aiProviders.apiKeyEditPlaceholder') : ''"
          />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.modelName')" required>
          <ElInput v-model="form.model_name" placeholder="gpt-image-2" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.timeout')">
          <ElInputNumber v-model="form.timeout" :min="10" :max="600" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.priority')">
          <ElInputNumber v-model="form.priority" :min="0" :max="100" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.aiProviders.enableAction')">
          <ElSwitch v-model="form.is_active" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">{{ $t('page.petposter.common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleSubmit">{{ $t('page.petposter.common.confirm') }}</ElButton>
      </template>
    </ElDialog>
  </ElSpace>
</template>
