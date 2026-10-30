import React from 'react';
import type { DecisionAction, RiskBand, WorkflowStatus } from '../types';
import { CheckCircle2, AlertTriangle, ArrowRightCircle, Clock } from 'lucide-react';

export const DecisionBadge: React.FC<{ action: DecisionAction }> = ({ action }) => {
  switch (action) {
    case 'SHIP_AS_IS':
      return (
        <span className="badge badge-low">
          <CheckCircle2 size={12} /> Ship As-Is
        </span>
      );
    case 'SHIP_AFTER_CONFIRMATION':
      return (
        <span className="badge badge-moderate">
          <Clock size={12} /> Confirm on WhatsApp
        </span>
      );
    case 'NUDGE_TO_PREPAID':
      return (
        <span className="badge badge-elevated">
          <ArrowRightCircle size={12} /> Nudge to Prepaid
        </span>
      );
    case 'HOLD_CANCEL':
      return (
        <span className="badge badge-high">
          <AlertTriangle size={12} /> Hold for Review
        </span>
      );
    default:
      return <span className="badge badge-moderate">Pending</span>;
  }
};

export const RiskBadge: React.FC<{ band: RiskBand; probability?: number }> = ({
  band,
  probability,
}) => {
  const probText = probability !== undefined ? `${Math.round(probability * 100)}%` : '';
  switch (band) {
    case 'LOW':
      return (
        <span className="badge badge-low">
          {probText} Low Risk
        </span>
      );
    case 'MODERATE':
      return (
        <span className="badge badge-moderate">
          {probText} Moderate
        </span>
      );
    case 'ELEVATED':
      return (
        <span className="badge badge-elevated">
          {probText} Elevated
        </span>
      );
    case 'HIGH':
      return (
        <span className="badge badge-high">
          {probText} High Risk
        </span>
      );
    default:
      return <span className="badge badge-moderate">Unknown</span>;
  }
};

export const StatusBadge: React.FC<{ status: WorkflowStatus }> = ({ status }) => {
  switch (status) {
    case 'SHIP_APPROVED':
      return <span className="badge badge-low">Approved to Ship</span>;
    case 'CONFIRMED':
      return <span className="badge badge-low">Customer Confirmed</span>;
    case 'AWAITING_CONFIRMATION':
      return <span className="badge badge-moderate">Awaiting Reply</span>;
    case 'PREPAID_OFFERED':
      return <span className="badge badge-elevated">Prepaid Offered</span>;
    case 'PAYMENT_PENDING':
      return <span className="badge badge-elevated">Payment Pending</span>;
    case 'PAYMENT_SUCCESSFUL':
      return <span className="badge badge-low">Prepaid Paid</span>;
    case 'HOLD':
      return <span className="badge badge-high">On Hold</span>;
    case 'MANUAL_REVIEW':
      return <span className="badge badge-high">Manual Review</span>;
    case 'CONFIRMATION_TIMEOUT':
      return <span className="badge badge-high">Timeout Hold</span>;
    case 'CUSTOMER_DECLINED':
    case 'CANCELLED':
      return <span className="badge badge-danger">Cancelled</span>;
    case 'DISPATCHED':
      return <span className="badge badge-low">Dispatched</span>;
    case 'DELIVERED':
      return <span className="badge badge-low">Delivered</span>;
    case 'RTO':
      return <span className="badge badge-danger">Returned (RTO)</span>;
    default:
      return <span className="badge badge-moderate">{status}</span>;
  }
};
