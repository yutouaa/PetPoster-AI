<script setup lang="ts">
import { computed, nextTick, onMounted, reactive, ref } from 'vue';
import type { UploadRequestOptions } from 'element-plus';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useI18n } from 'vue-i18n';
import {
  archiveTemplate,
  batchArchiveTemplates,
  createTemplate,
  deleteTemplate,
  duplicateTemplate,
  exportTemplates,
  fetchTemplateStats,
  fetchTemplates,
  importTemplates,
  restoreTemplate,
  toggleTemplateStatus,
  updateTemplate,
  uploadPetPosterImages
} from '@/service/api';
import StatsDrawer from './modules/stats-drawer.vue';

const { t } = useI18n();

defineOptions({ name: 'PetposterTemplates' });

type ImageField = 'cover_url' | 'preview_url';
type ViewMode = 'gallery' | 'table';

interface TemplateForm {
  name: string;
  category: string;
  description: string;
  cover_url: string;
  preview_url: string;
  prompt_template: string;
  negative_prompt: string;
  config: string;
  sort_order: number;
  is_active: boolean;
}

const loading = ref(false);
const tableData = ref<Api.PetPoster.Template[]>([]);
const total = ref(0);
const viewMode = ref<ViewMode>('gallery');
const drawerVisible = ref(false);
const drawerTitle = ref('新增模板');
const activeTab = ref('base');
const editingId = ref<number | null>(null);
const uploadingField = ref<ImageField | null>(null);

const searchParams = reactive({
  page: 1,
  pageSize: 12,
  keyword: '',
  category: '',
  includeArchived: false
});

const statsVisible = ref(false);
const statsLoading = ref(false);
const statsData = ref<Api.PetPoster.TemplateStats | null>(null);
const statsTemplate = ref<Api.PetPoster.Template | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

// 批量归档：两种视图共享 selection 状态
const selectedIds = ref<number[]>([]);
const tableRef = ref<{
  clearSelection: () => void;
  toggleRowSelection: (row: Api.PetPoster.Template, selected?: boolean) => void;
} | null>(null);

function isSelected(id: number) {
  return selectedIds.value.includes(id);
}

function toggleCardSelection(id: number, checked: boolean) {
  if (checked) {
    if (!selectedIds.value.includes(id)) selectedIds.value.push(id);
  } else {
    selectedIds.value = selectedIds.value.filter(x => x !== id);
  }
}

function handleSelectionChange(rows: Api.PetPoster.Template[]) {
  selectedIds.value = rows.map(r => r.id);
}

function clearSelection() {
  selectedIds.value = [];
  tableRef.value?.clearSelection();
}

function syncTableSelection() {
  if (!tableRef.value) return;
  const ids = new Set(selectedIds.value);
  tableData.value.forEach(row => {
    if (ids.has(row.id)) tableRef.value?.toggleRowSelection(row, true);
  });
}

const allOnPageSelected = computed(() => {
  return tableData.value.length > 0 && tableData.value.every(t => selectedIds.value.includes(t.id));
});

function selectAllOnPage() {
  if (allOnPageSelected.value) {
    const pageIds = new Set(tableData.value.map(t => t.id));
    selectedIds.value = selectedIds.value.filter(id => !pageIds.has(id));
  } else {
    const merged = new Set(selectedIds.value);
    tableData.value.forEach(t => merged.add(t.id));
    selectedIds.value = [...merged];
  }
}

async function handleBatchArchive() {
  if (selectedIds.value.length === 0) {
    ElMessage.warning(t('page.petposter.templates.selectFirst'));
    return;
  }
  try {
    await ElMessageBox.confirm(
      t('page.petposter.templates.confirmBatchArchive', { count: selectedIds.value.length }),
      t('common.confirm'),
      { type: 'warning' }
    );
  } catch {
    return;
  }
  const { data, error } = await batchArchiveTemplates([...selectedIds.value]);
  if (!error && data) {
    ElMessage.success(t('page.petposter.templates.archiveSuccess', {
      archived: data.archived,
      skipped: data.skipped
    }));
    clearSelection();
    loadData();
  } else if (error) {
    ElMessage.error(error.message || '批量归档失败');
  }
}

// 跨视图共享 selection：切到 table 时回显勾选到 ElTable
async function handleViewModeChange(val: string | number | boolean | undefined) {
  viewMode.value = (val as ViewMode) ?? 'gallery';
  if (viewMode.value === 'table') {
    await nextTick();
    syncTableSelection();
  }
}

const formData = reactive<TemplateForm>({
  name: '',
  category: '',
  description: '',
  cover_url: '',
  preview_url: '',
  prompt_template: '',
  negative_prompt: '',
  config: '{}',
  sort_order: 0,
  is_active: true
});

const categoryOptions = computed(() => {
  const defaults = ['油画', '水彩', '赛博朋克', '电影海报', '节日主题', '证件照'];
  const categories = tableData.value.map(item => item.category).filter(Boolean);

  return Array.from(new Set([...defaults, ...categories]));
});

