# QB-Bitrix24 Connector

A bi-directional integration connector that synchronizes data between **QuickBooks Desktop Enterprise** and **Bitrix24 CRM** (on-premise or cloud).

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Environment Details](#environment-details)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Bitrix24 Setup](#bitrix24-setup)
- [QuickBooks Web Connector Setup](#quickbooks-web-connector-setup)
- [Running the Connector](#running-the-connector)
- [Data Mapping](#data-mapping)
- [Troubleshooting](#troubleshooting)
- [File Structure](#file-structure)
- [API Reference](#api-reference)

---

## Overview

This connector enables automated synchronization between QuickBooks Desktop Enterprise and Bitrix24 CRM. It uses the **QuickBooks Web Connector** (SOAP/qbXML) to communicate with QuickBooks and the **Bitrix24 REST API** (webhooks) to communicate with Bitrix24.

### Key Features

- **Bi-directional sync**: Data flows both from QB to Bitrix24 and from Bitrix24 to QB
- **Polling-based**: Web Connector polls the connector service at configurable intervals
- **Entity mapping**: Tracks ID relationships between QB and Bitrix24 records
- **Incremental sync**: Only syncs records modified since the last sync
- **SQLite database**: Stores sync state, ID mappings, and queue items locally

### What Gets Synced

| QuickBooks Entity | Bitrix24 Entity | Direction |
|-------------------|-----------------|-----------|
| Customers | Contacts / Companies | QB ↔ Bitrix24 |
| Vendors | Contacts (vendor type) | QB → Bitrix24 |
| Items (Products/Services) | Products | QB ↔ Bitrix24 |
| Invoices | Deals | QB → Bitrix24 |
| Estimates | Deals (estimate stage) | QB → Bitrix24 |

---

## Architecture

```
┌─────────────────────┐                              ┌─────────────────────┐
│                     │                              │                     │
│  QuickBooks Desktop │                              │  Bitrix24 CRM       │
│  Enterprise 24.0    │                              │  (On-Premise/Cloud) │
│                     │                              │                     │
└──────────┬──────────┘                              └──────────┬──────────┘
           │                                                    │
           │ qbXML/SOAP                              REST API   │
           │ (via Web Connector)                    (webhooks)  │
           │                                                    │
           ▼                                                    ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                                                                          │
│                    QB-Bitrix24 Connector Service                         │
│                    (Python/Flask on localhost:8080)                      │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ SOAP Service    │  │ Sync Manager    │  │ Bitrix24 Client         │  │
│  │ (Web Connector) │  │ (Orchestration) │  │ (REST API)              │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ qbXML Builder   │  │ qbXML Parser    │  │ SQLite Database         │  │
│  │ (Request Gen)   │  │ (Response Parse)│  │ (Sync State/ID Maps)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘  │
│                                                                          │
└──────────────────────────────────────────────────────────────────────────┘
```

### How Sync Works

1. **QB → Bitrix24 (Polling)**:
   - Web Connector polls the connector service every N minutes
   - Connector queries QB for records modified since last sync
   - Connector pushes changes to Bitrix24 via REST API
   - ID mappings are stored for future reference

2. **Bitrix24 → QB (Queue-based)**:
   - Changes in Bitrix24 are queued (via outbound webhook or manual trigger)
   - On next Web Connector poll, queued items are sent to QB
   - QB processes the qbXML requests and returns results

---

## Environment Details

This connector was developed and tested in the following environment:

### Server Machine

| Property | Value |
|----------|-------|
| **Hostname** | Dell OptiPlex 3090 |
| **Type** | Physical Desktop (not a VM) |
| **OS** | Windows 10 (Build 19045.6456) |
| **Public IP** | 76.8.89.254 |
| **Role** | QuickBooks host + Connector service |

### QuickBooks Installation

| Property | Value |
|----------|-------|
| **Product** | QuickBooks Enterprise Solutions - Contractor Edition |
| **Version** | 24.0 (also has 22.0 installed) |
| **Install Path** | `C:\Program Files (x86)\Intuit\QuickBooks Enterprise Solutions 24.0` |
| **Architecture** | 32-bit |
| **Web Connector** | Included with QuickBooks |

### Bitrix24 Instance

| Property | Value |
|----------|-------|
| **URL** | https://hartzell.app |
| **Type** | On-Premise (hosted on AWS) |
| **API** | REST API via Inbound Webhook |

### Python Environment

| Property | Value |
|----------|-------|
| **Version** | Python 3.11.9 |
| **Architecture** | 32-bit (required for QB COM interface) |
| **Install Path** | `C:\Program Files (x86)\Python311-32` |

---

## Prerequisites

### Required Software

1. **QuickBooks Desktop Enterprise** (Pro/Premier may work but untested)
   - Must be installed on the same machine as the connector
   - Web Connector must be available (included with QB)

2. **Python 3.11+ (32-bit)** - IMPORTANT: Must be 32-bit for QuickBooks compatibility
   - Download from: https://www.python.org/downloads/windows/
   - Select "Windows installer (32-bit)"
   - Check "Add Python to PATH" during installation

3. **Bitrix24** (Cloud or On-Premise)
   - Must have admin access to create webhooks
   - CRM module required

### Network Requirements

- Connector service runs on `localhost:8080` by default
- QuickBooks and connector must be on the same machine
- Outbound HTTPS access to Bitrix24 URL required

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/botpros-admin/qb-bitrix-connector.git
cd qb-bitrix-connector
```

### 2. Install Python Dependencies

```bash
# Using 32-bit Python (adjust path as needed)
"C:\Program Files (x86)\Python311-32\python.exe" -m pip install spyne lxml flask requests pywin32 bitrix24-rest
```

**Required packages:**
- `spyne` - SOAP server framework for Web Connector interface
- `lxml` - XML parsing for qbXML
- `flask` - Web framework for HTTP endpoints
- `requests` - HTTP client for Bitrix24 API
- `pywin32` - Windows COM interface (for future direct QB access)
- `bitrix24-rest` - Bitrix24 REST API client

### 3. Initialize the Database

```bash
"C:\Program Files (x86)\Python311-32\python.exe" -c "from database import init_db; init_db()"
```

---

## Configuration

### config.py

Edit `config.py` with your settings:

```python
"""
Configuration for QB-Bitrix24 Connector
"""

# QuickBooks Settings
QB_APP_NAME = "QB-Bitrix24 Connector"
QB_COMPANY_FILE = ""  # Leave empty to use currently open company file

# Bitrix24 Settings
BITRIX24_URL = "https://your-bitrix24-domain.com"
BITRIX24_WEBHOOK = "https://your-bitrix24-domain.com/rest/1/your-webhook-code/"

# Web Connector SOAP Service Settings
SOAP_HOST = "127.0.0.1"
SOAP_PORT = 8080
SOAP_USERNAME = "qbconnector"
SOAP_PASSWORD = "your-secure-password-here"  # CHANGE THIS!

# Sync Settings
SYNC_INTERVAL_SECONDS = 300  # Controlled by Web Connector, not this setting

# Database for tracking sync state
DATABASE_PATH = "C:/Users/max/qb-bitrix-connector/sync_state.db"

# Logging
LOG_FILE = "C:/Users/max/qb-bitrix-connector/connector.log"
LOG_LEVEL = "INFO"
```

### Important Configuration Notes

1. **SOAP_PASSWORD**: Change this from the default! This is the password you'll enter in Web Connector.

2. **BITRIX24_WEBHOOK**: This is the inbound webhook URL from Bitrix24 (see Bitrix24 Setup below).

3. **Database paths**: Use forward slashes or escaped backslashes in paths.

---

## Bitrix24 Setup

### Creating an Inbound Webhook (Required)

The inbound webhook allows the connector to read/write data to Bitrix24.

1. Log into Bitrix24 as an administrator
2. Navigate to: **Developer resources → Other → Inbound webhook**
3. Configure the webhook:
   - **Name**: `QB Connector Inbound (API Access)`
   - **Permissions/Scopes**: Select at minimum:
     - `crm` - CRM access (contacts, companies, deals, products)
     - `catalog` - Product catalog (optional, for inventory sync)
     - `user` - User information (optional)
4. Click **Save**
5. Copy the webhook URL (looks like `https://your-domain.com/rest/1/abc123xyz/`)
6. Paste into `config.py` as `BITRIX24_WEBHOOK`

### Creating an Outbound Webhook (Optional)

The outbound webhook enables real-time sync from Bitrix24 to QuickBooks. **This is optional** - without it, Bitrix24 changes sync on the next polling interval.

**Requirements for outbound webhooks:**
- Your connector must be accessible from the internet
- Requires port forwarding or a tunnel service (ngrok, Cloudflare Tunnel)

**Setup:**
1. Navigate to: **Developer resources → Other → Outbound webhook**
2. Configure:
   - **Name**: `QB Connector Outbound (Event Notifications)`
   - **Handler URL**: `http://YOUR_PUBLIC_IP:8080/bitrix24/webhook`
   - **Events**: Select relevant events:
     - `ONCRMCONTACTADD`
     - `ONCRMCONTACTUPDATE`
     - `ONCRMCOMPANYADD`
     - `ONCRMCOMPANYUPDATE`
     - `ONCRMDEALADD`
     - `ONCRMDEALUPDATE`

---

## QuickBooks Web Connector Setup

### 1. Locate the QWC File

The Web Connector configuration file is at:
```
C:\Users\max\qb-bitrix-connector\qb_bitrix_connector.qwc
```

### 2. Start the Connector Service

Before adding to Web Connector, the service must be running:

```bash
# Option 1: Run directly
"C:\Program Files (x86)\Python311-32\python.exe" C:\Users\max\qb-bitrix-connector\main.py

# Option 2: Use the batch file
C:\Users\max\qb-bitrix-connector\run_connector.bat
```

Verify it's running by visiting: http://localhost:8080/status

### 3. Open QuickBooks and Web Connector

1. Open **QuickBooks Enterprise** with your company file
2. Open **Web Connector**:
   - In QuickBooks: **File → App Management → Update Web Services**
   - Or search "QuickBooks Web Connector" in Windows Start menu

### 4. Add the Application

1. In Web Connector, click **"Add an Application"**
2. Browse to: `C:\Users\max\qb-bitrix-connector\qb_bitrix_connector.qwc`
3. Click **Open**

### 5. Authorize in QuickBooks

When prompted by QuickBooks:
1. Select **"Yes, always allow access even if QuickBooks is not running"**
2. Click **Continue**

### 6. Enter Password

1. In Web Connector, find "QB-Bitrix24 Connector" in the list
2. Click the **Password** field
3. Enter the password from `config.py` (`SOAP_PASSWORD`)
4. Press Enter to save

### 7. Configure Auto-Run (Optional)

1. Check the checkbox next to "QB-Bitrix24 Connector"
2. Set **"Auto-Run"** interval (e.g., every 5 minutes)
3. Or manually click **"Update Selected"** to run sync

---

## Running the Connector

### Manual Start

```bash
"C:\Program Files (x86)\Python311-32\python.exe" C:\Users\max\qb-bitrix-connector\main.py
```

### Using Batch File

Double-click `run_connector.bat`

### As a Windows Service (Production)

For production deployment, consider running as a Windows service using `nssm` or similar:

```bash
# Install nssm from https://nssm.cc/
nssm install QBBitrixConnector "C:\Program Files (x86)\Python311-32\python.exe" "C:\Users\max\qb-bitrix-connector\main.py"
nssm start QBBitrixConnector
```

### Verify Running

- Web UI: http://localhost:8080
- Status API: http://localhost:8080/status
- WSDL: http://localhost:8080/soap/?wsdl

---

## Data Mapping

### QuickBooks Customer → Bitrix24 Contact/Company

| QB Field | Bitrix24 Field | Notes |
|----------|----------------|-------|
| `Name` | `NAME` / `TITLE` | Split for contacts, full for companies |
| `FirstName` | `NAME` | Contact first name |
| `LastName` | `LAST_NAME` | Contact last name |
| `CompanyName` | `COMPANY_TITLE` | Creates Company if present |
| `Email` | `EMAIL` | Array format in Bitrix24 |
| `Phone` | `PHONE` | Array format in Bitrix24 |
| `ListID` | `SOURCE_DESCRIPTION` | Stored for mapping |

### QuickBooks Invoice → Bitrix24 Deal

| QB Field | Bitrix24 Field | Notes |
|----------|----------------|-------|
| `RefNumber` | `TITLE` | "Invoice {RefNumber}" |
| `Subtotal` | `OPPORTUNITY` | Deal amount |
| `TxnID` | `COMMENTS` | Stored for mapping |
| `IsPaid` | `STAGE_ID` | WON if paid, EXECUTING if balance |
| `CustomerRef` | `COMPANY_ID` | Linked via ID mapping |

### QuickBooks Item → Bitrix24 Product

| QB Field | Bitrix24 Field | Notes |
|----------|----------------|-------|
| `Name` | `NAME` | Product name |
| `Description` | `DESCRIPTION` | Product description |
| `Price` | `PRICE` | Numeric price |
| `ListID` | `XML_ID` | `QB_{ListID}` format |

---

## Troubleshooting

### Common Issues

#### "Service Unavailable" Error in Web Connector

**Cause**: Connector service is not running or wrong port.

**Solution**:
1. Verify connector is running: `curl http://localhost:8080/status`
2. Check if port 8080 is in use: `netstat -an | findstr 8080`
3. Check connector logs: `C:\Users\max\qb-bitrix-connector\connector.log`

#### "No Valid User" Authentication Error

**Cause**: Username or password mismatch.

**Solution**:
1. Verify `SOAP_USERNAME` in `config.py` (default: `qbconnector`)
2. Verify `SOAP_PASSWORD` in `config.py`
3. Re-enter password in Web Connector

#### Python "32-bit vs 64-bit" Error

**Cause**: Using 64-bit Python with 32-bit QuickBooks.

**Solution**: Install 32-bit Python from python.org (Windows installer x86).

#### Bitrix24 API Errors

**Cause**: Invalid webhook URL or missing permissions.

**Solution**:
1. Test webhook: Visit `{WEBHOOK_URL}profile` in browser
2. Verify CRM scope is enabled on the webhook
3. Check webhook hasn't expired or been regenerated

#### "Empty Response" from QuickBooks

**Cause**: Company file not open or QB in single-user mode for list operations.

**Solution**:
1. Ensure QuickBooks is open with the correct company file
2. For some operations, QB must not be in single-user mode

### Checking Logs

```bash
# View connector log
type C:\Users\max\qb-bitrix-connector\connector.log

# View recent entries
powershell Get-Content C:\Users\max\qb-bitrix-connector\connector.log -Tail 50
```

### Testing Bitrix24 Connection

```python
"C:\Program Files (x86)\Python311-32\python.exe" -c "
from bitrix24_client import Bitrix24Client
client = Bitrix24Client('YOUR_WEBHOOK_URL')
print(client.get_contacts())
"
```

---

## File Structure

```
qb-bitrix-connector/
├── main.py                    # Main entry point - starts the service
├── config.py                  # Configuration settings
├── webconnector_service.py    # SOAP service for QB Web Connector
├── sync_manager.py            # Orchestrates sync between QB and Bitrix24
├── qbxml_builder.py           # Builds qbXML requests for QuickBooks
├── qbxml_parser.py            # Parses qbXML responses from QuickBooks
├── bitrix24_client.py         # REST API client for Bitrix24
├── bitrix24_webhook_handler.py # Handles incoming Bitrix24 webhooks
├── database.py                # SQLite database for sync state
├── qb_bitrix_connector.qwc    # Web Connector configuration file
├── run_connector.bat          # Windows batch file to start service
├── sync_state.db              # SQLite database (created on first run)
├── connector.log              # Log file (created on first run)
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

---

## API Reference

### Status Endpoint

```
GET http://localhost:8080/status
```

Returns:
```json
{
  "status": "running",
  "version": "1.0.0",
  "active_sessions": 0,
  "id_mappings": 150,
  "syncs_last_24h": 48,
  "pending_queue": 0,
  "bitrix24_configured": true
}
```

### SOAP Endpoints (for Web Connector)

```
WSDL: http://localhost:8080/soap/?wsdl
Endpoint: http://localhost:8080/soap/
```

Methods:
- `authenticate(username, password)` - Authenticate Web Connector session
- `sendRequestXML(...)` - Get next qbXML request
- `receiveResponseXML(...)` - Process QB response
- `getLastError(ticket)` - Get last error message
- `closeConnection(ticket)` - Close session
- `serverVersion()` - Get server version
- `clientVersion(version)` - Receive client version

### Bitrix24 Webhook Endpoint (Optional)

```
POST http://localhost:8080/bitrix24/webhook
```

Receives event notifications from Bitrix24 outbound webhooks.

---

## License

MIT License - See LICENSE file for details.

---

## Support

For issues and questions:
- GitHub Issues: https://github.com/botpros-admin/qb-bitrix-connector/issues

---

## Changelog

### v1.0.0 (2025-11-26)
- Initial release
- QuickBooks Desktop Enterprise 24.0 support
- Bitrix24 on-premise support
- Bi-directional sync for customers, items, invoices
- SQLite-based sync state tracking
- Web Connector SOAP interface
