import React, { useEffect, useState } from 'react';
import {
  Send,
  Clock,
  CheckCheck,
  CreditCard,
  CheckCircle2,
  XCircle,
  HelpCircle,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import type { OrderListItem } from '../types';
import { api } from '../services/apiClient';
import { StatusBadge } from '../components/Badges';

export const WhatsAppSimulatorPage: React.FC = () => {
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [selectedOrderId, setSelectedOrderId] = useState<string>('');
  const [selectedOrder, setSelectedOrder] = useState<any>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [inputText, setInputText] = useState('');
  const [_loading, setLoading] = useState(false);
  const [actionMessage, setActionMessage] = useState<string | null>(null);

  // Load orders
  const fetchOrders = async () => {
    try {
      const res = await api.getOrders({ page: 1, page_size: 20 });
      setOrders(res.orders || []);
      if (res.orders && res.orders.length > 0 && !selectedOrderId) {
        setSelectedOrderId(res.orders[0].order_id);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Load conversation & detail for selected order
  const fetchConversation = async (orderId: string) => {
    if (!orderId) return;
    try {
      setLoading(true);
      const [conv, detail] = await Promise.all([
        api.getConversation(orderId),
        api.getOrderDetail(orderId),
      ]);
      setMessages(conv || []);
      setSelectedOrder(detail.order || null);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  useEffect(() => {
    if (selectedOrderId) {
      fetchConversation(selectedOrderId);
    }
  }, [selectedOrderId]);

  // Reply handler
  const handleSendReply = async (text: string) => {
    if (!text.trim() || !selectedOrderId) return;
    try {
      setActionMessage(null);
      const res = await api.sendWhatsAppReply(selectedOrderId, text.trim());
      setActionMessage(`Customer replied: "${text}" → State updated to ${res.workflow_status}`);
      setInputText('');
      await fetchConversation(selectedOrderId);
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  // Timeout simulation
  const handleTimeout = async () => {
    if (!selectedOrderId) return;
    try {
      setActionMessage(null);
      const res = await api.sendWhatsAppTimeout(selectedOrderId);
      setActionMessage(`Timeout simulated: Order placed on ${res.workflow_status}`);
      await fetchConversation(selectedOrderId);
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  // Mock Payment Actions
  const handleMockPaymentSuccess = async () => {
    if (!selectedOrderId) return;
    try {
      setActionMessage(null);
      const res = await api.simulatePaymentSuccess(selectedOrderId);
      setActionMessage(res.message);
      await fetchConversation(selectedOrderId);
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleMockPaymentFailure = async () => {
    if (!selectedOrderId) return;
    try {
      setActionMessage(null);
      const res = await api.simulatePaymentFailure(selectedOrderId);
      setActionMessage(res.message);
      await fetchConversation(selectedOrderId);
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  const handleResendTemplate = async (templateType: string) => {
    if (!selectedOrderId) return;
    try {
      await api.sendWhatsAppMessage(selectedOrderId, templateType);
      await fetchConversation(selectedOrderId);
      setActionMessage(`Sent outbound ${templateType} message.`);
    } catch (err: any) {
      setActionMessage(`Error: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ marginBottom: 16 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>WhatsApp Confirmation & Prepaid Simulator</h2>
        <div style={{ fontSize: 13, color: 'var(--color-muted)' }}>
          Simulate two-way customer communication, reply parsing (YES/NO/ambiguous), 24h timeouts, and mock prepaid payments without external APIs.
        </div>
      </div>

      {actionMessage && (
        <div
          style={{
            padding: '10px 16px',
            borderRadius: 8,
            backgroundColor: 'var(--color-surface-raised)',
            border: '1px solid var(--color-primary)',
            color: 'var(--color-text)',
            fontSize: 13,
            marginBottom: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}
        >
          <Sparkles size={16} color="var(--color-primary)" />
          <span>{actionMessage}</span>
        </div>
      )}

      {/* 3-Column Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr 340px', gap: 20 }}>
        {/* Left Column: Order Selector */}
        <div className="card" style={{ height: 'fit-content', padding: 16 }}>
          <div className="card-title" style={{ marginBottom: 12 }}>
            Select Order to Test
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 520, overflowY: 'auto' }}>
            {orders.map((o) => (
              <div
                key={o.order_id}
                onClick={() => setSelectedOrderId(o.order_id)}
                style={{
                  padding: 10,
                  borderRadius: 6,
                  cursor: 'pointer',
                  backgroundColor: o.order_id === selectedOrderId ? 'var(--color-surface-raised)' : 'transparent',
                  border: o.order_id === selectedOrderId ? '1px solid var(--color-primary)' : '1px solid var(--color-border)',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{o.order_id}</span>
                  <span className="amount" style={{ fontSize: 12 }}>₹{o.order_value}</span>
                </div>
                <div style={{ fontSize: 12, fontWeight: 500, marginTop: 2 }}>{o.customer_name}</div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 6 }}>
                  <StatusBadge status={o.workflow_status} />
                  <span style={{ fontSize: 11, color: 'var(--color-muted)' }}>{o.payment_method}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Center Column: WhatsApp Chat Box */}
        <div className="whatsapp-chat-box">
          <div className="whatsapp-header">
            <div
              style={{
                width: 36,
                height: 36,
                borderRadius: '50%',
                backgroundColor: '#00A884',
                color: '#fff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 600,
                fontSize: 14,
              }}
            >
              {selectedOrder ? selectedOrder.customer_name.charAt(0) : 'C'}
            </div>
            <div>
              <div style={{ fontWeight: 600, color: '#E9EDEF', fontSize: 14 }}>
                {selectedOrder ? selectedOrder.customer_name : 'Customer'}
              </div>
              <div style={{ fontSize: 11, color: '#8696A0' }}>
                {selectedOrder ? `${selectedOrder.phone} • Order #${selectedOrder.order_id}` : 'WhatsApp Mock Simulator'}
              </div>
            </div>
          </div>

          {/* Messages Stream */}
          <div className="whatsapp-messages">
            <div
              style={{
                textAlign: 'center',
                backgroundColor: '#182229',
                color: '#FFE28C',
                padding: '6px 12px',
                borderRadius: 6,
                fontSize: 11,
                alignSelf: 'center',
                maxWidth: '85%',
              }}
            >
              🔒 Messages are end-to-end encrypted simulator events. No external API is connected.
            </div>

            {messages.length === 0 ? (
              <div style={{ textAlign: 'center', color: '#8696A0', marginTop: 40, fontSize: 13 }}>
                No messages yet. Send a confirmation or prepaid nudge using the controls on the right.
              </div>
            ) : (
              messages.map((m) => (
                <div
                  key={m.id}
                  className={`msg-bubble ${m.direction === 'OUTBOUND' ? 'msg-outbound' : 'msg-inbound'}`}
                >
                  <div>{m.message}</div>
                  <div className="msg-time" style={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 4 }}>
                    <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    {m.direction === 'OUTBOUND' && <CheckCheck size={14} color="#53BDEB" />}
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Chat Input Bar */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendReply(inputText);
            }}
            style={{
              padding: '10px 14px',
              backgroundColor: '#202C33',
              display: 'flex',
              gap: 8,
              borderTop: '1px solid #2A3942',
            }}
          >
            <input
              type="text"
              placeholder="Type customer reply (e.g. 'YES', 'NO', 'Maybe later')..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              style={{
                flex: 1,
                backgroundColor: '#2A3942',
                border: 'none',
                borderRadius: 8,
                padding: '10px 14px',
                color: '#E9EDEF',
                outline: 'none',
                fontSize: 13.5,
              }}
            />
            <button
              type="submit"
              disabled={!inputText.trim()}
              style={{
                backgroundColor: '#00A884',
                border: 'none',
                borderRadius: 8,
                padding: '0 16px',
                color: '#fff',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Send size={16} />
            </button>
          </form>
        </div>

        {/* Right Column: Interactive Test Controls */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Workflow Status Box */}
          <div className="card">
            <div className="card-title" style={{ fontSize: 13 }}>
              Current Workflow Status
            </div>
            {selectedOrder && (
              <div style={{ marginTop: 8 }}>
                <StatusBadge status={selectedOrder.workflow_status} />
                <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 8 }}>
                  Amount: ₹{selectedOrder.order_value} • Mode: {selectedOrder.payment_method}
                </div>
              </div>
            )}
          </div>

          {/* Customer Confirmation Simulation Controls */}
          <div className="card">
            <div className="card-title" style={{ fontSize: 13, color: '#62B6D9' }}>
              Confirmation Actions
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
              <button
                onClick={() => handleSendReply('YES')}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', color: 'var(--color-success)' }}
              >
                <CheckCircle2 size={16} /> Quick Reply: YES (Approve Ship)
              </button>

              <button
                onClick={() => handleSendReply('NO')}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', color: 'var(--color-danger)' }}
              >
                <XCircle size={16} /> Quick Reply: NO (Decline & Cancel)
              </button>

              <button
                onClick={() => handleSendReply('Maybe later')}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', color: 'var(--color-warning)' }}
              >
                <HelpCircle size={16} /> Ambiguous Reply: "Maybe later"
              </button>

              <button
                onClick={handleTimeout}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start' }}
              >
                <Clock size={16} /> Simulate 24h Timeout (Move to Hold)
              </button>

              <button
                onClick={() => handleResendTemplate('CONFIRMATION')}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', marginTop: 4 }}
              >
                <RefreshCw size={14} /> Re-send Confirmation Prompt
              </button>
            </div>
          </div>

          {/* Prepaid Offer & Payment Simulation */}
          <div className="card">
            <div className="card-title" style={{ fontSize: 13, color: '#A78BFA' }}>
              Prepaid Flow Simulation
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 10 }}>
              <button
                onClick={() => handleResendTemplate('PREPAID_NUDGE')}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start' }}
              >
                <CreditCard size={16} /> Send ₹15 Prepaid Offer Link
              </button>

              <button
                onClick={handleMockPaymentSuccess}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', color: 'var(--color-success)' }}
              >
                <CheckCircle2 size={16} /> Mock Payment SUCCESS (Convert)
              </button>

              <button
                onClick={handleMockPaymentFailure}
                className="btn btn-secondary btn-sm"
                style={{ justifyContent: 'flex-start', color: 'var(--color-danger)' }}
              >
                <XCircle size={16} /> Mock Payment FAILURE (Keep COD)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
