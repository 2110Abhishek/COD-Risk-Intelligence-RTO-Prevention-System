import React, { useEffect, useState } from 'react';
import { Sliders, Save, CheckCircle2, AlertTriangle, Shield, DollarSign, History } from 'lucide-react';
import type { FullConfiguration } from '../types';
import { api } from '../services/apiClient';

export const ConfigurationPage: React.FC = () => {
  const [config, setConfig] = useState<FullConfiguration | null>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchConfig = async () => {
    try {
      setLoading(true);
      const [cfg, hist] = await Promise.all([
        api.getConfiguration(),
        api.getConfigHistory(),
      ]);
      setConfig(cfg);
      setHistory(hist || []);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!config) return;

    // Validation
    const th = config.risk_thresholds;
    if (
      th.ship_as_is_max > th.confirmation_max ||
      th.confirmation_max > th.prepaid_max ||
      th.prepaid_max > th.hold_min
    ) {
      setErrorMsg('Thresholds must be strictly ordered: Ship As-Is ≤ Confirmation ≤ Prepaid ≤ Hold.');
      return;
    }

    try {
      setSaving(true);
      setErrorMsg(null);
      setSuccessMsg(null);
      const updated = await api.updateConfiguration(config);
      setConfig(updated);
      setSuccessMsg(`Configuration successfully updated to version ${updated.policy_version}. Active for all future decisions.`);
      const hist = await api.getConfigHistory();
      setHistory(hist || []);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  if (loading || !config) {
    return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-muted)' }}>Loading operational configuration...</div>;
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ fontSize: 18, fontWeight: 700 }}>Operational Policy & Threshold Management</h2>
        <div style={{ fontSize: 13, color: 'var(--color-muted)' }}>
          Edit operational risk thresholds, financial assumptions, and customer protection safeguards without code changes. (Active Version: {config.policy_version})
        </div>
      </div>

      {successMsg && (
        <div style={{ padding: '12px 16px', background: 'var(--color-success-bg)', border: '1px solid var(--color-success)', color: 'var(--color-success)', borderRadius: 8, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <CheckCircle2 size={16} /> {successMsg}
        </div>
      )}

      {errorMsg && (
        <div style={{ padding: '12px 16px', background: 'var(--color-danger-bg)', border: '1px solid var(--color-danger)', color: 'var(--color-danger)', borderRadius: 8, marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
          <AlertTriangle size={16} /> {errorMsg}
        </div>
      )}

      <form onSubmit={handleSave}>
        {/* 1. Risk Thresholds */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title">
            <Sliders size={16} /> Risk Bands & Decision Cutoffs
          </div>
          <div className="grid-4" style={{ marginTop: 14 }}>
            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>SHIP AS-IS MAX (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.risk_thresholds.ship_as_is_max}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    risk_thresholds: {
                      ...config.risk_thresholds,
                      ship_as_is_max: parseFloat(e.target.value) || 0,
                    },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
              <span style={{ fontSize: 11, color: 'var(--color-faint)' }}>Default: 0.20 (20%)</span>
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>CONFIRMATION MAX (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.risk_thresholds.confirmation_max}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    risk_thresholds: {
                      ...config.risk_thresholds,
                      confirmation_max: parseFloat(e.target.value) || 0,
                    },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
              <span style={{ fontSize: 11, color: 'var(--color-faint)' }}>Default: 0.40 (40%)</span>
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>PREPAID NUDGE MAX (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.risk_thresholds.prepaid_max}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    risk_thresholds: {
                      ...config.risk_thresholds,
                      prepaid_max: parseFloat(e.target.value) || 0,
                    },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
              <span style={{ fontSize: 11, color: 'var(--color-faint)' }}>Default: 0.65 (65%)</span>
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>HOLD MINIMUM (%)</label>
              <input
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={config.risk_thresholds.hold_min}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    risk_thresholds: {
                      ...config.risk_thresholds,
                      hold_min: parseFloat(e.target.value) || 0,
                    },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
              <span style={{ fontSize: 11, color: 'var(--color-faint)' }}>Default: 0.65 (65%)</span>
            </div>
          </div>
        </div>

        {/* 2. Customer Safeguards & Protection */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title">
            <Shield size={16} /> Customer Protection & Anti-Bias Safeguards
          </div>
          <div className="grid-2" style={{ marginTop: 14 }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={config.customer_protection.protect_first_time_customers}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    customer_protection: {
                      ...config.customer_protection,
                      protect_first_time_customers: e.target.checked,
                    },
                  })
                }
                style={{ width: 16, height: 16 }}
              />
              <div>
                <div style={{ fontWeight: 600 }}>Protect First-Time Customers</div>
                <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>
                  Forbid automatic cancellation solely due to lack of prior order history.
                </div>
              </div>
            </label>

            <label style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={config.customer_protection.manual_review_before_cancellation}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    customer_protection: {
                      ...config.customer_protection,
                      manual_review_before_cancellation: e.target.checked,
                    },
                  })
                }
                style={{ width: 16, height: 16 }}
              />
              <div>
                <div style={{ fontWeight: 600 }}>Manual Review Before Cancellation</div>
                <div style={{ fontSize: 11.5, color: 'var(--color-muted)' }}>
                  High-risk orders go to HOLD queue; human sign-off required for cancellation.
                </div>
              </div>
            </label>
          </div>
        </div>

        {/* 3. Financial Assumptions */}
        <div className="card" style={{ marginBottom: 20 }}>
          <div className="card-title">
            <DollarSign size={16} /> Financial Assumptions (Unit Economics)
          </div>
          <div className="grid-4" style={{ marginTop: 14 }}>
            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>FORWARD SHIPPING (₹)</label>
              <input
                type="number"
                value={config.financials.forward_shipping}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    financials: { ...config.financials, forward_shipping: parseFloat(e.target.value) || 0 },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>RETURN SHIPPING (₹)</label>
              <input
                type="number"
                value={config.financials.return_shipping}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    financials: { ...config.financials, return_shipping: parseFloat(e.target.value) || 0 },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>PACKAGING (₹)</label>
              <input
                type="number"
                value={config.financials.packaging_handling}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    financials: { ...config.financials, packaging_handling: parseFloat(e.target.value) || 0 },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
            </div>

            <div>
              <label style={{ fontSize: 12, color: 'var(--color-muted)', fontWeight: 600 }}>PREPAID DISCOUNT (₹)</label>
              <input
                type="number"
                value={config.prepaid_offer.discount_amount}
                onChange={(e) =>
                  setConfig({
                    ...config,
                    prepaid_offer: { ...config.prepaid_offer, discount_amount: parseFloat(e.target.value) || 0 },
                  })
                }
                className="input-text"
                style={{ width: '100%', marginTop: 6 }}
              />
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 28 }}>
          <button type="submit" disabled={saving} className="btn btn-primary" style={{ padding: '10px 24px' }}>
            <Save size={16} />
            <span>{saving ? 'Validating & Saving...' : 'Save Configuration Version'}</span>
          </button>
        </div>
      </form>

      {/* 4. Configuration Audit History */}
      <div className="card">
        <div className="card-header">
          <div className="card-title">
            <History size={16} /> Configuration Change Audit Trail
          </div>
          <div style={{ fontSize: 12, color: 'var(--color-muted)' }}>
            Every modification is versioned and logged
          </div>
        </div>

        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Actor</th>
                <th>Action</th>
                <th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan={4} style={{ textAlign: 'center', padding: 20, color: 'var(--color-muted)' }}>
                    Initial default configuration active. No manual updates recorded yet.
                  </td>
                </tr>
              ) : (
                history.map((h) => (
                  <tr key={h.id}>
                    <td style={{ fontSize: 12, color: 'var(--color-muted)' }}>{new Date(h.timestamp).toLocaleString()}</td>
                    <td>{h.actor}</td>
                    <td><span className="badge badge-low">{h.action}</span></td>
                    <td>{h.reason}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
