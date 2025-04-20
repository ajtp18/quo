<template>
  <v-app-bar :elevation="2">
    <v-app-bar-nav-icon @click="goBack">
      <v-icon>mdi-arrow-left</v-icon>
    </v-app-bar-nav-icon>
    <v-app-bar-title>Accounts</v-app-bar-title>
  </v-app-bar>

  <v-main>
    <v-container class="py-8">
      <v-row>
        <v-col cols="12">
          <h2 class="text-h5 mb-4">Account List</h2>
        </v-col>
      </v-row>

      <v-row v-if="isFetching">
        <v-col cols="12" class="text-center">
          <v-progress-circular indeterminate></v-progress-circular>
        </v-col>
      </v-row>

      <v-row v-else-if="error">
        <v-col cols="12">
          <v-alert type="error" title="Error" :text="error"></v-alert>
        </v-col>
      </v-row>

      <v-row v-else>
        <v-col cols="12">
          <v-card>
            <v-list lines="two">
              <v-list-item
                v-for="account in accounts"
                :key="account.id"
                :title="account.name"
                :subtitle="account.category"
                @click="goToTransactions(account.id)"
              >
                <template v-slot:prepend>
                  <v-icon :icon="getCategoryIcon(account.category)"></v-icon>
                </template>

                <template v-slot:append>
                  <v-chip
                    :color="getBalanceColor(account.balance.current)"
                    variant="tonal"
                  >
                    {{ account.balance.current }} {{ account.currency }}
                  </v-chip>
                </template>
              </v-list-item>
            </v-list>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </v-main>
</template>

<script setup lang="ts">
import { ENDPOINT } from '@/utils'
import { useRoute, useRouter } from 'vue-router'
import { useSession } from '@/stores/session'
import { useFetch } from '@vueuse/core'
import { computed } from 'vue'

const route = useRoute()
const router = useRouter()
const session = useSession()

const { isFetching, error, data: accounts } = useFetch(
  `${ENDPOINT}/banks/${route.params.linkId}/accounts`,
  {
    beforeFetch: (ctx) => session.injectHeaders(ctx)
  }
).json()

const getCategoryIcon = (category: string) => {
  const icons: Record<string, string> = {
    CHECKING_ACCOUNT: 'mdi-bank',
    SAVINGS_ACCOUNT: 'mdi-piggy-bank',
    CREDIT_CARD: 'mdi-credit-card',
    LOAN_ACCOUNT: 'mdi-cash',
    PENSION_FUND_ACCOUNT: 'mdi-account-cash'
  }
  return icons[category] || 'mdi-help-circle'
}

const getBalanceColor = (balance: number) => {
  if (balance > 0) return 'success'
  if (balance < 0) return 'error'
  return 'info'
}

const goBack = () => {
  router.push('/banks')
}

const goToTransactions = (accountId: string) => {
  router.push(`/banks/${route.params.linkId}/accounts/${accountId}/transactions`)
}
</script> 