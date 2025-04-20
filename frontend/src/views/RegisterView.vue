<template>
<v-container height="100vh">
    <v-row align-content="center" class="h-100">
    <v-col cols="12" offset-sm="2" sm="8" offset-md="4" md="4">
        <v-card>
        <v-card-item>
            <v-card-title>
                Register
            </v-card-title>


            <div v-if="alert.show" class="pa-4">
                <v-alert
                    :text="alert.text"
                    :title="alert.title"
                    :type="alert.type as 'error' | 'warning' | 'success' | 'info'"
                    variant="tonal"
                ></v-alert>
            </div>
        </v-card-item>

        <v-card-text>
            <v-text-field
                v-model="email"
                label="Email"
                type="email"
                required
            />
            <v-text-field
                v-model="username"
                label="User Name"
                required
            />
            <v-text-field
                v-model="password"
                label="Password"
                :type="showPassword? 'text' : 'password'"
                :rules="[rules.required, rules.password]"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                required
            />
            <v-text-field
                v-model="confirmPassword"
                label="Confirm Password"
                :type="showPassword? 'text' : 'password'"
                :append-inner-icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"
                @click:append-inner="showPassword = !showPassword"
                required
            />
            <v-checkbox v-model="showPassword" label="Show password" />
            <v-divider class="my-4" :thickness="4"></v-divider>
            <v-row align="center" justify="center">
            <v-col cols="auto">
                <v-btn :disabled="isProgress"  @click="sendForm" prepend-icon="mdi-account-key" color="primary">
                Register
                </v-btn>
            </v-col>
            <v-col cols="auto">
                <v-btn :disabled="isProgress"  @click="goToLogin" prepend-icon="mdi-share" variant="tonal" color=""info>
                Log in
                </v-btn>
            </v-col>
            </v-row>
        </v-card-text>
        </v-card>
    </v-col>
    </v-row>
</v-container>
</template>

<script lang="ts" setup>
import { ENDPOINT } from '@/utils';
import { useRegisterStatus } from '@/stores/registerStatus';
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const registerStatus = useRegisterStatus();

const email = ref('');
const username = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);

const isProgress = ref(false);

const alert = reactive({
    show: false,
    type: '',
    title: '',
    text: ''
});

const rules = {
  required: (v: string) => !!v || 'Field is required',
  password: (v: string) => {
    const hasNumber = /\d/.test(v);
    const hasMinLength = v.length >= 8;
    if (!hasNumber || !hasMinLength) {
      return 'Password must be at least 8 characters and include numbers';
    }
    return true;
  }
};

const sendForm = async () => {
    alert.show = false;

    if (email.value === '' || username.value === '' || password.value === '' || confirmPassword.value === '') {
        alert.type = 'warning';
        alert.title = 'Validation error';
        alert.text = 'All fields must be filled, verify and try again.'
        alert.show = true;
        return;
    }

    if (confirmPassword.value != password.value) {
        alert.type = 'warning';
        alert.title = 'Validation error';
        alert.text = 'The password does not match with the confirm password, verify and try again.'
        alert.show = true;
        return;
    }


    isProgress.value = true;

    const data = {
        email: email.value,
        username: username.value,
        password: password.value,
    };

    const response = await fetch(`${ENDPOINT}/auth/register`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(data),
    });
    if (response.ok) {
        registerStatus.setStatus(email.value);
        goToLogin();
    } else {
        const errorData = await response.json() as {
            detail: {
                msg: string;
            }[]
        };

        alert.type = 'error';
        alert.title = 'Server validation error';
        alert.text = errorData.detail.map(el => el.msg).join('. ') + '.';
        alert.show = true;
    }

    isProgress.value = false;
};

const goToLogin = () => {
    router.push('/login');
};
</script>