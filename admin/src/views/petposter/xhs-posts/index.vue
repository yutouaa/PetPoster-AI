<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  createXhsPost,
  deleteXhsPost,
  fetchXhsPosts,
  fetchXhsStats,
  generateXhsContent,
  publishXhsPost,
  updateXhsPost
} from '@/service/api';

defineOptions({ name: 'PetposterXhsPosts' });

const { t } = useI18n();

const loading = ref(false);
const posts = ref<Api.PetPoster.XhsPost[]>([]);
const total = ref(0);
const query = reactive({ page: 1, pageSize: 20, status: '' });

const dialogVisible = ref(false);
const editingId = ref<number | null>(null);
const form = reactive({
  title: '',
  content: '',
  image_urls: [] as string[],
  tags: [] as string[],
  status: 'draft',
  scheduled_at: null as string | null,
  llm_prompt: null as string | null
});

const generateDialogVisible = ref(false);
const generatePostId = ref<number | null>(null);
const generatePrompt = ref('');
const generating = ref(false);
const tagInput = ref('');

const statusCounts = reactive({ published: 0, scheduled: 0, draft: 0, failed: 0, total: 0 });

const stats = computed(() => ({
  all: statusCounts.total,
  published: statusCounts.published,
  scheduled: statusCounts.scheduled,
  draft: statusCounts.draft
}));

async function loadStats() {
  const { data, error } = await fetchXhsStats();
  if (!error && data) {
    statusCounts.published = data.published;
    statusCounts.scheduled = data.scheduled;
    statusCounts.draft = data.draft;
    statusCounts.failed = data.failed;
    statusCounts.total = data.total;
  }
}

const statusOptions = computed(() => [
  { label: t('page.petposter.xhs.statusAll'), value: '' },
  { label: t('page.petposter.xhs.statusDraft'), value: 'draft' },
  { label: t('page.petposter.xhs.statusScheduled'), value: 'scheduled' },
  { label: t('page.petposter.xhs.statusPublished'), value: 'published' },
  { label: t('page.petposter.xhs.statusFailed'), value: 'failed' }
]);

function resetForm() {
  form.title = '';
  form.content = '';
  form.image_urls = [];
  form.tags = [];
  form.status = 'draft';
  form.scheduled_at = null;
  form.llm_prompt = null;
}

async function loadData() {
  loading.value = true;
  try {
    const params: { page: number; pageSize: number; status?: string } = {
      page: query.page,
      pageSize: query.pageSize
    };
    if (query.status) params.status = query.status;
    const [listRes] = await Promise.all([fetchXhsPosts(params), loadStats()]);
    if (!listRes.error && listRes.data) {
      posts.value = listRes.data.records;
      total.value = listRes.data.total;
    } else if (listRes.error) {
      ElMessage.error(listRes.error.message || t('page.petposter.common.loadFailed'));
    }
  } finally {
    loading.value = false;
  }
}

function handleAdd() {
  resetForm();
  editingId.value = null;
  dialogVisible.value = true;
}

function handleEdit(row: Api.PetPoster.XhsPost) {
  editingId.value = row.id;
  form.title = row.title;
  form.content = row.content;
  form.image_urls = [...row.imageUrls];
  form.tags = [...row.tags];
  form.status = row.status;
  form.scheduled_at = row.scheduledAt;
  form.llm_prompt = row.llmPrompt;
  dialogVisible.value = true;
}

async function handleSubmit() {
  if (!form.title.trim()) {
    ElMessage.warning(t('page.petposter.xhs.titleRequired'));
    return;
  }
  const payload: Api.PetPoster.XhsPostForm = {
    title: form.title,
    content: form.content,
    image_urls: form.image_urls,
    tags: form.tags,
    status: form.status,
    scheduled_at: form.scheduled_at,
    llm_prompt: form.llm_prompt
  };

  if (editingId.value) {
    const { error } = await updateXhsPost(editingId.value, payload);
    if (!error) {
      ElMessage.success(t('page.petposter.xhs.updateSuccess'));
      dialogVisible.value = false;
      loadData();
    } else {
      ElMessage.error(error.message || t('page.petposter.xhs.updateFailed'));
    }
  } else {
    const { error } = await createXhsPost(payload);
    if (!error) {
      ElMessage.success(t('page.petposter.xhs.createSuccess'));
      dialogVisible.value = false;
      loadData();
    } else {
      ElMessage.error(error.message || t('page.petposter.xhs.createFailed'));
    }
  }
}

