export const dialogsTemplate = String.raw`
  <div class="toast" :class="[toast.type, { show: toast.show }]" v-if="toast.show">{{ toast.message }}</div>

  <div class="confirm-dialog" :class="{ visible: dialog.show }" v-if="dialog.show" style="display:flex;">
    <div class="confirm-dialog-overlay" @click="dialog.resolve(false)"></div>
    <div class="confirm-dialog-content">
      <h4>{{ dialog.title }}</h4>
      <p>{{ dialog.message }}</p>
      <label v-if="dialog.optionLabel" class="confirm-option">
        <input type="checkbox" v-model="dialog.optionValue" />
        <span>{{ dialog.optionLabel }}</span>
      </label>
      <div class="confirm-dialog-actions">
        <button type="button" class="btn btn-secondary" @click="dialog.resolve(false)">取消</button>
        <button type="button" class="btn" :class="dialog.okClass" @click="dialog.resolve(true)">{{ dialog.okText }}</button>
      </div>
    </div>
  </div>

  <div class="confirm-dialog" :class="{ visible: subCreateVisible }" v-if="subCreateVisible" style="display:flex;">
    <div class="confirm-dialog-overlay" @click="closeCreateSubDialog()"></div>
    <div class="confirm-dialog-content" style="max-width:520px;text-align:left;">
      <h4>新建订阅</h4>
      <div class="form-group">
        <label>RSS 链接</label>
        <div class="input-wrapper"><input type="text" v-model="subCreateForm.url" placeholder="https://example.com/feed.xml" /></div>
      </div>
      <div class="form-group">
        <label>推送目标会话</label>
        <div class="input-wrapper"><input type="text" v-model="subCreateForm.target_session" list="sub-create-sessions" placeholder="aiocqhttp:FriendMessage:123456" /></div>
        <datalist id="sub-create-sessions">
          <option v-for="s in subs" :key="'opt-' + s.id" :value="s.target_session"></option>
        </datalist>
      </div>
      <div class="form-group">
        <label>平台（留空自动推断）</label>
        <div class="input-wrapper"><input type="text" v-model="subCreateForm.platform_name" placeholder="留空则按目标会话前缀推断" /></div>
      </div>
      <div class="form-group">
        <label>标题（可选）</label>
        <div class="input-wrapper"><input type="text" v-model="subCreateForm.title" placeholder="留空则使用 Feed 标题" /></div>
      </div>
      <div class="confirm-dialog-actions">
        <button type="button" class="btn btn-secondary" @click="closeCreateSubDialog()">取消</button>
        <button type="button" class="btn btn-primary" :class="{ 'is-loading': isPending('sub:create') }" :disabled="isPending('sub:create')" @click="submitCreateSub()">创建</button>
      </div>
    </div>
  </div>

  <div class="confirm-dialog" :class="{ visible: feedCreateVisible }" v-if="feedCreateVisible" style="display:flex;">
    <div class="confirm-dialog-overlay" @click="closeCreateFeedDialog()"></div>
    <div class="confirm-dialog-content" style="max-width:520px;text-align:left;">
      <h4>新建 Feed</h4>
      <div class="form-group">
        <label>Feed 链接</label>
        <div class="input-wrapper"><input type="text" v-model="feedCreateForm.url" placeholder="https://example.com/feed.xml" /></div>
      </div>
      <div class="form-group">
        <label>标题（可选）</label>
        <div class="input-wrapper"><input type="text" v-model="feedCreateForm.title" placeholder="留空则自动抓取" /></div>
      </div>
      <div class="confirm-dialog-actions">
        <button type="button" class="btn btn-secondary" @click="closeCreateFeedDialog()">取消</button>
        <button type="button" class="btn btn-primary" :class="{ 'is-loading': isPending('feed:create') }" :disabled="isPending('feed:create')" @click="submitCreateFeed()">创建</button>
      </div>
    </div>
  </div>
`;
