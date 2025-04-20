import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import AccountsView from '@/views/AccountsView.vue'
import TransactionsView from '@/views/TransactionsView.vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/banks'
    },
    {
      path: '/banks',
      component: HomeView,
    },
    {
      path: '/login',
      component: LoginView,
    },
    {
      path: '/register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/banks/:linkId/accounts',
      component: AccountsView,
    },
    {
      path: '/banks/:linkId/accounts/:accountId/transactions',
      component: TransactionsView,
    }
  ],
})

export default router
