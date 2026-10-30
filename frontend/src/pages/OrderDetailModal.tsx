import React, { useEffect, useState } from 'react';
import {
  X,
  AlertTriangle,
  User,
  MapPin,
  TrendingDown,
  Activity,
  ShieldAlert,
} from 'lucide-react';
import type { OrderDetailResponse } from '../types';
import { api } from '../services/apiClient';
import { DecisionBadge, StatusBadge, RiskBadge } from '../components/Badges';

interface OrderDetailModalProps {
  orderId: string;
  onClose: () => void;
  onRefresh: () => void;
}

export const OrderDetailModal: React.FC<OrderDetailModalProps> = ({
  orderId,
  onClose,
  onRefresh,
}) => {
  const [data, setData] = useState<OrderDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Manual Override State
  const [overrideAction, setOverrideAction] = useState('SHIP_APPROVED');
  const [overrideReason, setOverrideReason] = useState('');
  const [overrideSubmitting, setOverrideSubmitting] = useState(false);
  const [overrideError, setOverrideError] = useState<string | null>(null);

  const fetchDetail = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getOrderDetail(orderId);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
  }, [orderId]);

  const handleOverrideSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!overrideReason.trim() || overrideReason.length < 5) {
      setOverrideError('A specific operational reason (at least 5 characters) is required for audit logs.');
      return;
    }

    try {
      setOverrideSubmitting(true);
      setOverrideError(null);
      await api.overrideOrder(orderId, overrideAction, overrideReason.trim());
      await fetchDetail();
      onRefresh();
      setOverrideReason('');
    } catch (err: any) {
      setOverrideError(err.message || 'Failed to apply override');
    } finally {
      setOverrideSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div style={modalBackdropStyle}>
        <div style={modalContentStyle}>
          <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-muted)' }}>
            Loading order details for #{orderId}...
          </div>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div style={modalBackdropStyle}>
        <div style={modalContentStyle}>
          <div style={{ padding: 32, textAlign: 'center', color: 'var(--color-danger)' }}>
            <AlertTriangle size={32} style={{ marginBottom: 12 }} />
            <div>Error: {error || 'Order not found'}</div>
            <button onClick={onClose} className="btn btn-secondary btn-sm" style={{ marginTop: 16 }}>
              Close
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { order, latest_decision, latest_prediction, timeline } = data;

  return (
    <div style={modalBackdropStyle} onClick={onClose}>
      <div style={modalContentStyle} onClick={(e) => e.stopPropagation()}>
        {/* Modal Header */}
        <div style={modalHeaderStyle}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <h2 style={{ fontSize: 18, fontWeight: 700 }}>Order #{order.order_id}</h2>
              {latest_decision && <DecisionBadge action={latest_decision.action} />}
              <StatusBadge status={order.workflow_status} />
            </div>
            <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 4 }}>
              Created: {new Date(order.order_datetime).toLocaleString()} • Method: {order.payment_method}
            </div>
          </div>
          <button onClick={onClose} className="btn btn-secondary btn-sm" style={{ padding: 6 }}>
            <X size={18} />
          </button>
        </div>

        {/* Modal Body */}
        <div style={{ padding: '24px', overflowY: 'auto', maxHeight: 'calc(90vh - 120px)' }}>
          {/* 1. Risk & Decision Explanation Card */}
          <div className="card" style={{ marginBottom: 20, borderLeft: '4px solid var(--color-primary)' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 20 }}>
              <div>
                <div style={{ fontSize: 13, color: 'var(--color-muted)', fontWeight: 600 }}>DECISION EXPLANATION</div>
                <div style={{ fontSize: 15, fontWeight: 500, color: 'var(--color-text)', marginTop: 6 }}>
                  {latest_decision?.explanation || 'Order evaluated by deterministic risk engine.'}
                </div>
                {/* Reason codes list */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 12 }}>
                  {latest_decision?.reason_codes.map((rc) => (
                    <span
                      key={rc}
                      style={{
                        background: 'var(--color-surface-raised)',
                        color: 'var(--color-primary)',
                        padding: '3px 8px',
                        borderRadius: 4,
                        fontSize: 11.5,
                        fontWeight: 600,
                        border: '1px solid var(--color-border)',
                      }}
                    >
                      {rc}
                    </span>
                  ))}
                </div>
              </div>

              {latest_prediction && (
                <div style={{ textAlign: 'right', minWidth: 120 }}>
                  <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>PREDICTED RTO RISK</div>
                  <div style={{ fontSize: 26, fontWeight: 700, color: 'var(--color-primary)' }} className="percentage">
                    {Math.round(latest_prediction.rto_probability * 100)}%
                  </div>
                  <RiskBadge band={latest_prediction.risk_band} />
                </div>
              )}
            </div>

            <div style={{ fontSize: 11, color: 'var(--color-faint)', marginTop: 14, borderTop: '1px solid var(--color-border)', paddingTop: 10 }}>
              Model: {latest_prediction?.model_version || 'rto-pipeline-v1.0'} • Policy Version: {latest_decision?.rule_version || '1.0'}
            </div>
          </div>

          {/* 2. Customer & Address Details Grid */}
          <div className="grid-2" style={{ marginBottom: 20 }}>
            {/* Customer History */}
            <div className="card">
              <div className="card-title">
                <User size={16} /> Customer History
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 12, fontSize: 13.5 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-muted)' }}>Customer Name:</span>
                  <span style={{ fontWeight: 600 }}>{order.customer_name}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-muted)' }}>Masked Phone:</span>
                  <span style={{ fontWeight: 600 }}>{order.phone}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-muted)' }}>Prior Completed Orders:</span>
                  <span style={{ fontWeight: 600 }}>{order.customer_prior_orders}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-muted)' }}>Prior RTO Deliveries:</span>
                  <span style={{ fontWeight: 600, color: order.customer_prior_rto > 0 ? 'var(--color-danger)' : 'var(--color-success)' }}>
                    {order.customer_prior_rto}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--color-muted)' }}>Customer Cohort:</span>
                  <span style={{ fontWeight: 600, color: order.customer_prior_orders === 0 ? 'var(--color-info)' : 'var(--color-text)' }}>
                    {order.customer_prior_orders === 0 ? 'First-Time Buyer (Protected)' : 'Repeat Customer'}
                  </span>
                </div>
              </div>
            </div>

            {/* Address Quality */}
            <div className="card">
              <div className="card-title">
                <MapPin size={16} /> Delivery Address
              </div>
              <div style={{ marginTop: 12, fontSize: 13.5 }}>
                <div style={{ background: 'var(--color-surface-raised)', padding: 12, borderRadius: 6, marginBottom: 10, lineHeight: 1.4 }}>
                  {order.address}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-muted)' }}>City & State:</span>
                    <span style={{ fontWeight: 500 }}>{order.city || 'N/A'}, {order.state || 'N/A'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Pincode:</span>
                    <span style={{ fontWeight: 600 }}>{order.pincode || 'Missing Pincode'}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: 'var(--color-muted)' }}>Assigned Courier:</span>
                    <span style={{ fontWeight: 500 }}>{order.courier || 'Auto-routed'}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 3. Financial Unit Economics */}
          {latest_decision?.financial_estimate && (
            <div className="card" style={{ marginBottom: 20 }}>
              <div className="card-title">
                <TrendingDown size={16} /> Intervention Unit Economics
              </div>
              <div className="grid-3" style={{ marginTop: 12, marginBottom: 12 }}>
                <div style={{ background: 'var(--color-surface-raised)', padding: 12, borderRadius: 6 }}>
                  <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>UNMITIGATED RTO RISK</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-warning)', marginTop: 4 }}>
                    ₹{latest_decision.financial_estimate.expected_rto_cost_without_intervention.toFixed(2)}
                  </div>
                </div>
                <div style={{ background: 'var(--color-surface-raised)', padding: 12, borderRadius: 6 }}>
                  <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>EXPECTED AVOIDED LOSS</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-success)', marginTop: 4 }}>
                    ₹{latest_decision.financial_estimate.expected_avoided_rto_cost.toFixed(2)}
                  </div>
                </div>
                <div style={{ background: 'var(--color-surface-raised)', padding: 12, borderRadius: 6 }}>
                  <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>NET BENEFIT</div>
                  <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--color-primary)', marginTop: 4 }}>
                    ₹{latest_decision.financial_estimate.net_expected_benefit.toFixed(2)}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>
                Basis: Forward shipping ₹65 + Return shipping ₹65 + Packaging ₹25 + Expected damage ₹14.40 = ₹169.40 baseline cost per RTO.
              </div>
            </div>
          )}

          {/* 4. Manual Review & Override Action */}
          <div className="card" style={{ marginBottom: 20, border: '1px solid #7C9CFF' }}>
            <div className="card-title" style={{ color: '#7C9CFF' }}>
              <ShieldAlert size={16} /> Operations Manual Override
            </div>
            <form onSubmit={handleOverrideSubmit} style={{ marginTop: 14 }}>
              <div style={{ display: 'flex', gap: 12, marginBottom: 12 }}>
                <select
                  value={overrideAction}
                  onChange={(e) => setOverrideAction(e.target.value)}
                  className="select-input"
                  style={{ flex: 1 }}
                >
                  <option value="SHIP_APPROVED">Approve Shipment (Override to Dispatch)</option>
                  <option value="HOLD">Place On Hold (Escalate for Investigation)</option>
                  <option value="CANCELLED">Cancel Order (Confirm Cancellation)</option>
                </select>
              </div>

              <div style={{ marginBottom: 12 }}>
                <input
                  type="text"
                  placeholder="Enter mandatory reason for audit log (e.g., 'Customer called and verified address landmark')..."
                  value={overrideReason}
                  onChange={(e) => setOverrideReason(e.target.value)}
                  className="input-text"
                  style={{ width: '100%' }}
                />
              </div>

              {overrideError && (
                <div style={{ color: 'var(--color-danger)', fontSize: 12, marginBottom: 10 }}>
                  {overrideError}
                </div>
              )}

              <button
                type="submit"
                disabled={overrideSubmitting}
                className="btn btn-primary btn-sm"
              >
                {overrideSubmitting ? 'Recording Audit Override...' : 'Apply Manual Override'}
              </button>
            </form>
          </div>

          {/* 5. Immutable Event Timeline */}
          <div className="card">
            <div className="card-title">
              <Activity size={16} /> Event Audit Trail ({timeline.length} events)
            </div>
            <div style={{ marginTop: 14, display: 'flex', flexDirection: 'column', gap: 10 }}>
              {timeline.map((ev) => (
                <div
                  key={ev.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '8px 12px',
                    background: 'var(--color-surface-raised)',
                    borderRadius: 6,
                    fontSize: 12.5,
                  }}
                >
                  <div>
                    <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{ev.event_type}</span>
                    <span style={{ color: 'var(--color-muted)', marginLeft: 8 }}>
                      {ev.previous_status ? `${ev.previous_status} → ${ev.new_status}` : ev.new_status}
                    </span>
                  </div>
                  <div style={{ color: 'var(--color-faint)', fontSize: 11 }}>
                    {new Date(ev.created_at).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const modalBackdropStyle: React.CSSProperties = {
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: 'rgba(0, 0, 0, 0.7)',
  backdropFilter: 'blur(4px)',
  zIndex: 200,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  padding: 20,
};

const modalContentStyle: React.CSSProperties = {
  backgroundColor: 'var(--color-surface)',
  border: '1px solid var(--color-border)',
  borderRadius: 'var(--radius-lg)',
  maxWidth: 840,
  width: '100%',
  maxHeight: '90vh',
  boxShadow: 'var(--shadow-md)',
  display: 'flex',
  flexDirection: 'column',
};

const modalHeaderStyle: React.CSSProperties = {
  padding: '20px 24px',
  borderBottom: '1px solid var(--color-border)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
};
