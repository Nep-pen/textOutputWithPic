<template>
    <div class="api-switcher-container">
      <div class="toggle-control">
        <span class="label" :class="{ active: !modelValue.useOwnKey }">
          {{ $t('apiKeySwitcher.useDefaultKey') }}
        </span>
  
        <div class="toggle-switch" @click="toggle" :class="{ active: modelValue.useOwnKey }">
          <div class="thumb"></div>
        </div>
  
        <span class="label" :class="{ active: modelValue.useOwnKey }">
          {{ $t('apiKeySwitcher.useYourKey') }}
        </span>
      </div>
  
      <transition name="fade">
        <div v-if="modelValue.useOwnKey" class="api-key-input-area">
          <label for="apiKeyInput">{{ $t('apiKeySwitcher.label') }}</label>
          <input
            id="apiKeyInput"
            type="password"
            :placeholder= "$t('apiKeySwitcher.placeholder')"
            v-model="apiKey"
          />
        </div>
      </transition>
    </div>
  </template>
  
  <script setup>
  import { computed } from 'vue';
  
  // 1. 定义 props，接收来自父组件的 v-model
  // modelValue 是 v-model 的标准 prop 名称
  const props = defineProps({
    modelValue: {
      type: Object,
      required: true,
      // 提供一个默认工厂函数，确保对象结构
      default: () => ({ useOwnKey: false, apiKey: '' })
    }
  });
  
  // 2. 定义 emits，声明将要触发的事件
  // update:modelValue 是 v-model 的标准事件名称
  const emit = defineEmits(['update:modelValue']);
  
  // 3. 点击开关时调用的方法
  function toggle() {
    // 创建一个新对象来更新状态，并触发事件
    emit('update:modelValue', {
      ...props.modelValue, // 复制已有属性
      useOwnKey: !props.modelValue.useOwnKey // 切换布尔值
    });
  }
  
  // 4. 为输入框创建一个计算属性，实现与父组件 prop 的安全双向绑定
  // 这是处理 v-model 绑定到 prop 对象内部属性的最佳实践
  const apiKey = computed({
    get() {
      return props.modelValue.apiKey;
    },
    set(newValue) {
      // 当输入框的值变化时，触发事件
      emit('update:modelValue', {
        ...props.modelValue, // 复制已有属性
        apiKey: newValue // 更新 apiKey 的值
      });
    }
  });
  </script>

<style scoped>
/* 根容器样式不变 */
.api-switcher-container {
  /* background-color: rgb(18, 18, 18); */
  border-radius: 8px;
  padding: 16px;
  /* border: 1px solid #e1e8ed; */
  max-width: 400px;
}

/* --- 以下是为解决间距问题而修改的样式 --- */

/* 开关控制部分的布局 */
.toggle-control {
  display: flex;
  /* 核心修改 #1: 从 space-between 改为 center，让所有元素在水平方向上居中聚合 */
  /* justify-content: center; */
  align-items: center;
  /* 核心修改 #2 (推荐): 使用 gap 属性来优雅地定义元素间的间距 */
  gap: 12px; /* 你可以调整这个值，比如 8px 或 15px，来控制紧凑程度 */
}

/* 开关旁边的文字标签 */
.toggle-control .label {
  font-size: 14px;
  color: #7d7b7b;
  font-weight: 500;
  transition: color 0.3s ease, font-weight 0.3s ease;
  user-select: none;
}

/* 激活状态的标签样式 */
.toggle-control .label.active {
  color: #f4f2f2;
  font-weight: 700;
}

/* 开关轨道 */
.toggle-switch {
  position: relative;
  width: 52px;
  height: 28px;
  background-color: #dcdfe6;
  border-radius: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
  /* 核心修改 #3: 移除了 margin，因为父元素的 gap 已经负责了间距控制 */
  /* margin: 0 15px; */ /* <-- 移除或注释掉这一行 */
  flex-shrink: 0;
}

/* --- 其余样式保持不变 --- */

.toggle-switch.active {
  background-color: #42b983;
}

.thumb {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  background-color: white;
  border-radius: 50%;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
  transition: transform 0.3s ease;
}

.toggle-switch.active .thumb {
  transform: translateX(24px);
}

.api-key-input-area {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
}

.api-key-input-area label {
  margin-bottom: 8px;
  font-weight: 600;
}

.api-key-input-area input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}

.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>