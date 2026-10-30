import React, { useEffect, useState } from 'react';
import { Search, Filter, Eye, AlertCircle } from 'lucide-react';
import type { OrderListItem } from '../types';
import { api } from '../services/apiClient';
import { DecisionBadge, StatusBadge, RiskBadge } from '../components/Badges';

interface OrdersPageProps {
  onOpenOrder: (orderId: string) => void;
}

export const OrdersPage: React.FC<OrdersPageProps> = ({ onOpenOrder }) => {
  const [orders, setOrders] = useState<OrderListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('');
  const [riskFilter, setRiskFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  const fetchOrders = async () => {
    try {
      setLoading(true);
      const res = await api.getOrders({
        search: search.trim() || undefined,
        action: actionFilter || undefined,
        risk_band: riskFilter || undefined,
        workflow_status: statusFilter || undefined,
        page,
        page_size: 15,
      });
      setOrders(res.orders || []);
      setTotal(res.total);
      setTotalPages(res.total_pages);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, [page, actionFilter, riskFilter, statusFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchOrders();
  };

  return (
    <div>
      {/* Header and Controls */}
      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center', justifyContent: 'space-between' }}>
          <form onSubmit={handleSearchSubmit} style={{ display: 'flex', gap: 8, flex: '1 1 300px' }}>
            <div style={{ position: 'relative', width: '100%' }}>
              <Search size={16} color="var(--color-muted)" style={{ position: 'absolute', left: 10, top: 11 }} />
              <input
                type="text"
                placeholder="Search by Order ID, Customer Name, Phone, or City..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="input-text"
                style={{ width: '100%', paddingLeft: 34 }}
              />
            </div>
            <button type="submit" className="btn btn-primary btn-sm">
              Search
            </button>
          </form>

          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Filter size={14} color="var(--color-muted)" />
              <select
                value={actionFilter}
                onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
                className="select-input"
                style={{ fontSize: 13, padding: '6px 10px' }}
              >
                <option value="">All Decisions</option>
                <option value="SHIP_AS_IS">Ship As-Is</option>
                <option value="SHIP_AFTER_CONFIRMATION">Confirmation Required</option>
                <option value="NUDGE_TO_PREPAID">Nudge to Prepaid</option>
                <option value="HOLD_CANCEL">Hold / Review</option>
              </select>
            </div>

            <select
              value={riskFilter}
              onChange={(e) => { setRiskFilter(e.target.value); setPage(1); }}
              className="select-input"
              style={{ fontSize: 13, padding: '6px 10px' }}
            >
              <option value="">All Risk Bands</option>
              <option value="LOW">Low Risk</option>
              <option value="MODERATE">Moderate</option>
              <option value="ELEVATED">Elevated</option>
              <option value="HIGH">High Risk</option>
            </select>

            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="select-input"
              style={{ fontSize: 13, padding: '6px 10px' }}
            >
              <option value="">All Statuses</option>
              <option value="SHIP_APPROVED">Ship Approved</option>
              <option value="AWAITING_CONFIRMATION">Awaiting Confirmation</option>
              <option value="PREPAID_OFFERED">Prepaid Offered</option>
              <option value="HOLD">On Hold</option>
              <option value="MANUAL_REVIEW">Manual Review</option>
              <option value="CANCELLED">Cancelled</option>
            </select>
          </div>
        </div>
      </div>

      {/* Orders Table */}
      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Customer</th>
              <th>Address & City</th>
              <th>Order Value</th>
              <th>Predicted Risk</th>
              <th>Recommended Action</th>
              <th>Workflow Status</th>
              <th>Decision Reason</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: 40, color: 'var(--color-muted)' }}>
                  Loading orders queue...
                </td>
              </tr>
            ) : orders.length === 0 ? (
              <tr>
                <td colSpan={9} style={{ textAlign: 'center', padding: 40, color: 'var(--color-muted)' }}>
                  <AlertCircle size={24} style={{ marginBottom: 8 }} />
                  <div>No orders match the selected search or filter criteria.</div>
                </td>
              </tr>
            ) : (
              orders.map((o) => (
                <tr key={o.order_id}>
                  <td>
                    <span
                      style={{ fontWeight: 600, color: 'var(--color-primary)', cursor: 'pointer' }}
                      onClick={() => onOpenOrder(o.order_id)}
                    >
                      {o.order_id}
                    </span>
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>{o.customer_name}</div>
                    <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>{o.phone_masked}</div>
                  </td>
                  <td>
                    <div style={{ maxWidth: 220, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={o.address}>
                      {o.address}
                    </div>
                    <div style={{ fontSize: 11, color: 'var(--color-muted)' }}>
                      {o.city || 'Unknown'}, {o.state || ''}
                    </div>
                  </td>
                  <td className="amount" style={{ fontWeight: 600 }}>
                    ₹{o.order_value.toLocaleString('en-IN')}
                  </td>
                  <td>
                    <RiskBadge band={o.risk_band} probability={o.rto_probability} />
                  </td>
                  <td>
                    <DecisionBadge action={o.decision} />
                  </td>
                  <td>
                    <StatusBadge status={o.workflow_status} />
                  </td>
                  <td>
                    <div
                      style={{ maxWidth: 200, fontSize: 12, color: 'var(--color-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}
                      title={o.explanation || ''}
                    >
                      {o.explanation || 'Normal order'}
                    </div>
                  </td>
                  <td>
                    <button
                      onClick={() => onOpenOrder(o.order_id)}
                      className="btn btn-secondary btn-sm"
                    >
                      <Eye size={12} /> View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 16 }}>
        <div style={{ fontSize: 12.5, color: 'var(--color-muted)' }}>
          Showing <strong>{orders.length}</strong> of <strong>{total}</strong> orders
        </div>

        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page <= 1}
            className="btn btn-secondary btn-sm"
          >
            Previous
          </button>
          <span style={{ fontSize: 12.5, color: 'var(--color-muted)' }}>
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page >= totalPages}
            className="btn btn-secondary btn-sm"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
};
