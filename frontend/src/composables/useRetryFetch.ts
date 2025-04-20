import { ref, computed } from 'vue'
import { useSession } from '@/stores/session'

interface RetryOptions {
  maxRetries?: number
  backoffMs?: number
  timeout?: number
}

export function useRetryFetch<T>(url: string, options: RetryOptions = {}) {
  const data = ref<T | null>(null)
  const error = ref<Error | null>(null)
  const isLoading = ref(false)
  const session = useSession()

  const {
    maxRetries = 2,
    backoffMs = 500,
    timeout = 3000
  } = options

  const fetchWithTimeout = async (url: string, options = {}) => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    try {
      const headers = await session.getFetchHeaders({})
      const response = await fetch(url, { 
        ...options, 
        signal: controller.signal,
        headers
      })
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  }

  const execute = async () => {
    isLoading.value = true
    error.value = null

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        if (attempt > 0) await new Promise(r => setTimeout(r, attempt * backoffMs))
        
        const response = await fetchWithTimeout(url)
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
        
        const result = await response.json()
        data.value = result as T
        isLoading.value = false
        return result
      } catch (e) {
        if (attempt === maxRetries) {
          error.value = e as Error
          isLoading.value = false
        }
      }
    }
  }

  return {
    data: computed(() => data.value),
    error: computed(() => error.value),
    isLoading: computed(() => isLoading.value),
    execute
  }
} 