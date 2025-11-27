# QB-Bitrix24 Connector

Bi-directional sync between **QuickBooks Desktop** and **Bitrix24 CRM**.

```mermaid
flowchart LR
    QB["QuickBooks Desktop"] <-->|"auto sync"| C["Connector"] <-->|"auto sync"| B24["Bitrix24 CRM"]
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/botpros-admin/qb-bitrix-connector.git && cd qb-bitrix-connector

# 2. Install (32-bit Python required)
"C:\Program Files (x86)\Python311-32\python.exe" -m pip install spyne lxml flask requests pywin32 bitrix24-rest

# 3. Initialize database
"C:\Program Files (x86)\Python311-32\python.exe" -c "from database import init_db; init_db()"

# 4. Configure (edit config.py)
#    - Set BITRIX24_WEBHOOK to your webhook URL
#    - Set SOAP_PASSWORD (you'll enter this in Web Connector)

# 5. Run
"C:\Program Files (x86)\Python311-32\python.exe" main.py
```

Then add to QuickBooks Web Connector:
1. Open QB → **File → App Management → Update Web Services**
2. **Add Application** → select `qb_bitrix_connector.qwc`
3. Authorize access, enter your password, click **Update Selected**

Verify: http://localhost:8080/status

---

## What Gets Synced

```mermaid
flowchart LR
    subgraph QB["QuickBooks"]
        QBC["Customers"]
        QBI["Invoices"]
        QBE["Estimates"]
        QBP["Products"]
    end
    subgraph B24["Bitrix24"]
        BC["Contacts/Companies"]
        BD["Deals"]
        BP["Products"]
    end
    QBC <-->|"bi-directional"| BC
    QBI <-->|"bi-directional"| BD
    QBE -->|"one-way"| BD
    QBP <-->|"bi-directional"| BP
```

---

## How It Works

```mermaid
flowchart TB
    A["1. Web Connector polls every N minutes"] --> B["2. Connector checks both systems for changes"]
    B --> C["3. Pushes updates in both directions"]
    C --> D["4. Saves sync state to SQLite"]
    D -.->|"repeat"| A
```

**QB → Bitrix24**: Web Connector polls → Connector queries QB for changes → pushes to Bitrix24 REST API

**Bitrix24 → QB**: Changes queued → sent to QB on next poll via qbXML

---

## Configuration

Edit `config.py`:

```python
BITRIX24_WEBHOOK = "https://your-domain.com/rest/1/your-webhook-code/"  # From Bitrix24
SOAP_PASSWORD = "your-secure-password"  # For Web Connector authentication
```

<details>
<summary>Full config.py options</summary>

```python
QB_APP_NAME = "QB-Bitrix24 Connector"
QB_COMPANY_FILE = ""  # Empty = use open company file

BITRIX24_URL = "https://your-bitrix24-domain.com"
BITRIX24_WEBHOOK = "https://your-bitrix24-domain.com/rest/1/your-webhook-code/"

SOAP_HOST = "127.0.0.1"
SOAP_PORT = 8080
SOAP_USERNAME = "qbconnector"
SOAP_PASSWORD = "change-this"

DATABASE_PATH = "sync_state.db"
LOG_FILE = "connector.log"
LOG_LEVEL = "INFO"
```

</details>

---

## Bitrix24 Webhook Setup

1. **Developer resources → Other → Inbound webhook**
2. Name it, select permissions: `crm` (required), `catalog`, `user`
3. Copy webhook URL → paste into `config.py`

**Optional outbound webhook** (for real-time sync): Point `http://YOUR_IP:8080/bitrix24/webhook` at events like `ONCRMCONTACTADD`, `ONCRMCONTACTUPDATE`, etc.

---

## Data Mapping

