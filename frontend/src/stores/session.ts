import { defineStore } from 'pinia'
import { useFetch, useStorage, type BeforeFetchContext } from '@vueuse/core'
import { onMounted, reactive, watch } from 'vue'
import { ENDPOINT } from '@/utils'
import { computed } from '@vue/reactivity'

export const useSession = defineStore('session', () => {
  const accessToken = useStorage('accessToken', '', sessionStorage)
  const refreshToken = useStorage('refreshToken', '', sessionStorage)

  const session = reactive({
    email: '',
    username: '',
    id: -1,
  })

  const initializeSession = () => {
    if (accessToken.value === '') {
      session.email = ''
      session.username = ''
      session.id = -1
      return
    }

    fetch(`${ENDPOINT}/users/me`, {
      method: 'GET',
      headers: new Headers({
        Authorization: `Bearer ${accessToken.value}`,
      }),
    }).then(async (res) => {
      if (res.ok) {
        const data = (await res.json()) as typeof session
        session.email = data.email
        session.username = data.username
        session.id = data.id
      }
    })
  }

  const isExpired = computed(() => {
    if (accessToken.value === '') return true

    const data = JSON.parse(atob(accessToken.value.split('.')[1])) as { exp: number }

    return new Date(data.exp * 1000) < new Date()
  })

  const doRefresh = async () => {
    const response = await fetch(`${ENDPOINT}/auth/refresh`, {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json',
      }),
      body: JSON.stringify({
        refresh_token: refreshToken.value,
      }),
    })

    const data = (await response.json()) as { access_token: string; refresh_token: string }
    setSession(data.access_token, data.refresh_token)
  }

  const injectHeaders = async (ctx: BeforeFetchContext) => {
    if (isExpired.value) {
      await doRefresh()
    }

    ctx.options.headers = {
      Authorization: `Bearer ${accessToken.value}`,
      ...ctx.options.headers,
    }

    return ctx
  }

  const getFetchHeaders = async (headers: { [k: string]: string }) => {
    if (isExpired.value) {
      await doRefresh()
    }

    return new Headers({
      Authorization: `Bearer ${accessToken.value}`,
      ...headers,
    })
  }

  watch(accessToken, initializeSession)
  onMounted(initializeSession)

  const setSession = (access: string, refresh: string) => {
    accessToken.value = access
    refreshToken.value = refresh
  }

  const $reset = () => {
    accessToken.value = ''
    refreshToken.value = ''
    session.email = ''
    session.username = ''
    session.id = -1
  }

  return {
    accessToken,
    refreshToken,
    session,
    setSession,
    injectHeaders,
    getFetchHeaders,
    $reset
  }
})