const pageStats = computed(() => {
  const activeCount = tableData.value.filter(item => item.isActive).length;
  const withImageCount = tableData.value.filter(item => item.coverUrl || item.previewUrl).length;
  const categoryCount = new Set(tableData.value.map(item => item.category).filter(Boolean)).size;

  return [
    { label: '当前页模板', value: tableData.value.length, icon: 'material-symbols:dashboard-customize-rounded' },
    { label: '已上架', value: activeCount, icon: 'material-symbols:toggle-on-rounded' },
    { label: '有海报图', value: withImageCount, icon: 'material-symbols:image-rounded' },
    { label: '分类覆盖', value: categoryCount, icon: 'material-symbols:category-rounded' }
  ];
});

const previewImageUrl = computed(() => resolveImageUrl(formData.preview_url || formData.cover_url));
const coverImageUrl = computed(() => resolveImageUrl(formData.cover_url));

async function loadData() {
  loading.value = true;
  try {
    const { data, error } = await fetchTemplates(searchParams);
    if (!error && data) {
      tableData.value = data.records;
      total.value = data.total;
    }
  } finally {
    loading.value = false;
  }
}

function handleSearch() {
  searchParams.page = 1;
  loadData();
}

function handleReset() {
  searchParams.keyword = '';
  searchParams.category = '';
  searchParams.page = 1;
  loadData();
}

function resetForm() {
  formData.name = '';
  formData.category = '';
  formData.description = '';
  formData.cover_url = '';
  formData.preview_url = '';
  formData.prompt_template = '';
  formData.negative_prompt = '';
  formData.config = '{}';
  formData.sort_order = 0;
  formData.is_active = true;
  activeTab.value = 'base';
}

function handleCreate() {
  editingId.value = null;
  drawerTitle.value = '新增模板';
  resetForm();
  drawerVisible.value = true;
}

function fillForm(row: Api.PetPoster.Template) {
  editingId.value = row.id;
  drawerTitle.value = `编辑模板：${row.name}`;
  formData.name = row.name;
  formData.category = row.category;
  formData.description = row.description;
  formData.cover_url = row.coverUrl;
  formData.preview_url = row.previewUrl;
  formData.prompt_template = row.promptTemplate;
  formData.negative_prompt = row.negativePrompt;
  formData.config = row.config || '{}';
  formData.sort_order = row.sortOrder;
  formData.is_active = row.isActive;
}

function handleEdit(row: Api.PetPoster.Template, tab = 'base') {
  fillForm(row);
  activeTab.value = tab;
  drawerVisible.value = true;
}

function getServiceBaseUrl() {
  if (import.meta.env.DEV && import.meta.env.VITE_HTTP_PROXY === 'Y') {
    return '/proxy-default';
  }

  return import.meta.env.VITE_SERVICE_BASE_URL || '';
}

function resolveImageUrl(url?: string | null) {
  if (!url) return '';
  if (/^(https?:)?\/\//.test(url) || url.startsWith('data:') || url.startsWith('blob:')) return url;

  const baseUrl = getServiceBaseUrl().replace(/\/$/, '');
  const path = url.startsWith('/') ? url : `/${url}`;

  return `${baseUrl}${path}`;
}

function getPosterUrl(row: Api.PetPoster.Template) {
  return resolveImageUrl(row.previewUrl || row.coverUrl);
}

function getCoverUrl(row: Api.PetPoster.Template) {
  return resolveImageUrl(row.coverUrl);
}

function getPreviewList(row: Api.PetPoster.Template) {
  return [getPosterUrl(row), getCoverUrl(row)].filter(Boolean);
}

function getDescription(row: Api.PetPoster.Template) {
  return row.description || row.promptTemplate || '未填写描述，建议补充模板用途和适用宠物类型。';
}

function formatDate(value?: string) {
  if (!value) return '-';

  return new Date(value).toLocaleDateString('zh-CN');
}

function beforeImageUpload(file: File) {
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请上传图片文件');
    return false;
  }

  if (file.size / 1024 / 1024 > 10) {
    ElMessage.warning('图片大小不能超过 10MB');
    return false;
  }

  return true;
}

async function handleImageUpload(options: UploadRequestOptions, field: ImageField) {
  uploadingField.value = field;
  try {
    const { data, error } = await uploadPetPosterImages([options.file as File]);
    const url = data?.urls?.[0];

    if (error || !url) {
      throw new Error('上传失败');
    }

    formData[field] = url;
    options.onSuccess?.(data);
    ElMessage.success(field === 'cover_url' ? '封面图已上传' : '预览图已上传');
  } catch (error) {
    options.onError?.(error as any);
    ElMessage.error('图片上传失败');
  } finally {
    uploadingField.value = null;
  }
}

function clearImage(field: ImageField) {
  formData[field] = '';
}

function useCoverAsPreview() {
  if (!formData.cover_url) {
    ElMessage.warning('请先上传或填写封面图');
    return;
  }

  formData.preview_url = formData.cover_url;
}

