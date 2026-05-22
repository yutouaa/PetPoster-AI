declare namespace Api {
  namespace PetPoster {
    interface DashboardMetrics {
      userCount: number;
      templateCount: number;
      generationCount: number;
      todayGenerationCount: number;
      todayRevenue: number;
      todayCost: number;
      failureRate: number;
      successRate: number;
      activeUserCount: number;
      styleDistribution: ChartItem[];
      statusDistribution: ChartItem[];
      generationTrend: TrendItem[];
      userPortrait: UserPortrait;
      topTemplates: TopTemplate[];
      recentTasks: RecentTask[];
      // 新增
      taskDuration: TaskDuration;
      failureTypeDistribution: FailureTypeItem[];
      retryEffectiveness: RetryEffectiveness;
      revenueTrend: RevenueTrendItem[];
      consumptionPerUser: number;
      recentTimeouts24h: number;
      periodComparison: PeriodComparison | null;
      days: number;
    }

    interface TaskDuration {
      avg: number;
      p50: number;
      p95: number;
      sampleSize: number;
    }

    interface FailureTypeItem {
      type: string;
      count: number;
    }

    interface RetryEffectiveness {
      attempted: number;
      succeeded: number;
      rate: number;
    }

    interface RevenueTrendItem {
      date: string;
      amount: number;
    }

    interface PeriodComparison {
      current: { generations: number; cost: number; failureRate: number };
      previous: { generations: number; cost: number; failureRate: number };
      generationsPct: number | null;
      costPct: number | null;
      failureRateDelta: number;
    }

    interface ChartItem {
      name: string;
      value: number;
    }

    interface TrendItem {
      date: string;
      count: number;
      success: number;
      failed: number;
      cost: number;
    }

    interface UserPortrait {
      activeUserCount: number;
      newUserCount: number;
      repeatUserCount: number;
      anonymousCount: number;
      highValueUserCount: number;
    }

    interface TopTemplate {
      templateId: number;
      name: string;
      category: string;
      count: number;
      successRate: number;
      failureRate: number;
      avgDurationMs: number;
    }

    interface RecentTask {
      id: number;
      templateName: string;
      status: 'pending' | 'processing' | 'success' | 'failed' | string;
      cost: number;
      createdAt: string;
    }

    interface Template {
      id: number;
      name: string;
      category: string;
      description: string;
      coverUrl: string;
      previewUrl: string;
      promptTemplate: string;
      negativePrompt: string;
      config: string;
      sortOrder: number;
      isActive: boolean;
      deletedAt: string | null;
      usageCount: number;
      successCount: number;
      successRate: number;
      createdAt: string;
      updatedAt: string;
    }

    interface TemplateStats {
      usageCount: number;
      successCount: number;
      failedCount: number;
      successRate: number;
      avgDurationMs: number;
      recent30d: { date: string; count: number; success: number }[];
    }

    interface TemplateImportResult {
      created: number;
      updated: number;
      skipped: number;
    }

    interface TemplateListParams {
      page?: number;
      pageSize?: number;
      keyword?: string;
      category?: string;
      isActive?: boolean;
      includeArchived?: boolean;
    }

    interface PaginatedList<T> {
      records: T[];
      current: number;
      size: number;
      total: number;
    }

    interface TemplateCreate {
      name: string;
      category: string;
      description?: string;
      cover_url?: string;
      preview_url?: string;
      prompt_template?: string;
      negative_prompt?: string;
      config?: string;
      sort_order?: number;
      is_active?: boolean;
    }

    type TemplateUpdate = Partial<TemplateCreate>;

    interface GenerationTask {
      id: number;
      templateId: number;
      templateName: string;
      status: 'pending' | 'processing' | 'success' | 'failed' | string;
      originalImageUrls: string[];
      resultImageUrl: string | null;
      prompt: string;
      cost: number;
      failureType: string | null;
      errorMessage: string | null;
      retryCount: number;
      requestId: string | null;
      createdAt: string;
      updatedAt: string;
      completedAt: string | null;
    }

    interface GenerationTaskListParams {
      page?: number;
      pageSize?: number;
      status?: string;
      userId?: string;
    }

    interface UploadResult {
      urls: string[];
    }

    // ===== AI Provider =====

    interface AiProvider {
      id: number;
      name: string;
      baseUrl: string;
      apiKey: string;
      modelName: string;
      timeout: number;
      isActive: boolean;
      priority: number;
      createdAt: string;
      updatedAt: string;
    }

    interface AiProviderForm {
      name: string;
      base_url: string;
      api_key: string;
      model_name: string;
      timeout?: number;
      is_active?: boolean;
      priority?: number;
    }

    // ===== 失败任务 =====

    interface FailedTaskSummary {
      userId: string;
      failedCount: number;
      lastFailedAt: string;
      totalTasks: number;
      tasks: GenerationTask[];
    }

    // ===== 用户配额 =====

    interface UserQuota {
      id: number;
      userId: string;
      balance: number;
      totalPurchased: number;
      totalConsumed: number;
      createdAt: string;
      updatedAt: string;
    }

    interface QuotaTransaction {
      id: number;
      userId: string;
      type: 'recharge' | 'consume' | 'refund' | 'admin_adjust';
      amount: number;
      balanceAfter: number;
      referenceId: string | null;
      remark: string | null;
      createdAt: string;
    }

    interface QuotaAdjustForm {
      user_id: string;
      amount: number;
      remark: string;
    }

    // ===== 审计日志 =====

    interface AuditLog {
      id: number;
      adminId: string;
      action: string;
      resourceType: string;
      resourceId: string | null;
      detail: string | null;
      ipAddress: string | null;
      createdAt: string;
    }

    interface AuditLogListParams {
      page?: number;
      pageSize?: number;
      action?: string;
      resourceType?: string;
      adminId?: string;
    }

    // ===== 小红书推广 =====

    interface XhsPost {
      id: number;
      title: string;
      content: string;
      imageUrls: string[];
      tags: string[];
      status: 'draft' | 'scheduled' | 'published' | 'failed' | string;
      scheduledAt: string | null;
      publishedAt: string | null;
      platformPostId: string | null;
      llmPrompt: string | null;
      createdAt: string;
      updatedAt: string;
    }

    interface XhsPostForm {
      title: string;
      content: string;
      image_urls?: string[];
      tags?: string[];
      status?: string;
      scheduled_at?: string | null;
      llm_prompt?: string | null;
    }

    interface XhsStats {
      draft: number;
      scheduled: number;
      published: number;
      failed: number;
      total: number;
    }
  }
}
