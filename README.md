# Customer Order Data Extractor

Transform messy, nested customer‑order data into a tidy, **analysis‑ready DataFrame** with a single class: `CustomerDataExtractor`.

---

## ✨ Key Features

| Feature                    | Why it matters                                                                                                     |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **One‑line flattening**    | Convert customers → orders → items into a single table for BI, SQL, or ML.                                         |
| **Robust parsing**         | Handles free‑text prices ("\$1,299.00", "free"), quantities ("3 pcs"), mixed ID formats, and partial/missing data. |
| **VIP flag**               | Automatically tags VIP customers based on an external `cust.txt`.                                                  |
| **Category normalisation** | Maps messy category strings to clean labels with an override table.                                                |
| **Strict dtypes**          | Outputs the exact schema you need (ints, floats, bools, datetimes) for reliable downstream use.                    |

---

## 🗂️ Repository Layout

```
.
├── customer_orders_cleaned.pkl   # cleaned nested data (pickle)
├── VIP_customers.txt                     # newline‑separated VIP customer IDs
├── CustomerDataExt.py                 # contains CustomerDataExtractor class
├── examples/                    # runnable notebooks & scripts
└── README.md                    # you are here
```

> **Note** : If you only have the raw (uncleaned) pickle, first run the cleaning script in `examples/01_clean_data.py`.

---

## ⚙️ Requirements

| Package | Version |
| ------- | ------- |
| Python  | 3.9 +   |
| pandas  | ≥ 1.5   |
| numpy   | ≥ 1.24  |

Install everything in one go:

```bash
pip install -r requirements.txt
```

---

## 🚀 Quick Start

```python
from extractor import CustomerDataExtractor

# Paths to your data
PICKLE_PATH = "customer_orders_cleaned.pkl"
VIP_FILE    = "VIP_customers.txt"

extractor = CustomerDataExtractor(
    cleaned_pickle_path=PICKLE_PATH,
    vip_ids_path=VIP_FILE,
)

flat_df = extractor.transform()
print(flat_df.head())
```

Output schema:

| column                         | dtype            |
| ------------------------------ | ---------------- |
| `customer_id`                  | `Int64`          |
| `customer_name`                | `object`         |
| `registration_date`            | `datetime64[ns]` |
| `is_vip`                       | `bool`           |
| `order_id`                     | `Int64`          |
| `order_date`                   | `datetime64[ns]` |
| `product_id`                   | `Int64`          |
| `product_name`                 | `object`         |
| `unit_price`                   | `float64`        |
| `item_quantity`                | `Int64`          |
| `total_item_price`             | `float64`        |
| `total_order_value_percentage` | `float64`        |
| `category`                     | `object`         |


---

## 🤝 Contributing

1. Fork the repo & create your branch (`git checkout -b feat/my-feature`).
2. Commit your changes (`git commit -m 'feat: add my feature'`).
3. Push to the branch (`git push origin feat/my-feature`).
4. Open a Pull Request.

We follow conventional commits and black formatting.


