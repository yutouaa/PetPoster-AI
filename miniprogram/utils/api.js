const DEFAULT_BASE_URL = "http://127.0.0.1:8000/api";

function getBaseUrl() {
  const app = getApp();
  const configured = app && app.globalData && app.globalData.apiBaseUrl;
  return (configured || DEFAULT_BASE_URL).replace(/\/$/, "");
}

function request(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${getBaseUrl()}${options.url}`,
      method: options.method || "GET",
      data: options.data || {},
      success(res) {
        const body = res.data || {};
        if (res.statusCode >= 200 && res.statusCode < 300 && body.success !== false) {
          resolve(body.data);
          return;
        }
        reject(new Error(body.message || body.msg || `请求失败：${res.statusCode}`));
      },
      fail(err) {
        reject(new Error(err.errMsg || "网络请求失败"));
      }
    });
  });
}

function uploadImage(filePath) {
  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${getBaseUrl()}/upload/images`,
      filePath,
      name: "files",
      success(res) {
        let body = {};
        try {
          body = JSON.parse(res.data || "{}");
        } catch (error) {
          reject(new Error("上传响应解析失败"));
          return;
        }
        if (res.statusCode >= 200 && res.statusCode < 300 && body.success !== false) {
          resolve((body.data && body.data.urls && body.data.urls[0]) || "");
          return;
        }
        reject(new Error(body.message || body.msg || "上传失败"));
      },
      fail(err) {
        reject(new Error(err.errMsg || "上传失败"));
      }
    });
  });
}

module.exports = {
  listTemplates() {
    return request({ url: "/templates" });
  },
  createGenerationTask(data) {
    return request({ url: "/generation-tasks", method: "POST", data });
  },
  getGenerationTask(id, userId) {
    return request({ url: `/generation-tasks/${id}`, data: { userId } });
  },
  listGenerationTasks(params) {
    return request({ url: "/generation-tasks", data: params || {} });
  },
  uploadImage
};