async function handleDelete(row: Api.PetPoster.XhsPost) {
  try {
    await ElMessageBox.confirm(
      t('page.petposter.xhs.confirmDelete', { title: row.title }),
      t('page.petposter.xhs.confirmTitle')
    );
  } catch {
    return;
  }
  const { error } = await deleteXhsPost(row.id);
  if (!error) {
    ElMessage.success(t('page.petposter.xhs.deleteSuccess'));
    loadData();
  } else {
    ElMessage.error(error.message || t('page.petposter.xhs.deleteFailed'));
  }
}

function openGenerateDialog(row: Api.PetPoster.XhsPost) {
  generatePostId.value = row.id;
  generatePrompt.value = row.llmPrompt || '';
  generateDialogVisible.value = true;
}

async function handleGenerate() {
  if (!generatePrompt.value.trim()) {
    ElMessage.warning(t('page.petposter.xhs.promptRequired'));
    return;
  }
  if (!generatePostId.value) return;
  generating.value = true;
  try {
    const { data, error } = await generateXhsContent(generatePostId.value, generatePrompt.value);
    if (!error && data) {
      ElMessage.success(t('page.petposter.xhs.aiGenSuccess'));
      generateDialogVisible.value = false;
      loadData();
    } else if (error) {
      ElMessage.error(error.message || t('page.petposter.xhs.generateFailed'));
    }
  } finally {
    generating.value = false;
  }
}

async function handlePublish(row: Api.PetPoster.XhsPost) {
  try {
    await ElMessageBox.confirm(
      t('page.petposter.xhs.confirmPublish', { title: row.title }),
      t('page.petposter.xhs.confirmTitle')
    );
  } catch {
    return;
  }
  const { error } = await publishXhsPost(row.id);
  if (!error) {
    ElMessage.success(t('page.petposter.xhs.publishSuccess'));
    loadData();
  } else {
    ElMessage.error(error.message || t('page.petposter.xhs.publishFailed'));
  }
}

type TagType = 'success' | 'warning' | 'info' | 'primary' | 'danger';

function getStatusType(status: string): TagType {
  const map: Record<string, TagType> = {
    draft: 'info',
    scheduled: 'warning',
    published: 'success',
    failed: 'danger'
  };
  return map[status] || 'info';
}

function getStatusLabel(status: string) {
  const map: Record<string, string> = {
    draft: t('page.petposter.xhs.statusDraft'),
    scheduled: t('page.petposter.xhs.statusScheduled'),
    published: t('page.petposter.xhs.statusPublished'),
    failed: t('page.petposter.xhs.statusFailed')
  };
  return map[status] || status;
}

function handleTagInput() {
  if (tagInput.value.trim()) {
    form.tags.push(tagInput.value.trim());
    tagInput.value = '';
  }
}

function removeTag(index: number) {
  form.tags.splice(index, 1);
}

onMounted(loadData);
</script>

