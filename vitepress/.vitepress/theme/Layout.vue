<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import BackroomsNotFound from './components/BackroomsNotFound.vue'

// 只替换「没找到页面」那一格，其余版式完全沿用 VitePress 默认主题
const { Layout } = DefaultTheme
</script>

<template>
  <Layout>
    <template #not-found>
      <BackroomsNotFound />
    </template>
  </Layout>
</template>
