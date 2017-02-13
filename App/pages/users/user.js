const App = getApp();
const api = require('../../utils/api.js');

Page({
  data: {
    user: {},
    lives: [],
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
  },
  onReady() {
    const self = this;
    wx.setNavigationBarTitle({
      title: self.data.user.name,
    });
  },
  onLoad(options) {
    const {id} = options;
    const data = { userId: id };
    const self = this;
    wx.showToast({
      title: '正在加载',
      icon: 'loading',
      duration: 10000,
    });
    api.getUserInfoById({
      data,
      success: (res) => {
        let rs = res.data.rs;
        let lives = [], user = [];
        rs.map((item) => {
          if (item.type === 'live') {
            item.pic_url = item.cover;
            item.hiddenUser = true;
            lives.push(item);
          } else {
            item.pic_url = item.avatar_url;
            let gender = "Ta";
            if (item.gender === 0) {
              gender = "她";
            } else if (item.gedner === 1) {
              gender = "他";
            }
            item.gender = gender;
            user = item;
          }
          return item;
        });
        self.setData({ user, lives })
        wx.hideToast();
      },
    });
  },
  onViewTap(e) {
    const ds = e.currentTarget.dataset;
    const t = ds['type'] === 'live' ? `live/live?id=${ds.id}` : 'users/users'
    wx.navigateTo({
      url: `../${t}`,
    });
  },
  viewUserList() {
    const self = this;
    wx.navigateTo({
      url: '../users/users',
    });
  },
});