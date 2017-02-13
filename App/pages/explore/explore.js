const App = getApp();
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');

const formatTime = util.formatTime;

Page({
  data: {
    lives: [],
    start: 0,
    limit: 20,
    loading: false,
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
  },
  onLoad() {
    this.loadMore();
  },
  onPullDownRefresh() {
    this.loadMore(null, true);
  },
  loadMore(e, needRefresh) {
    const self = this;
    const loading = self.data.loading;
    const data = {
      start: self.data.start,
    };
    if (loading) {
      return;
    }
    self.setData({
      loading: true,
    });
    api.explore({
      data,
      success: (res) => {
        let lives = res.data.rs;
        lives.map((live) => {
          const item = live;
          item.starts_at = formatTime(new Date(item.starts_at * 1000), 1);
          return item;
        });
        if (needRefresh) {
          wx.stopPullDownRefresh();
        } else {
          lives = self.data.lives.concat(lives);
        }
        self.setData({
          lives: lives,
          start: self.data.start + self.data.limit,
          loading: false,
        });
      },
    });
  },
  onViewTap(e) {
    const ds = e.currentTarget.dataset;
    const t = ds['type'] === 'live' ? 'live/live' : 'users/user'
    wx.navigateTo({
      url: `../${t}?id=${ds.id}`,
    });
  },
});
