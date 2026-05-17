import { request } from '../request';

/** 获取 Dashboard 指标 */
export function fetchPetPosterDashboard() {
  return request<Api.PetPoster.DashboardMetrics>({ url: '/admin/dashboard' });
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

/** 上传模板海报图片 */
export function uploadPetPosterImages(files: File[]) {
  const data = new FormData();

  files.forEach(file => {
    data.append('files', file);
  });

  return request<Api.PetPoster.UploadResult>({
    url: '/upload/images',
    method: 'post',
    data
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
