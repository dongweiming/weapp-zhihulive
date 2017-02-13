const App = getApp();
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');

const formatTime = util.formatTime;

Page({
  data: {
    best_answerers_count: '',
    best_answers_count: '',
    name: '',
    followers_count: '',
    lives: [],
    start: 0,
    limit: 20,
    loading: false,
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
  },
  onReady() {
    const self = this;
    wx.setNavigationBarTitle({
      title: self.data.name,
    });
  },
  onLoad(options) {
    const {id, name, best_answerers_count, best_answers_count, followers_count} = options;

    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration: 10000,
    });
    this.setData({
      name: name,
      best_answerers_count: best_answerers_count,
      best_answers_count: best_answers_count,
      followers_count: followers_count
    });
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
      topic: self.data.name,
    };
    if (loading) {
      return;
    }
    self.setData({
      loading: true,
    });
    api.getTopicByName({
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
        wx.hideToast();
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