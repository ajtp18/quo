interface Credentials {
    username: string
    password: string
    username_type?: string
    username2?: string
    password2?: string
}

interface InstitutionConfig {
    [key: string]: Credentials
}

export const INSTITUTION_CREDENTIALS: InstitutionConfig = {
    // Bancos normales
    default_bank: {
        username: "12345678901",
        password: "123456"
    },
    
    // Iron Bank (requiere campos adicionales)
    ironbank_br_retail: {
        username: "12345678901",
        password: "123456",
        username_type: "003",  // Passport (valid)
        username2: "12345678901",
        password2: "123456"
    },
    
    ironbank_br_business: {
        username: "12345678901",
        password: "123456",
        username_type: "003",  // Passport (valid)
        username2: "12345678901",
        password2: "123456"
    },
    
    // Empleo
    planet_mx_employment: {
        username: "LOLJ970312MBSPPN08",
        password: "fake-password"
    },
    
    // Fiscal
    tatooine_mx_fiscal: {
        username: "12345678901",
        password: "123456"
    }
}

interface UnavailableInstitution {
    name: string
    message: string
}

// Lista de instituciones no disponibles con mensajes personalizados
export const UNAVAILABLE_INSTITUTIONS: UnavailableInstitution[] = [
    {
        name: 'ofmockbank_br_retail',
        message: 'This institution is temporarily unavailable'
    },
    {
        name: 'ironbank_br_business',
        message: 'Business accounts are currently under maintenance'
    },
    {
        name: 'planet_mx_employment',
        message: 'Employment verification service is not available at the moment'
    },
    {
        name: 'tatooine_mx_fiscal',
        message: 'Fiscal services are temporarily disabled'
    }
] 