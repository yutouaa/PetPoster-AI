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
      createdAt: string;
      updatedAt: string;
    }

    interface TemplateListParams {
      page?: number;
      pageSize?: number;
      keyword?: string;
      category?: string;
      isActive?: boolean;
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
  }
}
