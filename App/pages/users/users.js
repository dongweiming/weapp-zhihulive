const App = getApp();
const api = require('../../utils/api.js');

const sortArray = [
  {
    type: "live_count",
    name: "举办次数"
  },
  {
    type: "updated_time",
    name: "最近更新"
  },
  {
    type: "id",
    name: "加入时间"
  }
];

Page({
  data: {
    orderBy: "live_count",
    users: [],
    sortArray: sortArray,
    sortMap: sortArray.reduce(function (map, obj) {
      map[obj.type] = obj.name;
      return map;
    }, {}),
    start: 0,
    desc: 1,
    loading: false,
    limit: 20,
    hasMore: true,
    windowWidth: App.systemInfo.windowWidth,
    windowHeight: App.systemInfo.windowHeight,
    pixelRatio: App.systemInfo.pixelRatio,
  },
  onLoad() {
    this.loadMore();
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
      limit: self.data.limit,
      order_by: self.data.orderBy,
      desc: self.data.desc
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
    api.getUsers({
      data,
      success: (res) => {
        let users = res.data.rs;
        const hasMore = users.length === self.data.limit;
        if (needRefresh) {
          wx.stopPullDownRefresh();
        } else {
          users = self.data.users.concat(users);
        }
        self.setData({
          users, hasMore,
          start: self.data.start + self.data.limit,
          loading: false
        });
        wx.hideToast();
      },
    });
  },
  bindPickerChange(e) {
    const self = this;
    const index = [e.detail.value];
    this.setData({
      orderBy: this.data.sortArray[index].type
    })
    self.loadData(true);
  },
  loadData(refresh) {
    if (refresh) {
      this.setData({
        start: 0, users: [], hasMore: true
      });
    }
    this.loadMore(null, !refresh);
  },
  onViewTap(e) {
    const ds = e.currentTarget.dataset;
    wx.navigateTo({
      url: `../users/user?id=${ds.id}`,
    });
  },
});