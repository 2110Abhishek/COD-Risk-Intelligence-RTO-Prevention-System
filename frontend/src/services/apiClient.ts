import type {
  DashboardSummary,
  OrderListItem,
  OrderDetailResponse,
  FullConfiguration,
} from '../types';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    let errorDetail = 'API Request Failed';
    try {
      const errObj = await res.json();
      errorDetail = errObj.detail || errObj.message || errorDetail;
    } catch {
      // keep fallback
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Dashboard
  getDashboardSummary: (dateFilter = 'yesterday') =>
    fetchJson<DashboardSummary>(`/dashboard/summary?date_filter=${dateFilter}`),

  getTrends: () => fetchJson<any[]>('/dashboard/trends'),

  // Orders
  getOrders: (params: {
    search?: string;
    action?: string;
    risk_band?: string;
    workflow_status?: string;
    date_filter?: string;
    state?: string;
    courier?: string;
    page?: number;
    page_size?: number;
  }) => {
    const q = new URLSearchParams();
    if (params.search) q.append('search', params.search);
    if (params.action) q.append('action', params.action);
    if (params.risk_band) q.append('risk_band', params.risk_band);
    if (params.workflow_status) q.append('workflow_status', params.workflow_status);
    if (params.date_filter) q.append('date_filter', params.date_filter);
    if (params.state) q.append('state', params.state);
    if (params.courier) q.append('courier', params.courier);
    q.append('page', (params.page || 1).toString());
    q.append('page_size', (params.page_size || 20).toString());
    return fetchJson<{
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
      orders: OrderListItem[];
    }>(`/orders?${q.toString()}`);
  },

  getOrderDetail: (orderId: string) =>
    fetchJson<OrderDetailResponse>(`/orders/${orderId}`),

  overrideOrder: (orderId: string, action: string, reason: string) =>
    fetchJson<any>(`/orders/${orderId}/override`, {
      method: 'POST',
      body: JSON.stringify({ action, reason }),
    }),

  evaluateOrder: (order: any) =>
    fetchJson<any>('/decisions/evaluate', {
      method: 'POST',
      body: JSON.stringify(order),
    }),

  // WhatsApp Simulator
  getConversation: (orderId: string) =>
    fetchJson<any[]>(`/whatsapp/conversations/${orderId}`),

  sendWhatsAppReply: (orderId: string, replyText: string) =>
    fetchJson<any>('/whatsapp/reply', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId, reply_text: replyText }),
    }),

  sendWhatsAppTimeout: (orderId: string) =>
    fetchJson<any>('/whatsapp/timeout', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId }),
    }),

  sendWhatsAppMessage: (orderId: string, templateType = 'CONFIRMATION') =>
    fetchJson<any>('/whatsapp/send', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId, template_type: templateType }),
    }),

  // Payment Mock Simulation
  createMockPayment: (orderId: string) =>
    fetchJson<any>('/payments/create-mock', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId }),
    }),

  simulatePaymentSuccess: (orderId: string) =>
    fetchJson<any>('/payments/mock-success', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId }),
    }),

  simulatePaymentFailure: (orderId: string) =>
    fetchJson<any>('/payments/mock-failure', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId }),
    }),

  // Configuration
  getConfiguration: () => fetchJson<FullConfiguration>('/config'),

  updateConfiguration: (cfg: FullConfiguration) =>
    fetchJson<FullConfiguration>('/config', {
      method: 'PUT',
      body: JSON.stringify(cfg),
    }),

  getConfigHistory: () => fetchJson<any[]>('/config/history'),

  // Analytics & Logs
  getModelPerformance: () => fetchJson<any>('/analytics/model-performance'),
  getRegionAnalytics: () => fetchJson<any[]>('/analytics/rto-by-region'),
  getCourierAnalytics: () => fetchJson<any[]>('/analytics/courier-performance'),
  getDecisionLogs: (limit = 50) => fetchJson<any[]>(`/decisions?limit=${limit}`),
};