function formatConfig() {
  try {
    formData.config = JSON.stringify(JSON.parse(formData.config || '{}'), null, 2);
    ElMessage.success('JSON 已格式化');
  } catch {
    ElMessage.warning('配置字段不是有效的 JSON 格式');
  }
}

async function handleSubmit() {
  if (!formData.name || !formData.category) {
    ElMessage.warning('请填写模板名称和分类');
    activeTab.value = 'base';
    return;
  }

  if (formData.config && formData.config.trim()) {
    try {
      JSON.parse(formData.config);
    } catch {
      ElMessage.warning('配置字段不是有效的 JSON 格式');
      activeTab.value = 'config';
      return;
    }
  }

  const payload: Api.PetPoster.TemplateCreate = { ...formData };

  if (editingId.value) {
    const { error } = await updateTemplate(editingId.value, payload);
    if (!error) {
      ElMessage.success('更新成功');
      drawerVisible.value = false;
      loadData();
    }
  } else {
    const { error } = await createTemplate(payload);
    if (!error) {
      ElMessage.success('创建成功');
      drawerVisible.value = false;
      loadData();
    }
  }
}

async function handleDelete(row: Api.PetPoster.Template) {
  try {
    await ElMessageBox.confirm(`确定归档模板「${row.name}」吗？归档后不再展示，但历史任务记录保留。`, '确认归档', {
      confirmButtonText: '归档',
      cancelButtonText: '取消',
      type: 'warning'
    });
    const { error } = await deleteTemplate(row.id);
    if (!error) {
      ElMessage.success('已归档');
      loadData();
    } else {
      ElMessage.error(error.message || '归档失败');
    }
  } catch {
    // 用户取消
  }
}

async function handleToggleStatus(row: Api.PetPoster.Template, val: boolean) {
  const { error } = await toggleTemplateStatus(row.id, val);
  if (!error) {
    ElMessage.success(val ? '已上架' : '已下架');
    loadData();
  } else {
    ElMessage.error(error.message || '切换失败');
  }
}

async function handleDuplicate(row: Api.PetPoster.Template) {
  const { error } = await duplicateTemplate(row.id);
  if (!error) {
    ElMessage.success('已复制为新副本');
    loadData();
  } else {
    ElMessage.error(error.message || '复制失败');
  }
}

async function handleArchive(row: Api.PetPoster.Template) {
  try {
    await ElMessageBox.confirm(`确定归档模板「${row.name}」？`, '归档确认', { type: 'warning' });
    const { error } = await archiveTemplate(row.id);
    if (!error) {
      ElMessage.success('已归档');
      loadData();
    } else {
      ElMessage.error(error.message || '归档失败');
    }
  } catch {
    // ignored
  }
}

async function handleRestore(row: Api.PetPoster.Template) {
  const { error } = await restoreTemplate(row.id);
  if (!error) {
    ElMessage.success('已恢复');
    loadData();
  } else {
    ElMessage.error(error.message || '恢复失败');
  }
}

async function openStats(row: Api.PetPoster.Template) {
  statsTemplate.value = row;
  statsVisible.value = true;
  statsLoading.value = true;
  try {
    const { data, error } = await fetchTemplateStats(row.id);
    if (!error && data) {
      statsData.value = data;
    } else if (error) {
      ElMessage.error(error.message || '获取统计失败');
    }
  } finally {
    statsLoading.value = false;
  }
}

