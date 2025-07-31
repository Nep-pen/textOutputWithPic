<template>
  <div id="app">
    <LanguageSwitcher />
    <h1>{{ selectFields[selectedType] && selectFields[selectedType][labelType] ? selectFields[selectedType][labelType] + $t('topTitle.text') : selectedType + $t('topTitle.text') }}</h1>
    <ApiKeySwitcher v-model="apiSettings" />

    <div class="container">
      <div class="controls">
        <!-- 新增：弹窗按钮 -->
        <button @click="showDialog = true">{{ $t('geminiApiNotice.buttonTexr') }}</button>
        <!-- 弹窗结构 -->
        <div v-if="showDialog" class="custom-dialog-overlay">
          <div class="custom-dialog">
            <p>{{ $t('geminiApiNotice.experienceOnly') }}</p>
            <p v-html="$t('geminiApiNotice.customKeyPrompt')"></p>
            <p v-html="$t('geminiApiNotice.usageWarning')"></p>
            <p>{{ $t('geminiApiNotice.disclaimer') }}</p>
            <p v-html="$t('geminiApiNotice.knowledge')"></p>
            <button @click="showDialog = false">{{ $t('geminiApiNotice.close') }}</button>
          </div>
        </div>
        <h3>1. {{ $t('uploadPic.titleText') }}</h3>
        <div
          class="drop-zone"
          :class="{ 'is-dragging': isDragging }"
          @dragenter.prevent="handleDragEnter"
          @dragover.prevent
          @dragleave.prevent="handleDragLeave"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
          v-if="imageUrl === ''"
        >
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            class="file-input"
            @change="handleFileChange"
          />
          <div class="drop-zone-text">
            <p>{{ $t('uploadPic.dropZone') }}</p>
            <p>{{ $t('uploadPic.or') }} <strong>{{ $t('uploadPic.clickUpload') }}</strong></p>
          </div>
        </div>
        <img v-if="imageUrl" :src="imageUrl" alt="Image preview" class="preview" style="width: 100%; height: auto; object-fit: contain;"/>
        <button @click="imageUrl = ''; imageFile = null" :disabled="isLoading || !imageFile">
          {{ $t('uploadPic.deletePic') }}
        </button>

        <h3>2. {{ $t('selectType.titleText') }}</h3>
        <div class="radio-group">
          <div v-for="(field, key) in selectFields" class="radio-option">
            <input type="radio" :id="key" :value="key" v-model="selectedType">
            <label :for="key">{{ field[labelType]? field[labelType] : key }}</label>
          </div>
        </div>

        <h3>3. {{ $t('inputSetting.titleText') }}</h3>
        <form v-if="!isFormLoading && !noFields">
          <div v-for="(field, key) in sortedFormFields" :key="key" class="input-group">
            <label :for="key">{{ field[labelType] }}</label>
            <input type="text" :id="key" v-model="formData[field.key]" :placeholder="`${$t('inputSetting.inputPlaceHolder')}${field[labelType]}`">
          </div>
          <div key="userSettings" class="input-group">
            <label for="userSettings">{{ $t('inputSetting.extraSetting') }}</label>
            <input type="text" id="userSetting" v-model="userSettings" :placeholder="$t('inputSetting.extraSettingPlaceHolder')">
          </div>
        </form>

        <button @click="generate" :disabled="isLoading || !imageFile">
          {{ isLoading ? $t('loadingText.loading') : $t('loadingText.beginLoad') }}
        </button>
      </div>

      <div class="results">
        <h3>{{ $t('resultText.titleText') }}</h3>
        <img v-if="imageUrl && generatedJson" :src="imageUrl" alt="Image preview" class="preview" style="width: 100%; height: 100%; object-fit: contain;"/>
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="isLoading" class="loading-spinner"></div>
        <div v-for="(field, key) in sortedOutputFormFields" v-if="generatedJson">
          <h4>{{ field[labelType]? field[labelType] : key }}</h4>
          <pre class="rating-result" v-if="field.key == 'rating'">{{ generatedJson[field.key] }}</pre>
          <pre class="field-result" v-if="field.key !== 'rating'">{{ generatedJson[field.key] }}</pre>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// 1. 引入外部库
