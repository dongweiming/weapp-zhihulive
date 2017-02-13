const apiURL = 'http://localhost:8300/api/v1';

const wxRequest = (params, url) => {
  wx.request({
    url,
    method: params.method || 'GET',
    data: params.data || {},
    header: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
    },
    success(res) {
      if (params.success) {
        params.success(res);
      }
    },
    fail(res) {
      if (params.fail) {
        params.fail(res);
      }
    },
    complete(res) {
      if (params.complete) {
        params.complete(res);
      }
    },
  });
};

const search = (params) => {
  wxRequest(params, `${apiURL}/search`);
};
const suggest = (params) => {
  wxRequest(params, `${apiURL}/suggest`);
};
const explore = (params) => {
  wxRequest(params, `${apiURL}/explore`);
};
const getLiveInfoById = (params) => {
  wxRequest({ success: params.success }, `${apiURL}/live/${params.data.id}`);
};
const getHotTopics = (params) => {
  wxRequest(params, `${apiURL}/hot_topics`);
};
const getTopicByName = (params) => {
  wxRequest(params, `${apiURL}/topic`);
};
const getUsers = (params) => {
  wxRequest(params, `${apiURL}/users`);
};
const getUserInfoById = (params) => {
  wxRequest({ success: params.success }, `${apiURL}/user/${params.data.userId}`);
};
const getHotByWeekly = (params) => {
  wxRequest(params, `${apiURL}/hot/weekly`);
};
const getHotByMonthly = (params) => {
  wxRequest(params, `${apiURL}/hot/monthly`);
};

module.exports = {
  search,
  suggest,
  explore,
  getHotTopics,
  getTopicByName,
  getUsers,
  getUserInfoById,
  getHotByWeekly,
  getHotByMonthly,
  getLiveInfoById
};
