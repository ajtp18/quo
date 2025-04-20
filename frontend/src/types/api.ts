export interface Transaction {
  id: string
  description: string
  amount: number
  currency: string
  type: 'INFLOW' | 'OUTFLOW'
  category?: string
}

export interface KPI {
  total_income: number
  total_expenses: number
  net_balance: number
}

export interface AccountInfo {
  id: string
  name: string
  balance: {
    current: number
    available: number
  }
}

export interface TransactionResponse {
  transactions: Transaction[]
  kpi: KPI
  account_info: AccountInfo
}

export interface Institution {
  id: number
  name: string
  type: string
  icon_logo: string
} 