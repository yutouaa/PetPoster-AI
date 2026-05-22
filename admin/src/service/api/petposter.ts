import { request } from '../request';

/** 获取 Dashboard 指标 */
export function fetchPetPosterDashboard(params?: { days?: number; compare?: boolean }) {
  return request<Api.PetPoster.DashboardMetrics>({
    url: '/admin/dashboard',
    params
  });
}

/** 获取模板列表 */
export function fetchTemplates(params?: Api.PetPoster.TemplateListParams) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.Template>>({
    url: '/admin/templates',
    params
  });
}

/** 创建模板 */
export function createTemplate(data: Api.PetPoster.TemplateCreate) {
  return request<Api.PetPoster.Template>({
    url: '/admin/templates',
    method: 'post',
    data
  });
}

/** 更新模板 */
export function updateTemplate(id: number, data: Api.PetPoster.TemplateUpdate) {
  return request<Api.PetPoster.Template>({
    url: `/admin/templates/${id}`,
    method: 'put',
    data
  });
}

/** 删除模板 */
export function deleteTemplate(id: number) {
  return request<null>({
    url: `/admin/templates/${id}`,
    method: 'delete'
  });
}

/** 切换模板状态 */
export function toggleTemplateStatus(id: number, isActive: boolean) {
  return request<Api.PetPoster.Template>({
    url: `/admin/templates/${id}/status`,
    method: 'patch',
    data: { is_active: isActive }
  });
}

/** 复制模板 */
export function duplicateTemplate(id: number) {
  return request<Api.PetPoster.Template>({
    url: `/admin/templates/${id}/duplicate`,
    method: 'post'
  });
}

/** 归档模板（软删除） */
export function archiveTemplate(id: number) {
  return request<null>({
    url: `/admin/templates/${id}/archive`,
    method: 'post'
  });
}

/** 恢复模板 */
export function restoreTemplate(id: number) {
  return request<Api.PetPoster.Template>({
    url: `/admin/templates/${id}/restore`,
    method: 'post'
  });
}

/** 模板统计 */
export function fetchTemplateStats(id: number) {
  return request<Api.PetPoster.TemplateStats>({
    url: `/admin/templates/${id}/stats`
  });
}

/** 导出模板 */
export function exportTemplates(ids?: number[]) {
  return request<{ templates: Record<string, unknown>[]; count: number }>({
    url: '/admin/templates/export',
    params: ids && ids.length ? { ids: ids.join(',') } : undefined
  });
}

/** 导入模板 */
export function importTemplates(templates: Record<string, unknown>[]) {
  return request<Api.PetPoster.TemplateImportResult>({
    url: '/admin/templates/import',
    method: 'post',
    data: { templates }
  });
}

/** 批量归档模板 */
export function batchArchiveTemplates(ids: number[]) {
  return request<{ archived: number; skipped: number }>({
    url: '/admin/templates/batch-archive',
    method: 'post',
    data: { ids }
  });
}

/** 上传模板海报图片 */
export function uploadPetPosterImages(files: File[]) {
  const data = new FormData();

  files.forEach(file => {
    data.append('files', file);
  });

  return request<Api.PetPoster.UploadResult>({
    url: '/upload/images',
    method: 'post',
    data,
    // 必须显式声明 multipart/form-data，否则会被 SoybeanAdmin 的 axios 封装默认设为
    // application/json，导致 FormData 被错误序列化为空 JSON，FastAPI 收不到 files 字段 → 422。
    // axios 在 Content-Type=multipart/form-data 时会自动接管 boundary。
    headers: { 'Content-Type': 'multipart/form-data' }
  });
}

/** 获取生成任务列表 */
export function fetchGenerationTasks(params?: Api.PetPoster.GenerationTaskListParams) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.GenerationTask>>({
    url: '/admin/generation-tasks',
    params
  });
}

/** 重新提交生成任务 */
export function retryGenerationTask(id: number) {
  return request<Api.PetPoster.GenerationTask>({
    url: `/admin/generation-tasks/${id}/retry`,
    method: 'post'
  });
}

// ===== AI Provider 管理 =====

/** 获取 AI 供应商列表 */
export function fetchAiProviders(params?: { page?: number; pageSize?: number }) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.AiProvider>>({
    url: '/admin/ai-providers',
    params
  });
}

