import pickle, re, pandas as pd, numpy as np

# ── helpers ────────────────────────────────────────────────────────────
def parse_price(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        clean = re.sub(r"^[^\d\-.]+", "", x.strip().replace(",", ""))
        try:
            return float(clean)
        except ValueError:
            return None
    return None


def parse_qty(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    if isinstance(x, (int, float)):
        return int(x)
    if isinstance(x, str):
        txt = x.strip().lower()
        if txt == "free":
            return 0
        digits = re.sub(r"[^\d\-]", "", txt)
        try:
            return int(digits) if digits else None
        except ValueError:
            return None
    return None


def to_int_or_na(x):
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return None
    if isinstance(x, (int, np.integer)):
        return int(x)
    if isinstance(x, str):
        digits = re.sub(r"[^\d\-]", "", x)
        try:
            return int(digits) if digits else None
        except ValueError:
            return None
    if isinstance(x, dict):                       # nested {"id": 4}
        for k in ("id", "code", "order_id"):
            if k in x:
                return to_int_or_na(x[k])
    return None


# ── extractor ──────────────────────────────────────────────────────────
class CustomerDataExtractor:
    _CAT_MAP = {1: "Electronics", 2: "Apparel", 3: "Books", 4: "Home Goods"}

    def __init__(self, pkl_path: str, vip_path: str):
        self.pkl_path, self.vip_path = pkl_path, vip_path

    # ------------------------------------------------------------------ #
    def load_data(self):
        with open(self.pkl_path, "rb") as f:
            self.customers = pickle.load(f)
        with open(self.vip_path) as f:
            self.vip_ids = {int(line) for line in f if line.strip().isdigit()}

    # ------------------------------------------------------------------ #
    @classmethod
    def _map_category(cls, raw):
        """
        Accept int / str / float / dict / list and return canonical label.
        """
        # flatten list/tuple/dict
        if isinstance(raw, (list, tuple)) and raw:
            raw = raw[0]
        if isinstance(raw, dict):
            for k in ("id", "code", "category", "value"):
                if k in raw:
                    raw = raw[k]
                    break

        # numeric code path
        try:
            key = int(float(raw))
            return cls._CAT_MAP.get(key, "Misc")
        except Exception:
            pass

        # free-text path
        txt = str(raw).strip().lower()
        if "elect" in txt:
            return "Electronics"
        if "apparel" in txt or "cloth" in txt:
            return "Apparel"
        if "book" in txt:
            return "Books"
        if "home" in txt:
            return "Home Goods"
        return "Misc"

    # ------------------------------------------------------------------ #
    @staticmethod
    def _infer_order_id(order_dict):
        """
        If order_id is None, extract digits from first item's `product_name`
        (pattern: 'Order <num>')  else None.
        """
        if order_dict.get("order_id") is not None:
            return to_int_or_na(order_dict["order_id"])

        if order_dict.get("items"):
            first_name = order_dict["items"][0].get("product_name", "")
            m = re.search(r"order\s+(\d+)", first_name, flags=re.I)
            if m:
                return int(m.group(1))
        return None

    # ------------------------------------------------------------------ #
    def transform(self) -> pd.DataFrame:
        rows = []

        for cust in self.customers:
            cid   = to_int_or_na(cust.get("id"))
            cname = cust.get("name") or ""
            rdate = cust.get("registration_date")

            for order in cust.get("orders", []):
                oid   = self._infer_order_id(order)
                odate = order.get("order_date")

                for item in order.get("items", []):
                    price = parse_price(item.get("price"))
                    qty   = parse_qty(item.get("quantity"))
                    total = price * qty if price is not None and qty is not None else None

                    rows.append({
                        "customer_id"      : cid,
                        "customer_name"    : cname,
                        "registration_date": rdate,
                        "is_vip"           : bool(cid in self.vip_ids) if cid is not None else False,
                        "order_id"         : oid,
                        "order_date"       : odate,
                        "product_id"       : to_int_or_na(item.get("item_id")),
                        "product_name"     : (item.get("product_name") or "").strip(),
                        "unit_price"       : price,
                        "item_quantity"    : qty,
                        "total_item_price" : total,
                        "category"         : self._map_category(item.get("category")),
                    })

        df = pd.DataFrame(rows)

        # dates
        df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
        df["order_date"]        = pd.to_datetime(df["order_date"],        errors="coerce")

        # order-level percentage
        order_totals = df.groupby("order_id")["total_item_price"].transform("sum")
        df["total_order_value_percentage"] = df["total_item_price"] / order_totals * 100

        # final schema
        df = df.astype({
            "customer_id"                 : "Int64",
            "customer_name"               : "string",
            "registration_date"           : "datetime64[ns]",
            "is_vip"                      : "boolean",
            "order_id"                    : "Int64",
            "order_date"                  : "datetime64[ns]",
            "product_id"                  : "Int64",
            "product_name"                : "string",
            "unit_price"                  : "float64",
            "item_quantity"               : "Int64",
            "total_item_price"            : "float64",
            "total_order_value_percentage": "float64",
            "category"                    : "string",
        })

        return df

    # ------------------------------------------------------------------ #
    def extract(self) -> pd.DataFrame:
        self.load_data()
        return self.transform()
