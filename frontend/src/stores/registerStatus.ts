import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useRegisterStatus = defineStore('register-status', () => {
  const status = ref(false)
  const email = ref('')
  const setStatus = (_email: string) => {
    status.value = true
    email.value = _email
  }

  return { status, email, setStatus }
})
