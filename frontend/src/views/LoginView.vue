<template>
<v-container height="100vh">
    <v-row align-content="center" class="h-100">
    <v-col cols="12" offset-sm="2" sm="8" offset-md="4" md="4">
        <v-card>
        <v-card-item>
            <v-card-title>
                Log In
            </v-card-title>

            <div v-if="registerStatus.status" class="pa-4">
                <v-alert
                    text="The account was registerd successfully."
                    title="Register completed"
                    type="success"
                    variant="tonal"
                    closable
                ></v-alert>
            </div>
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
                v-model="password"
                label="Password"
                :type="showPassword? 'text' : 'password'"
                required
            />
            <v-checkbox v-model="showPassword" label="Show password" />
            <v-divider class="my-4" :thickness="4"></v-divider>
            <v-row align="center" justify="center">
            <v-col cols="auto">
                <v-btn :disabled="isProgress" @click="sendForm" prepend-icon="mdi-door" color="primary">
                Log In
                </v-btn>
            </v-col>
            <v-col cols="auto">
                <v-btn :disabled="isProgress" @click="goToRegister" prepend-icon="mdi-share" variant="tonal" color=""info>
                Register
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
import { ref, reactive, onMounted, onBeforeMount } from 'vue';
import { useRegisterStatus } from '@/stores/registerStatus';
import { useSession } from '@/stores/session';
import { useRouter } from 'vue-router';

const router = useRouter();
const registerStatus = useRegisterStatus();
const session = useSession();

onBeforeMount(() => {
    if (session.accessToken !== '') {
        router.push('/');
    }
})

onMounted(() => {
    if (registerStatus.email !== '') {
        email.value = registerStatus.email;
    }

    setTimeout(() => {
        registerStatus.status = false;
    }, 5000);
});

const email = ref('');
const password = ref('');
const showPassword = ref(false);

const isProgress = ref(false);

const alert = reactive({
    show: false,
    type: '',
    title: '',
    text: ''
});

const sendForm = async () => {
    alert.show = false;

    if (email.value === '' || password.value === '') {
        alert.type = 'warning';
        alert.title = 'Validation error';
        alert.text = 'All fields must be filled, verify and try again.'
        alert.show = true;
        return;
    }

    isProgress.value = true;

    const data = {
        email: email.value,
        password: password.value,
    };

    const response = await fetch(`${ENDPOINT}/auth/login`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json',
        }),
        body: JSON.stringify(data),
    });
    if (response.ok) {
        const data = await response.json() as {access_token: string, refresh_token: string};
        session.setSession(data.access_token, data.refresh_token);
        router.push('/banks');
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

const goToRegister = () => {
    router.push('/register');
};
</script>