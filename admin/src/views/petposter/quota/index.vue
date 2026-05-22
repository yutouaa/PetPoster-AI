<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage } from 'element-plus';
import { adjustQuota, fetchQuotaTransactions, fetchQuotaUsers } from '@/service/api';

defineOptions({ name: 'PetposterQuota' });

const { t } = useI18n();

const loading = ref(false);
const quotas = ref<Api.PetPoster.UserQuota[]>([]);
const total = ref(0);
const query = reactive({ page: 1, pageSize: 20, search: '' });

const adjustVisible = ref(false);
const adjustForm = reactive({ user_id: '', amount: 0, remark: '' });

const txVisible = ref(false);
const txLoading = ref(false);
const txList = ref<Api.PetPoster.QuotaTransaction[]>([]);
const txTotal = ref(0);
const txQuery = reactive({ page: 1, pageSize: 10, userId: '' });

async function loadData() {
  loading.value = true;
  try {
    const { data, error } = await fetchQuotaUsers({ page: query.page, pageSize: query.pageSize, search: query.search });
    if (!error && data) {
      quotas.value = data.records;
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

function openAdjust(row?: Api.PetPoster.UserQuota) {
  adjustForm.user_id = row?.userId || '';
  adjustForm.amount = 0;
  adjustForm.remark = '';
  adjustVisible.value = true;
}

async function handleAdjust() {
  if (!adjustForm.user_id) {
    ElMessage.warning(t('page.petposter.quota.needUserId'));
    return;
  }
  if (adjustForm.amount === 0) {
    ElMessage.warning(t('page.petposter.quota.amountNotZero'));
    return;
  }
  const { error } = await adjustQuota(adjustForm);
  if (!error) {
    ElMessage.success(t('page.petposter.quota.adjustSuccess'));
    adjustVisible.value = false;
    loadData();
  } else {
    ElMessage.error(error.message || t('page.petposter.quota.adjustFailed'));
  }
}

function openTransactions(row: Api.PetPoster.UserQuota) {
  txQuery.userId = row.userId;
  txQuery.page = 1;
  txVisible.value = true;
  loadTransactions();
}

async function loadTransactions() {
  txLoading.value = true;
  try {
    const { data, error } = await fetchQuotaTransactions({
      page: txQuery.page,
      pageSize: txQuery.pageSize,
      userId: txQuery.userId
    });
    if (!error && data) {
      txList.value = data.records;
      txTotal.value = data.total;
    }
  } finally {
    txLoading.value = false;
  }
}

function txTypeLabel(type: string) {
  const map: Record<string, string> = {
    recharge: t('page.petposter.quota.typeRecharge'),
    consume: t('page.petposter.quota.typeConsume'),
    refund: t('page.petposter.quota.typeRefund'),
    admin_adjust: t('page.petposter.quota.typeAdjust')
  };
  return map[type] || type;
}

function txTypeTag(type: string): 'success' | 'danger' | 'warning' | 'info' {
  const map: Record<string, 'success' | 'danger' | 'warning' | 'info'> = {
    recharge: 'success',
    consume: 'danger',
    refund: 'warning',
    admin_adjust: 'info'
  };
  return map[type] || 'info';
}

onMounted(loadData);
</script>

<template>
  <ElSpace direction="vertical" fill :size="16" class="page-wrapper">
    <ElCard class="card-wrapper">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">{{ $t('page.petposter.quota.pageTitle') }}</div>
            <div class="card-subtitle">{{ $t('page.petposter.quota.pageSubtitle') }}</div>
          </div>
          <div class="header-actions">
            <ElInput
              v-model="query.search"
              :placeholder="$t('page.petposter.quota.searchPlaceholder')"
              clearable
              style="width: 200px"
              @keyup.enter="handleSearch"
              @clear="handleSearch"
            />
            <ElButton type="primary" @click="openAdjust()">
              <SvgIcon icon="material-symbols:add-rounded" class="mr-4px text-icon" />
              {{ $t('page.petposter.quota.adjust') }}
            </ElButton>
          </div>
        </div>
      </template>

      <ElTable v-loading="loading" :data="quotas" stripe row-key="id">
        <ElTableColumn prop="userId" :label="$t('page.petposter.quota.userId')" min-width="180" show-overflow-tooltip />
        <ElTableColumn prop="balance" :label="$t('page.petposter.quota.balance')" width="100" align="center">
          <template #default="{ row }">
            <span :class="row.balance <= 0 ? 'text-danger' : ''">{{ row.balance }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="totalPurchased" :label="$t('page.petposter.quota.totalPurchased')" width="100" align="center" />
        <ElTableColumn prop="totalConsumed" :label="$t('page.petposter.quota.totalConsumed')" width="100" align="center" />
        <ElTableColumn prop="updatedAt" :label="$t('page.petposter.quota.updatedAt')" min-width="160" show-overflow-tooltip />
        <ElTableColumn :label="$t('page.petposter.common.operations')" width="160" fixed="right" align="center">
          <template #default="{ row }">
            <ElButton link type="primary" size="small" @click="openAdjust(row)">
              {{ $t('page.petposter.quota.adjust') }}
            </ElButton>
            <ElButton link type="info" size="small" @click="openTransactions(row)">
              {{ $t('page.petposter.quota.viewTransactions') }}
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

    <ElDialog v-model="adjustVisible" :title="$t('page.petposter.quota.adjustDialogTitle')" width="440px" destroy-on-close>
      <ElForm :model="adjustForm" label-width="80px">
        <ElFormItem :label="$t('page.petposter.quota.userId')" required>
          <ElInput v-model="adjustForm.user_id" :placeholder="$t('page.petposter.quota.searchPlaceholder')" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.quota.amountLabel')" required>
          <ElInputNumber v-model="adjustForm.amount" :step="1" :placeholder="$t('page.petposter.quota.amountTip')" style="width: 100%" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.quota.remarkLabel')">
          <ElInput v-model="adjustForm.remark" type="textarea" :rows="2" :placeholder="$t('page.petposter.quota.remarkPlaceholder')" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="adjustVisible = false">{{ $t('page.petposter.common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleAdjust">{{ $t('page.petposter.common.confirm') }}</ElButton>
      </template>
    </ElDialog>

    <ElDialog v-model="txVisible" :title="$t('page.petposter.quota.txDialogTitle')" width="700px" destroy-on-close>
      <ElTable v-loading="txLoading" :data="txList" stripe size="small">
        <ElTableColumn prop="id" label="ID" width="60" align="center" />
        <ElTableColumn :label="$t('page.petposter.quota.txType')" width="110" align="center">
          <template #default="{ row }">
            <ElTag :type="txTypeTag(row.type)" size="small">{{ txTypeLabel(row.type) }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.quota.txAmount')" width="80" align="center">
          <template #default="{ row }">
            <span :class="row.amount > 0 ? 'text-success' : 'text-danger'">
              {{ row.amount > 0 ? `+${row.amount}` : row.amount }}
            </span>
          </template>
        </ElTableColumn>
        <ElTableColumn prop="balanceAfter" :label="$t('page.petposter.quota.txBalanceAfter')" width="100" align="center" />
        <ElTableColumn prop="remark" :label="$t('page.petposter.quota.txRemark')" min-width="140" show-overflow-tooltip />
        <ElTableColumn prop="createdAt" :label="$t('page.petposter.quota.txCreatedAt')" min-width="160" show-overflow-tooltip />
      </ElTable>
      <div class="pagination-bar">
        <ElPagination
          v-model:current-page="txQuery.page"
          :total="txTotal"
          :page-size="txQuery.pageSize"
          layout="total, prev, pager, next"
          @current-change="loadTransactions"
        />
      </div>
    </ElDialog>
  </ElSpace>
</template>

<style scoped>
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.text-danger {
  color: var(--el-color-danger);
}

.text-success {
  color: var(--el-color-success);
}
</style>