async function handleExport() {
  const { data, error } = await exportTemplates();
  if (error || !data) {
    ElMessage.error(error?.message || '导出失败');
    return;
  }
  const blob = new Blob([JSON.stringify(data.templates, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `templates-${new Date().toISOString().slice(0, 10)}.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
  ElMessage.success(`已导出 ${data.count} 个模板`);
}

function triggerImport() {
  fileInput.value?.click();
}

async function handleImportFile(event: Event) {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;
  if (file.size > 1024 * 1024) {
    ElMessage.error('文件超过 1MB，请拆分后再导入');
    target.value = '';
    return;
  }
  try {
    const text = await file.text();
    const payload = JSON.parse(text);
    const list = Array.isArray(payload) ? payload : Array.isArray(payload.templates) ? payload.templates : null;
    if (!list) {
      ElMessage.error('文件格式不正确：需为模板数组或 { templates: [...] }');
      return;
    }
    const { data, error } = await importTemplates(list);
    if (!error && data) {
      ElMessage.success(`导入完成：新增 ${data.created}，更新 ${data.updated}，跳过 ${data.skipped}`);
      loadData();
    } else if (error) {
      ElMessage.error(error.message || '导入失败');
    }
  } catch (e) {
    ElMessage.error('解析 JSON 失败：' + (e instanceof Error ? e.message : '未知错误'));
  } finally {
    target.value = '';
  }
}

onMounted(() => {
  loadData();
});
</script>

<template>
  <div class="template-page" style="display: grid; gap: 16px;">
    <section
      class="template-hero"
      style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 16px;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 18px 20px;
        background: var(--el-bg-color);
      "
    >
      <div>
        <h2 style="margin: 0; color: var(--el-text-color-primary); font-size: 22px; font-weight: 800; line-height: 1.2;">
          模板资产库
        </h2>
        <p style="margin: 8px 0 0; color: var(--el-text-color-secondary); font-size: 13px;">
          优先管理海报视觉资产，快速维护分类、上下架状态、排序和生成提示词。
        </p>
      </div>
      <div style="display: flex; gap: 8px;">
        <ElButton size="large" @click="triggerImport">
          <SvgIcon icon="material-symbols:upload-rounded" class="mr-4px text-icon" />
          导入
        </ElButton>
        <ElButton size="large" @click="handleExport">
          <SvgIcon icon="material-symbols:download-rounded" class="mr-4px text-icon" />
          导出
        </ElButton>
        <ElButton type="primary" size="large" @click="handleCreate">
          <SvgIcon icon="material-symbols:add-rounded" class="mr-4px text-icon" />
          新增模板
        </ElButton>
        <input
          ref="fileInput"
          type="file"
          accept="application/json,.json"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
    </section>

    <section
      class="stats-strip"
      style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;"
    >
      <div
        v-for="item in pageStats"
        :key="item.label"
        class="stat-item"
        style="
          display: flex;
          align-items: center;
          gap: 12px;
          border: 1px solid var(--el-border-color-lighter);
          border-radius: 8px;
          padding: 14px;
          background: var(--el-bg-color);
        "
      >
        <div
          class="stat-icon"
          style="
            display: grid;
            width: 38px;
            height: 38px;
            flex: none;
            place-items: center;
            border-radius: 8px;
            background: rgb(217 119 87 / 12%);
            color: #d97757;
            font-size: 22px;
          "
        >
          <SvgIcon :icon="item.icon" />
        </div>
        <div>
          <strong style="display: block; color: var(--el-text-color-primary); font-size: 22px; line-height: 1;">
            {{ item.value }}
          </strong>
          <span style="display: block; margin-top: 6px; color: var(--el-text-color-secondary); font-size: 12px;">
            {{ item.label }}
          </span>
        </div>
      </div>
    </section>

    <section
      class="filter-panel"
      style="
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 14px;
        background: var(--el-bg-color);
      "
    >
      <div class="filter-fields" style="display: flex; flex: 1; flex-wrap: wrap; align-items: center; gap: 10px;">
        <ElInput
          v-model="searchParams.keyword"
          placeholder="搜索模板名称"
          clearable
          class="search-input"
          @clear="handleSearch"
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <SvgIcon icon="material-symbols:search-rounded" />
          </template>
        </ElInput>
        <ElSelect
          v-model="searchParams.category"
          placeholder="按分类筛选"
          clearable
          filterable
          class="category-select"
          @clear="handleSearch"
          @change="handleSearch"
        >
          <ElOption v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
        </ElSelect>
        <ElButton type="primary" @click="handleSearch">搜索</ElButton>
        <ElButton @click="handleReset">重置</ElButton>
      </div>
      <div style="display: flex; align-items: center; gap: 12px;">
        <template v-if="selectedIds.length > 0">
          <ElButton type="warning" size="small" @click="handleBatchArchive">
            <SvgIcon icon="material-symbols:archive-rounded" class="mr-4px text-icon" />
            {{ $t('page.petposter.templates.batchArchive') }}
            <span class="ml-4px op-80">({{ selectedIds.length }})</span>
          </ElButton>
          <ElButton size="small" plain @click="clearSelection">
            {{ $t('page.petposter.templates.clearSelection') }}
          </ElButton>
          <ElDivider direction="vertical" />
        </template>
        <ElButton
          v-if="viewMode === 'gallery' && tableData.length > 0"
          size="small"
          link
          @click="selectAllOnPage"
        >
          {{
            allOnPageSelected
              ? $t('page.petposter.templates.deselectAll')
              : $t('page.petposter.templates.selectAllOnPage')
          }}
        </ElButton>
        <ElCheckbox v-model="searchParams.includeArchived" @change="handleSearch">显示已归档</ElCheckbox>
        <ElRadioGroup :model-value="viewMode" size="small" @change="handleViewModeChange">
          <ElRadioButton label="gallery">网格</ElRadioButton>
          <ElRadioButton label="table">表格</ElRadioButton>
        </ElRadioGroup>
      </div>
    </section>

    <section
      v-loading="loading"
      class="content-panel"
      style="
        min-height: 360px;
        border: 1px solid var(--el-border-color-lighter);
        border-radius: 8px;
        padding: 16px;
        background: var(--el-bg-color);
      "
    >
      <template v-if="loading && !tableData.length">
        <div
          class="template-grid"
          style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px;"
        >
          <div
            v-for="n in 8"
            :key="`skeleton-${n}`"
            style="overflow: hidden; border: 1px solid var(--el-border-color-lighter); border-radius: 8px; background: var(--el-bg-color);"
          >
            <ElSkeleton animated>
              <template #template>
                <ElSkeletonItem variant="image" style="width: 100%; aspect-ratio: 4 / 3;" />
                <div style="padding: 14px; display: grid; gap: 10px;">
                  <ElSkeletonItem variant="h3" style="width: 60%;" />
                  <ElSkeletonItem variant="text" style="width: 90%;" />
                  <ElSkeletonItem variant="text" style="width: 70%;" />
                </div>
              </template>
            </ElSkeleton>
          </div>
        </div>
      </template>

      <template v-else-if="viewMode === 'gallery'">
        <div
          v-if="tableData.length"
          class="template-grid"
          style="display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px;"
        >
          <article
            v-for="row in tableData"
            :key="row.id"
            class="template-card"
            :class="{ 'is-selected': isSelected(row.id) }"
            style="
              overflow: hidden;
              border-radius: 8px;
              background: var(--el-bg-color);
            "
          >
            <div
              class="poster-frame"
              style="
                position: relative;
                overflow: hidden;
                aspect-ratio: 4 / 3;
                background: linear-gradient(135deg, var(--el-fill-color-light), var(--el-fill-color-extra-light));
              "
            >
              <ElCheckbox
                class="card-select"
                :class="{ 'is-selected': isSelected(row.id) }"
                :model-value="isSelected(row.id)"
                @click.stop
                @change="(v: string | number | boolean | undefined) => toggleCardSelection(row.id, Boolean(v))"
              />
              <ElImage
                v-if="getPosterUrl(row)"
                :src="getPosterUrl(row)"
                :preview-src-list="getPreviewList(row)"
                fit="cover"
                class="poster-image"
                style="width: 100%; height: 100%;"
                preview-teleported
              />
              <div
                v-else
                class="poster-placeholder"
                style="
                  display: grid;
                  width: 100%;
                  height: 100%;
                  place-items: center;
                  align-content: center;
                  gap: 8px;
                  color: var(--el-text-color-secondary);
                  font-size: 13px;
                "
              >
                <SvgIcon icon="material-symbols:add-photo-alternate-rounded" />
                <span>未上传海报</span>
              </div>
              <div
                class="poster-status"
                :class="{ inactive: !row.isActive }"
                :style="{
                  position: 'absolute',
                  top: '10px',
                  left: '44px',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  background: row.deletedAt
                    ? 'rgb(245 108 108 / 88%)'
                    : row.isActive ? 'rgb(103 194 58 / 92%)' : 'rgb(144 147 153 / 88%)',
                  color: '#fff',
                  fontSize: '12px',
                  fontWeight: '700'
                }"
              >
                {{ row.deletedAt ? '已归档' : row.isActive ? '已上架' : '已下架' }}
              </div>
              <div
                v-if="row.usageCount > 0"
                :style="{
                  position: 'absolute',
                  top: '10px',
                  right: '10px',
                  borderRadius: '6px',
                  padding: '4px 8px',
                  background: 'rgb(15 23 42 / 70%)',
                  color: '#fff',
                  fontSize: '11px',
                  fontWeight: '600',
                  backdropFilter: 'blur(4px)'
                }"
              >
                {{ row.usageCount }} 用 · {{ row.successRate }}%
              </div>
              <ElButton
                class="poster-edit"
                circle
                @click="handleEdit(row, 'base')"
              >
                <SvgIcon icon="material-symbols:edit-rounded" class="text-icon" />
              </ElButton>
            </div>
            <div class="card-main" style="display: grid; gap: 10px; padding: 14px;">
              <div class="card-title-row" style="display: flex; align-items: center; justify-content: space-between; gap: 8px;">
                <h3
                  style="
                    overflow: hidden;
                    margin: 0;
                    color: var(--el-text-color-primary);
                    font-size: 16px;
                    font-weight: 800;
                    line-height: 1.4;
                    text-overflow: ellipsis;
                    white-space: nowrap;
                  "
                >
                  {{ row.name }}
                </h3>
                <ElTag effect="plain" size="small">{{ row.category || '未分类' }}</ElTag>
              </div>
              <p
                style="
                  display: -webkit-box;
                  min-height: 40px;
                  overflow: hidden;
                  margin: 0;
                  color: var(--el-text-color-secondary);
                  font-size: 13px;
                  line-height: 1.55;
                  -webkit-box-orient: vertical;
                  -webkit-line-clamp: 2;
                "
              >
                {{ getDescription(row) }}
              </p>
              <div
                class="card-meta"
                style="display: flex; justify-content: space-between; color: var(--el-text-color-placeholder); font-size: 12px;"
              >
                <span>排序 {{ row.sortOrder }}</span>
                <span>{{ formatDate(row.createdAt) }}</span>
              </div>
              <div class="card-actions" style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                <ElButton size="small" type="primary" plain @click="handleEdit(row, 'base')">编辑</ElButton>
                <ElButton size="small" plain @click="openStats(row)">
                  <SvgIcon icon="material-symbols:bar-chart-rounded" class="mr-2px text-icon" />
                  统计
                </ElButton>
                <ElDropdown trigger="click">
                  <ElButton size="small" plain>
                    更多
                    <SvgIcon icon="material-symbols:arrow-drop-down-rounded" class="ml-2px text-icon" />
                  </ElButton>
                  <template #dropdown>
                    <ElDropdownMenu>
                      <ElDropdownItem @click="handleEdit(row, 'prompt')">提示词</ElDropdownItem>
                      <ElDropdownItem @click="handleDuplicate(row)">复制为副本</ElDropdownItem>
                      <ElDropdownItem v-if="row.deletedAt" @click="handleRestore(row)">恢复</ElDropdownItem>
                      <ElDropdownItem v-else divided @click="handleArchive(row)">归档</ElDropdownItem>
                    </ElDropdownMenu>
                  </template>
                </ElDropdown>
                <ElSwitch
                  v-if="!row.deletedAt"
                  :model-value="row.isActive"
                  inline-prompt
                  active-text="上架"
                  inactive-text="下架"
                  @change="(val: string | number | boolean) => handleToggleStatus(row, Boolean(val))"
                />
              </div>
            </div>
          </article>
        </div>
        <ElEmpty v-else description="暂无模板，先新增一个海报模板" />
      </template>

      <template v-else>
        <ElTable
          ref="tableRef"
          :data="tableData"
          border
          row-key="id"
          class="template-table"
          @selection-change="handleSelectionChange"
        >
          <ElTableColumn type="selection" width="50" reserve-selection align="center" />
          <ElTableColumn label="海报" width="92" align="center">
            <template #default="{ row }">
              <ElImage
                v-if="getPosterUrl(row)"
                :src="getPosterUrl(row)"
                :preview-src-list="getPreviewList(row)"
                fit="cover"
                class="table-poster"
                preview-teleported
              />
              <div v-else class="table-poster-empty">无图</div>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="name" label="模板名称" min-width="180" show-overflow-tooltip />
          <ElTableColumn prop="category" label="分类" width="120">
            <template #default="{ row }">
              <ElTag effect="plain">{{ row.category || '未分类' }}</ElTag>
            </template>
          </ElTableColumn>
          <ElTableColumn prop="sortOrder" label="排序" width="70" align="center" />
          <ElTableColumn label="用量" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.usageCount > 0">{{ row.usageCount }} ({{ row.successRate }}%)</span>
              <span v-else class="text-gray-400">-</span>
            </template>
          </ElTableColumn>
          <ElTableColumn label="状态" width="100" align="center">
            <template #default="{ row }">
              <ElTag v-if="row.deletedAt" type="danger" size="small">已归档</ElTag>
              <ElSwitch
                v-else
                :model-value="row.isActive"
                @change="(val: string | number | boolean) => handleToggleStatus(row, Boolean(val))"
              />
            </template>
          </ElTableColumn>
          <ElTableColumn prop="createdAt" label="创建时间" width="150">
            <template #default="{ row }">{{ formatDate(row.createdAt) }}</template>
          </ElTableColumn>
          <ElTableColumn label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <ElButton link type="primary" @click="handleEdit(row)">编辑</ElButton>
              <ElButton link type="primary" @click="openStats(row)">统计</ElButton>
              <ElButton link @click="handleDuplicate(row)">复制</ElButton>
              <ElButton v-if="row.deletedAt" link type="success" @click="handleRestore(row)">恢复</ElButton>
              <ElButton v-else link type="danger" @click="handleDelete(row)">归档</ElButton>
            </template>
          </ElTableColumn>
        </ElTable>
      </template>

      <div class="pagination-row">
        <ElPagination
          v-model:current-page="searchParams.page"
          v-model:page-size="searchParams.pageSize"
          :total="total"
          :page-sizes="[12, 24, 48]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </section>

    <ElDrawer v-model="drawerVisible" :title="drawerTitle" size="960px" destroy-on-close>
      <div class="drawer-body">
        <ElForm :model="formData" label-width="96px" class="template-form">
          <ElTabs v-model="activeTab">
            <ElTabPane label="基础信息" name="base">
              <ElFormItem label="模板名称" required>
                <ElInput v-model="formData.name" placeholder="请输入模板名称" />
              </ElFormItem>
              <ElFormItem label="分类" required>
                <ElSelect v-model="formData.category" filterable allow-create default-first-option placeholder="选择或输入分类">
                  <ElOption v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
                </ElSelect>
              </ElFormItem>
              <ElFormItem label="描述">
                <ElInput v-model="formData.description" type="textarea" :rows="3" placeholder="请输入描述" />
              </ElFormItem>
              <ElFormItem label="封面图">
                <div class="image-edit-row">
                  <ElInput v-model="formData.cover_url" placeholder="上传后自动填入，或手动输入图片地址" />
                  <ElUpload
                    :http-request="options => handleImageUpload(options, 'cover_url')"
                    :before-upload="beforeImageUpload"
                    :show-file-list="false"
                    accept="image/*"
                  >
                    <ElButton :loading="uploadingField === 'cover_url'">
                      <SvgIcon icon="material-symbols:upload-rounded" class="mr-4px text-icon" />
                      上传
                    </ElButton>
                  </ElUpload>
                  <ElButton @click="clearImage('cover_url')">清空</ElButton>
                </div>
              </ElFormItem>
              <ElFormItem label="预览图">
                <div class="image-edit-row">
                  <ElInput v-model="formData.preview_url" placeholder="用于列表和小程序展示的海报图" />
                  <ElUpload
                    :http-request="options => handleImageUpload(options, 'preview_url')"
                    :before-upload="beforeImageUpload"
                    :show-file-list="false"
                    accept="image/*"
                  >
                    <ElButton :loading="uploadingField === 'preview_url'">
                      <SvgIcon icon="material-symbols:upload-rounded" class="mr-4px text-icon" />
                      上传
                    </ElButton>
                  </ElUpload>
                  <ElButton @click="useCoverAsPreview">同封面</ElButton>
                </div>
              </ElFormItem>
              <ElFormItem label="排序">
                <ElInputNumber v-model="formData.sort_order" :min="0" />
              </ElFormItem>
              <ElFormItem label="是否上架">
                <ElSwitch v-model="formData.is_active" />
              </ElFormItem>
            </ElTabPane>

            <ElTabPane label="提示词" name="prompt">
              <ElFormItem label="提示词模板">
                <ElInput
                  v-model="formData.prompt_template"
                  type="textarea"
                  :rows="8"
                  placeholder="请输入提示词模板，可包含宠物类型、风格和构图说明"
                />
              </ElFormItem>
              <ElFormItem label="反向提示词">
                <ElInput v-model="formData.negative_prompt" type="textarea" :rows="5" placeholder="请输入反向提示词" />
              </ElFormItem>
            </ElTabPane>

            <ElTabPane label="高级配置" name="config">
              <ElFormItem label="配置 JSON">
                <div class="config-editor">
                  <ElInput
                    v-model="formData.config"
                    type="textarea"
                    :rows="12"
                    placeholder='{"bg": "linear-gradient(...)"}'
                  />
                  <ElButton class="mt-10px" @click="formatConfig">
                    <SvgIcon icon="material-symbols:data-object-rounded" class="mr-4px text-icon" />
                    格式化 JSON
                  </ElButton>
                </div>
              </ElFormItem>
            </ElTabPane>
          </ElTabs>
        </ElForm>

        <aside class="preview-panel">
          <div class="preview-title">海报预览</div>
          <div class="poster-preview">
            <ElImage v-if="previewImageUrl" :src="previewImageUrl" fit="cover" class="poster-preview-image" />
            <div v-else class="poster-preview-empty">
              <SvgIcon icon="material-symbols:add-photo-alternate-rounded" />
              <span>上传或填写预览图后显示</span>
            </div>
          </div>
          <div class="preview-meta">
            <strong>{{ formData.name || '未命名模板' }}</strong>
            <span>{{ formData.category || '未分类' }}</span>
            <p>{{ formData.description || '暂无描述' }}</p>
          </div>
          <ElDivider />
          <div class="cover-preview">
            <span>封面图</span>
            <ElImage v-if="coverImageUrl" :src="coverImageUrl" fit="cover" class="cover-preview-image" />
            <div v-else class="cover-preview-empty">暂无</div>
          </div>
        </aside>
      </div>

      <template #footer>
        <ElButton @click="drawerVisible = false">取消</ElButton>
        <ElButton type="primary" @click="handleSubmit">
          <SvgIcon icon="material-symbols:save-rounded" class="mr-4px text-icon" />
          保存模板
        </ElButton>
      </template>
    </ElDrawer>

    <StatsDrawer
      v-model:visible="statsVisible"
      :loading="statsLoading"
      :template="statsTemplate"
      :stats="statsData"
    />
  </div>
</template>

<style scoped>
.template-page {
  display: grid;
  gap: 16px;
}

.template-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 18px 20px;
  background: var(--el-bg-color);
}

.template-hero h2 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 22px;
  font-weight: 800;
  line-height: 1.2;
}

.template-hero p {
  margin: 8px 0 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 14px;
  background: var(--el-bg-color);
}

.stat-icon {
  display: grid;
  width: 38px;
  height: 38px;
  flex: none;
  place-items: center;
  border-radius: 8px;
  background: rgb(217 119 87 / 12%);
  color: #d97757;
  font-size: 22px;
}

.stat-item strong {
  display: block;
  color: var(--el-text-color-primary);
  font-size: 22px;
  line-height: 1;
}

.stat-item span {
  display: block;
  margin-top: 6px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.filter-panel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 14px;
  background: var(--el-bg-color);
}

.filter-fields {
  display: flex;
  flex: 1;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.search-input {
  width: min(320px, 100%);
}

.category-select {
  width: 180px;
}

.content-panel {
  min-height: 360px;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 16px;
  background: var(--el-bg-color);
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.template-card {
  overflow: hidden;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  background: var(--el-bg-color);
  box-shadow: 0 8px 22px rgb(15 23 42 / 5%);
  transition:
    border-color 0.22s ease,
    box-shadow 0.22s ease,
    transform 0.22s ease;
}

.template-card:hover {
  border-color: var(--el-color-primary-light-5);
  box-shadow: 0 14px 34px rgb(15 23 42 / 14%);
  transform: translateY(-3px);
}

.template-card.is-selected {
  border-color: var(--el-color-primary);
  box-shadow: 0 14px 34px var(--el-color-primary-light-7);
}

.card-select {
  position: absolute;
  top: 8px;
  left: 8px;
  z-index: 2;
  opacity: 0;
  padding: 2px 4px;
  border-radius: 4px;
  background: rgb(255 255 255 / 88%);
  backdrop-filter: blur(4px);
  transition: opacity 0.22s ease;
}

.template-card:hover .card-select,
.card-select.is-selected {
  opacity: 1;
}

.poster-frame {
  position: relative;
  overflow: hidden;
  aspect-ratio: 4 / 3;
  background: linear-gradient(135deg, var(--el-fill-color-light), var(--el-fill-color-extra-light));
}

.poster-image {
  width: 100%;
  height: 100%;
}

.poster-placeholder {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  align-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.poster-placeholder :deep(svg) {
  font-size: 34px;
}

.poster-status {
  position: absolute;
  top: 10px;
  left: 10px;
  border-radius: 6px;
  padding: 4px 8px;
  background: rgb(103 194 58 / 92%);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
}

.poster-status.inactive {
  background: rgb(144 147 153 / 88%);
}

.poster-edit {
  position: absolute;
  right: 10px;
  bottom: 10px;
  opacity: 0;
  transform: scale(0.82);
  box-shadow: 0 6px 18px rgb(15 23 42 / 18%);
  transition: opacity 0.22s ease, transform 0.22s ease, box-shadow 0.22s ease;
}

.template-card:hover .poster-edit {
  opacity: 1;
  transform: scale(1);
}

.template-card:hover .poster-edit:hover {
  transform: scale(1.08);
  box-shadow: 0 10px 24px rgb(15 23 42 / 25%);
}

.card-main {
  display: grid;
  gap: 10px;
  padding: 14px;
}

.card-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.card-title-row h3 {
  overflow: hidden;
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 800;
  line-height: 1.4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-main p {
  display: -webkit-box;
  min-height: 40px;
  overflow: hidden;
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.card-meta {
  display: flex;
  justify-content: space-between;
  color: var(--el-text-color-placeholder);
  font-size: 12px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-actions :deep(.el-switch) {
  margin-left: auto;
}

.template-table :deep(.el-table__row) {
  height: 88px;
}

.table-poster,
.table-poster-empty {
  width: 54px;
  height: 68px;
  border-radius: 6px;
}

.table-poster-empty {
  display: grid;
  margin: 0 auto;
  place-items: center;
  border: 1px dashed var(--el-border-color);
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.drawer-body {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 22px;
}

.template-form {
  min-width: 0;
}

.image-edit-row {
  display: grid;
  width: 100%;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 8px;
}

.config-editor {
  width: 100%;
}

.preview-panel {
  position: sticky;
  top: 0;
  align-self: start;
  border: 1px solid var(--el-border-color-lighter);
  border-radius: 8px;
  padding: 14px;
  background: var(--el-bg-color-page);
}

.preview-title {
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
  font-weight: 800;
}

.poster-preview {
  overflow: hidden;
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: 8px;
  background: var(--el-fill-color-light);
}

.poster-preview-image {
  width: 100%;
  height: 100%;
}

.poster-preview-empty {
  display: grid;
  width: 100%;
  height: 100%;
  place-items: center;
  align-content: center;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.poster-preview-empty :deep(svg) {
  font-size: 34px;
}

.preview-meta {
  display: grid;
  gap: 6px;
  margin-top: 12px;
}

.preview-meta strong {
  color: var(--el-text-color-primary);
  font-size: 16px;
}

.preview-meta span,
.preview-meta p {
  margin: 0;
  color: var(--el-text-color-secondary);
  font-size: 13px;
  line-height: 1.6;
}

.cover-preview {
  display: grid;
  gap: 8px;
  color: var(--el-text-color-secondary);
  font-size: 13px;
}

.cover-preview-image,
.cover-preview-empty {
  width: 100%;
  height: 120px;
  border-radius: 6px;
}

.cover-preview-empty {
  display: grid;
  place-items: center;
  border: 1px dashed var(--el-border-color);
}

@media (max-width: 1100px) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .drawer-body {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .template-hero,
  .filter-panel {
    align-items: stretch;
    flex-direction: column;
  }

  .stats-strip {
    grid-template-columns: 1fr;
  }

  .category-select,
  .search-input {
    width: 100%;
  }

  .image-edit-row {
    grid-template-columns: 1fr;
  }
}
</style>
