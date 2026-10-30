import React, { useEffect, useState } from 'react';
import {
  TrendingUp,
  AlertOctagon,
  CheckCircle,
  Clock,
  ArrowRightCircle,
  AlertTriangle,
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';
import type { DashboardSummary, OrderListItem } from '../types';
import { api } from '../services/apiClient';
import { DecisionBadge, StatusBadge, RiskBadge } from '../components/Badges';

interface OverviewPageProps {
  onOpenOrder: (orderId: string) => void;
  dateFilter: string;
}

const CustomDecisionTooltip: React.FC<any> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    const color = data.payload.color || '#34C78A';
    return (
      <div
        style={{
          backgroundColor: '#111827',
          border: `1.5px solid ${color}`,
          borderRadius: 8,
          padding: '10px 14px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 600, color: '#FFFFFF', marginBottom: 6 }}>
          {data.payload.name}
        </div>
        <div style={{ fontSize: 14, fontWeight: 700, color: color, display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ color: '#94A3B8', fontWeight: 500, fontSize: 12 }}>Count:</span>
          <span>{Number(data.value).toLocaleString()} orders</span>
        </div>
      </div>
    );
  }
  return null;
};

const CustomFinancialTooltip: React.FC<any> = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    const color = data.payload.fill || '#7C9CFF';
    return (
      <div
        style={{
          backgroundColor: '#111827',
          border: `1.5px solid ${color}`,
          borderRadius: 8,
          padding: '10px 14px',
          boxShadow: '0 8px 24px rgba(0,0,0,0.6)',
        }}
      >
        <div style={{ fontSize: 13, fontWeight: 600, color: '#FFFFFF', marginBottom: 6 }}>
          {data.payload.name}
        </div>
        <div style={{ fontSize: 14, fontWeight: 700, color: color, display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{ color: '#94A3B8', fontWeight: 500, fontSize: 12 }}>Amount:</span>
          <span>₹{Number(data.value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}</span>
        </div>
      </div>
    );
  }
  return null;
};

export const OverviewPage: React.FC<OverviewPageProps> = ({ onOpenOrder, dateFilter }) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentOrders, setRecentOrders] = useState<OrderListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [sumRes, ordersRes] = await Promise.all([
        api.getDashboardSummary(dateFilter),
        api.getOrders({ page: 1, page_size: 6, date_filter: dateFilter }),
      ]);
      setSummary(sumRes);
      setRecentOrders(ordersRes.orders || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [dateFilter]);

  if (loading) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-muted)' }}>
        <div style={{ marginBottom: 12 }}>Loading operations dashboard...</div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-danger)' }}>
        <AlertTriangle size={32} style={{ marginBottom: 12 }} />
        <div>Error: {error || 'No data found'}</div>
        <button onClick={fetchData} className="btn btn-secondary btn-sm" style={{ marginTop: 16 }}>
          Retry
        </button>
      </div>
    );
  }

  const { bucket_counts, financial_impact } = summary;

  // Chart data
  const decisionChartData = [
    { name: 'Ship As-Is', count: bucket_counts.ship_as_is, color: '#34C78A' },
    { name: 'Confirmation', count: bucket_counts.ship_after_confirmation, color: '#62B6D9' },
    { name: 'Prepaid Nudge', count: bucket_counts.nudge_to_prepaid, color: '#A78BFA' },
    { name: 'Hold / Review', count: bucket_counts.hold_cancel, color: '#F4B860' },
  ];

  const financialChartData = [
    { name: 'Avoided RTO Savings', amount: financial_impact.estimated_rto_savings, fill: '#34C78A' },
    { name: 'Genuine Cancel Loss', amount: financial_impact.estimated_genuine_cancellation_loss, fill: '#F07878' },
    { name: 'Redeemed Discounts', amount: financial_impact.redeemed_prepaid_discounts, fill: '#A78BFA' },
    { name: 'Net Estimated Impact', amount: financial_impact.net_estimated_financial_impact, fill: '#7C9CFF' },
  ];

  return (
    <div>
      {/* 1. Decision Bucket Cards */}
      <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>Decision Distribution (Reporting Period: {summary.reporting_date})</h2>
        <span style={{ fontSize: 12, color: 'var(--color-muted)' }}>
          Total COD Evaluated: <strong>{bucket_counts.total_cod_evaluated} orders</strong>
        </span>
      </div>

      <div className="grid-4">
        {/* Card 1: Ship As-Is */}
        <div className="card" style={{ borderTop: '3px solid #34C78A' }}>
          <div className="card-header">
            <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-muted)' }}>1. SHIP AS-IS</span>
            <CheckCircle size={16} color="#34C78A" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700 }} className="num">
            {bucket_counts.ship_as_is}
          </div>
          <div style={{ fontSize: 12, color: '#34C78A', marginTop: 4 }}>
            {Math.round(bucket_counts.ship_as_is_share * 100)}% of COD orders
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-faint)', marginTop: 8 }}>
            Low predicted risk • Immediate dispatch
          </div>
        </div>

        {/* Card 2: Ship After Confirmation */}
        <div className="card" style={{ borderTop: '3px solid #62B6D9' }}>
          <div className="card-header">
            <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-muted)' }}>2. CONFIRMATION</span>
            <Clock size={16} color="#62B6D9" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700 }} className="num">
            {bucket_counts.ship_after_confirmation}
          </div>
          <div style={{ fontSize: 12, color: '#62B6D9', marginTop: 4 }}>
            {Math.round(bucket_counts.confirmation_share * 100)}% of COD orders
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-faint)', marginTop: 8 }}>
            Moderate risk • WhatsApp reply needed
          </div>
        </div>

        {/* Card 3: Nudge to Prepaid */}
        <div className="card" style={{ borderTop: '3px solid #A78BFA' }}>
          <div className="card-header">
            <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-muted)' }}>3. NUDGE PREPAID</span>
            <ArrowRightCircle size={16} color="#A78BFA" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700 }} className="num">
            {bucket_counts.nudge_to_prepaid}
          </div>
          <div style={{ fontSize: 12, color: '#A78BFA', marginTop: 4 }}>
            {Math.round(bucket_counts.prepaid_share * 100)}% of COD orders
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-faint)', marginTop: 8 }}>
            Elevated risk • ₹15 discount incentive
          </div>
        </div>

        {/* Card 4: Hold / Review */}
        <div className="card" style={{ borderTop: '3px solid #F4B860' }}>
          <div className="card-header">
            <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--color-muted)' }}>4. HOLD / REVIEW</span>
            <AlertOctagon size={16} color="#F4B860" />
          </div>
          <div style={{ fontSize: 28, fontWeight: 700 }} className="num">
            {bucket_counts.hold_cancel}
          </div>
          <div style={{ fontSize: 12, color: '#F4B860', marginTop: 4 }}>
            {Math.round(bucket_counts.hold_share * 100)}% of COD orders
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-faint)', marginTop: 8 }}>
            High risk • Human ops review required
          </div>
        </div>
      </div>

      {/* 2. Financial KPI Cards */}
      <div style={{ marginBottom: 12 }}>
        <h2 style={{ fontSize: 16, fontWeight: 600 }}>Financial Impact (Estimated Unit Economics)</h2>
        <div style={{ fontSize: 12, color: 'var(--color-muted)', marginTop: 2 }}>
          {financial_impact.reporting_note}
        </div>
      </div>

      <div className="grid-4">
        {/* Estimated RTO Savings */}
        <div className="card">
          <div className="card-header">
            <span style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>ESTIMATED RTO SAVINGS</span>
            <span className="badge badge-low" style={{ fontSize: 10 }}>Estimate</span>
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#34C78A' }} className="amount">
            ₹{financial_impact.estimated_rto_savings.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-muted)', marginTop: 6 }}>
            Avoided forward + reverse shipping & packaging
          </div>
        </div>

        {/* Genuine Cancellation Opportunity Loss */}
        <div className="card">
          <div className="card-header">
            <span style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>GENUINE CANCEL LOSS</span>
            <span className="badge badge-danger" style={{ fontSize: 10 }}>Opportunity Cost</span>
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#F07878' }} className="amount">
            ₹{financial_impact.estimated_genuine_cancellation_loss.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-muted)', marginTop: 6 }}>
            Lost 62% gross contribution on genuine orders
          </div>
        </div>

        {/* Prepaid Discounts Redeemed */}
        <div className="card">
          <div className="card-header">
            <span style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>REDEEMED DISCOUNTS</span>
            <span className="badge badge-elevated" style={{ fontSize: 10 }}>Realised Cash</span>
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#A78BFA' }} className="amount">
            ₹{financial_impact.redeemed_prepaid_discounts.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-muted)', marginTop: 6 }}>
            ₹15 discount granted for successful conversions
          </div>
        </div>

        {/* Net Financial Impact */}
        <div className="card" style={{ background: 'linear-gradient(180deg, #182338 0%, #121A2B 100%)', borderColor: '#7C9CFF' }}>
          <div className="card-header">
            <span style={{ fontSize: 12, color: '#7C9CFF', fontWeight: 700 }}>NET ESTIMATED IMPACT</span>
            <TrendingUp size={16} color="#7C9CFF" />
          </div>
          <div style={{ fontSize: 24, fontWeight: 700, color: '#7C9CFF' }} className="amount">
            ₹{financial_impact.net_estimated_financial_impact.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div style={{ fontSize: 11.5, color: 'var(--color-text)', marginTop: 6 }}>
            Savings − Lost contribution − Discounts
          </div>
        </div>
      </div>

      {/* 3. Visual Charts Grid */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            Decision Volume Distribution
          </div>
          <div style={{ height: 240, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={decisionChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="var(--color-muted)" fontSize={12} />
                <YAxis stroke="var(--color-muted)" fontSize={12} />
                <Tooltip content={<CustomDecisionTooltip />} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {decisionChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card">
          <div className="card-title" style={{ marginBottom: 16 }}>
            Financial Breakdown (INR)
          </div>
          <div style={{ height: 240, width: '100%' }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={financialChartData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                <XAxis dataKey="name" stroke="var(--color-muted)" fontSize={11} />
                <YAxis stroke="var(--color-muted)" fontSize={12} />
                <Tooltip content={<CustomFinancialTooltip />} />
                <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
                  {financialChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. Recent Decisions & Action Queue */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            Recent Order Evaluations
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
            Showing latest {recentOrders.length} processed orders
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Customer</th>
                <th>Amount</th>
                <th>Predicted Risk</th>
                <th>Decision Action</th>
                <th>Workflow Status</th>
                <th>Date & Time</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {recentOrders.map((o) => (
                <tr key={o.order_id}>
                  <td>
                    <span style={{ fontWeight: 600, color: 'var(--color-primary)', cursor: 'pointer' }} onClick={() => onOpenOrder(o.order_id)}>
                      {o.order_id}
                    </span>
                  </td>
                  <td>
                    <div>{o.customer_name}</div>
                    <div style={{ fontSize: 11, color: 'var(--color-muted)' }}>{o.phone_masked} • {o.city || 'India'}</div>
                  </td>
                  <td className="amount">₹{o.order_value.toLocaleString('en-IN')}</td>
                  <td>
                    <RiskBadge band={o.risk_band} probability={o.rto_probability} />
                  </td>
                  <td>
                    <DecisionBadge action={o.decision} />
                  </td>
                  <td>
                    <StatusBadge status={o.workflow_status} />
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--color-muted)' }}>
                    {o.order_datetime ? new Date(o.order_datetime).toLocaleString() : 'N/A'}
                  </td>
                  <td>
                    <button
                      onClick={() => onOpenOrder(o.order_id)}
                      className="btn btn-secondary btn-sm"
                    >
                      Review
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
