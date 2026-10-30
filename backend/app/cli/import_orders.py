import argparse
import pandas as pd
from datetime import datetime
from app.core.database import SessionLocal, Base, engine
from app.models.entities import Order
from app.services.decision_service import DecisionService
from app.api.routes.configuration import load_active_config_from_file
from app.utils.normalization import normalize_datetime, normalize_pincode


def import_and_evaluate_orders(csv_path: str = "data/orders_sample.csv", limit: int = None):
    print(f"Reading orders from: {csv_path}")
    raw_df = pd.read_csv(csv_path)
    # Deduplicate by order_id
    df = raw_df.drop_duplicates(subset=["order_id"]).copy()
    if limit:
        df = df.head(limit)

    db = SessionLocal()
    config = load_active_config_from_file()

    created_count = 0
    evaluated_count = 0

    try:
        for idx, row in df.iterrows():
            order_id = str(row["order_id"]).strip()
            existing = db.query(Order).filter(Order.order_id == order_id).first()
            
            dt = normalize_datetime(row.get("order_datetime")) or datetime.utcnow()
            pin = normalize_pincode(row.get("pincode"))

            if not existing:
                order = Order(
                    order_id=order_id,
                    order_datetime=dt,
                    customer_name=str(row["customer_name"]).strip(),
                    phone=str(row["phone"]).strip(),
                    address=str(row["address"]).strip(),
                    city=str(row["city"]).strip() if pd.notna(row.get("city")) else None,
                    state=str(row["state"]).strip() if pd.notna(row.get("state")) else None,
                    pincode=pin,
                    order_value=float(row["order_value"]),
                    items=str(row["items"]).strip() if pd.notna(row.get("items")) else None,
                    num_items=int(row["num_items"]) if pd.notna(row.get("num_items")) else 1,
                    customer_prior_orders=int(row["customer_prior_orders"]) if pd.notna(row.get("customer_prior_orders")) else 0,
                    customer_prior_rto=int(row["customer_prior_rto"]) if pd.notna(row.get("customer_prior_rto")) else 0,
                    utm_source=str(row["utm_source"]).strip() if pd.notna(row.get("utm_source")) else None,
                    courier=str(row["courier"]).strip() if pd.notna(row.get("courier")) else None,
                    payment_method=str(row["payment_method"]).strip() if pd.notna(row.get("payment_method")) else "COD",
                    final_status=str(row["final_status"]).strip() if pd.notna(row.get("final_status")) else None,
                    workflow_status="RECEIVED"
                )
                db.add(order)
                db.commit()
                created_count += 1
            else:
                order = existing
                from app.models.entities import OrderDecision
                if db.query(OrderDecision).filter(OrderDecision.order_id == order.order_id).first():
                    continue

            # Evaluate COD orders
            if order.payment_method == "COD":
                order_dict = {
                    "order_id": order.order_id,
                    "customer_name": order.customer_name,
                    "phone": order.phone,
                    "address": order.address,
                    "city": order.city,
                    "state": order.state,
                    "pincode": order.pincode,
                    "order_value": order.order_value,
                    "items": order.items,
                    "num_items": order.num_items,
                    "customer_prior_orders": order.customer_prior_orders,
                    "customer_prior_rto": order.customer_prior_rto,
                    "utm_source": order.utm_source,
                    "courier": order.courier,
                    "payment_method": order.payment_method,
                    "order_datetime": order.order_datetime,
                }
                DecisionService.evaluate_order(db, order_dict, config)
                evaluated_count += 1

            if idx % 100 == 0 and idx > 0:
                print(f"Processed {idx} / {len(df)} orders...")

        print(f"Import complete! Ingested {created_count} orders, evaluated {evaluated_count} COD orders.")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data/orders_sample.csv")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    import_and_evaluate_orders(args.file, args.limit)