<template>
  <div class="min-h-500px flex-col-stretch gap-16px overflow-hidden lt-sm:overflow-auto">
    <!-- Stats bar -->
    <ElRow :gutter="16">
      <ElCol :span="6">
        <ElStatistic :title="$t('page.petposter.xhs.statsTotal')" :value="stats.all" />
      </ElCol>
      <ElCol :span="6">
        <ElStatistic :title="$t('page.petposter.xhs.statsPublished')" :value="stats.published" />
      </ElCol>
      <ElCol :span="6">
        <ElStatistic :title="$t('page.petposter.xhs.statsScheduled')" :value="stats.scheduled" />
      </ElCol>
      <ElCol :span="6">
        <ElStatistic :title="$t('page.petposter.xhs.statsDraft')" :value="stats.draft" />
      </ElCol>
    </ElRow>

    <!-- Toolbar -->
    <ElCard shadow="never">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-12px">
          <ElSelect
            v-model="query.status"
            :placeholder="$t('page.petposter.xhs.statusFilter')"
            clearable
            style="width: 140px"
            @change="loadData"
          >
            <ElOption v-for="opt in statusOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </ElSelect>
        </div>
        <ElButton type="primary" @click="handleAdd">{{ $t('page.petposter.xhs.addPost') }}</ElButton>
      </div>
    </ElCard>

    <!-- Table -->
    <ElCard shadow="never" class="flex-1">
      <ElTable v-loading="loading" :data="posts" stripe>
        <ElTableColumn prop="id" :label="$t('page.petposter.xhs.id')" width="60" />
        <ElTableColumn prop="title" :label="$t('page.petposter.xhs.titleField')" min-width="180" show-overflow-tooltip />
        <ElTableColumn :label="$t('page.petposter.xhs.status')" width="100">
          <template #default="{ row }">
            <ElTag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</ElTag>
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.xhs.tags')" min-width="160">
          <template #default="{ row }">
            <ElTag v-for="(tag, i) in row.tags.slice(0, 3)" :key="i" size="small" class="mr-4px">
              {{ tag }}
            </ElTag>
            <span v-if="row.tags.length > 3" class="text-12px text-gray">+{{ row.tags.length - 3 }}</span>
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.xhs.scheduledAt')" width="160">
          <template #default="{ row }">
            {{ row.scheduledAt ? row.scheduledAt.replace('T', ' ').slice(0, 16) : '-' }}
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.xhs.publishedAt')" width="160">
          <template #default="{ row }">
            {{ row.publishedAt ? row.publishedAt.replace('T', ' ').slice(0, 16) : '-' }}
          </template>
        </ElTableColumn>
        <ElTableColumn :label="$t('page.petposter.common.operations')" width="260" fixed="right">
          <template #default="{ row }">
            <ElButton size="small" @click="openGenerateDialog(row)">{{ $t('page.petposter.xhs.aiGenerate') }}</ElButton>
            <ElButton v-if="row.status !== 'published'" size="small" type="success" @click="handlePublish(row)">
              {{ $t('page.petposter.xhs.publish') }}
            </ElButton>
            <ElButton size="small" @click="handleEdit(row)">{{ $t('page.petposter.aiProviders.dialogTitleEdit') }}</ElButton>
            <ElButton size="small" type="danger" @click="handleDelete(row)">{{ $t('page.petposter.aiProviders.deleteConfirmTitle') }}</ElButton>
          </template>
        </ElTableColumn>
      </ElTable>

      <div class="mt-16px flex justify-end">
        <ElPagination
          v-model:current-page="query.page"
          v-model:page-size="query.pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadData"
        />
      </div>
    </ElCard>

    <!-- Create/Edit dialog -->
    <ElDialog
      v-model="dialogVisible"
      :title="editingId ? $t('page.petposter.xhs.dialogTitleEdit') : $t('page.petposter.xhs.dialogTitleAdd')"
      width="640px"
      destroy-on-close
    >
      <ElForm label-width="100px">
        <ElFormItem :label="$t('page.petposter.xhs.titleField')">
          <ElInput v-model="form.title" :placeholder="$t('page.petposter.xhs.titleFieldPlaceholder')" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.xhs.content')">
          <ElInput v-model="form.content" type="textarea" :rows="6" :placeholder="$t('page.petposter.xhs.contentPlaceholder')" />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.xhs.tags')">
          <div class="flex flex-wrap items-center gap-6px">
            <ElTag v-for="(tag, i) in form.tags" :key="i" closable size="small" @close="removeTag(i)">
              {{ tag }}
            </ElTag>
            <ElInput
              v-model="tagInput"
              style="width: 120px"
              size="small"
              :placeholder="$t('page.petposter.xhs.tagInputPlaceholder')"
              @keyup.enter="handleTagInput"
            />
          </div>
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.xhs.status')">
          <ElSelect v-model="form.status" style="width: 160px">
            <ElOption :label="$t('page.petposter.xhs.statusDraft')" value="draft" />
            <ElOption :label="$t('page.petposter.xhs.statusScheduled')" value="scheduled" />
          </ElSelect>
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.xhs.scheduledAtFull')">
          <ElDatePicker
            v-model="form.scheduled_at"
            type="datetime"
            :placeholder="$t('page.petposter.xhs.selectScheduleTime')"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </ElFormItem>
        <ElFormItem :label="$t('page.petposter.xhs.llmPrompt')">
          <ElInput v-model="form.llm_prompt" type="textarea" :rows="3" :placeholder="$t('page.petposter.xhs.llmPromptPlaceholder')" />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="dialogVisible = false">{{ $t('page.petposter.common.cancel') }}</ElButton>
        <ElButton type="primary" @click="handleSubmit">{{ $t('page.petposter.common.confirm') }}</ElButton>
      </template>
    </ElDialog>

    <!-- AI content generation dialog -->
    <ElDialog
      v-model="generateDialogVisible"
      :title="$t('page.petposter.xhs.aiGenDialogTitle')"
      width="500px"
      destroy-on-close
    >
      <ElForm label-width="80px">
        <ElFormItem :label="$t('page.petposter.xhs.llmPrompt')">
          <ElInput
            v-model="generatePrompt"
            type="textarea"
            :rows="5"
            :placeholder="$t('page.petposter.xhs.aiGenPromptPlaceholder')"
          />
        </ElFormItem>
      </ElForm>
      <template #footer>
        <ElButton @click="generateDialogVisible = false">{{ $t('page.petposter.common.cancel') }}</ElButton>
        <ElButton type="primary" :loading="generating" @click="handleGenerate">
          {{ $t('page.petposter.xhs.aiGenButton') }}
        </ElButton>
      </template>
    </ElDialog>
  </div>
</template>
