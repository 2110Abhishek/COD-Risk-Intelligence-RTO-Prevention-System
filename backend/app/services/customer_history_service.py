from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.entities import Order


class CustomerHistoryService:
    @staticmethod
    def get_point_in_time_customer_history(
        db: Session,
        phone: str,
        current_order_id: Optional[str] = None,
        as_of_datetime: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Calculates point-in-time customer history strictly before as_of_datetime
        and excluding current_order_id.
        Prevents any target or future leakage.
        """
        if not phone:
            return {
                "prior_orders": 0,
                "prior_rto": 0,
                "prior_delivered": 0,
                "prior_rto_rate": 0.0,
                "delivery_success_rate": 0.0,
                "is_first_time": True,
            }

        query = db.query(Order).filter(Order.phone == phone)

        if current_order_id:
            query = query.filter(Order.order_id != current_order_id)
        if as_of_datetime:
            query = query.filter(Order.order_datetime < as_of_datetime)

        past_orders = query.all()
        prior_orders = len(past_orders)

        if prior_orders == 0:
            return {
                "prior_orders": 0,
                "prior_rto": 0,
                "prior_delivered": 0,
                "prior_rto_rate": 0.0,
                "delivery_success_rate": 0.0,
                "is_first_time": True,
            }

        prior_rto = sum(1 for o in past_orders if o.final_status == "RTO")
        prior_delivered = sum(1 for o in past_orders if o.final_status == "DELIVERED")

        resolved_count = prior_rto + prior_delivered
        rto_rate = round(prior_rto / resolved_count, 4) if resolved_count > 0 else 0.0
        success_rate = round(prior_delivered / resolved_count, 4) if resolved_count > 0 else 0.0

        return {
            "prior_orders": prior_orders,
            "prior_rto": prior_rto,
            "prior_delivered": prior_delivered,
            "prior_rto_rate": rto_rate,
            "delivery_success_rate": success_rate,
            "is_first_time": False,
        }