import axios from 'axios';
import LanguageSwitcher from './components/LanguageSwitcher.vue';
import ApiKeySwitcher from './components/ApiKeySwitcher.vue';
import { ref } from 'vue';
// 2. 使用 export default 定义组件选项
export default {
  name: 'App', // 定义组件名是一个好习惯
  components: {
    LanguageSwitcher,
    ApiKeySwitcher
  },
  // 3. data() 函数负责组件的响应式状态
  data() {
    return {
      apiSettings: {
        useOwnKey: false,
        apiKey: ''
      },
      imageFile: null,
      imageUrl: '',
      userSettings: '',
      generatedJson: '',
      isLoading: false,
      error: '',
      isDragging: false,
      selectedType: 'story_dynamic',
      formFields: {},
      outputFormFields: {},
      selectFields: {},
      formData: {},
      outputFormData: {},
      submittedData: null,
      error: null,
      isFormLoading: true,
      showDialog: true, // 新增：控制弹窗显示
      noFields: false
    };
  },

  mounted() {
    this.loadFormConfig('story_dynamic');
  },

  watch: {
    selectedType(newType, oldType) {
      this.loadFormConfig(newType);
    }
  },

  computed: {
    sortedFormFields() {
      if(!this.formFields) return;
      const dataAsArray = Object.keys(this.formFields).map(key => {
        return {
          key: key,
          ...this.formFields[key]
        }
      })

      return dataAsArray.sort((a,b) => {
        return a.sort - b.sort
      })
    },
    sortedOutputFormFields() {
      const dataAsArray = Object.keys(this.outputFormFields).map(key => {
        return {
          key: key,
          ...this.outputFormFields[key]
        }
      })

      return dataAsArray.sort((a,b) => {
        return a.sort - b.sort
      })
    },
    labelType() {
      if(this.$i18n.locale === 'zh') { return 'label-zh'; }
      else if(this.$i18n.locale === 'en') { return 'label-en'; }
      else { return '' }
    }
  },

  // 4. methods 对象包含了所有的业务逻辑和事件处理函数
  // 注意：在方法内部，需要使用 `this` 来访问 `data` 中的属性
  methods: {
    async loadFormConfig(typeStr) {
      this.error = '';
      try {
        const response = await fetch('/api/get-form-config');
        if (!response.ok) {
          throw new Error(`fail to access form config: ${response.statusText}`);
        }
        const parsedData = await response.json();
        // if ('fields' in parsedData.types[typeStr]) 
        if (!'fields' in parsedData.types[typeStr]) this.noFields = true;
        else this.noFields = false;
        const fields = parsedData.types[typeStr].fields;
        // 使用 'this' 关键字来访问和修改 data 中的属性
        this.selectFields = parsedData.types
        this.formFields = fields;
        
        // 初始化 formData
        const initialFormData = {};
        for (const key in fields) {
          initialFormData[key] = '';
        }
        this.formData = initialFormData;

      } catch (e) {
        console.error('fail to parse YAML or access config:', e);
        // 更新 error 状态
        this.error = 'fail to load form config, please check the form config file';
      } finally {
        // 结束加载状态
        this.isFormLoading = false;
      }
    },
    async loadOutputConfig(typeStr) {
      try {
        const response = await fetch('/api/get-output-config');
        if (!response.ok) {
          throw new Error(`fail to access output config: ${response.statusText}`);
        }
        const parsedData = await response.json();
        const fields = parsedData.types[typeStr].fields;
        // 使用 'this' 关键字来访问和修改 data 中的属性
        this.outputFormFields = fields;
        
        // 初始化 formData
        const initialFormData = {};
        for (const key in fields) {
          initialFormData[key] = '';
        }
        this.outputFormData = initialFormData;
      } catch (e) {
        console.error('fail to parse YAML or access config:', e);
        // 更新 error 状态
        this.error = 'fail to load form config, please check the output config file';
      }
    },
    handleDragEnter(event) {
      this.isDragging = true;
    },
    handleDragLeave(event) {
      this.isDragging = false;
    },
    handleDrop(event) {
      this.isDragging = false;
      // 从 event.dataTransfer.files 获取拖入的文件列表
      const files = event.dataTransfer.files;
      if (files.length > 0) {
        // 通常我们只处理第一个文件
        this.handleImageUpload(files[0]);
      }
    },
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileChange(event) {
      const files = event.target.files;
      if (files.length > 0) {
        this.handleImageUpload(files[0]);
      }
    },
    handleImageUpload(file) {
      if (!file) return;
      // 验证文件类型
      if (!file.type.startsWith('image/')) {
        alert('请上传图片文件 (Please upload an image file).');
        return;
      }
      if (file) {
        // 使用 this.imageFile 替代 imageFile.value
        this.imageFile = file;
        this.imageUrl = URL.createObjectURL(file);
      }
    },

    // async/await 语法在 methods 中同样适用
    async generate() {
      if (!this.imageFile) {
        alert(this.$t('generateText.generateAlert'));
        return;
      }

      if (this.apiSettings.useOwnKey === true && this.apiSettings.apiKey === '') {
        alert(this.$t('generateText.apiAlert'));
        return;
      }

      this.isLoading = true;
      this.generatedJson = '',
      this.error = '';

      this.formData['image'] = this.imageFile;
      this.formData['user_settings'] = this.userSettings;
      this.formData['used_type'] = this.selectedType;
      this.formData['apiSettings'] = this.apiSettings;
      this.formData['lang'] = this.$i18n.locale

      this.loadOutputConfig(this.selectedType);

      try {
        const response = await axios.post('/api/generate', this.formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        this.generatedJson = response.data

      } catch (err) {
        const errorMessage =  err.response?.data?.error || err.message;
        this.error = `${this.$t('generateText.error')} ${errorMessage}`;
        console.error(err);
      } finally {
        this.isLoading = false;
      }
    },
  },
};
</script>

<!-- <style>
/* 样式部分无需任何改动，保持原样即可 */
:root {
  --primary-color: #42b983;
  --dark-color: #35495e;
  --light-gray: #f4f4f4;
  --medium-gray: #ddd;
  --dark-gray: #888;
  --error-color: #d33;
  --background-color: #fff;
  --font-family: Avenir, Helvetica, Arial, sans-serif;
  --border-radius: 8px;
}
/* ... 其它所有样式 ... */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--light-gray);
  color: #2c3e50;
}

