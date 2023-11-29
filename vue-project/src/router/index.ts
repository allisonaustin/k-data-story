import { createRouter, createWebHistory } from 'vue-router'
import App from '../App.vue'
import SpatialView from '../components/SpatialView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: SpatialView
    },
  ]
})

export default router
