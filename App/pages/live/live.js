const App = getApp();
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');

const formatTime = util.formatTime;

Page({
  data: {
    'live': {},
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
  },
  onReady() {
    const self = this;
    wx.setNavigationBarTitle({
      title: self.data.live.subject,
    });
  },
  onLoad(options) {
    const {id} = options;
    const data = { id };
    const self = this;
    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration: 10000,
    });
    api.getLiveInfoById({
      data,
      success: (res) => {
        let live = res.data.rs;
        live.starts_at = formatTime(new Date(live.starts_at * 1000), 1);
        live.description = live.description.split('\r\n');
        self.setData({ live });
        wx.hideToast();
      },
    });
  },
  onViewTap(e) {
    const ds = e.currentTarget.dataset;
    wx.navigateTo({
      url: `../users/user?id=${ds.id}`,
    });
  },
});