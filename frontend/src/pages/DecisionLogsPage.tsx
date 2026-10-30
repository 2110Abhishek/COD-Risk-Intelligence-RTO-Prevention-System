import React, { useEffect, useState } from 'react';
import { api } from '../services/apiClient';
import { DecisionBadge } from '../components/Badges';

interface DecisionLogsPageProps {
  onOpenOrder: (orderId: string) => void;
}

export const DecisionLogsPage: React.FC<DecisionLogsPageProps> = ({ onOpenOrder }) => {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const data = await api.getDecisionLogs(100);
        setLogs(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  if (loading) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-muted)' }}>Loading decision audit logs...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Decision History & System Audit Logs</h2>
        <div style={{ fontSize: 13, color: 'var(--color-muted)' }}>
          Immutable record of every AI score, policy action, and manual override.
        </div>
      </div>

      <div className="table-container">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Order ID</th>
              <th>Decision Action</th>
              <th>Operational Status</th>
              <th>Policy Version</th>
              <th>Override Flag</th>
              <th>Reason Summary</th>
              <th>Inspect</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={8} style={{ textAlign: 'center', padding: 40, color: 'var(--color-muted)' }}>
                  No historical decisions logged yet.
                </td>
              </tr>
            ) : (
              logs.map((d) => (
                <tr key={d.id}>
                  <td style={{ fontSize: 12, color: 'var(--color-muted)' }}>
                    {d.created_at ? new Date(d.created_at).toLocaleString() : 'N/A'}
                  </td>
                  <td>
                    <span
                      style={{ fontWeight: 600, color: 'var(--color-primary)', cursor: 'pointer' }}
                      onClick={() => onOpenOrder(d.order_id)}
                    >
                      {d.order_id}
                    </span>
                  </td>
                  <td>
                    <DecisionBadge action={d.action} />
                  </td>
                  <td>
                    <span className="badge badge-low">{d.operational_status}</span>
                  </td>
                  <td style={{ fontSize: 12 }}>v{d.rule_version}</td>
                  <td>
                    {d.is_override ? (
                      <span className="badge badge-high">Manual Override</span>
                    ) : (
                      <span className="badge badge-low">Automated</span>
                    )}
                  </td>
                  <td style={{ fontSize: 12, color: 'var(--color-muted)', maxWidth: 260, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {d.explanation}
                  </td>
                  <td>
                    <button
                      onClick={() => onOpenOrder(d.order_id)}
                      className="btn btn-secondary btn-sm"
                    >
                      View
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
