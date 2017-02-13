const App = getApp();
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');

const lengthStr = util.lengthStr;

Page({
  data: {
    title: '',
    q: '',
    suggest: false,
    status: 'all',
    lives: [],
    users: [],
    start: 0,
    loading: false,
    limit: 20,
    hasMore: true,
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
    pixelRatio: App.systemInfo.pixelRatio,
  },
  onPullDownRefresh() {
    this.loadMore(null, true);
  },
  loadMore(e, needRefresh) {
    const self = this;
    if (!self.data.hasMore) {
      return;
    }
    const loading = self.data.loading;
    const data = {
      start: self.data.start,
      q: self.data.q,
      status: self.data.status,
      limit: self.data.limit
    };
    if (loading
    ) {
      return;
    }
    self.setData({
      loading: true
    });
    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration: 10000,
    });
    api.search({
      data,
      success: (res) => {
        let rs = res.data.rs;
        let lives = [], users = [];
        rs.map((item) => {
          if (item.type === 'live') {
            item.pic_url = item.cover;
            lives.push(item);
          } else {
            item.pic_url = item.avatar_url;
            users.push(item);
          }
          return item;
        });
        if (needRefresh) {
          wx.stopPullDownRefresh();
        } else {
          lives = self.data.lives.concat(lives);
          users = self.data.users.concat(users);
        }
        if (self.data.status !== 'all') {
          users = [];
        }
        self.setData({
          lives, users,
          start: self.data.start + self.data.limit,
          loading: false,
          hasMore: lives.length === self.data.limit
        });
        wx.hideToast();
      },
    });
  },
  bindKeyInput(e) {
    const self = this;
    const q = e.detail.value.replace(/'/g, '').trim();
    const data = { q };
    this.setData({ q, suggest: true, users: [] });
    if (lengthStr(q) > 4) {
      api.suggest({
        data,
        success: (res) => {
          let lives = res.data.rs;
          self.setData({ lives });
        },
      });
    }
  },
  onSearch(e) {
    const self = this;
    self.setData({ suggest: false });
    self.loadData(true);
  },
  onChangeTab(e) {
    const self = this;
    const status = e.currentTarget.dataset.status;
    self.setData({ status });
    self.loadData(true);
  },
  loadData(refresh) {
    if (refresh) {
      this.setData({
        start: 0, lives: [], users: [], hasMore: true
      });
    }
    this.loadMore(null, !refresh);
  },
  viewHotTopics() {
    wx.navigateTo({
      url: `../topic/hot_topics`,
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