import {
  getSubscriptions,
  createSubscription,
  unsubscribe,
  updateSubscription,
  setSubscriptionState,
  testSubscription,
  batchActivate,
  batchDeactivate,
  batchUnsubscribe,
  getStats
} from '../../js/api.js';
import {
  normalizeTagValues,
  normalizeTextFilterValue,
  inheritedNumberToPayload,
  createEmptySubscriptionFilters
} from '../helpers.js';

export const subscriptionsModule = {
  async loadData(resetPage = true) {
    this.loading = true;
    try {
      const [subResult, statsResult] = await Promise.all([
        getSubscriptions(this.subFilters),
        getStats(),
      ]);
      this.subs = subResult.items || [];
      this.stats = statsResult.stats || this.stats;
      this.filteredSubs = [...this.subs];
      if (resetPage) {
        this.resetSubPage();
        this.selectedIds = [];
      }
      this.clampSubPage();
    } catch (err) {
      this.showToast(`加载失败: ${err.message}`, 'error');
    } finally {
      this.loading = false;
    }
  },

  async openSubscriptionsWithFilter(filters = {}) {
    const nextFilters = createEmptySubscriptionFilters();
    for (const [key, value] of Object.entries(filters)) {
      if (!nextFilters[key]) continue;
      if (nextFilters[key] && typeof nextFilters[key] === 'object' && Array.isArray(nextFilters[key].values)) {
        nextFilters[key].values = normalizeTagValues(value);
        nextFilters[key].input = '';
      } else {
        nextFilters[key] = normalizeTextFilterValue(value);
      }
    }
    this.subFilters = nextFilters;
    this.activeTab = 'subs';
    await this.runPending('subs:refresh', () => this.loadData());
  },

  async selectFeed(feedId) {
    await this.openSubscriptionsWithFilter({ feed_id: feedId || '' });
  },

  async selectSubscription(subId) {
    await this.openSubscriptionsWithFilter({ sub_id: subId || '' });
  },

  resetSubPage() {
    this.subPagination.page = 1;
  },

  clampSubPage() {
    const totalPages = this.subTotalPages();
    if (this.subPagination.page > totalPages) this.subPagination.page = totalPages;
    if (this.subPagination.page < 1) this.subPagination.page = 1;
  },

  subTotalPages() {
    const pageSize = this.subPagination.pageSize || 20;
    return Math.max(1, Math.ceil(this.filteredSubs.length / pageSize));
  },

  showSubPagination() {
    return this.filteredSubs.length > (this.subPagination.pageSize || 20);
  },

  pagedSubs() {
    this.clampSubPage();
    const pageSize = this.subPagination.pageSize || 20;
    const start = (this.subPagination.page - 1) * pageSize;
    return this.filteredSubs.slice(start, start + pageSize);
  },

  subPrevPage() {
    if (this.subPagination.page > 1) {
      this.subPagination.page -= 1;
      this.selectedIds = [];
    }
  },

  subNextPage() {
    if (this.subPagination.page < this.subTotalPages()) {
      this.subPagination.page += 1;
      this.selectedIds = [];
    }
  },

  toggleEditMode() {
    this.editMode = !this.editMode;
    if (!this.editMode) this.selectedIds = [];
  },

  toggleSelect(id) {
    const index = this.selectedIds.indexOf(id);
    if (index >= 0) {
      this.selectedIds.splice(index, 1);
    } else {
      this.selectedIds.push(id);
    }
  },

  openCreateSubDialog() {
    this.subCreateForm = {
      url: '',
      title: '',
      target_session: '',
      platform_name: '',
    };
    this.subCreateVisible = true;
  },

  closeCreateSubDialog() {
    this.subCreateVisible = false;
  },

  async submitCreateSub() {
    const form = this.subCreateForm;
    if (!form.url.trim()) {
      this.showToast('请填写 RSS 链接', 'error');
      return;
    }
    if (!form.target_session.trim()) {
      this.showToast('请填写推送目标会话', 'error');
      return;
    }
    await this.runPending('sub:create', async () => {
      const result = await createSubscription(
        form.url.trim(),
        form.target_session.trim(),
        form.platform_name.trim(),
        form.title.trim()
      );
      if (result.ok === false) {
        throw new Error(result.error || result.message || '创建失败');
      }
      this.subCreateVisible = false;
      this.showToast(result.message || '订阅已创建');
      await this.loadData();
    }).catch((err) => {
      this.showToast(`创建失败: ${err.message}`, 'error');
    });
  },

  async toggleSubState(sub) {
    if (!sub || !sub.id) return;
    const nextState = sub.state === 1 ? 0 : 1;
    await this.runPending(`sub:state:${sub.id}`, async () => {
      const result = await setSubscriptionState(sub.id, nextState);
      if (result.ok === false) {
        throw new Error(result.error || result.message || '操作失败');
      }
      sub.state = nextState;
      this.showToast(nextState === 1 ? '订阅已启用' : '订阅已停用');
      await this.loadData();
    }).catch((err) => {
      this.showToast(`操作失败: ${err.message}`, 'error');
    });
  },

  async batchActivate() {
    if (this.selectedIds.length === 0) return;
    const count = this.selectedIds.length;
    await this.runPending('batch:activate', async () => {
      await batchActivate(this.selectedIds);
      this.selectedIds = [];
      this.showToast(`已启用 ${count} 个订阅`);
      await this.loadData();
    }).catch((err) => {
      this.showToast(`批量启用失败: ${err.message}`, 'error');
    });
  },

  async batchDeactivate() {
    if (this.selectedIds.length === 0) return;
    const count = this.selectedIds.length;
    await this.runPending('batch:deactivate', async () => {
      await batchDeactivate(this.selectedIds);
      this.selectedIds = [];
      this.showToast(`已禁用 ${count} 个订阅`);
      await this.loadData();
    }).catch((err) => {
      this.showToast(`批量禁用失败: ${err.message}`, 'error');
    });
  },

  async batchUnsubscribe() {
    if (this.selectedIds.length === 0) return;
    const confirm = await this.showConfirm(
      `确定取消 ${this.selectedIds.length} 个订阅？此操作不可恢复。`,
      '批量取消订阅',
      '取消订阅',
      'btn-danger',
      { optionLabel: '同时清理对应推送历史' }
    );
    if (!confirm.ok) return;
    const count = this.selectedIds.length;
    await this.runPending('batch:unsubscribe', async () => {
      await batchUnsubscribe(this.selectedIds, confirm.optionChecked);
      this.selectedIds = [];
      this.showToast(`已取消 ${count} 个订阅`);
      await this.loadData();
      if (confirm.optionChecked) await this.loadPushHistory();
    }).catch((err) => {
      this.showToast(`批量取消失败: ${err.message}`, 'error');
    });
  },

  async handleTestDetail(subId) {
    if (!subId) return;
    const targetSession =
      this.panelMode === 'edit'
        ? this.editForm.target_session
        : this.detailSub.target_session;
    const platformName =
      this.panelMode === 'edit'
        ? this.editForm.platform_name
        : this.detailSub.platform_name;
    await this.runPending(`sub:test:${subId}`, async () => {
      const result = await testSubscription(subId, targetSession, platformName);
      this.showToast(result.message || '测试完成');
    }).catch((err) => {
      this.showToast(`测试失败: ${err.message}`, 'error');
    });
  },

  async handleEditSub() {
    await this.runPending(`sub:save:${this.editForm.id}`, async () => {
      const options = {};
      if (this.editForm.title !== undefined) options.title = this.editForm.title;
      if (this.editForm.tags !== undefined) options.tags = this.editForm.tags;
      options.interval = inheritedNumberToPayload(this.editForm.interval_control);
      if (this.editForm.target_session !== undefined) {
        options.target_session = this.editForm.target_session;
      }
      options.length_limit = inheritedNumberToPayload(this.editForm.length_limit_control);
      options.state = this.editForm.state_ ? 1 : 0;
      options.notify = this.editForm.notify;
      options.send_mode = this.editForm.send_mode;
      options.display_author = this.editForm.display_author;
      options.display_via = this.editForm.display_via;
      options.display_title = this.editForm.display_title;
      options.display_entry_tags = this.editForm.display_entry_tags;
      options.style = this.editForm.style;
      options.display_media = this.editForm.display_media;

      await updateSubscription(this.editForm.id, options);
      this.showToast('订阅已更新');
      this.closePanel();
      await this.loadData();
    }).catch((err) => {
      this.showToast(`更新失败: ${err.message}`, 'error');
    });
  },

  async handleDeleteSub() {
    const id = this.panelMode === 'edit' ? this.editForm.id : this.detailSub.id;
    if (!id) return;
    const confirm = await this.showConfirm(
      '确定删除此订阅？此操作不可恢复。',
      '删除订阅',
      '删除',
      'btn-danger',
      { optionLabel: '同时清理对应推送历史' }
    );
    if (!confirm.ok) return;
    await this.runPending(`sub:delete:${id}`, async () => {
      await unsubscribe(id, confirm.optionChecked);
      this.showToast('订阅已删除');
      this.closePanel();
      await this.loadData();
      if (confirm.optionChecked) await this.loadPushHistory();
    }).catch((err) => {
      this.showToast(`删除失败: ${err.message}`, 'error');
    });
  }
};
