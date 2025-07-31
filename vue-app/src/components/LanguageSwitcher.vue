<template>
    <div class="language-switcher">
      <button @click="switchLang('zh')" :class="{ active: $i18n.locale === 'zh' }">中文</button>
      <button @click="switchLang('en')" :class="{ active: $i18n.locale === 'en' }">English</button>
    </div>
  </template>
  
  <script>
  export default {
    name: 'LanguageSwitcher',
    methods: {
      switchLang(lang) {
        this.$i18n.locale = lang;
        localStorage.setItem('lang', lang);
        document.cookie = `lang=${lang};path=/`;
      }
    }
  }
  </script>
  
  <!-- <style scoped>
  /* 使用 ::v-deep 穿透 scoped 限制，并提高选择器特殊性，
    确保我们的规则能够应用到子组件或深层元素上。
    给根元素一个唯一的类名，比如 .lang-switcher-wrapper
  */
  .language-switcher {
    display: flex; /* 让父容器也使用flex，确保对齐 */
    align-items: center;
  }
  
  /* 使用一个更具体的选择器来提高优先级，
    以对抗全局样式。
  */
  .language-switcher button,
  .language-switcher button:hover,
  .language-switcher button:active,
  .language-switcher button:focus {
    /* --- 核心修复代码 --- */
  
    /* 1. 统一盒模型 */
    box-sizing: border-box !important;
  
    /* 2. 强制设置高度 */
    height: 32px !important;
    min-height: 32px !important; /* 防止被最小高度影响 */
  
    /* 3. 重置可能影响高度的内外边距和行高 */
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 1 !important; /* 强制行高为1，让文字在flex中对齐 */
  
    /* --- 其他辅助样式 --- */
    padding-left: 12px;
    padding-right: 12px;
    margin: 0 5px;
    color: rgb(92, 89, 89) !important;
    border: 1px solid #ccc;
    cursor: pointer;
    background-color: #f0f0f0;
    font-size: 14px;
    border-radius: 4px;
    transition: all 0.2s ease;
    
    /* 使用 Flexbox 来保证内容垂直居中 */
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  
  .language-switcher button.active {
    background-color: #42b983 !important;
    color: white !important;
    border-color: #42b983 !important;
  }
  </style> -->



<style scoped>
  /* 使用 ::v-deep 穿透 scoped 限制，并提高选择器特殊性，
    确保我们的规则能够应用到子组件或深层元素上。
    给根元素一个唯一的类名，比如 .lang-switcher-wrapper
  */
  .language-switcher {
    display: flex; /* 让父容器也使用flex，确保对齐 */
    align-items: center;
  }
  
  /* 使用一个更具体的选择器来提高优先级，
    以对抗全局样式。
  */
  .language-switcher button,
  .language-switcher button:hover,
  .language-switcher button:active,
  .language-switcher button:focus {
    /* --- 核心修复代码 --- */
  
    /* 1. 统一盒模型 */
    box-sizing: border-box !important;
  
    /* 2. 强制设置高度 */
    height: 32px !important;
    min-height: 32px !important; /* 防止被最小高度影响 */
  
    /* 3. 重置可能影响高度的内外边距和行高 */
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    line-height: 1 !important; /* 强制行高为1，让文字在flex中对齐 */
  
    /* --- 其他辅助样式 --- */
    padding-left: 12px;
    padding-right: 12px;
    margin: 0 5px;
    color: rgb(92, 89, 89) !important;
    border: 1px solid #ccc;
    cursor: pointer;
    background-color: #f0f0f0;
    font-size: 14px;
    border-radius: 4px;
    transition: all 0.2s ease;
    
    /* 使用 Flexbox 来保证内容垂直居中 */
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
  }
  
  .language-switcher button.active {
    background-color: rgba(255, 153, 0, 0.5) !important;
    color: white !important;
    border-color: rgba(255, 153, 0, 0.5) !important;
  }
  </style>