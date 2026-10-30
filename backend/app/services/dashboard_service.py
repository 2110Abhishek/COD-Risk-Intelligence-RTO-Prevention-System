from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.entities import Order, OrderDecision, RiskPrediction, OrderEvent, PaymentAttempt
from app.services.financial_service import FinancialService


class DashboardService:
    @staticmethod
    def get_dashboard_summary(
        db: Session,
        config: Dict[str, Any],
        date_filter: Optional[str] = "yesterday"
    ) -> Dict[str, Any]:
        """
        Founder Dashboard Summary with bucket counts and financial metrics.
        """
        now = datetime.utcnow()
        # Filter range mapped to operational periods:
        # In historical evaluation context, "yesterday" refers to the last closed baseline operating day (2026-09-30),
        # "today" refers to active intake (2026-10-30),
        # "last_7_days" refers to the last 7 operating days of the holdout (Sep 24 - 30),
        # "last_30_days" refers to the full September 2026 holdout month,
        # "all" refers to the full multi-month operating history.
        if date_filter == "today":
            start_time = datetime(now.year, now.month, now.day, 0, 0, 0)
            end_time = now
            reporting_label = now.strftime("%B %d, %Y")
        elif date_filter == "yesterday":
            start_time = datetime(2026, 9, 30, 0, 0, 0)
            end_time = datetime(2026, 9, 30, 23, 59, 59)
            reporting_label = "September 30, 2026"
        elif date_filter == "last_7_days":
            start_time = datetime(2026, 9, 24, 0, 0, 0)
            end_time = datetime(2026, 9, 30, 23, 59, 59)
            reporting_label = "Last 7 Days (Sep 24 – Sep 30, 2026)"
        elif date_filter == "last_30_days":
            start_time = datetime(2026, 9, 1, 0, 0, 0)
            end_time = datetime(2026, 9, 30, 23, 59, 59)
            reporting_label = "Last 30 Days (September 2026 Holdout)"
        else:
            start_time = None
            end_time = None
            reporting_label = "All Time History (Apr – Oct 2026)"

        # Join OrderDecision with Order to filter on order placement timestamp
        query = db.query(OrderDecision).join(Order, OrderDecision.order_id == Order.order_id)
        order_query = db.query(Order)

        if start_time and end_time:
            query = query.filter(Order.order_datetime >= start_time, Order.order_datetime <= end_time)
            order_query = order_query.filter(Order.order_datetime >= start_time, Order.order_datetime <= end_time)
        elif start_time:
            query = query.filter(Order.order_datetime >= start_time)
            order_query = order_query.filter(Order.order_datetime >= start_time)

        decisions = query.all()
        orders = order_query.all()
        metrics = FinancialService.calculate_dashboard_metrics(decisions, orders, config)

        # Needs attention count in current scope
        att_query = db.query(Order).filter(
            Order.workflow_status.in_(["HOLD", "AWAITING_CONFIRMATION", "CONFIRMATION_TIMEOUT", "MANUAL_REVIEW"])
        )
        if start_time and end_time:
            att_query = att_query.filter(Order.order_datetime >= start_time, Order.order_datetime <= end_time)
        elif start_time:
            att_query = att_query.filter(Order.order_datetime >= start_time)
        needs_attention = att_query.count()

        return {
            "reporting_date": reporting_label,
            "last_updated": now.isoformat(),
            "bucket_counts": {
                "total_cod_evaluated": metrics["total_cod_evaluated"],
                "ship_as_is": metrics["ship_as_is"],
                "ship_as_is_share": metrics["ship_as_is_share"],
                "ship_after_confirmation": metrics["ship_after_confirmation"],
                "confirmation_share": metrics["confirmation_share"],
                "nudge_to_prepaid": metrics["nudge_to_prepaid"],
                "prepaid_share": metrics["prepaid_share"],
                "hold_cancel": metrics["hold_cancel"],
                "hold_share": metrics["hold_share"],
            },
            "financial_impact": metrics["financial_impact"],
            "needs_attention_count": needs_attention,
        }

    @staticmethod
    def get_trends(db: Session) -> List[Dict[str, Any]]:
        """
        Historical daily decision distribution and RTO rates.
        """
        # Group decisions by date
        orders = db.query(Order).order_by(Order.order_datetime).all()
        if not orders:
            return []

        # Aggregate by month or date
        date_groups = {}
        for o in orders:
            d_str = o.order_datetime.strftime("%Y-%m-%d") if o.order_datetime else "Unknown"
            if d_str not in date_groups:
                date_groups[d_str] = {
                    "date": d_str,
                    "total_orders": 0,
                    "cod_orders": 0,
                    "prepaid_orders": 0,
                    "rto_orders": 0,
                    "delivered_orders": 0,
                }
            g = date_groups[d_str]
            g["total_orders"] += 1
            if o.payment_method == "COD":
                g["cod_orders"] += 1
            else:
                g["prepaid_orders"] += 1
            if o.final_status == "RTO":
                g["rto_orders"] += 1
            elif o.final_status == "DELIVERED":
                g["delivered_orders"] += 1

        # Calculate rates
        result = []
        for d_str, g in sorted(date_groups.items()):
            resolved = g["rto_orders"] + g["delivered_orders"]
            g["rto_rate"] = round(g["rto_orders"] / resolved, 4) if resolved > 0 else 0.0
            result.append(g)

        # Return latest 30 days
        return result[-30:] if len(result) > 30 else result

    @staticmethod
    def get_region_analytics(db: Session) -> List[Dict[str, Any]]:
        """
        Orders and RTO rate by State with sample sizes.
        """
        orders = db.query(Order).all()
        state_map = {}
        for o in orders:
            st = (o.state or "Unknown").strip().title()
            if st not in state_map:
                state_map[st] = {"state": st, "total_orders": 0, "rto_orders": 0, "delivered_orders": 0}
            state_map[st]["total_orders"] += 1
            if o.final_status == "RTO":
                state_map[st]["rto_orders"] += 1
            elif o.final_status == "DELIVERED":
                state_map[st]["delivered_orders"] += 1

        rows = []
        for st, data in state_map.items():
            resolved = data["rto_orders"] + data["delivered_orders"]
            rto_rate = round(data["rto_orders"] / resolved, 4) if resolved > 0 else 0.0
            rows.append({
                "state": st,
                "total_orders": data["total_orders"],
                "resolved_orders": resolved,
                "rto_orders": data["rto_orders"],
                "rto_rate": rto_rate,
                "confidence": "HIGH" if resolved >= 30 else ("MEDIUM" if resolved >= 10 else "LOW_SAMPLE")
            })
        return sorted(rows, key=lambda x: x["total_orders"], reverse=True)

    @staticmethod
    def get_courier_analytics(db: Session) -> List[Dict[str, Any]]:
        """
        Delivery and RTO metrics by logistics partner.
        """
        orders = db.query(Order).all()
        courier_map = {}
        for o in orders:
            c = (o.courier or "Unknown").strip()
            if c not in courier_map:
                courier_map[c] = {"courier": c, "total_orders": 0, "rto_orders": 0, "delivered_orders": 0}
            courier_map[c]["total_orders"] += 1
            if o.final_status == "RTO":
                courier_map[c]["rto_orders"] += 1
            elif o.final_status == "DELIVERED":
                courier_map[c]["delivered_orders"] += 1

        rows = []
        for c, data in courier_map.items():
            resolved = data["rto_orders"] + data["delivered_orders"]
            rto_rate = round(data["rto_orders"] / resolved, 4) if resolved > 0 else 0.0
            rows.append({
                "courier": c,
                "total_orders": data["total_orders"],
                "resolved_orders": resolved,
                "rto_orders": data["rto_orders"],
                "rto_rate": rto_rate,
            })
        return sorted(rows, key=lambda x: x["total_orders"], reverse=True)
