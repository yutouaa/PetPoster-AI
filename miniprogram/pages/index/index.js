const api = require("../../utils/api");

const petPhotos = [
  "/assets/images/pet-01.png",
  "/assets/images/pet-02.png",
  "/assets/images/pet-03.png",
  "/assets/images/pet-04.png",
  "/assets/images/pet-05.png",
  "/assets/images/pet-06.png",
  "/assets/images/pet-07.png",
  "/assets/images/pet-08.png",
  "/assets/images/pet-09.png"
];

const styleCards = [
  {
    id: "oil",
    no: "01",
    name: "古典油画",
    en: "Oil Painting",
    enUpper: "OIL PAINTING",
    cat: "经典",
    image: "/assets/images/style-oil.png"
  },
  {
    id: "anime",
    no: "02",
    name: "东方水墨",
    en: "Ink Wash",
    enUpper: "INK WASH",
    cat: "经典",
    image: "/assets/images/style-ink-wash.png"
  },
  {
    id: "watercolor",
    no: "03",
    name: "水彩写意",
    en: "Watercolor",
    enUpper: "WATERCOLOR",
    cat: "经典",
    image: "/assets/images/style-watercolor.png"
  },
  {
    id: "magazine",
    no: "04",
    name: "时尚封面",
    en: "Editorial",
    enUpper: "EDITORIAL",
    cat: "潮流",
    image: "/assets/images/style-editorial.png"
  },
  {
    id: "polaroid",
    no: "05",
    name: "复古胶片",
    en: "Vintage Film",
    enUpper: "VINTAGE FILM",
    cat: "复古",
    image: "/assets/images/style-vintage-film.png"
  },
  {
    id: "studio",
    no: "06",
    name: "极简肖像",
    en: "Minimal Portrait",
    enUpper: "MINIMAL PORTRAIT",
    cat: "潮流",
    image: "/assets/images/style-minimal-portrait.png"
  },
  {
    id: "fairy",
    no: "07",
    name: "梦境插画",
    en: "Dreamscape",
    enUpper: "DREAMSCAPE",
    cat: "趣味",
    image: "/assets/images/style-dreamscape.png"
  },
  {
    id: "ink",
    no: "08",
    name: "炭笔素描",
    en: "Charcoal",
    enUpper: "CHARCOAL",
    cat: "经典",
    image: "/assets/images/style-charcoal.png"
  }
];

const historyItems = [];

const steps = [
  "解析照片中的宠物特征",
  "调用风格艺术模型",
  "绘制构图与色调",
  "精修细节与光影",
  "即将完成"
];

const purchases = [
  { id: "p1", title: "高级会员 · 季度", credit: "+ 60 次", amount: "¥ 68.00", date: "2026-05-10", status: "成功" },
  { id: "p2", title: "单次套餐 · 10 张", credit: "+ 10 次", amount: "¥ 18.00", date: "2026-04-22", status: "成功" },
  { id: "p3", title: "单次套餐 · 5 张", credit: "+ 5 次", amount: "¥ 10.00", date: "2026-04-08", status: "成功" },
  { id: "p4", title: "新用户体验包", credit: "+ 3 次", amount: "¥ 0.00", date: "2026-03-30", status: "赠送" }
];

const notifs = [
  { id: "n1", tag: "活动", title: "六折充值仅剩 2 天", body: "限时优惠到 5 月 17 日，错过再等三个月。", time: "刚刚", unread: true },
  { id: "n2", tag: "创作", title: "你的「古典油画」已完成", body: "海报已生成，前往查看与保存。", time: "今天 14:22", unread: true },
  { id: "n3", tag: "系统", title: "新增「炭笔素描」风格", body: "更高级的肖像感，欢迎尝试。", time: "昨天", unread: false },
  { id: "n4", tag: "账户", title: "高级会员续费成功", body: "有效期至 2026-09-12。", time: "5 月 10 日", unread: false }
];

const faqs = [
  { q: "生成失败会扣次数吗？", a: "生成失败不会消耗额度，可在历史里重新尝试。" },
  { q: "支持几种风格？", a: "目前提供 8 种精选风格，每月会更新 1-2 种。" },
  { q: "海报的版权归谁？", a: "你拥有使用权，可个人保存与分享，禁止商用。" },
  { q: "如何获得更高清版本？", a: "高级会员默认 2K，4K 增强版可单独购买。" }
];