#app {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  padding: 1.5rem; /* 在移动端提供边距 */
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

h1 {
  text-align: center;
  color: var(--dark-color);
  margin-bottom: 2rem;
}

/* --- 移动端优先布局 (默认) --- */
.container {
  display: flex;
  flex-direction: column; /* 移动端默认垂直堆叠 */
  gap: 2.5rem; /* 上下模块的间距 */
  width: 100%;
}

.controls, .results {
  background: var(--background-color);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  display: flex;
  flex-direction: column;
  gap: 1rem; /* 内部元素间距 */
}

h3 {
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

.preview {
  width: 100%;
  height: auto; /* 高度自适应 */
  max-height: 300px; /* 限制最大高度，防止图片过大 */
  object-fit: cover; /* 保持图片比例，裁剪多余部分 */
  border-radius: var(--border-radius);
  border: 1px solid var(--medium-gray);
}

input[type="file"] {
  font-size: 1rem;
}

.radio-group {
  display: flex;
  flex-wrap: wrap; /* 在小屏幕上允许换行 */
  gap: 1.5rem; /* 选项之间的间距 */
  padding: 0.5rem 0;
}
.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem; /* 单选按钮和文字的间距 */
}
.radio-option label {
  cursor: pointer;
  font-weight: 500;
  color: #333;
}
.radio-option input[type="radio"] {
  cursor: pointer;
  /* 使用 accent-color 可以轻松改变单选框和复选框的颜色 */
  accent-color: var(--primary-color);
  width: 1.15em;
  height: 1.15em;
}
.input-group {
  padding-top: 3%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 80;
}
.input-group label {
  font-weight: 500;
  color: #333;
}
.input-group input[type="text"],
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  resize: vertical; /* 允许用户垂直调整大小 */
  font-family: inherit;
  font-size: 1rem;
}

textarea:focus, input[type="file"]:focus {
  outline: 2px solid var(--primary-color);
  border-color: transparent;
}

