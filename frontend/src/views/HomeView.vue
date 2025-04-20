<template>
<v-app-bar :elevation="2">
  <v-app-bar-title>
    <div class="text-truncate d-flex align-center">
      <span class="text-body-1">Welcome again! &nbsp;</span>
    </div>
  </v-app-bar-title>
  <v-spacer></v-spacer>
  <v-btn
    icon
    @click="handleLogout"
  >
    <v-icon>mdi-logout</v-icon>
    <v-tooltip
      activator="parent"
      location="bottom"
    >
      Logout
    </v-tooltip>
  </v-btn>
</v-app-bar>

<v-main>
  <v-container class="py-8">
    <!-- Título descriptivo -->
    <v-row>
      <v-col cols="12">
        <h2 class="text-h5 mb-4">Available Banks</h2>
      </v-col>
    </v-row>

    <v-list
        v-if="!isFetching && !error"
        lines="two"
    >
        <v-list-item
            v-for="item in sortedInstitutions"
            :key="item.name"
            :value="item.name"
            :subtitle="item.type"
            :title="item.name"
            :disabled="isInstitutionUnavailable(item.name)"
            @click="onInstitutionClick(item)"
            :class="{ 'cursor-pointer': !isInstitutionUnavailable(item.name) }"
        >
            <template v-slot:prepend>
                <v-avatar>
                    <v-img
                        :alt="item.name"
                        :src="item.icon_logo"
                    ></v-img>
                </v-avatar>
            </template>

            <template v-slot:append>
                <v-icon
                    :color="isInstitutionUnavailable(item.name) ? 'error' : 'primary'"
                >
                    {{ isInstitutionUnavailable(item.name) ? 'mdi-alert-circle' : 'mdi-chevron-right' }}
                </v-icon>
            </template>

            <template v-if="isInstitutionUnavailable(item.name)">
                <v-tooltip activator="parent" location="end">
                    {{ getUnavailableMessage(item.name) }}
                </v-tooltip>
            </template>
        </v-list-item>
    </v-list>

    <!-- Loading Dialog -->
    <v-dialog v-model="isLoading" persistent width="300">
      <v-card>
        <v-card-text>
          Connecting to bank...
          <v-progress-linear
            indeterminate
            color="primary"
            class="mb-0"
          ></v-progress-linear>
        </v-card-text>
      </v-card>
    </v-dialog>

    <v-snackbar
      v-model="showError"
      color="warning"
      timeout="3000"
    >
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="retryConnection"
        >
          Retry
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</v-main>
</template>

<script setup lang="ts">
import { ENDPOINT } from '@/utils';
import { computed, onBeforeMount, onMounted, ref } from 'vue';
import { useSession } from '@/stores/session';
import { useRouter } from 'vue-router';
import { useFetch } from '@vueuse/core'
import { INSTITUTION_CREDENTIALS, UNAVAILABLE_INSTITUTIONS } from '@/config'

const { isFetching, error, data: institutions, execute } = useFetch(`${ENDPOINT}/banks/institutions`, {
    immediate: false,
    beforeFetch: (ctx) => session.injectHeaders(ctx),
}).json<{name: string, type: string, icon_logo: string}[]>()

const router = useRouter();
const session = useSession();

const isLoading = ref(false)
const showError = ref(false)
const errorMessage = ref('')
const currentInstitution = ref<{name: string, type: string} | null>(null)

const retryConnection = () => {
  if (currentInstitution.value) {
    onInstitutionClick(currentInstitution.value)
  }
}

const isInstitutionUnavailable = (name: string) => {
    return UNAVAILABLE_INSTITUTIONS.some(inst => inst.name === name)
}

const getUnavailableMessage = (name: string) => {
    const institution = UNAVAILABLE_INSTITUTIONS.find(inst => inst.name === name)
    return institution?.message || 'Temporarily unavailable'
}

const onInstitutionClick = async (item: {name: string, type: string}) => {
    if (isInstitutionUnavailable(item.name)) {
        showError.value = true
        errorMessage.value = `${item.name} is not available at this moment`
        return
    }

    currentInstitution.value = item
    isLoading.value = true
    
    try {
        // Get credentials
        const credentials = INSTITUTION_CREDENTIALS[item.name] || 
                          INSTITUTION_CREDENTIALS.default_bank

        const res = await fetch(`${ENDPOINT}/banks/links/`, {
            method: 'POST',
            headers: await session.getFetchHeaders({
                'Content-Type': 'application/json',
            }),
            body: JSON.stringify({
                institution: item.name,
                credentials
            })
        })

        if (!res.ok) {
            const errorData = await res.json()
            throw new Error(errorData.detail || 'Failed to create link')
        }

        const data = await res.json()
        if (data.results && data.results.length > 0) {
            const linkId = data.results[0].id
            
            // Wait for Belvo to process the information
            await new Promise(resolve => setTimeout(resolve, 2000))
            
            // Check if the link is ready
            const statusRes = await fetch(`${ENDPOINT}/banks/links/${linkId}/status`, {
                headers: await session.getFetchHeaders({})
            })
            
            if (!statusRes.ok) {
                throw new Error('Link is not ready yet')
            }
            
            router.push(`/banks/${linkId}/accounts`)
        } else {
            throw new Error('No link created')
        }
    } catch (error) {
        console.error('Error:', error)
        errorMessage.value = error instanceof Error ? 
            error.message : 
            'Connection failed. Please try again.'
        showError.value = true
    } finally {
        isLoading.value = false
    }
}

const sortedInstitutions = computed(() => {
    if (!institutions.value) return []
    
    return [...institutions.value].sort((a, b) => {
        const aUnavailable = isInstitutionUnavailable(a.name)
        const bUnavailable = isInstitutionUnavailable(b.name)
        
        if (aUnavailable === bUnavailable) return 0
        return aUnavailable ? 1 : -1
    })
})

const handleLogout = async () => {
  if (!session.refreshToken || !session.accessToken) {
    console.error('No tokens found')
    session.$reset()
    router.push('/login')
    return
  }

  try {
    const res = await fetch(`${ENDPOINT}/auth/logout`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...await session.getFetchHeaders({})
      },
      body: JSON.stringify({
        refresh_token: session.refreshToken,
        access_token: session.accessToken
      })
    })

    if (!res.ok) {
      const errorData = await res.json()
      console.log('Error details:', errorData)
      throw new Error(
        errorData.detail?.[0]?.msg || 
        errorData.detail || 
        'Logout failed'
      )
    }

    // Limpiar sesión y redirigir
    session.$reset()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    errorMessage.value = error instanceof Error ? error.message : 'Failed to logout'
    showError.value = true
  }
}

onBeforeMount(() => {
    if (session.accessToken === '') {
        router.push('/login');
    }
})

onMounted(() => {
    execute();
})
</script>