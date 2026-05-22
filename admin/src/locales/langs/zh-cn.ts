const local: App.I18n.Schema = {
  system: {
    title: 'PetPoster AI 后台',
    updateTitle: '系统版本更新通知',
    updateContent: '检测到系统有新版本发布，是否立即刷新页面？',
    updateConfirm: '立即刷新',
    updateCancel: '稍后再说'
  },
  common: {
    action: '操作',
    add: '新增',
    addSuccess: '添加成功',
    backToHome: '返回首页',
    batchDelete: '批量删除',
    cancel: '取消',
    close: '关闭',
    check: '勾选',
    expandColumn: '展开列',
    columnSetting: '列设置',
    config: '配置',
    confirm: '确认',
    delete: '删除',
    deleteSuccess: '删除成功',
    confirmDelete: '确认删除吗？',
    edit: '编辑',
    warning: '警告',
    error: '错误',
    index: '序号',
    keywordSearch: '请输入关键词搜索',
    logout: '退出登录',
    logoutConfirm: '确认退出登录吗？',
    lookForward: '敬请期待',
    modify: '修改',
    modifySuccess: '修改成功',
    noData: '无数据',
    operate: '操作',
    pleaseCheckValue: '请检查输入的值是否合法',
    refresh: '刷新',
    reset: '重置',
    search: '搜索',
    switch: '切换',
    tip: '提示',
    trigger: '触发',
    update: '更新',
    updateSuccess: '更新成功',
    userCenter: '个人中心',
    yesOrNo: {
      yes: '是',
      no: '否'
    }
  },
  request: {
    logout: '请求失败后登出用户',
    logoutMsg: '用户状态失效，请重新登录',
    logoutWithModal: '请求失败后弹出模态框再登出用户',
    logoutWithModalMsg: '用户状态失效，请重新登录',
    refreshToken: '请求的token已过期，刷新token',
    tokenExpired: 'token已过期'
  },
  theme: {
    themeSchema: {
      title: '主题模式',
      light: '亮色模式',
      dark: '暗黑模式',
      auto: '跟随系统'
    },
    grayscale: '灰色模式',
    colourWeakness: '色弱模式',
    layoutMode: {
      title: '布局模式',
      vertical: '左侧菜单模式',
      'vertical-mix': '左侧菜单混合模式',
      horizontal: '顶部菜单模式',
      'horizontal-mix': '顶部菜单混合模式',
      reverseHorizontalMix: '一级菜单与子级菜单位置反转'
    },
    recommendColor: '应用推荐算法的颜色',
    recommendColorDesc: '推荐颜色的算法参照',
    themeColor: {
      title: '主题颜色',
      primary: '主色',
      info: '信息色',
      success: '成功色',
      warning: '警告色',
      error: '错误色',
      followPrimary: '跟随主色'
    },
    scrollMode: {
      title: '滚动模式',
      wrapper: '外层滚动',
      content: '主体滚动'
    },
    page: {
      animate: '页面切换动画',
      mode: {
        title: '页面切换动画类型',
        'fade-slide': '滑动',
        fade: '淡入淡出',
        'fade-bottom': '底部消退',
        'fade-scale': '缩放消退',
        'zoom-fade': '渐变',
        'zoom-out': '闪现',
        none: '无'
      }
    },
    fixedHeaderAndTab: '固定头部和标签栏',
    header: {
      height: '头部高度',
      breadcrumb: {
        visible: '显示面包屑',
        showIcon: '显示面包屑图标'
      },
      multilingual: {
        visible: '显示多语言按钮'
      },
      globalSearch: {
        visible: '显示全局搜索按钮'
      }
    },
    tab: {
      visible: '显示标签栏',
      cache: '标签栏信息缓存',
      height: '标签栏高度',
      mode: {
        title: '标签栏风格',
        chrome: '谷歌风格',
        button: '按钮风格'
      }
    },
    sider: {
      inverted: '深色侧边栏',
      width: '侧边栏宽度',
      collapsedWidth: '侧边栏折叠宽度',
      mixWidth: '混合布局侧边栏宽度',
      mixCollapsedWidth: '混合布局侧边栏折叠宽度',
      mixChildMenuWidth: '混合布局子菜单宽度'
    },
    footer: {
      visible: '显示底部',
      fixed: '固定底部',
      height: '底部高度',
      right: '底部局右'
    },
    watermark: {
      visible: '显示全屏水印',
      text: '水印文本',
      enableUserName: '启用用户名水印'
    },
    themeDrawerTitle: '主题配置',
    pageFunTitle: '页面功能',
    configOperation: {
      copyConfig: '复制配置',
      copySuccessMsg: '复制成功，请替换 src/theme/settings.ts 中的变量 themeSettings',
      resetConfig: '重置配置',
      resetSuccessMsg: '重置成功'
    }
  },
  route: {
    login: '登录',
    403: '无权限',
    404: '页面不存在',
    500: '服务器错误',
    'iframe-page': '外链页面',
    home: '首页',
    document: '文档',
    document_project: '项目文档',
    'document_project-link': '项目文档(外链)',
    document_vue: 'Vue文档',
    document_vite: 'Vite文档',
    document_unocss: 'UnoCSS文档',
    document_naive: 'Naive UI文档',
    document_antd: 'Ant Design Vue文档',
    'document_element-plus': 'Element Plus文档',
    document_alova: 'Alova文档',
    petposter: '宠物海报 AI',
    petposter_dashboard: '数据概览',
    petposter_templates: '模板管理',
    petposter_generations: '生成任务',
    'petposter_ai-providers': 'AI 服务配置',
    'petposter_failed-tasks': '失败任务补发',
    'petposter_xhs-posts': '小红书推广',
    petposter_quota: '配额管理',
    'petposter_audit-log': '操作审计',
    'user-center': '个人中心',
    about: '关于',
    function: '系统功能',
    alova: 'alova示例',
    alova_request: 'alova请求',
    alova_user: '用户列表',
    alova_scenes: '场景化请求',
    function_tab: '标签页',
    'function_multi-tab': '多标签页',
    'function_hide-child': '隐藏子菜单',
    'function_hide-child_one': '隐藏子菜单',
    'function_hide-child_two': '菜单二',
    'function_hide-child_three': '菜单三',
    function_request: '请求',
    'function_toggle-auth': '切换权限',
    'function_super-page': '超级管理员可见',
    manage: '系统管理',
    manage_user: '用户管理',
    'manage_user-detail': '用户详情',
    manage_role: '角色管理',
    manage_menu: '菜单管理',
    'multi-menu': '多级菜单',
    'multi-menu_first': '菜单一',
    'multi-menu_first_child': '菜单一子菜单',
    'multi-menu_second': '菜单二',
    'multi-menu_second_child': '菜单二子菜单',
    'multi-menu_second_child_home': '菜单二子菜单首页',
    exception: '异常页',
    exception_403: '403',
    exception_404: '404',
    exception_500: '500',
    plugin: '插件示例',
    plugin_copy: '剪贴板',
    plugin_charts: '图表',
    plugin_charts_echarts: 'ECharts',
    plugin_charts_antv: 'AntV',
    plugin_charts_vchart: 'VChart',
    plugin_editor: '编辑器',
    plugin_editor_quill: '富文本编辑器',
    plugin_editor_markdown: 'MD 编辑器',
    plugin_icon: '图标',
    plugin_map: '地图',
    plugin_print: '打印',
    plugin_swiper: 'Swiper',
    plugin_video: '视频',
    plugin_barcode: '条形码',
    plugin_pinyin: '拼音',
    plugin_excel: 'Excel',
    plugin_pdf: 'PDF 预览',
    plugin_gantt: '甘特图',
    plugin_gantt_dhtmlx: 'dhtmlxGantt',
    plugin_gantt_vtable: 'VTableGantt',
    plugin_typeit: '打字机',
    plugin_tables: '表格',
    plugin_tables_vtable: 'VTable'
  },
  page: {
    login: {
      common: {
        loginOrRegister: '登录 / 注册',
        userNamePlaceholder: '请输入用户名',
        phonePlaceholder: '请输入手机号',
        codePlaceholder: '请输入验证码',
        passwordPlaceholder: '请输入密码',
        confirmPasswordPlaceholder: '请再次输入密码',
        codeLogin: '验证码登录',
        confirm: '确定',
        back: '返回',
        validateSuccess: '验证成功',
        loginSuccess: '登录成功',
        welcomeBack: '欢迎回来，{userName} ！'
      },
      pwdLogin: {
        title: '密码登录',
        rememberMe: '记住我',
        forgetPassword: '忘记密码？',
        register: '注册账号',
        otherAccountLogin: '其他账号登录',
        otherLoginMode: '其他登录方式',
        superAdmin: '超级管理员',
        admin: '管理员',
        user: '普通用户'
      },
      codeLogin: {
        title: '验证码登录',
        getCode: '获取验证码',
        reGetCode: '{time}秒后重新获取',
        sendCodeSuccess: '验证码发送成功',
        imageCodePlaceholder: '请输入图片验证码'
      },
      register: {
        title: '注册账号',
        agreement: '我已经仔细阅读并接受',
        protocol: '《用户协议》',
        policy: '《隐私权政策》'
      },
      resetPwd: {
        title: '重置密码'
      },
      bindWeChat: {
        title: '绑定微信'
      }
    },
    about: {
      title: '关于',
      introduction: `PetPoster AI 后台管理系统，基于 Vue3、Vite、TypeScript、Element Plus 和 UnoCSS 构建。提供宠物海报模板管理、AI 生成任务监控和数据分析等功能，是 PetPoster AI 微信小程序的运营支撑平台。`,
      projectInfo: {
        title: '项目信息',
        version: '版本',
        latestBuildTime: '最新构建时间',
        githubLink: 'Github 地址',
        previewLink: '预览地址'
      },
      prdDep: '生产依赖',
      devDep: '开发依赖'
    },
    home: {
      branchDesc: '',
      greeting: '欢迎回来，{userName}，祝你工作顺利！',
      weatherDesc: '今日系统运行正常',
      projectCount: '模板数',
      todo: '待处理',
      message: '消息',
      downloadCount: '生成量',
      registerCount: '用户数',
      schedule: '任务状态分布',
      study: '成功',
      work: '处理中',
      rest: '待处理',
      entertainment: '失败',
      visitCount: '访问量',
      turnover: '收入',
      dealCount: '生成量',
      projectNews: {
        title: '运营动态',
        moreNews: '更多动态',
        desc1: '系统上线了「炭笔素描」新风格模板',
        desc2: '用户生成量本周较上周增长 15%',
        desc3: '新增高价值用户识别功能',
        desc4: '优化了海报生成速度，平均耗时降低 20%',
        desc5: '小程序端新增批量上传和历史记录功能'
      },
      creativity: '创意',
      dateToday: '今日',
      date7d: '7 天',
      date30d: '30 天',
      compareWithPrev: '与上期对比',
      revenue: '收入',
      taskDuration: '任务耗时',
      taskDurationP50: '耗时 P50',
      durationAvg: '平均',
      sampleSize: '样本 {count}',
      timeouts24h: '24h 超时',
      failureBreakdown: '失败原因分析',
      failureType: '失败类型',
      retryEffectiveness: '重试成功率',
      failureTypes: {
        timeout: '超时',
        api_error: 'API 错误',
        rate_limit: '限流',
        template_missing: '模板缺失',
        unknown: '其他'
      }
    },
    function: {
      tab: {
        tabOperate: {
          title: '标签页操作',
          addTab: '添加标签页',
          addTabDesc: '跳转到关于页面',
          closeTab: '关闭标签页',
          closeCurrentTab: '关闭当前标签页',
          closeAboutTab: '关闭"关于"标签页',
          addMultiTab: '添加多标签页',
          addMultiTabDesc1: '跳转到多标签页页面',
          addMultiTabDesc2: '跳转到多标签页页面(带有查询参数)'
        },
        tabTitle: {
          title: '标签页标题',
          changeTitle: '修改标题',
          change: '修改',
          resetTitle: '重置标题',
          reset: '重置'
        }
      },
      multiTab: {
        routeParam: '路由参数',
        backTab: '返回 function_tab'
      },
      toggleAuth: {
        toggleAccount: '切换账号',
        authHook: '权限钩子函数 `hasAuth`',
        superAdminVisible: '超级管理员可见',
        adminVisible: '管理员可见',
        adminOrUserVisible: '管理员和用户可见'
      },
      request: {
        repeatedErrorOccurOnce: '重复请求错误只出现一次',
        repeatedError: '重复请求错误',
        repeatedErrorMsg1: '自定义请求错误 1',
        repeatedErrorMsg2: '自定义请求错误 2'
      }
    },
    alova: {
      scenes: {
        captchaSend: '发送验证码',
        autoRequest: '自动请求',
        visibilityRequestTips: '浏览器窗口切换自动请求数据',
        pollingRequestTips: '每3秒自动请求一次',
        networkRequestTips: '网络重连后自动请求',
        refreshTime: '更新时间',
        startRequest: '开始请求',
        stopRequest: '停止请求',
        requestCrossComponent: '跨组件触发请求',
        triggerAllRequest: '手动触发所有自动请求'
      }
    },
    manage: {
      common: {
        status: {
          enable: '启用',
          disable: '禁用'
        }
      },
      role: {
        title: '角色列表',
        roleName: '角色名称',
        roleCode: '角色编码',
        roleStatus: '角色状态',
        roleDesc: '角色描述',
        menuAuth: '菜单权限',
        buttonAuth: '按钮权限',
        form: {
          roleName: '请输入角色名称',
          roleCode: '请输入角色编码',
          roleStatus: '请选择角色状态',
          roleDesc: '请输入角色描述'
        },
        addRole: '新增角色',
        editRole: '编辑角色'
      },
      user: {
        title: '用户列表',
        userName: '用户名',
        userGender: '性别',
        nickName: '昵称',
        userPhone: '手机号',
        userEmail: '邮箱',
        userStatus: '用户状态',
        userRole: '用户角色',
        form: {
          userName: '请输入用户名',
          userGender: '请选择性别',
          nickName: '请输入昵称',
          userPhone: '请输入手机号',
          userEmail: '请输入邮箱',
          userStatus: '请选择用户状态',
          userRole: '请选择用户角色'
        },
        addUser: '新增用户',
        editUser: '编辑用户',
        gender: {
          male: '男',
          female: '女'
        }
      },
      menu: {
        home: '首页',
        title: '菜单列表',
        id: 'ID',
        parentId: '父级菜单ID',
        menuType: '菜单类型',
        menuName: '菜单名称',
        routeName: '路由名称',
        routePath: '路由路径',
        pathParam: '路径参数',
        layout: '布局',
        page: '页面组件',
        i18nKey: '国际化key',
        icon: '图标',
        localIcon: '本地图标',
        iconTypeTitle: '图标类型',
        order: '排序',
        constant: '常量路由',
        keepAlive: '缓存路由',
        href: '外链',
        hideInMenu: '隐藏菜单',
        activeMenu: '高亮的菜单',
        multiTab: '支持多页签',
        fixedIndexInTab: '固定在页签中的序号',
        query: '路由参数',
        button: '按钮',
        buttonCode: '按钮编码',
        buttonDesc: '按钮描述',
        menuStatus: '菜单状态',
        form: {
          home: '请选择首页',
          menuType: '请选择菜单类型',
          menuName: '请输入菜单名称',
          routeName: '请输入路由名称',
          routePath: '请输入路由路径',
          pathParam: '请输入路径参数',
          page: '请选择页面组件',
          layout: '请选择布局组件',
          i18nKey: '请输入国际化key',
          icon: '请输入图标',
          localIcon: '请选择本地图标',
          order: '请输入排序',
          keepAlive: '请选择是否缓存路由',
          href: '请输入外链',
          hideInMenu: '请选择是否隐藏菜单',
          activeMenu: '请选择高亮的菜单的路由名称',
          multiTab: '请选择是否支持多标签',
          fixedInTab: '请选择是否固定在页签中',
          fixedIndexInTab: '请输入固定在页签中的序号',
          queryKey: '请输入路由参数Key',
          queryValue: '请输入路由参数Value',
          button: '请选择是否按钮',
          buttonCode: '请输入按钮编码',
          buttonDesc: '请输入按钮描述',
          menuStatus: '请选择菜单状态'
        },
        addMenu: '新增菜单',
        editMenu: '编辑菜单',
        addChildMenu: '新增子菜单',
        type: {
          directory: '目录',
          menu: '菜单'
        },
        iconType: {
          iconify: 'iconify图标',
          local: '本地图标'
        }
      }
    },
    petposter: {
      common: {
        refresh: '刷新',
        confirm: '确认',
        cancel: '取消',
        loadFailed: '加载失败',
        operations: '操作'
      },
      quota: {
        pageTitle: '用户配额管理',
        pageSubtitle: '查看与调整用户的生成额度',
        userId: '用户 ID',
        balance: '当前余额',
        totalPurchased: '总充值',
        totalConsumed: '总消耗',
        updatedAt: '更新时间',
        adjust: '调整',
        viewTransactions: '查看流水',
        searchPlaceholder: '搜索用户 ID',
        adjustDialogTitle: '调整配额',
        amountLabel: '调整数量',
        amountTip: '正数为充值，负数为扣减',
        remarkLabel: '备注',
        remarkPlaceholder: '调整原因',
        needUserId: '请输入用户 ID',
        amountNotZero: '调整数量不能为 0',
        adjustSuccess: '配额调整成功',
        adjustFailed: '调整失败',
        txDialogTitle: '交易流水',
        txType: '类型',
        txAmount: '数量',
        txBalanceAfter: '操作后余额',
        txReferenceId: '关联 ID',
        txRemark: '备注',
        txCreatedAt: '时间',
        typeRecharge: '充值',
        typeConsume: '消费',
        typeRefund: '退款',
        typeAdjust: '管理员调整'
      },
      auditLog: {
        pageTitle: '操作审计',
        pageSubtitle: '管理员操作日志，仅可查询不可删除',
        filterAction: '操作类型',
        filterResourceType: '资源类型',
        filterAdminId: '管理员',
        actionPlaceholder: '输入操作名',
        resourceTypePlaceholder: '输入资源类型',
        adminIdPlaceholder: '输入管理员 ID',
        time: '时间',
        adminId: '管理员',
        action: '操作',
        resourceType: '资源类型',
        resourceId: '资源 ID',
        detail: '详情',
        ipAddress: 'IP 地址'
      },
      aiProviders: {
        pageTitle: 'AI 服务配置',
        pageSubtitle: '配置多个 AI 服务供应商，支持优先级切换',
        addProvider: '添加供应商',
        name: '名称',
        baseUrl: '基础地址',
        apiKey: 'API Key',
        modelName: '模型',
        timeout: '超时（秒）',
        priority: '优先级',
        isActive: '状态',
        enabled: '已启用',
        disabled: '已停用',
        enableAction: '启用',
        disableAction: '停用',
        dialogTitleAdd: '新增供应商',
        dialogTitleEdit: '编辑供应商',
        apiKeyEditPlaceholder: '留空则不修改',
        apiKeyRequired: '新建时必须填写 API Key',
        confirmDelete: '确认删除供应商「{name}」？',
        deleteConfirmTitle: '删除确认',
        deleted: '已删除',
        createSuccess: '创建成功',
        updateSuccess: '更新成功',
        deleteFailed: '删除失败',
        createFailed: '创建失败',
        updateFailed: '更新失败',
        toggleFailed: '切换失败'
      },
      failedTasks: {
        pageTitle: '失败任务补发',
        pageSubtitle: '按用户聚合失败任务，支持批量重新提交',
        batchRetry: '批量补发',
        user: '用户',
        failedCount: '失败次数',
        totalTasks: '总任务数',
        lastFailedAt: '最近失败时间',
        viewDetails: '查看详情',
        collapse: '收起',
        selectAll: '全选补发',
        detailsTitle: '用户「{userId}」的失败任务',
        errorMessage: '失败原因',
        retryCount: '重试次数',
        createdAt: '创建时间',
        selectFirst: '请先选择要补发的任务',
        confirmBatchRetry: '确认批量补发 {count} 个失败任务？',
        confirmBatchRetryTitle: '批量补发',
        confirmRetryBtn: '确认补发',
        retrySuccess: '已成功补发 {count} 个任务',
        retryFailed: '补发失败'
      },
      templateStats: {
        drawerTitle: '统计详情',
        usageCount: '累计用量',
        successCount: '成功次数',
        failedCount: '失败次数',
        successRate: '成功率',
        avgDuration: '平均耗时',
        last30Days: '最近 30 天',
        noUsage: '暂无使用记录'
      },
      templates: {
        batchArchive: '批量归档',
        selectFirst: '请先勾选要归档的模板',
        confirmBatchArchive: '确认归档选中的 {count} 个模板？归档后历史任务记录仍保留',
        archiveSuccess: '已归档 {archived} 个，跳过 {skipped} 个',
        clearSelection: '清空选择',
        selectedCount: '已选 {count}',
        selectAllOnPage: '全选本页',
        deselectAll: '取消全选'
      },
      xhs: {
        pageTitle: '小红书推广',
        statsTotal: '总帖数',
        statsPublished: '已发布',
        statsScheduled: '待发布',
        statsDraft: '草稿',
        statusFilter: '状态筛选',
        addPost: '新建帖子',
        id: 'ID',
        titleField: '标题',
        content: '内容',
        tags: '标签',
        addTag: '添加标签',
        status: '状态',
        scheduledAt: '计划发布',
        scheduledAtFull: '计划发布时间',
        publishedAt: '发布时间',
        selectScheduleTime: '选择发布时间',
        llmPrompt: '提示词',
        llmPromptPlaceholder: '用于 AI 生成文案的提示词',
        aiGenerate: 'AI 生成',
        publish: '发布',
        dialogTitleAdd: '新建帖子',
        dialogTitleEdit: '编辑帖子',
        titleRequired: '请输入标题',
        statusDraft: '草稿',
        statusScheduled: '待发布',
        statusPublished: '已发布',
        statusFailed: '失败',
        statusAll: '全部',
        confirmDelete: '确认删除帖子「{title}」？',
        confirmPublish: '确认发布帖子「{title}」？',
        confirmTitle: '确认',
        aiGenDialogTitle: 'AI 生成文案',
        aiGenPromptPlaceholder: '输入推广关键词...',
        aiGenButton: '生成文案',
        aiGenSuccess: '文案生成成功',
        promptRequired: '请输入生成提示词',
        titleFieldPlaceholder: '帖子标题',
        contentPlaceholder: '帖子正文内容',
        tagInputPlaceholder: '添加标签',
        createSuccess: '创建成功',
        updateSuccess: '更新成功',
        deleteSuccess: '删除成功',
        publishSuccess: '发布成功',
        createFailed: '创建失败',
        updateFailed: '更新失败',
        deleteFailed: '删除失败',
        publishFailed: '发布失败',
        generateFailed: '生成失败'
      }
    }
  },
  form: {
    required: '不能为空',
    userName: {
      required: '请输入用户名',
      invalid: '用户名格式不正确'
    },
    phone: {
      required: '请输入手机号',
      invalid: '手机号格式不正确'
    },
    pwd: {
      required: '请输入密码',
      invalid: '密码格式不正确，6-18位字符，包含字母、数字、下划线'
    },
    confirmPwd: {
      required: '请输入确认密码',
      invalid: '两次输入密码不一致'
    },
    code: {
      required: '请输入验证码',
      invalid: '验证码格式不正确'
    },
    email: {
      required: '请输入邮箱',
      invalid: '邮箱格式不正确'
    }
  },
  dropdown: {
    closeCurrent: '关闭',
    closeOther: '关闭其它',
    closeLeft: '关闭左侧',
    closeRight: '关闭右侧',
    closeAll: '关闭所有'
  },
  icon: {
    themeConfig: '主题配置',
    themeSchema: '主题模式',
    lang: '切换语言',
    fullscreen: '全屏',
    fullscreenExit: '退出全屏',
    reload: '刷新页面',
    collapse: '折叠菜单',
    expand: '展开菜单',
    pin: '固定',
    unpin: '取消固定'
  },
  datatable: {
    itemCount: '共 {total} 条'
  }
};

export default local;