const screenStates = [
  "home",
  "style",
  "generating",
  "result",
  "history",
  "mine",
  "favorites",
  "wallet",
  "notif",
  "settings",
  "help"
];

function buildPhotos(count) {
  return petPhotos.slice(0, count).map((url, index) => ({
    id: index,
    url,
    remoteUrl: url,
    cover: index === 0
  }));
}

function safeScreen(value) {
  return screenStates.indexOf(value) >= 0 ? value : "home";
}

function safeStyle(value, cards) {
  const source = cards && cards.length ? cards : styleCards;
  const normalized = String(value || "");
  return source.some((item) => String(item.id) === normalized) ? normalized : String(source[0].id);
}

function safeProgress(value, fallback) {
  const num = Number(value);
  if (!isFinite(num)) {
    return fallback;
  }
  return Math.max(0, Math.min(100, Math.round(num)));
}

function normalizeTemplate(template, index) {
  const fallback = styleCards[index % styleCards.length];
  let config = template.config || {};
  if (typeof config === "string") {
    try {
      config = JSON.parse(config);
    } catch (error) {
      config = {};
    }
  }
  const slug = config.slug || String(template.id);
  const en = config.en || fallback.en;
  return {
    id: String(template.id),
    templateId: template.id,
    no: config.no || String(index + 1).padStart(2, "0"),
    name: template.name,
    en,
    enUpper: String(en).toUpperCase(),
    cat: config.cat || template.category || fallback.cat,
    image: template.coverUrl || template.previewUrl || config.localImage || fallback.image
  };
}