| QB Field | Bitrix24 Field |
|----------|----------------|
| **Customer** | |
| `Name`, `FirstName`, `LastName` | `NAME`, `LAST_NAME` |
| `CompanyName` | `COMPANY_TITLE` (creates Company) |
| `Email`, `Phone` | `EMAIL`, `PHONE` (arrays) |
| `BillAddress.*` | `ADDRESS_*` |
| **Invoice** | |
| `RefNumber` | `TITLE` |
| `TxnDate`, `DueDate` | `DATE_CREATE`, `CLOSEDATE` |
| `Subtotal` | `OPPORTUNITY` |
| `IsPaid` | `STAGE_ID` (WON if paid) |
| **Item** | |
| `Name`, `SalesDesc` | `NAME`, `DESCRIPTION` |
| `SalesPrice` | `PRICE` |

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| "Service Unavailable" | Connector not running | Check http://localhost:8080/status |
| "No Valid User" | Password mismatch | Re-enter `SOAP_PASSWORD` in Web Connector |
| 32/64-bit error | Wrong Python architecture | Install 32-bit Python |
| Bitrix24 API errors | Bad webhook/permissions | Test `{WEBHOOK_URL}profile` in browser |
| Empty QB response | Company file not open | Open QuickBooks with your file |

**Logs**: `powershell Get-Content connector.log -Tail 50`

---

## Architecture

```mermaid
flowchart TB
    subgraph QB["QuickBooks Desktop"]
        QBApp["QuickBooks"] <--> WC["Web Connector"]
    end
    subgraph Connector["Connector Service :8080"]
        SOAP["SOAP"] <--> Sync["Sync Manager"] <--> B24C["Bitrix24 Client"]
        Sync <--> DB[("SQLite")]
    end
    subgraph B24["Bitrix24"]
        API["REST API"] <--> Data["CRM Data"]
    end
    WC <-->|"qbXML"| SOAP
    B24C <-->|"REST"| API
```

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `webconnector_service.py` | SOAP/qbXML for Web Connector |
| `sync_manager.py` | Sync orchestration |
| `qbxml_builder.py` / `qbxml_parser.py` | QB request/response handling |
| `bitrix24_client.py` | Bitrix24 REST API |
| `database.py` | SQLite sync state |

---

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /status` | Health check, sync stats |
| `GET /soap/?wsdl` | WSDL for Web Connector |
| `POST /soap/` | SOAP endpoint |
| `POST /bitrix24/webhook` | Inbound Bitrix24 events |
| `GET /schema` | QB schema as JSON |

---

## QuickBooks Schema

Supports **35 entities**, **719+ fields** (qbXML SDK 16.0).

**Key entities**: Customer (57 fields), Vendor (49), Invoice (46), Estimate (34), ItemInventory (35), ItemService (18), Employee (34), Account (25)

<details>
<summary>Customer fields (excerpt)</summary>

```
ListID, Name, FullName, CompanyName, FirstName, LastName
Phone, Email, Fax, BillAddress, ShipAddress
Balance, CreditLimit, TermsRef, SalesRepRef, CustomerTypeRef
```

</details>

<details>
<summary>Invoice fields (excerpt)</summary>

```
TxnID, RefNumber, TxnDate, DueDate, ShipDate
Subtotal, SalesTaxTotal, BalanceRemaining, IsPaid
CustomerRef, SalesRepRef, TermsRef, InvoiceLineRet
```

</details>

---

## Requirements

- **QuickBooks Desktop Enterprise** (same machine as connector)
- **Python 3.11+ 32-bit** (required for QB compatibility)
- **Bitrix24** with admin access for webhooks
- Outbound HTTPS to Bitrix24

---

## Running as Windows Service

```bash
nssm install QBBitrixConnector "C:\Program Files (x86)\Python311-32\python.exe" "C:\path\to\main.py"
nssm start QBBitrixConnector
```

---

## License & Support

MIT License | [GitHub Issues](https://github.com/botpros-admin/qb-bitrix-connector/issues)

---

## Changelog

**v1.0.0** (2025-11-26): Initial release - bi-directional sync for customers, invoices, products
