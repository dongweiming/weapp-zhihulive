const api = require('../../utils/api.js');

const App = getApp();
Page({
  data: {
    topics: [],
    windowWidth: App.systemInfo.windowWidth,
  },
  onLoad() {
    const self = this;
    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration: 10000,
    });
    api.getHotTopics({
      success: (res) => {
        const topics = res.data.rs;
        self.setData({
          topics: topics,
        });
        wx.hideToast();
      },
    });
  },
  onViewTap(e) {
    const data = e.currentTarget.dataset;
    console.log();
    wx.navigateTo({
      url: `../topic/topic?id=${data.id}&followers_count=${data.followers_count}&best_answerers_count=${data.best_answerers_count}&best_answers_count=${data.best_answers_count}&name=${data.name}`,
    });
  },
});
