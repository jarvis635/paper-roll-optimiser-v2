<template>
  <div class="app-container">
    <CspTool />
  </div>
</template>

<script>
import CspTool from './components/CspTool.vue'

export default {
  name: 'App',
  components: {
    CspTool
  }
}
</script>

<style>
@import './assets/claymorphism.css';

.app-container {
  min-height: 100vh;
  padding: 32px 20px;
  box-sizing: border-box;
}
</style>