/** 创建 AI 供应商 */
export function createAiProvider(data: Api.PetPoster.AiProviderForm) {
  return request<Api.PetPoster.AiProvider>({
    url: '/admin/ai-providers',
    method: 'post',
    data
  });
}

/** 更新 AI 供应商 */
export function updateAiProvider(id: number, data: Partial<Api.PetPoster.AiProviderForm>) {
  return request<Api.PetPoster.AiProvider>({
    url: `/admin/ai-providers/${id}`,
    method: 'put',
    data
  });
}

/** 删除 AI 供应商 */
export function deleteAiProvider(id: number) {
  return request<null>({
    url: `/admin/ai-providers/${id}`,
    method: 'delete'
  });
}

/** 切换 AI 供应商状态 */
export function toggleAiProviderActive(id: number) {
  return request<Api.PetPoster.AiProvider>({
    url: `/admin/ai-providers/${id}/active`,
    method: 'patch'
  });
}

// ===== 失败任务管理 =====

/** 获取失败任务汇总 */
export function fetchFailedTasksSummary(params?: { page?: number; pageSize?: number }) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.FailedTaskSummary>>({
    url: '/admin/failed-tasks/summary',
    params
  });
}

/** 批量重试失败任务 */
export function batchRetryTasks(taskIds: number[]) {
  return request<{ retried: number }>({
    url: '/admin/failed-tasks/batch-retry',
    method: 'post',
    data: { task_ids: taskIds }
  });
}

// ===== 用户配额管理 =====

/** 获取用户配额列表 */
export function fetchQuotaUsers(params?: { page?: number; pageSize?: number; search?: string }) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.UserQuota>>({
    url: '/admin/quota/users',
    params
  });
}

/** 调整用户配额 */
export function adjustQuota(data: Api.PetPoster.QuotaAdjustForm) {
  return request<{ userId: string; balance: number; totalPurchased: number }>({
    url: '/admin/quota/adjust',
    method: 'post',
    data
  });
}

/** 获取配额流水列表 */
export function fetchQuotaTransactions(params?: { page?: number; pageSize?: number; userId?: string; type?: string }) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.QuotaTransaction>>({
    url: '/admin/quota/transactions',
    params
  });
}

// ===== 审计日志 =====

/** 获取审计日志列表 */
export function fetchAuditLogs(params?: Api.PetPoster.AuditLogListParams) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.AuditLog>>({
    url: '/admin/audit-logs',
    params
  });
}

// ===== 小红书推广管理 =====

/** 获取小红书帖子列表 */
export function fetchXhsPosts(params?: { page?: number; pageSize?: number; status?: string }) {
  return request<Api.PetPoster.PaginatedList<Api.PetPoster.XhsPost>>({
    url: '/admin/xhs-posts',
    params
  });
}

/** 获取小红书帖子状态统计 */
export function fetchXhsStats() {
  return request<Api.PetPoster.XhsStats>({
    url: '/admin/xhs-posts/stats'
  });
}

/** 创建小红书帖子 */
export function createXhsPost(data: Api.PetPoster.XhsPostForm) {
  return request<Api.PetPoster.XhsPost>({
    url: '/admin/xhs-posts',
    method: 'post',
    data
  });
}

/** 更新小红书帖子 */
export function updateXhsPost(id: number, data: Partial<Api.PetPoster.XhsPostForm>) {
  return request<Api.PetPoster.XhsPost>({
    url: `/admin/xhs-posts/${id}`,
    method: 'put',
    data
  });
}

/** 删除小红书帖子 */
export function deleteXhsPost(id: number) {
  return request<null>({
    url: `/admin/xhs-posts/${id}`,
    method: 'delete'
  });
}

/** AI 生成小红书文案 */
export function generateXhsContent(id: number, prompt: string) {
  return request<{ content: string }>({
    url: `/admin/xhs-posts/${id}/generate-content`,
    method: 'post',
    data: { prompt }
  });
}

/** 发布小红书帖子 */
export function publishXhsPost(id: number) {
  return request<Api.PetPoster.XhsPost>({
    url: `/admin/xhs-posts/${id}/publish`,
    method: 'post'
  });
}