button {
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  border: none;
  border-radius: var(--border-radius);
  background-color: var(--primary-color);
  color: white;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

button:hover:not(:disabled) {
  background-color: #35a071;
}

button:active:not(:disabled) {
    transform: scale(0.98);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.results pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: var(--light-gray);
  padding: 15px;
  border-radius: var(--border-radius);
  min-height: 100px;
  font-size: 0.95rem;
  line-height: 1.6;
}

.error-message {
  color: var(--error-color);
  background-color: #fdd;
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid var(--error-color);
}

/* 简单的加载动画 */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.loading-spinner {
  margin: 2rem auto;
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
}

.drop-zone {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%; /* 或者你需要的具体宽度，如 300px */
  min-height: 200px;
  padding: 25px;
  border: 2px dashed #ccc;
  border-radius: 12px;
  background-color: #f9f9f9;
  color: #888;
  cursor: pointer;
  transition: border-color 0.3s, background-color 0.3s;
  text-align: center;
}

.drop-zone:hover {
  border-color: #aaa;
}

/* 当文件被拖拽到区域上方的活动样式 */
.drop-zone.is-dragging {
  border-color: #2196F3; /* 使用一个高亮颜色 */
  background-color: #e3f2fd;
}

.drop-zone-text p {
  margin: 0;
  line-height: 1.5;
}

/* 隐藏原始的 input[type=file] */
.file-input {
  display: none;
}

/* --- 桌面端布局 (屏幕宽度 > 768px) --- */
@media (min-width: 768px) {
  #app {
    /* 在大屏上限制内容最大宽度，使其更易读 */
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .container {
    flex-direction: row; /* 桌面端改为水平排列 */
    align-items: flex-start; /* 顶部对齐 */
    gap: 2rem; /* 左右模块的间距 */
  }

  .controls, .results {
    flex: 1; /* 让两个模块平分宽度 */
    min-width: 0; /* 允许 flex item 收缩 */
  }

  /* 让结果区可以变得更高 */
  .results {
    align-self: stretch; /* 让结果区和控制区等高 */
  }

  .results pre {
      flex-grow: 1; /* 让 pre 标签填满剩余空间 */
  }
}
</style> -->


<style>
/* style for the Vue webpage */

/* Define custom CSS variables for the theme */
:root {
  --primary-color: #f90; /* Vibrant orange */
  --dark-color: #000; /* Deep black for backgrounds */
  --light-gray: #222; /* Darker gray for secondary backgrounds */
  --medium-gray: #444; /* Medium gray for borders */
  --dark-gray: #666; /* Lighter gray for text */
  --error-color: #c00; /* Red for error messages */
  --background-color: #111; /* Near-black background for main content */
  --font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; /* Sleek, modern font */
  --border-radius: 6px; /* Slightly softer corners for a modern look */
}

/* Reset and base styles */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--dark-color); /* Black background */
  color: #fff; /* White text for contrast */
}

#app {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  padding: 1.5rem;
  width: 100%;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #000, #1a1a1a); /* Subtle gradient for depth */
}

h1 {
  text-align: center;
  color: var(--primary-color); /* Orange for headings */
  margin-bottom: 2rem;
  font-weight: bold;
  text-transform: uppercase; /* Bold and uppercase for impact */
  letter-spacing: 1px;
}

/* Mobile-first layout */
.container {
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  width: 100%;
}

.controls, .results {
  background: var(--background-color);
  padding: 1.5rem;
  border-radius: var(--border-radius);
  box-shadow: 0 4px 12px rgba(255, 153, 0, 0.2); /* Orange-tinted shadow */
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border: 1px solid var(--medium-gray); /* Subtle border */
}

h3 {
  border-bottom: 2px solid var(--primary-color);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
  color: #fff;
  font-weight: bold;
}

.preview {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: cover;
  border-radius: var(--border-radius);
  border: 1px solid var(--primary-color); /* Orange border for images */
}

input[type="file"] {
  font-size: 1rem;
  color: #fff;
}

.radio-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 0.5rem 0;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.radio-option label {
  cursor: pointer;
  font-weight: 500;
  color: #fff; /* White text for labels */
}

.radio-option input[type="radio"] {
  cursor: pointer;
  accent-color: var(--primary-color); /* Orange radio buttons */
  width: 1.15em;
  height: 1.15em;
}

.input-group {
  padding-top: 3%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-height: 80px;
}

.input-group label {
  font-weight: 500;
  color: #fff;
}

