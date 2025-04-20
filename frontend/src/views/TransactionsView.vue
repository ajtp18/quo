<template>
  <v-app-bar :elevation="2">
    <v-app-bar-nav-icon @click="goBack">
      <v-icon>mdi-arrow-left</v-icon>
    </v-app-bar-nav-icon>
    <v-app-bar-title>{{ accountInfo?.name || 'Transactions' }}</v-app-bar-title>
  </v-app-bar>

  <v-main>
    <!-- Loading Dialog -->
    <v-dialog v-model="isLoading" persistent width="300">
      <v-card>
        <v-card-text class="text-center pa-4">
          <v-progress-circular
            indeterminate
            color="primary"
            class="mb-3"
          ></v-progress-circular>
          <div class="text-body-1 mb-1">Loading transactions...</div>
          <div class="text-caption text-medium-emphasis">
            {{ loadingMessage }}
          </div>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-container class="py-8">
      <!-- KPI Section -->
      <v-row v-if="!isLoading && !error && kpi">
        <v-col cols="12">
          <v-card class="mb-6">
            <v-card-title class="d-flex align-center">
              <span class="text-h6">KPI</span>
              <v-chip
                class="ml-2"
                color="primary"
                size="small"
                variant="flat"
              >
                Balance Metrics
              </v-chip>
            </v-card-title>
            <v-card-text>
              <div class="d-flex justify-space-between align-center">
                <div>
                  <div class="text-subtitle-1">Total Income</div>
                  <div class="text-h5 text-success">{{ kpi.total_income }}</div>
                </div>
                <div>
                  <div class="text-subtitle-1">Total Expenses</div>
                  <div class="text-h5 text-error">{{ kpi.total_expenses }}</div>
                </div>
                <div>
                  <div class="text-subtitle-1">Net Balance</div>
                  <div class="text-h5">{{ kpi.net_balance }}</div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>

      <!-- Loading State -->
      <v-row v-if="isLoading">
        <v-col cols="12" class="text-center">
          <v-progress-circular indeterminate></v-progress-circular>
        </v-col>
      </v-row>

      <!-- Error State -->
      <v-row v-else-if="error">
        <v-col cols="12">
          <v-alert type="error" title="Error" :text="error.message"></v-alert>
        </v-col>
      </v-row>

      <!-- Transactions List -->
      <v-row v-else>
        <v-col cols="12">
          <v-card>
            <v-list lines="two">
              <v-list-item
                v-for="transaction in transactions"
                :key="transaction.id"
                :title="transaction.description"
                :subtitle="transaction.category || 'Uncategorized'"
              >
                <template v-slot:prepend>
                  <v-icon :icon="transaction.type === 'INFLOW' ? 'mdi-arrow-up' : 'mdi-arrow-down'"
                         :color="transaction.type === 'INFLOW' ? 'success' : 'error'">
                  </v-icon>
                </template>

                <template v-slot:append>
                  <v-chip
                    :color="transaction.type === 'INFLOW' ? 'success' : 'error'"
                    variant="tonal"
                  >
                    {{ transaction.amount }} {{ transaction.currency }}
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
import { useRetryFetch } from '@/composables/useRetryFetch'
import { computed, onMounted, ref, onUnmounted } from 'vue'
import type { TransactionResponse } from '@/types/api'

const route = useRoute()
const router = useRouter()
const session = useSession()

const loadingMessages = [
  'Fetching your transaction history...',
  'Calculating balances...',
  'Almost there...',
  'Processing data...',
  'Getting everything ready...'
]

const loadingMessage = ref(loadingMessages[0])
let messageInterval: number

const startLoadingMessages = () => {
  let index = 0
  messageInterval = window.setInterval(() => {
    index = (index + 1) % loadingMessages.length
    loadingMessage.value = loadingMessages[index]
  }, 2000)
}

const stopLoadingMessages = () => {
  clearInterval(messageInterval)
}

const { data, error, isLoading, execute } = useRetryFetch<TransactionResponse>(
  `${ENDPOINT}/banks/${route.params.linkId}/accounts/${route.params.accountId}/transactions`,
  {
    maxRetries: 2,
    backoffMs: 500,
    timeout: 7000  // Aumentamos el timeout a 7s
  }
)

const transactions = computed(() => data.value?.transactions || [])
const kpi = computed(() => data.value?.kpi)
const accountInfo = computed(() => data.value?.account_info)

const goBack = () => {
  router.push(`/banks/${route.params.linkId}/accounts`)
}

onMounted(async () => {
  startLoadingMessages()
  await execute()
  stopLoadingMessages()
})

onUnmounted(() => {
  stopLoadingMessages()
})
</script> 