"""
Data Discovery Script

Since QB Web Connector isn't set up yet, this script will:
1. Query Bitrix24 to see what data exists there (what we'll be syncing TO/FROM)
2. Document what QB entities we should focus on based on Bitrix24 data

This gives us a realistic picture of what data flows are needed.
"""

import requests
import json
from collections import defaultdict

# Bitrix24 webhook
BITRIX_WEBHOOK = "https://hartzell.app/rest/1/rdz3zqhd8m0bqcxd/"

def call_bitrix(method, params=None):
    """Call Bitrix24 REST API"""
    url = f"{BITRIX_WEBHOOK}{method}"
    try:
        if params:
            response = requests.post(url, json=params, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_entity(name, method, sample_method=None, count_field="total"):
    """Analyze a Bitrix24 entity"""
    print(f"\n{'='*60}")
    print(f"ANALYZING: {name}")
    print('='*60)

    # Get count
    result = call_bitrix(method, {"start": 0})

    if "error" in result and isinstance(result["error"], str):
        print(f"  ERROR: {result['error']}")
        return None

    if "error" in result:
        print(f"  ERROR: {result.get('error_description', result['error'])}")
        return None

    total = result.get(count_field, result.get("total", 0))
    items = result.get("result", [])

    # Handle nested results
    if isinstance(items, dict):
        # Some endpoints return dict with entity name as key
        for key in items:
            if isinstance(items[key], list):
                items = items[key]
                break

    print(f"  Total Records: {total}")

    if not items:
        print(f"  No data to analyze")
        return {"count": 0, "fields": [], "sample": None}

    # Analyze fields from first few items
    all_fields = defaultdict(lambda: {"count": 0, "non_empty": 0, "sample_values": []})

    sample_size = min(len(items), 10)
    for item in items[:sample_size]:
        if isinstance(item, dict):
            for key, value in item.items():
                all_fields[key]["count"] += 1
                if value and value != "" and value != "0" and value != "0.00":
                    all_fields[key]["non_empty"] += 1
                    if len(all_fields[key]["sample_values"]) < 2:
                        # Truncate long values
                        str_val = str(value)[:50]
                        if str_val not in all_fields[key]["sample_values"]:
                            all_fields[key]["sample_values"].append(str_val)

    # Print field analysis
    print(f"\n  Fields with Data ({len(all_fields)} total fields):")
    print(f"  {'Field':<30} {'Has Data':<10} {'Sample Values'}")
    print(f"  {'-'*30} {'-'*10} {'-'*40}")

    populated_fields = []
    for field, info in sorted(all_fields.items()):
        pct = (info["non_empty"] / info["count"] * 100) if info["count"] > 0 else 0
        if pct > 0:
            populated_fields.append(field)
            samples = ", ".join(info["sample_values"][:2])
            print(f"  {field:<30} {pct:>6.0f}%    {samples[:40]}")

    # Print one full sample record
    if items:
        print(f"\n  Sample Record (first item):")
        sample = items[0]
        if isinstance(sample, dict):
            for k, v in sample.items():
                if v and v != "" and v != "0":
                    print(f"    {k}: {str(v)[:60]}")

    return {
        "count": total,
        "fields": populated_fields,
        "sample": items[0] if items else None
    }

def main():
    print("="*70)
    print("BITRIX24 DATA DISCOVERY")
    print("Analyzing what data exists to determine QB sync requirements")
    print("="*70)

    results = {}

    # ===== CRM ENTITIES =====
    print("\n" + "#"*70)
    print("# CRM ENTITIES (Map to QB Customers/Vendors)")
    print("#"*70)

    # Contacts (-> QB Customers)
    results["contacts"] = analyze_entity(
        "CRM Contacts (-> QB Customers)",
        "crm.contact.list"
    )

    # Companies (-> QB Customers with CompanyName)
    results["companies"] = analyze_entity(
        "CRM Companies (-> QB Customers)",
        "crm.company.list"
    )

    # Leads
    results["leads"] = analyze_entity(
        "CRM Leads",
        "crm.lead.list"
    )

    # ===== DEALS/TRANSACTIONS =====
    print("\n" + "#"*70)
    print("# DEALS/TRANSACTIONS (Map to QB Invoices/Estimates)")
    print("#"*70)

    # Deals (-> QB Invoices or Estimates)
    results["deals"] = analyze_entity(
        "CRM Deals (-> QB Invoices/Estimates)",
        "crm.deal.list"
    )

    # Quotes (-> QB Estimates)
    results["quotes"] = analyze_entity(
        "CRM Quotes (-> QB Estimates)",
        "crm.quote.list"
    )

    # Invoices (-> QB Invoices)
    results["invoices"] = analyze_entity(
        "CRM Invoices (-> QB Invoices)",
        "crm.invoice.list"
    )

    # ===== PRODUCTS =====
    print("\n" + "#"*70)
    print("# PRODUCTS/CATALOG (Map to QB Items)")
    print("#"*70)

    # Products (-> QB Items)
    results["products"] = analyze_entity(
        "CRM Products (-> QB Items)",
        "crm.product.list"
    )

    # Product Sections/Categories
    results["product_sections"] = analyze_entity(
        "Product Sections/Categories",
        "crm.productsection.list"
    )

    # ===== DEAL STAGES & PIPELINES =====
    print("\n" + "#"*70)
    print("# DEAL STAGES & CONFIGURATION")
    print("#"*70)

    # Deal Categories (Pipelines)
    results["deal_categories"] = analyze_entity(
        "Deal Categories/Pipelines",
        "crm.dealcategory.list"
    )

    # Deal Stages
    print("\n" + "="*60)
    print("ANALYZING: Deal Stages")
    print("="*60)
    stages_result = call_bitrix("crm.dealcategory.stage.list", {"ID": 0})
    if "result" in stages_result:
        print(f"  Default Pipeline Stages:")
        for stage in stages_result.get("result", []):
            print(f"    - {stage.get('NAME')} (ID: {stage.get('STATUS_ID')}, Sort: {stage.get('SORT')})")

    # ===== ADDITIONAL ENTITIES =====
    print("\n" + "#"*70)
    print("# ADDITIONAL ENTITIES")
    print("#"*70)

    # Activities/Tasks
    results["activities"] = analyze_entity(
        "CRM Activities",
        "crm.activity.list"
    )

    # Users (for mapping sales reps)
    results["users"] = analyze_entity(
        "Users (-> QB Sales Reps)",
        "user.get"
    )

    # ===== SUMMARY =====
    print("\n" + "="*70)
    print("DISCOVERY SUMMARY")
    print("="*70)

    print("\n  Entity Counts:")
    print(f"  {'-'*40}")
    for entity, data in results.items():
        if data:
            count = data.get("count", 0)
            status = "HAS DATA" if count > 0 else "EMPTY"
            print(f"  {entity:<25} {count:>6} records  [{status}]")

    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDED QB ENTITIES TO SYNC")
    print("="*70)

    recommendations = []

    if results.get("contacts", {}).get("count", 0) > 0 or results.get("companies", {}).get("count", 0) > 0:
        recommendations.append(("Customer", "HIGH", "Sync with Contacts/Companies"))

    if results.get("deals", {}).get("count", 0) > 0:
        recommendations.append(("Invoice", "HIGH", "Sync with Deals"))
        recommendations.append(("Estimate", "MEDIUM", "Sync with Deals (pre-sale stage)"))

    if results.get("products", {}).get("count", 0) > 0:
        recommendations.append(("ItemService", "HIGH", "Sync with Products"))
        recommendations.append(("ItemInventory", "MEDIUM", "If tracking inventory"))

    if results.get("invoices", {}).get("count", 0) > 0:
        recommendations.append(("Invoice", "HIGH", "Direct invoice sync"))

    if results.get("quotes", {}).get("count", 0) > 0:
        recommendations.append(("Estimate", "HIGH", "Direct quote sync"))

    recommendations.append(("Account", "LOW", "Chart of accounts (reference only)"))
    recommendations.append(("PaymentMethod", "LOW", "Payment methods (reference only)"))
    recommendations.append(("Terms", "LOW", "Payment terms (reference only)"))

    print(f"\n  {'QB Entity':<20} {'Priority':<10} {'Reason'}")
    print(f"  {'-'*20} {'-'*10} {'-'*40}")
    for entity, priority, reason in recommendations:
        print(f"  {entity:<20} {priority:<10} {reason}")

    print("\n" + "="*70)
    print("QB ENTITIES WITH LIKELY DATA (Based on Bitrix24 analysis)")
    print("="*70)

    likely_entities = [
        "Customer - Will have data (from Contacts/Companies)",
        "Invoice - Will have data (from Deals/Invoices)",
        "Estimate - May have data (from Deals/Quotes)",
        "ItemService - Will have data (from Products)",
        "ItemInventory - May have data (if inventory tracked)",
        "Account - Will have data (default chart of accounts)",
        "Class - May have data (if job costing used)",
        "Terms - Will have data (Net 30, etc.)",
        "PaymentMethod - Will have data (Check, CC, etc.)",
        "SalesTaxCode - Will have data (Tax/Non-tax)",
        "Employee - May have data (if payroll used)",
    ]

    for entity in likely_entities:
        print(f"  - {entity}")

if __name__ == "__main__":
    main()