.input-group input[type="text"],
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--medium-gray);
  border-radius: var(--border-radius);
  resize: vertical;
  font-family: inherit;
  font-size: 1rem;
  background-color: #222; /* Dark input background */
  color: #fff; /* White text in inputs */
}

textarea:focus, input[type="file"]:focus {
  outline: 2px solid var(--primary-color);
  border-color: transparent;
}

button {
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  border: none;
  border-radius: var(--border-radius);
  background-color: var(--primary-color); /* Orange buttons */
  color: #000; /* Black text for contrast */
  transition: background-color 0.2s ease, transform 0.1s ease, box-shadow 0.2s ease;
}

button:hover:not(:disabled) {
  background-color: #e80; /* Slightly darker orange on hover */
  box-shadow: 0 0 10px rgba(255, 153, 0, 0.5); /* Glowing effect */
}

button:active:not(:disabled) {
  transform: scale(0.98);
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.6;
  background-color: var(--medium-gray);
}

.results pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #222; /* Darker result background */
  padding: 15px;
  border-radius: var(--border-radius);
  min-height: 100px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #fff;
  border: 1px solid var(--medium-gray);
  color: #e1c4c4;
}

.error-message {
  color: #fff;
  background-color: var(--error-color); /* Red background for errors */
  padding: 1rem;
  border-radius: var(--border-radius);
  border: 1px solid #a00;
}

/* Loading animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-spinner {
  margin: 2rem auto;
  border: 4px solid rgba(255, 255, 255, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: var(--primary-color);
  animation: spin 1s ease-in-out infinite;
}

.drop-zone {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 200px;
  padding: 25px;
  border: 2px dashed var(--medium-gray);
  border-radius: 12px;
  background-color: #1a1a1a; /* Dark drop zone */
  color: var(--dark-gray);
  cursor: pointer;
  transition: border-color 0.3s, background-color 0.3s;
}

.drop-zone:hover {
  border-color: var(--primary-color); /* Orange border on hover */
  background-color: #222;
}

.drop-zone.is-dragging {
  border-color: var(--primary-color);
  background-color: #333;
}

.drop-zone-text p {
  margin: 0;
  line-height: 1.5;
  color: #fff;
}

.file-input {
  display: none;
}

.field-result {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #222;
  padding: 15px;
  border-radius: var(--border-radius);
  min-height: 100px;
  font-size: 0.95rem;
  line-height: 1.6;
  color: #fff;
  border: 1px solid var(--medium-gray);
}

.rating-result {
  white-space: pre-wrap;
  word-wrap: break-word;
  background: linear-gradient(45deg, var(--primary-color), #ff6200); /* Orange gradient */
  padding: 20px; /* More padding for emphasis */
  border-radius: var(--border-radius);
  min-height: 100px;
  font-size: 5rem !important; /* Slightly larger font */
  line-height: 1.6;
  color: #000; /* Black text for contrast */
  font-weight: bold; /* Bold text for impact */
  box-shadow: 0 0 15px rgba(255, 153, 0, 0.7); /* Glowing orange shadow */
  border: 2px solid var(--primary-color); /* Thicker orange border */
  text-align: center; /* Centered text for prominence */
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.rating-result:hover {
  transform: scale(1.02); /* Subtle scale-up on hover */
  box-shadow: 0 0 20px rgba(255, 153, 0, 0.9); /* Enhanced glow on hover */
}

/* Desktop layout (screens > 768px) */
@media (min-width: 768px) {
  #app {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
  }

  .container {
    flex-direction: row;
    align-items: flex-start;
    gap: 2rem;
  }

  .controls, .results {
    flex: 1;
    min-width: 0;
  }

  .results {
    align-self: stretch;
  }

  .results pre {
    flex-grow: 1;
    color: #e1c4c4;
  }
}

.custom-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.custom-dialog {
  background: #222;
  color: #fff;
  padding: 2rem 2.5rem;
  border-radius: 10px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.25);
  min-width: 260px;
  text-align: center;
}
.custom-dialog button {
  margin-top: 1.5rem;
  background: var(--primary-color);
  color: #000;
  border: none;
  border-radius: var(--border-radius);
  padding: 0.5rem 1.5rem;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}
.custom-dialog button:hover {
  background: #e80;
}
</style>