function normalizeHistoryTask(task, cards) {
  const currentCards = cards && cards.length ? cards : styleCards;
  const style = currentCards.find((item) => item.templateId === task.templateId || item.id === String(task.templateId)) || currentCards[0];
  const createdAt = task.createdAt ? new Date(task.createdAt) : null;
  return {
    id: String(task.id),
    no: String(task.id).padStart(3, "0"),
    style: task.templateName || (style && style.name) || "宠物海报",
    date: createdAt ? createdAt.toLocaleString("zh-CN", { month: "numeric", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "-",
    status: task.status === "success" ? "已完成" : (task.status === "failed" ? "失败" : "生成中"),
    saved: false,
    image: task.resultImageUrl || (style && style.image) || styleCards[0].image
  };
}

Page({
  timer: null,
  pollTimer: null,
  enterTimer: null,
  sheetTimer: null,
  photoPopTimer: null,

  data: {
    current: "home",
    screenReady: true,
    cats: ["全部", "经典", "潮流", "复古", "趣味"],
    cat: "全部",
    picked: "oil",
    styleId: "oil",
    progress: 6,
    generatingTaskId: null,
    resultImageUrl: "",
    displayResultImage: styleCards[0].image,
    generationError: "",
    apiError: "",
    uploading: false,
    resultMeta: {
      elapsed: "-",
      resolution: "1024 × 1024",
      style: ""
    },
    saved: false,
    liked: false,
    sheetOpen: false,
    sheetVisible: false,
    sheetActive: false,
    lastAddedPhotoId: null,
    nextPhotoId: 4,
    photos: buildPhotos(4),
    petPhotos,
    styleCards,
    filteredStyles: styleCards,
    pickedStyle: styleCards[0],
    currentStyle: styleCards[0],
    historyItems,
    favs: historyItems.filter((item) => item.saved),
    purchases,
    notifs,
    faqs,
    renderSteps: [],
    photoCount: 4,
    canAddPhoto: true,
    sourcePhotos: buildPhotos(4),
    remainSeconds: 12,
    prefs: {
      done: true,
      promo: true,
      save: false
    }
  },

  onLoad(options) {
    const screen = safeScreen(options && options.previewScreen);
    const styleId = safeStyle(options && options.style, this.data.styleCards);
    const progress = screen === "generating"
      ? safeProgress(options && options.progress, 48)
      : (screen === "result" ? 100 : 6);
    this.setWithComputed({
      current: screen,
      picked: styleId,
      styleId,
      progress,
      screenReady: true
    });
    this.loadTemplates();
    this.loadHistory();
  },

  onUnload() {
    this.stopTimer();
    this.clearMotionTimers();
  },

  buildComputed(patch) {
    const next = Object.assign({}, this.data, patch);
    const styleSource = next.styleCards && next.styleCards.length ? next.styleCards : styleCards;
    const historySource = next.historyItems && next.historyItems.length ? next.historyItems : historyItems;
    const filteredStyles = next.cat === "全部"
      ? styleSource
      : styleSource.filter((item) => item.cat === next.cat);
    const pickedStyle = styleSource.find((item) => String(item.id) === String(next.picked)) || styleSource[0];
    const currentStyle = styleSource.find((item) => String(item.id) === String(next.styleId)) || styleSource[0];
    const stepIdx = Math.min(steps.length - 1, Math.floor(next.progress / 20));
    return Object.assign({}, patch, {
      filteredStyles,
      pickedStyle,
      currentStyle,
      favs: historySource.filter((item) => item.saved),
      photoCount: next.photos.length,
      canAddPhoto: next.photos.length < 9,
      sourcePhotos: next.photos.slice(0, 4),
      displayResultImage: next.resultImageUrl || currentStyle.image,
      remainSeconds: Math.max(2, Math.ceil((100 - next.progress) / 8)),
      renderSteps: steps.map((label, index) => ({
        id: index,
        label,
        mark: String(index + 1),
        done: index < stepIdx,
        active: index === stepIdx
      }))
    });
  },

  setWithComputed(patch) {
    this.setData(this.buildComputed(patch));
  },

  async loadTemplates() {
    try {
      const templates = await api.listTemplates();
      const cards = (templates || []).map(normalizeTemplate);
      if (!cards.length) {
        return;
      }
      const cats = ["全部"].concat(Array.from(new Set(cards.map((item) => item.cat))));
      const picked = safeStyle(this.data.picked, cards);
      this.setWithComputed({
        apiError: "",
        cats,
        styleCards: cards,
        picked,
        styleId: safeStyle(this.data.styleId, cards)
      });
    } catch (error) {
      this.setData({ apiError: error.message || "模板接口不可用，已使用本地样式" });
    }
  },

  async loadHistory() {
    try {
      const data = await api.listGenerationTasks({
        page: 1,
        pageSize: 20,
        userId: getApp().globalData.userId
      });
      const records = data && data.records ? data.records : [];
      if (!records.length) {
        return;
      }
      this.setWithComputed({
        historyItems: records.map((item) => normalizeHistoryTask(item, this.data.styleCards))
      });
    } catch (error) {
      this.setData({ apiError: error.message || "历史接口不可用，已使用本地记录" });
    }
  },

  clearMotionTimers() {
    if (this.enterTimer) {
      clearTimeout(this.enterTimer);
      this.enterTimer = null;
    }
    if (this.sheetTimer) {
      clearTimeout(this.sheetTimer);
      this.sheetTimer = null;
    }
    if (this.photoPopTimer) {
      clearTimeout(this.photoPopTimer);
      this.photoPopTimer = null;
    }
  },

  enterScreen(patch) {
    if (this.enterTimer) {
      clearTimeout(this.enterTimer);
      this.enterTimer = null;
    }
    this.setWithComputed(Object.assign({ screenReady: false }, patch));
    this.enterTimer = setTimeout(() => {
      this.setData({ screenReady: true });
      this.enterTimer = null;
    }, 30);
  },

  navTo(screen) {
    if (screen === "generating") {
      this.startGenerating(this.data.picked);
      return;
    }
    this.stopTimer();
    this.closeSheet();
    this.enterScreen({ current: screen });
  },

  setScreen(event) {
    this.navTo(event.currentTarget.dataset.screen);
  },

  goBack() {
    const map = {
      style: "home",
      generating: "style",
      result: "style",
      history: "mine",
      favorites: "mine",
      wallet: "mine",
      notif: "mine",
      settings: "mine",
      help: "mine"
    };
    this.navTo(map[this.data.current] || "home");
  },

  switchTab(event) {
    const detail = event.detail || {};
    this.navTo(detail.tab || event.currentTarget.dataset.tab);
  },

  openStyle() {
    this.navTo("style");
  },

  openResult() {
    this.navTo("result");
  },

  setCat(event) {
    this.setWithComputed({ cat: event.currentTarget.dataset.cat });
  },

  pickStyle(event) {
    this.setWithComputed({ picked: event.currentTarget.dataset.id });
  },

  startGenerate() {
    this.startGenerating(this.data.picked);
  },

  startGenerating(styleId) {
    this.stopTimer();
    this.closeSheet();
    this.enterScreen({
      current: "generating",
      styleId,
      progress: 6,
      generatingTaskId: null,
      resultImageUrl: "",
      generationError: "",
      saved: false,
      liked: false
    });
    this.startProgressLoop();
    this.createGenerationTask(styleId);
  },

  startProgressLoop() {
    this.timer = setInterval(() => {
      const current = this.data.progress;
      const next = Math.min(96, current + 3);
      this.setWithComputed({ progress: next });
    }, 720);
  },

  async createGenerationTask(styleId) {
    const style = this.data.styleCards.find((item) => String(item.id) === String(styleId));
    const templateId = style && style.templateId;
    if (!templateId) {
      this.finishLocalGeneration("未找到后端模板，已使用本地预览结果");
      return;
    }

    try {
      const imageUrls = this.data.photos
        .map((item) => item.remoteUrl || item.url)
        .filter((url) => url.startsWith("http"));
      if (!imageUrls.length) {
        this.finishLocalGeneration("照片未上传成功，请重新选择照片");
        return;
      }
      const task = await api.createGenerationTask({
        templateId,
        userId: getApp().globalData.userId,
        imageUrls
      });
      this.setData({ generatingTaskId: task.id });
      this.pollGenerationTask(task.id);
    } catch (error) {
      this.finishLocalGeneration(error.message || "生成接口不可用，已使用本地预览结果");
    }
  },

  pollGenerationTask(taskId) {
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
    }
    let attempts = 0;
    const maxAttempts = 120;
    this.pollTimer = setInterval(async () => {
      attempts += 1;
      if (attempts > maxAttempts) {
        this.finishLocalGeneration("生成超时，请稍后在历史记录中查看结果");
        return;
      }
      try {
        const task = await api.getGenerationTask(taskId, getApp().globalData.userId);
        if (task.status === "success") {
          this.finishRemoteGeneration(task);
        } else if (task.status === "failed") {
          this.finishLocalGeneration(task.errorMessage || "生成失败，已使用本地预览结果");
        }
      } catch (error) {
        this.finishLocalGeneration(error.message || "查询任务失败，已使用本地预览结果");
      }
    }, 1500);
  },

  finishRemoteGeneration(task) {
    this.stopTimer();
    const createdAt = task.createdAt ? new Date(task.createdAt).getTime() : 0;
    const completedAt = task.completedAt ? new Date(task.completedAt).getTime() : Date.now();
    const elapsedSeconds = createdAt ? Math.round((completedAt - createdAt) / 1000) : 0;
    this.setWithComputed({
      progress: 100,
      resultImageUrl: task.resultImageUrl || "",
      generationError: "",
      resultMeta: {
        elapsed: elapsedSeconds > 0 ? `${elapsedSeconds} 秒` : "-",
        resolution: "1024 × 1024",
        style: this.data.currentStyle ? this.data.currentStyle.name : ""
      }
    });
    this.loadHistory();
    setTimeout(() => {
      this.enterScreen({ current: "result" });
    }, 420);
  },

  finishLocalGeneration(message) {
    this.stopTimer();
    this.setWithComputed({
      progress: 100,
      generationError: message,
      resultImageUrl: "",
      resultMeta: {
        elapsed: "-",
        resolution: "-",
        style: this.data.currentStyle ? this.data.currentStyle.name : ""
      }
    });
    setTimeout(() => {
      this.enterScreen({ current: "result" });
    }, 420);
  },

  stopTimer() {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = null;
    }
    if (this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  },

  openSheet() {
    if (this.sheetTimer) {
      clearTimeout(this.sheetTimer);
      this.sheetTimer = null;
    }
    this.setData({
      sheetOpen: true,
      sheetVisible: true,
      sheetActive: false
    });
    this.sheetTimer = setTimeout(() => {
      this.setData({ sheetActive: true });
      this.sheetTimer = null;
    }, 30);
  },

  closeSheet() {
    if (!this.data.sheetVisible && !this.data.sheetOpen) {
      return;
    }
    if (this.sheetTimer) {
      clearTimeout(this.sheetTimer);
      this.sheetTimer = null;
    }
    this.setData({
      sheetOpen: false,
      sheetActive: false
    });
    this.sheetTimer = setTimeout(() => {
      this.setData({ sheetVisible: false });
      this.sheetTimer = null;
    }, 300);
  },

  addPhoto() {
    if (wx.chooseMedia) {
      this.chooseAndUploadPhotos();
      return;
    }
    this.addLocalPhoto();
  },

  addLocalPhoto() {
    const photos = this.data.photos.slice();
    if (photos.length >= 9) {
      this.closeSheet();
      return;
    }
    const id = this.data.nextPhotoId;
    photos.push({
      id,
      url: petPhotos[id % petPhotos.length],
      cover: photos.length === 0
    });
    this.setWithComputed({
      photos,
      nextPhotoId: id + 1,
      lastAddedPhotoId: id
    });
    this.closeSheet();
    if (this.photoPopTimer) {
      clearTimeout(this.photoPopTimer);
    }
    this.photoPopTimer = setTimeout(() => {
      this.setData({ lastAddedPhotoId: null });
      this.photoPopTimer = null;
    }, 520);
  },

  async chooseAndUploadPhotos() {
    const remain = 9 - this.data.photos.length;
    if (remain <= 0) {
      this.closeSheet();
      return;
    }
    this.closeSheet();
    try {
      this.setData({ uploading: true });
      const media = await new Promise((resolve, reject) => {
        wx.chooseMedia({
          count: remain,
          mediaType: ["image"],
          sourceType: ["album", "camera"],
          success: resolve,
          fail: reject
        });
      });
      const files = media.tempFiles || [];
      const nextPhotos = this.data.photos.slice();
      for (let index = 0; index < files.length; index += 1) {
        const filePath = files[index].tempFilePath;
        let remoteUrl = filePath;
        try {
          remoteUrl = await api.uploadImage(filePath);
        } catch (error) {
          wx.showToast({ title: "上传失败，使用本地预览", icon: "none" });
        }
        nextPhotos.push({
          id: this.data.nextPhotoId + index,
          url: filePath,
          remoteUrl,
          cover: nextPhotos.length === 0
        });
      }
      this.setWithComputed({
        photos: nextPhotos,
        nextPhotoId: this.data.nextPhotoId + files.length,
        lastAddedPhotoId: files.length ? this.data.nextPhotoId + files.length - 1 : null
      });
    } catch (error) {
      if (!String(error.errMsg || "").includes("cancel")) {
        wx.showToast({ title: "选择图片失败", icon: "none" });
      }
    } finally {
      this.setData({ uploading: false });
    }
  },

  toggleLike() {
    this.setData({ liked: !this.data.liked });
  },

  saveResult() {
    const imageUrl = this.data.resultImageUrl;
    if (!imageUrl) {
      wx.showToast({ title: "暂无图片可保存", icon: "none" });
      return;
    }
    const doSave = (filePath) => {
      wx.saveImageToPhotosAlbum({
        filePath,
        success: () => {
          this.setData({ saved: true });
          wx.showToast({ title: "已保存到相册", icon: "success" });
        },
        fail: (err) => {
          if (String(err.errMsg || "").includes("auth deny")) {
            wx.showModal({
              title: "需要授权",
              content: "请在设置中允许保存图片到相册",
              confirmText: "去设置",
              success: (res) => { if (res.confirm) wx.openSetting(); }
            });
          } else {
            wx.showToast({ title: "保存失败", icon: "none" });
          }
        }
      });
    };
    if (imageUrl.startsWith("http")) {
      wx.downloadFile({
        url: imageUrl,
        success: (res) => {
          if (res.statusCode === 200) {
            doSave(res.tempFilePath);
          } else {
            wx.showToast({ title: "下载图片失败", icon: "none" });
          }
        },
        fail: () => {
          wx.showToast({ title: "下载图片失败", icon: "none" });
        }
      });
    } else {
      doSave(imageUrl);
    }
  },

  togglePref(event) {
    const key = event.currentTarget.dataset.key;
    const prefs = Object.assign({}, this.data.prefs);
    prefs[key] = !prefs[key];
    this.setData({ prefs });
  }
});
