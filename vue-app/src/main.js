import './assets/main.css'

import { createApp } from 'vue'
import { createI18n } from 'vue-i18n'
import App from './App.vue'

import en from './locales/en.js'
import zh from './locales/zh.js'

const i18n = createI18n({
    // highlight-start
    legacy: true, // 关键：设置为 true 以在选项式 API 中获得完整支持
    // highlight-end
    locale: localStorage.getItem('lang') || 'zh',
    fallbackLocale: 'en',
    messages: {
      en,
      zh
    }
})

const app = createApp(App)
app.use(i18n)
app.mount('#app')

console.log('i18n instance messages:', i18n.global.messages)
