const App = getApp();
const api = require('../../utils/api.js');
const util = require('../../utils/util.js');
const formatTime = util.formatTime;

export function gen_page(type) {
  return {
    data: {
      lives: [],
      windowWidth: App.systemInfo.windowWidth,
      windowHeight: App.systemInfo.windowHeight,
    },
    onLoad() {
      const self = this;
      wx.showToast({
        title: '正在加载',
        icon: 'loading',
        duration: 10000,
      });
      api[`getHotBy${type}ly`]({
        success: (res) => {
          let lives = res.data.rs;
          lives.map((live) => {
            const item = live;
            item.starts_at = formatTime(new Date(item.starts_at * 1000), 1);
            return item;
          });

          self.setData({ lives, type });
          wx.hideToast();
        }
      });
    },
    onViewTap(e) {
      const ds = e.currentTarget.dataset;
      wx.navigateTo({
        url: `../live/live?id=${ds.id}`,
      });
    },
    onChangeTab(e) {
      const ds = e.currentTarget.dataset;
      if (type == 'Month' && ds.type == 'Week') {
        wx.navigateBack('../hot/weekly');
      } else {
        wx.navigateTo({
          url: `../hot/${ds.type.toLowerCase()}ly`,
        });
      }
    },
  }
}
