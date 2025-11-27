"""
QuickBooks Desktop Full Schema Extractor

This script documents ALL available fields, field types, and nested structures
from QuickBooks Desktop qbXML API.

Based on qbXML SDK 16.0 specification for QuickBooks Enterprise.
"""

# =============================================================================
# QUICKBOOKS DESKTOP COMPLETE FIELD SCHEMA
# =============================================================================

QB_SCHEMA = {
    # =========================================================================
    # CUSTOMER (CustomerRet)
    # =========================================================================
    "Customer": {
        "description": "Customer/Client records in QuickBooks",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            # Core Identifiers
            "ListID": {"type": "IDTYPE", "description": "Unique QB identifier", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "description": "Record creation timestamp", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "description": "Last modification timestamp", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "description": "Revision number for optimistic locking", "readonly": True},

            # Basic Info
            "Name": {"type": "STRTYPE", "max_length": 41, "description": "Short name (must be unique)", "required": True},
            "FullName": {"type": "STRTYPE", "max_length": 209, "description": "Full hierarchical name (includes parent)", "readonly": True},
            "IsActive": {"type": "BOOLTYPE", "description": "Active/Inactive status"},
            "Sublevel": {"type": "INTTYPE", "description": "Nesting level in hierarchy", "readonly": True},

            # Company/Contact Info
            "CompanyName": {"type": "STRTYPE", "max_length": 41, "description": "Company name"},
            "Salutation": {"type": "STRTYPE", "max_length": 15, "description": "Mr., Mrs., Ms., etc."},
            "FirstName": {"type": "STRTYPE", "max_length": 25, "description": "Contact first name"},
            "MiddleName": {"type": "STRTYPE", "max_length": 5, "description": "Contact middle name/initial"},
            "LastName": {"type": "STRTYPE", "max_length": 25, "description": "Contact last name"},
            "Suffix": {"type": "STRTYPE", "max_length": 10, "description": "Jr., Sr., III, etc."},
            "JobTitle": {"type": "STRTYPE", "max_length": 41, "description": "Job title"},

            # Communication
            "Phone": {"type": "STRTYPE", "max_length": 21, "description": "Primary phone"},
            "AltPhone": {"type": "STRTYPE", "max_length": 21, "description": "Alternate phone"},
            "Fax": {"type": "STRTYPE", "max_length": 21, "description": "Fax number"},
            "Email": {"type": "STRTYPE", "max_length": 1023, "description": "Email address"},
            "Cc": {"type": "STRTYPE", "max_length": 1023, "description": "CC email addresses"},
            "Contact": {"type": "STRTYPE", "max_length": 41, "description": "Primary contact name"},
            "AltContact": {"type": "STRTYPE", "max_length": 41, "description": "Alternate contact name"},

            # Additional Contact Info (Multiple allowed)
            "AdditionalContactRef": {"type": "LIST", "description": "Additional contacts", "nested": {
                "ContactName": {"type": "STRTYPE", "max_length": 40},
                "ContactValue": {"type": "STRTYPE", "max_length": 255},
            }},

            # Addresses
            "BillAddress": {"type": "ADDRESS", "description": "Billing address", "nested": {
                "Addr1": {"type": "STRTYPE", "max_length": 41},
                "Addr2": {"type": "STRTYPE", "max_length": 41},
                "Addr3": {"type": "STRTYPE", "max_length": 41},
                "Addr4": {"type": "STRTYPE", "max_length": 41},
                "Addr5": {"type": "STRTYPE", "max_length": 41},
                "City": {"type": "STRTYPE", "max_length": 31},
                "State": {"type": "STRTYPE", "max_length": 21},
                "PostalCode": {"type": "STRTYPE", "max_length": 13},
                "Country": {"type": "STRTYPE", "max_length": 31},
                "Note": {"type": "STRTYPE", "max_length": 41},
            }},
            "BillAddressBlock": {"type": "ADDRESSBLOCK", "description": "Formatted billing address block", "nested": {
                "Addr1": {"type": "STRTYPE"},
                "Addr2": {"type": "STRTYPE"},
                "Addr3": {"type": "STRTYPE"},
                "Addr4": {"type": "STRTYPE"},
                "Addr5": {"type": "STRTYPE"},
            }},
            "ShipAddress": {"type": "ADDRESS", "description": "Shipping address", "nested": {
                "Addr1": {"type": "STRTYPE", "max_length": 41},
                "Addr2": {"type": "STRTYPE", "max_length": 41},
                "Addr3": {"type": "STRTYPE", "max_length": 41},
                "Addr4": {"type": "STRTYPE", "max_length": 41},
                "Addr5": {"type": "STRTYPE", "max_length": 41},
                "City": {"type": "STRTYPE", "max_length": 31},
                "State": {"type": "STRTYPE", "max_length": 21},
                "PostalCode": {"type": "STRTYPE", "max_length": 13},
                "Country": {"type": "STRTYPE", "max_length": 31},
                "Note": {"type": "STRTYPE", "max_length": 41},
            }},
            "ShipAddressBlock": {"type": "ADDRESSBLOCK", "description": "Formatted shipping address block"},
            "ShipToAddress": {"type": "LIST", "description": "Multiple ship-to addresses", "nested": {
                "Name": {"type": "STRTYPE", "max_length": 41},
                "Addr1": {"type": "STRTYPE", "max_length": 41},
                "Addr2": {"type": "STRTYPE", "max_length": 41},
                "Addr3": {"type": "STRTYPE", "max_length": 41},
                "Addr4": {"type": "STRTYPE", "max_length": 41},
                "Addr5": {"type": "STRTYPE", "max_length": 41},
                "City": {"type": "STRTYPE", "max_length": 31},
                "State": {"type": "STRTYPE", "max_length": 21},
                "PostalCode": {"type": "STRTYPE", "max_length": 13},
                "Country": {"type": "STRTYPE", "max_length": 31},
                "Note": {"type": "STRTYPE", "max_length": 41},
                "DefaultShipTo": {"type": "BOOLTYPE"},
            }},

            # Financial Info
            "Balance": {"type": "AMTTYPE", "description": "Current balance", "readonly": True},
            "TotalBalance": {"type": "AMTTYPE", "description": "Total balance including sub-customers", "readonly": True},
            "OpenBalance": {"type": "AMTTYPE", "description": "Opening balance"},
            "OpenBalanceDate": {"type": "DATETYPE", "description": "Opening balance date"},
            "CreditLimit": {"type": "AMTTYPE", "description": "Credit limit"},

            # References
            "ParentRef": {"type": "REF", "description": "Parent customer (for jobs/sub-customers)", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "CustomerTypeRef": {"type": "REF", "description": "Customer type category", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "TermsRef": {"type": "REF", "description": "Payment terms", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "SalesRepRef": {"type": "REF", "description": "Sales representative", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "SalesTaxCodeRef": {"type": "REF", "description": "Sales tax code", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "ItemSalesTaxRef": {"type": "REF", "description": "Default sales tax item", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "PreferredPaymentMethodRef": {"type": "REF", "description": "Preferred payment method", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "PriceLevelRef": {"type": "REF", "description": "Price level for this customer", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "CurrencyRef": {"type": "REF", "description": "Currency (multi-currency)", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "ClassRef": {"type": "REF", "description": "Class (job costing)", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},

            # Credit Card Info
            "CreditCardInfo": {"type": "CREDITCARD", "description": "Credit card on file", "nested": {
                "CreditCardNumber": {"type": "STRTYPE", "max_length": 25},
                "ExpirationMonth": {"type": "INTTYPE"},
                "ExpirationYear": {"type": "INTTYPE"},
                "NameOnCard": {"type": "STRTYPE", "max_length": 41},
                "CreditCardAddress": {"type": "STRTYPE", "max_length": 41},
                "CreditCardPostalCode": {"type": "STRTYPE", "max_length": 13},
            }},

            # Job/Project Info
            "JobStatus": {"type": "ENUMTYPE", "description": "Job status", "values": ["Awarded", "Closed", "InProgress", "None", "NotAwarded", "Pending"]},
            "JobStartDate": {"type": "DATETYPE", "description": "Job start date"},
            "JobProjectedEndDate": {"type": "DATETYPE", "description": "Projected end date"},
            "JobEndDate": {"type": "DATETYPE", "description": "Actual end date"},
            "JobDesc": {"type": "STRTYPE", "max_length": 99, "description": "Job description"},
            "JobTypeRef": {"type": "REF", "description": "Job type", "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},

            # Other
            "Notes": {"type": "STRTYPE", "max_length": 4095, "description": "Notes/comments"},
            "AccountNumber": {"type": "STRTYPE", "max_length": 99, "description": "Customer account number"},
            "ResaleNumber": {"type": "STRTYPE", "max_length": 15, "description": "Resale certificate number"},
            "PreferredDeliveryMethod": {"type": "ENUMTYPE", "values": ["None", "Email", "Fax", "Mail"]},
            "ExternalGUID": {"type": "GUIDTYPE", "description": "External system GUID"},
            "TaxRegistrationNumber": {"type": "STRTYPE", "max_length": 30, "description": "Tax ID/VAT number"},

            # Custom Fields (Data Extension)
            "DataExtRet": {"type": "LIST", "description": "Custom field values", "nested": {
                "OwnerID": {"type": "GUIDTYPE"},
                "DataExtName": {"type": "STRTYPE", "max_length": 31},
                "DataExtType": {"type": "ENUMTYPE", "values": ["AMTTYPE", "DATETIMETYPE", "INTTYPE", "PERCENTTYPE", "PRICETYPE", "QUANTYPE", "STR1024TYPE", "STR255TYPE"]},
                "DataExtValue": {"type": "STRTYPE", "max_length": 1024},
            }},
        }
    },

    # =========================================================================
    # VENDOR (VendorRet)
    # =========================================================================
    "Vendor": {
        "description": "Vendor/Supplier records",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            # Core Identifiers
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},

            # Basic Info
            "Name": {"type": "STRTYPE", "max_length": 41, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "CompanyName": {"type": "STRTYPE", "max_length": 41},
            "Salutation": {"type": "STRTYPE", "max_length": 15},
            "FirstName": {"type": "STRTYPE", "max_length": 25},
            "MiddleName": {"type": "STRTYPE", "max_length": 5},
            "LastName": {"type": "STRTYPE", "max_length": 25},
            "Suffix": {"type": "STRTYPE", "max_length": 10},
            "JobTitle": {"type": "STRTYPE", "max_length": 41},

            # Communication
            "Phone": {"type": "STRTYPE", "max_length": 21},
            "AltPhone": {"type": "STRTYPE", "max_length": 21},
            "Fax": {"type": "STRTYPE", "max_length": 21},
            "Email": {"type": "STRTYPE", "max_length": 1023},
            "Cc": {"type": "STRTYPE", "max_length": 1023},
            "Contact": {"type": "STRTYPE", "max_length": 41},
            "AltContact": {"type": "STRTYPE", "max_length": 41},

            # Addresses
            "VendorAddress": {"type": "ADDRESS", "nested": {
                "Addr1": {"type": "STRTYPE", "max_length": 41},
                "Addr2": {"type": "STRTYPE", "max_length": 41},
                "Addr3": {"type": "STRTYPE", "max_length": 41},
                "Addr4": {"type": "STRTYPE", "max_length": 41},
                "Addr5": {"type": "STRTYPE", "max_length": 41},
                "City": {"type": "STRTYPE", "max_length": 31},
                "State": {"type": "STRTYPE", "max_length": 21},
                "PostalCode": {"type": "STRTYPE", "max_length": 13},
                "Country": {"type": "STRTYPE", "max_length": 31},
                "Note": {"type": "STRTYPE", "max_length": 41},
            }},
            "ShipAddress": {"type": "ADDRESS", "nested": {
                "Addr1": {"type": "STRTYPE", "max_length": 41},
                "Addr2": {"type": "STRTYPE", "max_length": 41},
                "Addr3": {"type": "STRTYPE", "max_length": 41},
                "Addr4": {"type": "STRTYPE", "max_length": 41},
                "Addr5": {"type": "STRTYPE", "max_length": 41},
                "City": {"type": "STRTYPE", "max_length": 31},
                "State": {"type": "STRTYPE", "max_length": 21},
                "PostalCode": {"type": "STRTYPE", "max_length": 13},
                "Country": {"type": "STRTYPE", "max_length": 31},
                "Note": {"type": "STRTYPE", "max_length": 41},
            }},

            # Financial
            "Balance": {"type": "AMTTYPE", "readonly": True},
            "OpenBalance": {"type": "AMTTYPE"},
            "OpenBalanceDate": {"type": "DATETYPE"},
            "CreditLimit": {"type": "AMTTYPE"},

            # References
            "VendorTypeRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "TermsRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "BillingRateRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "PrefillAccountRef": {"type": "LIST", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "CurrencyRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},

            # Tax Info
            "VendorTaxIdent": {"type": "STRTYPE", "max_length": 15, "description": "Vendor Tax ID (SSN/EIN)"},
            "IsVendorEligibleFor1099": {"type": "BOOLTYPE"},
            "IsSalesTaxAgency": {"type": "BOOLTYPE"},
            "SalesTaxCodeRef": {"type": "REF"},
            "SalesTaxCountry": {"type": "ENUMTYPE", "values": ["Australia", "Canada", "UK", "US"]},
            "SalesTaxReturnRef": {"type": "REF"},
            "TaxRegistrationNumber": {"type": "STRTYPE", "max_length": 30},
            "ReportingPeriod": {"type": "ENUMTYPE", "values": ["Monthly", "Quarterly"]},
            "IsTaxTrackedOnPurchases": {"type": "BOOLTYPE"},
            "IsTaxTrackedOnSales": {"type": "BOOLTYPE"},
            "IsTaxOnTax": {"type": "BOOLTYPE"},
            "TaxOnPurchasesAccountRef": {"type": "REF"},
            "TaxOnSalesAccountRef": {"type": "REF"},

            # Other
            "Notes": {"type": "STRTYPE", "max_length": 4095},
            "AccountNumber": {"type": "STRTYPE", "max_length": 99},
            "NameOnCheck": {"type": "STRTYPE", "max_length": 41},
            "ExternalGUID": {"type": "GUIDTYPE"},

            # Custom Fields
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # INVOICE (InvoiceRet)
    # =========================================================================
    "Invoice": {
        "description": "Sales invoices",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            # Core Identifiers
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},

            # Basic Info
            "RefNumber": {"type": "STRTYPE", "max_length": 11, "description": "Invoice number"},
            "TxnDate": {"type": "DATETYPE"},
            "DueDate": {"type": "DATETYPE"},
            "ShipDate": {"type": "DATETYPE"},
            "PONumber": {"type": "STRTYPE", "max_length": 25},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsPending": {"type": "BOOLTYPE"},
            "IsFinanceCharge": {"type": "BOOLTYPE"},
            "IsPaid": {"type": "BOOLTYPE", "readonly": True},
            "IsToBeEmailed": {"type": "BOOLTYPE"},
            "IsToBePrinted": {"type": "BOOLTYPE"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},

            # Financial Totals
            "Subtotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxTotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxPercentage": {"type": "PERCENTTYPE", "readonly": True},
            "AppliedAmount": {"type": "AMTTYPE", "readonly": True},
            "BalanceRemaining": {"type": "AMTTYPE", "readonly": True},
            "BalanceRemainingInHomeCurrency": {"type": "AMTTYPE", "readonly": True},
            "ExchangeRate": {"type": "FLOATTYPE"},
            "SuggestedDiscountAmount": {"type": "AMTTYPE", "readonly": True},
            "SuggestedDiscountDate": {"type": "DATETYPE", "readonly": True},

            # References
            "CustomerRef": {"type": "REF", "required": True, "nested": {
                "ListID": {"type": "IDTYPE"},
                "FullName": {"type": "STRTYPE"},
            }},
            "ClassRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "ARAccountRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "TemplateRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "TermsRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "SalesRepRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "ShipMethodRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "ItemSalesTaxRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "CustomerMsgRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "CustomerSalesTaxCodeRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "CurrencyRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},

            # Addresses
            "BillAddress": {"type": "ADDRESS", "nested": {
                "Addr1": {"type": "STRTYPE"}, "Addr2": {"type": "STRTYPE"}, "Addr3": {"type": "STRTYPE"},
                "Addr4": {"type": "STRTYPE"}, "Addr5": {"type": "STRTYPE"},
                "City": {"type": "STRTYPE"}, "State": {"type": "STRTYPE"},
                "PostalCode": {"type": "STRTYPE"}, "Country": {"type": "STRTYPE"}, "Note": {"type": "STRTYPE"},
            }},
            "ShipAddress": {"type": "ADDRESS"},

            # Line Items
            "InvoiceLineRet": {"type": "LIST", "description": "Invoice line items", "nested": {
                "TxnLineID": {"type": "IDTYPE", "readonly": True},
                "ItemRef": {"type": "REF", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
                "Desc": {"type": "STRTYPE", "max_length": 4095},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE", "max_length": 31},
                "OverrideUOMSetRef": {"type": "REF"},
                "Rate": {"type": "PRICETYPE"},
                "RatePercent": {"type": "PERCENTTYPE"},
                "ClassRef": {"type": "REF"},
                "Amount": {"type": "AMTTYPE"},
                "OptionForPriceRuleConflict": {"type": "ENUMTYPE", "values": ["Zero", "BasePrice"]},
                "InventorySiteRef": {"type": "REF"},
                "InventorySiteLocationRef": {"type": "REF"},
                "SerialNumber": {"type": "STRTYPE", "max_length": 4095},
                "LotNumber": {"type": "STRTYPE", "max_length": 40},
                "ServiceDate": {"type": "DATETYPE"},
                "SalesTaxCodeRef": {"type": "REF"},
                "IsTaxable": {"type": "BOOLTYPE"},
                "Other1": {"type": "STRTYPE", "max_length": 29},
                "Other2": {"type": "STRTYPE", "max_length": 29},
                "DataExtRet": {"type": "LIST"},
            }},

            # Group Line Items
            "InvoiceLineGroupRet": {"type": "LIST", "description": "Grouped line items", "nested": {
                "TxnLineID": {"type": "IDTYPE"},
                "ItemGroupRef": {"type": "REF"},
                "Desc": {"type": "STRTYPE"},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE"},
                "IsPrintItemsInGroup": {"type": "BOOLTYPE"},
                "TotalAmount": {"type": "AMTTYPE"},
                "InvoiceLineRet": {"type": "LIST"},  # Nested line items within group
            }},

            # Linked Transactions
            "LinkedTxn": {"type": "LIST", "description": "Related transactions", "nested": {
                "TxnID": {"type": "IDTYPE"},
                "TxnType": {"type": "ENUMTYPE"},
                "TxnDate": {"type": "DATETYPE"},
                "RefNumber": {"type": "STRTYPE"},
                "LinkType": {"type": "ENUMTYPE"},
                "Amount": {"type": "AMTTYPE"},
            }},

            # Other
            "FOB": {"type": "STRTYPE", "max_length": 13},
            "Other": {"type": "STRTYPE", "max_length": 29},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # ESTIMATE (EstimateRet)
    # =========================================================================
    "Estimate": {
        "description": "Estimates/Quotes",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 11},
            "TxnDate": {"type": "DATETYPE"},
            "DueDate": {"type": "DATETYPE"},
            "ExpirationDate": {"type": "DATETYPE"},
            "Subtotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxTotal": {"type": "AMTTYPE", "readonly": True},
            "TotalAmount": {"type": "AMTTYPE", "readonly": True},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsActive": {"type": "BOOLTYPE"},
            "IsToBeEmailed": {"type": "BOOLTYPE"},
            "IsToBePrinted": {"type": "BOOLTYPE"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "PONumber": {"type": "STRTYPE", "max_length": 25},
            "FOB": {"type": "STRTYPE", "max_length": 13},
            "ExchangeRate": {"type": "FLOATTYPE"},

            # References
            "CustomerRef": {"type": "REF", "required": True},
            "ClassRef": {"type": "REF"},
            "TemplateRef": {"type": "REF"},
            "TermsRef": {"type": "REF"},
            "SalesRepRef": {"type": "REF"},
            "ItemSalesTaxRef": {"type": "REF"},
            "CustomerMsgRef": {"type": "REF"},
            "CustomerSalesTaxCodeRef": {"type": "REF"},
            "CurrencyRef": {"type": "REF"},

            # Addresses
            "BillAddress": {"type": "ADDRESS"},
            "ShipAddress": {"type": "ADDRESS"},

            # Line Items
            "EstimateLineRet": {"type": "LIST", "nested": {
                "TxnLineID": {"type": "IDTYPE"},
                "ItemRef": {"type": "REF"},
                "Desc": {"type": "STRTYPE"},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE"},
                "Rate": {"type": "PRICETYPE"},
                "RatePercent": {"type": "PERCENTTYPE"},
                "ClassRef": {"type": "REF"},
                "Amount": {"type": "AMTTYPE"},
                "InventorySiteRef": {"type": "REF"},
                "SalesTaxCodeRef": {"type": "REF"},
                "MarkupRate": {"type": "PRICETYPE"},
                "MarkupRatePercent": {"type": "PERCENTTYPE"},
                "Other1": {"type": "STRTYPE"},
                "Other2": {"type": "STRTYPE"},
                "DataExtRet": {"type": "LIST"},
            }},

            # Linked Transactions
            "LinkedTxn": {"type": "LIST"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # ITEM TYPES
    # =========================================================================
    "ItemService": {
        "description": "Service items",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},

            # Parent
            "ParentRef": {"type": "REF"},

            # Unit of Measure
            "UnitOfMeasureSetRef": {"type": "REF"},
            "ForceUOMChange": {"type": "BOOLTYPE"},

            # Sales Info
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "SalesTaxCodeRef": {"type": "REF"},

            # Sales OR Purchase (mutually exclusive)
            "SalesOrPurchase": {"type": "OBJECT", "nested": {
                "Desc": {"type": "STRTYPE", "max_length": 4095},
                "Price": {"type": "PRICETYPE"},
                "PricePercent": {"type": "PERCENTTYPE"},
                "AccountRef": {"type": "REF"},
            }},

            # Sales AND Purchase (both)
            "SalesAndPurchase": {"type": "OBJECT", "nested": {
                "SalesDesc": {"type": "STRTYPE", "max_length": 4095},
                "SalesPrice": {"type": "PRICETYPE"},
                "IncomeAccountRef": {"type": "REF"},
                "PurchaseDesc": {"type": "STRTYPE", "max_length": 4095},
                "PurchaseCost": {"type": "PRICETYPE"},
                "PurchaseTaxCodeRef": {"type": "REF"},
                "ExpenseAccountRef": {"type": "REF"},
                "PrefVendorRef": {"type": "REF"},
            }},

            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemInventory": {
        "description": "Inventory items with tracking",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
            "ClassRef": {"type": "REF"},
            "ParentRef": {"type": "REF"},
            "ManufacturerPartNumber": {"type": "STRTYPE", "max_length": 31},
            "UnitOfMeasureSetRef": {"type": "REF"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "SalesTaxCodeRef": {"type": "REF"},

            # Sales Info
            "SalesDesc": {"type": "STRTYPE", "max_length": 4095},
            "SalesPrice": {"type": "PRICETYPE"},
            "IncomeAccountRef": {"type": "REF"},

            # Purchase Info
            "PurchaseDesc": {"type": "STRTYPE", "max_length": 4095},
            "PurchaseCost": {"type": "PRICETYPE"},
            "PurchaseTaxCodeRef": {"type": "REF"},
            "COGSAccountRef": {"type": "REF"},
            "PrefVendorRef": {"type": "REF"},

            # Inventory Tracking
            "AssetAccountRef": {"type": "REF"},
            "ReorderPoint": {"type": "QUANTYPE"},
            "Max": {"type": "QUANTYPE"},
            "QuantityOnHand": {"type": "QUANTYPE", "readonly": True},
            "AverageCost": {"type": "PRICETYPE", "readonly": True},
            "QuantityOnOrder": {"type": "QUANTYPE", "readonly": True},
            "QuantityOnSalesOrder": {"type": "QUANTYPE", "readonly": True},

            # Advanced Inventory (Enterprise)
            "IsSerialOrLotPreassigned": {"type": "ENUMTYPE", "values": ["None", "SerialNumber", "LotNumber"]},
            "InventorySiteRef": {"type": "REF"},
            "InventorySiteLocationRef": {"type": "REF"},

            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemNonInventory": {
        "description": "Non-inventory items (not tracked)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "ClassRef": {"type": "REF"},
            "ManufacturerPartNumber": {"type": "STRTYPE", "max_length": 31},
            "UnitOfMeasureSetRef": {"type": "REF"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "SalesTaxCodeRef": {"type": "REF"},
            "SalesOrPurchase": {"type": "OBJECT"},
            "SalesAndPurchase": {"type": "OBJECT"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemOtherCharge": {
        "description": "Other charge items (shipping, handling, etc.)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "ClassRef": {"type": "REF"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "SalesTaxCodeRef": {"type": "REF"},
            "SalesOrPurchase": {"type": "OBJECT"},
            "SalesAndPurchase": {"type": "OBJECT"},
            "SpecialItemType": {"type": "ENUMTYPE", "values": ["FinanceCharge", "ReimbursableExpenseGroup", "ReimbursableExpenseSubtotal"]},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemDiscount": {
        "description": "Discount items",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "ItemDesc": {"type": "STRTYPE", "max_length": 4095},
            "SalesTaxCodeRef": {"type": "REF"},
            "DiscountRate": {"type": "PRICETYPE"},
            "DiscountRatePercent": {"type": "PERCENTTYPE"},
            "AccountRef": {"type": "REF"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemGroup": {
        "description": "Group items (bundle of items)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ItemDesc": {"type": "STRTYPE", "max_length": 4095},
            "UnitOfMeasureSetRef": {"type": "REF"},
            "ForceUOMChange": {"type": "BOOLTYPE"},
            "IsPrintItemsInGroup": {"type": "BOOLTYPE"},
            "SpecialItemType": {"type": "ENUMTYPE"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "ItemGroupLine": {"type": "LIST", "nested": {
                "ItemRef": {"type": "REF"},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE"},
            }},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemSubtotal": {
        "description": "Subtotal items",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ItemDesc": {"type": "STRTYPE", "max_length": 4095},
            "SpecialItemType": {"type": "ENUMTYPE"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemSalesTax": {
        "description": "Sales tax items",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ClassRef": {"type": "REF"},
            "ItemDesc": {"type": "STRTYPE", "max_length": 4095},
            "TaxRate": {"type": "PERCENTTYPE"},
            "TaxVendorRef": {"type": "REF"},
            "SalesTaxReturnLineRef": {"type": "REF"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    "ItemSalesTaxGroup": {
        "description": "Sales tax group (combined tax rates)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "BarCodeValue": {"type": "STRTYPE", "max_length": 50},
            "IsActive": {"type": "BOOLTYPE"},
            "ItemDesc": {"type": "STRTYPE", "max_length": 4095},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "ItemSalesTaxRef": {"type": "LIST", "nested": {"ListID": {"type": "IDTYPE"}, "FullName": {"type": "STRTYPE"}}},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # SALES ORDER (SalesOrderRet)
    # =========================================================================
    "SalesOrder": {
        "description": "Sales orders",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 11},
            "TxnDate": {"type": "DATETYPE"},
            "DueDate": {"type": "DATETYPE"},
            "ShipDate": {"type": "DATETYPE"},
            "PONumber": {"type": "STRTYPE", "max_length": 25},
            "Subtotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxTotal": {"type": "AMTTYPE", "readonly": True},
            "TotalAmount": {"type": "AMTTYPE", "readonly": True},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsManuallyClosed": {"type": "BOOLTYPE"},
            "IsFullyInvoiced": {"type": "BOOLTYPE", "readonly": True},
            "IsToBePrinted": {"type": "BOOLTYPE"},
            "IsToBeEmailed": {"type": "BOOLTYPE"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},

            # References (same as Invoice)
            "CustomerRef": {"type": "REF", "required": True},
            "ClassRef": {"type": "REF"},
            "TemplateRef": {"type": "REF"},
            "TermsRef": {"type": "REF"},
            "SalesRepRef": {"type": "REF"},
            "ShipMethodRef": {"type": "REF"},
            "ItemSalesTaxRef": {"type": "REF"},
            "CustomerMsgRef": {"type": "REF"},
            "CustomerSalesTaxCodeRef": {"type": "REF"},
            "CurrencyRef": {"type": "REF"},

            # Addresses
            "BillAddress": {"type": "ADDRESS"},
            "ShipAddress": {"type": "ADDRESS"},

            # Line Items
            "SalesOrderLineRet": {"type": "LIST"},
            "SalesOrderLineGroupRet": {"type": "LIST"},
            "LinkedTxn": {"type": "LIST"},
            "DataExtRet": {"type": "LIST"},

            "FOB": {"type": "STRTYPE", "max_length": 13},
            "Other": {"type": "STRTYPE", "max_length": 29},
            "ExternalGUID": {"type": "GUIDTYPE"},
        }
    },

    # =========================================================================
    # PURCHASE ORDER (PurchaseOrderRet)
    # =========================================================================
    "PurchaseOrder": {
        "description": "Purchase orders",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 11},
            "TxnDate": {"type": "DATETYPE"},
            "DueDate": {"type": "DATETYPE"},
            "ExpectedDate": {"type": "DATETYPE"},
            "ShipDate": {"type": "DATETYPE"},
            "Subtotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxTotal": {"type": "AMTTYPE", "readonly": True},
            "TotalAmount": {"type": "AMTTYPE", "readonly": True},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsManuallyClosed": {"type": "BOOLTYPE"},
            "IsFullyReceived": {"type": "BOOLTYPE", "readonly": True},
            "IsToBePrinted": {"type": "BOOLTYPE"},
            "IsToBeEmailed": {"type": "BOOLTYPE"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},

            # References
            "VendorRef": {"type": "REF", "required": True},
            "ClassRef": {"type": "REF"},
            "InventorySiteRef": {"type": "REF"},
            "ShipToEntityRef": {"type": "REF"},
            "TemplateRef": {"type": "REF"},
            "TermsRef": {"type": "REF"},
            "ShipMethodRef": {"type": "REF"},
            "VendorTaxCodeRef": {"type": "REF"},
            "CurrencyRef": {"type": "REF"},

            # Addresses
            "VendorAddress": {"type": "ADDRESS"},
            "ShipAddress": {"type": "ADDRESS"},

            # Line Items
            "PurchaseOrderLineRet": {"type": "LIST", "nested": {
                "TxnLineID": {"type": "IDTYPE"},
                "ItemRef": {"type": "REF"},
                "ManufacturerPartNumber": {"type": "STRTYPE"},
                "Desc": {"type": "STRTYPE"},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE"},
                "Rate": {"type": "PRICETYPE"},
                "ClassRef": {"type": "REF"},
                "Amount": {"type": "AMTTYPE"},
                "InventorySiteLocationRef": {"type": "REF"},
                "CustomerRef": {"type": "REF"},
                "ServiceDate": {"type": "DATETYPE"},
                "SalesTaxCodeRef": {"type": "REF"},
                "IsManuallyClosed": {"type": "BOOLTYPE"},
                "ReceivedQuantity": {"type": "QUANTYPE", "readonly": True},
                "UnbilledQuantity": {"type": "QUANTYPE", "readonly": True},
                "IsBilled": {"type": "BOOLTYPE", "readonly": True},
                "Other1": {"type": "STRTYPE"},
                "Other2": {"type": "STRTYPE"},
                "DataExtRet": {"type": "LIST"},
            }},

            "PurchaseOrderLineGroupRet": {"type": "LIST"},
            "LinkedTxn": {"type": "LIST"},
            "DataExtRet": {"type": "LIST"},

            "FOB": {"type": "STRTYPE", "max_length": 13},
            "Other1": {"type": "STRTYPE", "max_length": 29},
            "Other2": {"type": "STRTYPE", "max_length": 29},
            "ExternalGUID": {"type": "GUIDTYPE"},
        }
    },

    # =========================================================================
    # BILL (BillRet)
    # =========================================================================
    "Bill": {
        "description": "Vendor bills/invoices received",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 20},
            "TxnDate": {"type": "DATETYPE"},
            "DueDate": {"type": "DATETYPE"},
            "AmountDue": {"type": "AMTTYPE", "readonly": True},
            "OpenAmount": {"type": "AMTTYPE", "readonly": True},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsPaid": {"type": "BOOLTYPE", "readonly": True},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "ExchangeRate": {"type": "FLOATTYPE"},

            # References
            "VendorRef": {"type": "REF", "required": True},
            "APAccountRef": {"type": "REF"},
            "TermsRef": {"type": "REF"},
            "SalesTaxCodeRef": {"type": "REF"},
            "CurrencyRef": {"type": "REF"},

            # Addresses
            "VendorAddress": {"type": "ADDRESS"},

            # Line Items (Expense or Item)
            "ExpenseLineRet": {"type": "LIST", "nested": {
                "TxnLineID": {"type": "IDTYPE"},
                "AccountRef": {"type": "REF"},
                "Amount": {"type": "AMTTYPE"},
                "Memo": {"type": "STRTYPE"},
                "CustomerRef": {"type": "REF"},
                "ClassRef": {"type": "REF"},
                "SalesTaxCodeRef": {"type": "REF"},
                "BillableStatus": {"type": "ENUMTYPE", "values": ["Billable", "NotBillable", "HasBeenBilled"]},
                "DataExtRet": {"type": "LIST"},
            }},
            "ItemLineRet": {"type": "LIST", "nested": {
                "TxnLineID": {"type": "IDTYPE"},
                "ItemRef": {"type": "REF"},
                "InventorySiteRef": {"type": "REF"},
                "InventorySiteLocationRef": {"type": "REF"},
                "SerialNumber": {"type": "STRTYPE"},
                "LotNumber": {"type": "STRTYPE"},
                "Desc": {"type": "STRTYPE"},
                "Quantity": {"type": "QUANTYPE"},
                "UnitOfMeasure": {"type": "STRTYPE"},
                "Cost": {"type": "PRICETYPE"},
                "Amount": {"type": "AMTTYPE"},
                "CustomerRef": {"type": "REF"},
                "ClassRef": {"type": "REF"},
                "SalesTaxCodeRef": {"type": "REF"},
                "BillableStatus": {"type": "ENUMTYPE"},
                "OverrideItemAccountRef": {"type": "REF"},
                "LinkToTxn": {"type": "LIST", "nested": {"TxnID": {"type": "IDTYPE"}, "TxnLineID": {"type": "IDTYPE"}}},
                "DataExtRet": {"type": "LIST"},
            }},
            "ItemGroupLineRet": {"type": "LIST"},

            "LinkedTxn": {"type": "LIST"},
            "OpenAmount": {"type": "AMTTYPE", "readonly": True},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # PAYMENT (ReceivePaymentRet)
    # =========================================================================
    "ReceivePayment": {
        "description": "Customer payments received",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 20},
            "TxnDate": {"type": "DATETYPE"},
            "TotalAmount": {"type": "AMTTYPE"},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "UnusedPayment": {"type": "AMTTYPE", "readonly": True},
            "UnusedCredits": {"type": "AMTTYPE", "readonly": True},
            "ExchangeRate": {"type": "FLOATTYPE"},

            # References
            "CustomerRef": {"type": "REF", "required": True},
            "ARAccountRef": {"type": "REF"},
            "PaymentMethodRef": {"type": "REF"},
            "DepositToAccountRef": {"type": "REF"},
            "CreditCardTxnInfo": {"type": "OBJECT", "nested": {
                "CreditCardTxnInputInfo": {"type": "OBJECT"},
                "CreditCardTxnResultInfo": {"type": "OBJECT"},
            }},
            "CurrencyRef": {"type": "REF"},

            # Applied to Transactions
            "AppliedToTxnRet": {"type": "LIST", "nested": {
                "TxnID": {"type": "IDTYPE"},
                "TxnType": {"type": "ENUMTYPE"},
                "TxnDate": {"type": "DATETYPE"},
                "RefNumber": {"type": "STRTYPE"},
                "BalanceRemaining": {"type": "AMTTYPE"},
                "Amount": {"type": "AMTTYPE"},
                "DiscountAmount": {"type": "AMTTYPE"},
                "DiscountAccountRef": {"type": "REF"},
                "DiscountClassRef": {"type": "REF"},
                "LinkedTxn": {"type": "LIST"},
            }},

            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # CREDIT MEMO (CreditMemoRet)
    # =========================================================================
    "CreditMemo": {
        "description": "Credit memos to customers",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnNumber": {"type": "INTTYPE", "readonly": True},
            "RefNumber": {"type": "STRTYPE", "max_length": 11},
            "TxnDate": {"type": "DATETYPE"},
            "Subtotal": {"type": "AMTTYPE", "readonly": True},
            "SalesTaxTotal": {"type": "AMTTYPE", "readonly": True},
            "TotalCredit": {"type": "AMTTYPE", "readonly": True},
            "CreditRemaining": {"type": "AMTTYPE", "readonly": True},
            "Memo": {"type": "STRTYPE", "max_length": 4095},
            "IsPending": {"type": "BOOLTYPE"},
            "IsToBePrinted": {"type": "BOOLTYPE"},
            "IsToBeEmailed": {"type": "BOOLTYPE"},
            "IsTaxIncluded": {"type": "BOOLTYPE"},
            "PONumber": {"type": "STRTYPE", "max_length": 25},
            "ExchangeRate": {"type": "FLOATTYPE"},

            # References
            "CustomerRef": {"type": "REF", "required": True},
            "ClassRef": {"type": "REF"},
            "ARAccountRef": {"type": "REF"},
            "TemplateRef": {"type": "REF"},
            "SalesRepRef": {"type": "REF"},
            "ItemSalesTaxRef": {"type": "REF"},
            "CustomerMsgRef": {"type": "REF"},
            "CustomerSalesTaxCodeRef": {"type": "REF"},
            "CurrencyRef": {"type": "REF"},

            # Addresses
            "BillAddress": {"type": "ADDRESS"},
            "ShipAddress": {"type": "ADDRESS"},

            # Line Items
            "CreditMemoLineRet": {"type": "LIST"},
            "CreditMemoLineGroupRet": {"type": "LIST"},
            "LinkedTxn": {"type": "LIST"},

            "FOB": {"type": "STRTYPE", "max_length": 13},
            "Other": {"type": "STRTYPE", "max_length": 29},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # ACCOUNT (AccountRet)
    # =========================================================================
    "Account": {
        "description": "Chart of Accounts",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "IsActive": {"type": "BOOLTYPE"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
            "ParentRef": {"type": "REF"},
            "AccountType": {"type": "ENUMTYPE", "values": [
                "AccountsPayable", "AccountsReceivable", "Bank", "CostOfGoodsSold",
                "CreditCard", "Equity", "Expense", "FixedAsset", "Income",
                "LongTermLiability", "NonPosting", "OtherAsset", "OtherCurrentAsset",
                "OtherCurrentLiability", "OtherExpense", "OtherIncome"
            ]},
            "SpecialAccountType": {"type": "ENUMTYPE", "values": [
                "AccountsPayable", "AccountsReceivable", "CondenseItemAdjustmentExpenses",
                "CostOfGoodsSold", "DirectDepositLiabilities", "Estimates", "ExchangeGainLoss",
                "InventoryAssets", "ItemReceiptAccount", "OpeningBalanceEquity",
                "PayrollExpenses", "PayrollLiabilities", "PettyCash", "PurchaseOrders",
                "ReconciliationDifferences", "RetainedEarnings", "SalesOrders",
                "SalesTaxPayable", "UncategorizedExpenses", "UncategorizedIncome",
                "UndepositedFunds"
            ]},
            "AccountNumber": {"type": "STRTYPE", "max_length": 7},
            "BankNumber": {"type": "STRTYPE", "max_length": 25},
            "Desc": {"type": "STRTYPE", "max_length": 200},
            "Balance": {"type": "AMTTYPE", "readonly": True},
            "TotalBalance": {"type": "AMTTYPE", "readonly": True},
            "OpenBalance": {"type": "AMTTYPE"},
            "OpenBalanceDate": {"type": "DATETYPE"},
            "SalesTaxCodeRef": {"type": "REF"},
            "TaxLineID": {"type": "INTTYPE"},
            "TaxLineInfoRet": {"type": "OBJECT", "readonly": True},
            "CashFlowClassification": {"type": "ENUMTYPE", "values": ["None", "Operating", "Investing", "Financing", "NotApplicable"]},
            "CurrencyRef": {"type": "REF"},
            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # CLASS (ClassRet) - Job Costing
    # =========================================================================
    "Class": {
        "description": "Classes for job costing/departmental tracking",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "IsActive": {"type": "BOOLTYPE"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
            "ParentRef": {"type": "REF"},
            "ExternalGUID": {"type": "GUIDTYPE"},
        }
    },

    # =========================================================================
    # EMPLOYEE (EmployeeRet)
    # =========================================================================
    "Employee": {
        "description": "Employees",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 41, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "Salutation": {"type": "STRTYPE", "max_length": 15},
            "FirstName": {"type": "STRTYPE", "max_length": 25},
            "MiddleName": {"type": "STRTYPE", "max_length": 5},
            "LastName": {"type": "STRTYPE", "max_length": 25},
            "Suffix": {"type": "STRTYPE", "max_length": 10},
            "JobTitle": {"type": "STRTYPE", "max_length": 41},
            "PrintAs": {"type": "STRTYPE", "max_length": 41},
            "Phone": {"type": "STRTYPE", "max_length": 21},
            "Mobile": {"type": "STRTYPE", "max_length": 21},
            "Pager": {"type": "STRTYPE", "max_length": 21},
            "PagerPIN": {"type": "STRTYPE", "max_length": 10},
            "AltPhone": {"type": "STRTYPE", "max_length": 21},
            "Fax": {"type": "STRTYPE", "max_length": 21},
            "Email": {"type": "STRTYPE", "max_length": 1023},
            "SSN": {"type": "STRTYPE", "max_length": 11, "description": "Social Security Number"},
            "HiredDate": {"type": "DATETYPE"},
            "ReleasedDate": {"type": "DATETYPE"},
            "BirthDate": {"type": "DATETYPE"},
            "Gender": {"type": "ENUMTYPE", "values": ["Male", "Female"]},
            "AccountNumber": {"type": "STRTYPE", "max_length": 99},
            "Notes": {"type": "STRTYPE", "max_length": 4095},
            "BillingRateRef": {"type": "REF"},
            "EmployeeType": {"type": "ENUMTYPE", "values": ["Officer", "Owner", "Regular", "Statutory"]},

            # Address
            "EmployeeAddress": {"type": "ADDRESS"},

            # Emergency Contact
            "EmergencyContacts": {"type": "LIST", "nested": {
                "PrimaryContact": {"type": "OBJECT"},
                "SecondaryContact": {"type": "OBJECT"},
            }},

            # Payroll Info
            "EmployeePayrollInfo": {"type": "OBJECT", "nested": {
                "PayPeriod": {"type": "ENUMTYPE", "values": ["Daily", "Weekly", "Biweekly", "Semimonthly", "Monthly", "Quarterly", "Yearly"]},
                "ClassRef": {"type": "REF"},
                "ClearEarnings": {"type": "BOOLTYPE"},
                "Earnings": {"type": "LIST"},
                "UseTimeDataToCreatePaychecks": {"type": "ENUMTYPE"},
                "SickHours": {"type": "OBJECT"},
                "VacationHours": {"type": "OBJECT"},
            }},

            "ExternalGUID": {"type": "GUIDTYPE"},
            "DataExtRet": {"type": "LIST"},
        }
    },

    # =========================================================================
    # TIME TRACKING (TimeTrackingRet)
    # =========================================================================
    "TimeTracking": {
        "description": "Time tracking entries",
        "list_type": False,
        "id_field": "TxnID",
        "fields": {
            "TxnID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "TxnDate": {"type": "DATETYPE"},
            "EntityRef": {"type": "REF", "description": "Employee or Vendor"},
            "CustomerRef": {"type": "REF"},
            "ItemServiceRef": {"type": "REF"},
            "Rate": {"type": "PRICETYPE"},
            "Duration": {"type": "DURATIONTYPE", "description": "Time in minutes"},
            "ClassRef": {"type": "REF"},
            "PayrollItemWageRef": {"type": "REF"},
            "Notes": {"type": "STRTYPE", "max_length": 4095},
            "BillableStatus": {"type": "ENUMTYPE", "values": ["Billable", "NotBillable", "HasBeenBilled"]},
            "IsBillable": {"type": "BOOLTYPE"},
            "IsBilled": {"type": "BOOLTYPE", "readonly": True},
            "ExternalGUID": {"type": "GUIDTYPE"},
        }
    },

    # =========================================================================
    # COMPANY INFO (CompanyRet)
    # =========================================================================
    "Company": {
        "description": "Company file information",
        "list_type": False,
        "fields": {
            "CompanyName": {"type": "STRTYPE"},
            "LegalCompanyName": {"type": "STRTYPE"},
            "Address": {"type": "ADDRESS"},
            "AddressBlock": {"type": "ADDRESSBLOCK"},
            "LegalAddress": {"type": "ADDRESS"},
            "Phone": {"type": "STRTYPE"},
            "Fax": {"type": "STRTYPE"},
            "Email": {"type": "STRTYPE"},
            "Website": {"type": "STRTYPE"},
            "FirstMonthFiscalYear": {"type": "ENUMTYPE", "values": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
            "FirstMonthIncomeTaxYear": {"type": "ENUMTYPE"},
            "CompanyType": {"type": "STRTYPE"},
            "EIN": {"type": "STRTYPE", "description": "Employer ID Number"},
            "SSN": {"type": "STRTYPE"},
            "TaxForm": {"type": "ENUMTYPE"},
            "SubscribedServices": {"type": "OBJECT"},
            "AccountantCopy": {"type": "OBJECT"},
            "PayrollServiceActivityDate": {"type": "DATETYPE"},
        }
    },

    # =========================================================================
    # TERMS (TermsRet)
    # =========================================================================
    "Terms": {
        "description": "Payment terms (Net 30, etc.)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "IsActive": {"type": "BOOLTYPE"},

            # Standard Terms
            "StdDueDays": {"type": "INTTYPE"},
            "StdDiscountDays": {"type": "INTTYPE"},
            "DiscountPct": {"type": "PERCENTTYPE"},

            # Date Driven Terms
            "DueDateOffset": {"type": "INTTYPE"},
            "DiscountDateOffset": {"type": "INTTYPE"},
            "DueDateOfMonth": {"type": "INTTYPE"},
            "DiscountDayOfMonth": {"type": "INTTYPE"},
        }
    },

    # =========================================================================
    # CUSTOMER TYPE (CustomerTypeRet)
    # =========================================================================
    "CustomerType": {
        "description": "Customer type categories",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
        }
    },

    # =========================================================================
    # VENDOR TYPE (VendorTypeRet)
    # =========================================================================
    "VendorType": {
        "description": "Vendor type categories",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
        }
    },

    # =========================================================================
    # JOB TYPE (JobTypeRet)
    # =========================================================================
    "JobType": {
        "description": "Job type categories",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "FullName": {"type": "STRTYPE", "readonly": True},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentRef": {"type": "REF"},
            "Sublevel": {"type": "INTTYPE", "readonly": True},
        }
    },

    # =========================================================================
    # PAYMENT METHOD (PaymentMethodRet)
    # =========================================================================
    "PaymentMethod": {
        "description": "Payment methods (Check, Cash, Credit Card, etc.)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "PaymentMethodType": {"type": "ENUMTYPE", "values": ["AmericanExpress", "Cash", "Check", "DebitCard", "Discover", "ECheck", "GiftCard", "MasterCard", "Other", "OtherCreditCard", "Visa"]},
        }
    },

    # =========================================================================
    # SHIP METHOD (ShipMethodRet)
    # =========================================================================
    "ShipMethod": {
        "description": "Shipping methods",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 15, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
        }
    },

    # =========================================================================
    # SALES TAX CODE (SalesTaxCodeRet)
    # =========================================================================
    "SalesTaxCode": {
        "description": "Sales tax codes (Taxable/Non-taxable)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 3, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "IsTaxable": {"type": "BOOLTYPE"},
            "Desc": {"type": "STRTYPE", "max_length": 31},
            "ItemPurchaseTaxRef": {"type": "REF"},
            "ItemSalesTaxRef": {"type": "REF"},
        }
    },

    # =========================================================================
    # PRICE LEVEL (PriceLevelRet)
    # =========================================================================
    "PriceLevel": {
        "description": "Price levels for volume discounts",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "PriceLevelType": {"type": "ENUMTYPE", "values": ["FixedPercentage", "PerItem"]},
            "PriceLevelFixedPercentage": {"type": "PERCENTTYPE"},
            "PriceLevelPerItemRet": {"type": "LIST", "nested": {
                "ItemRef": {"type": "REF"},
                "CustomPrice": {"type": "PRICETYPE"},
                "CustomPricePercent": {"type": "PERCENTTYPE"},
            }},
            "CurrencyRef": {"type": "REF"},
        }
    },

    # =========================================================================
    # SALES REP (SalesRepRet)
    # =========================================================================
    "SalesRep": {
        "description": "Sales representatives",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Initial": {"type": "STRTYPE", "max_length": 5, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "SalesRepEntityRef": {"type": "REF"},
        }
    },

    # =========================================================================
    # CURRENCY (CurrencyRet) - Multi-currency
    # =========================================================================
    "Currency": {
        "description": "Currency definitions (multi-currency)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 64, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "CurrencyCode": {"type": "STRTYPE", "max_length": 3},
            "CurrencyFormat": {"type": "OBJECT", "nested": {
                "ThousandSeparator": {"type": "ENUMTYPE", "values": ["Comma", "Period", "Space", "Apostrophe"]},
                "ThousandSeparatorGrouping": {"type": "ENUMTYPE", "values": ["XX_XXX_XXX", "X_XX_XX_XXX"]},
                "DecimalPlaces": {"type": "ENUMTYPE", "values": ["0", "2"]},
                "DecimalSeparator": {"type": "ENUMTYPE", "values": ["Period", "Comma"]},
            }},
            "IsUserDefinedCurrency": {"type": "BOOLTYPE"},
            "ExchangeRate": {"type": "FLOATTYPE"},
            "AsOfDate": {"type": "DATETYPE"},
        }
    },

    # =========================================================================
    # INVENTORY SITE (InventorySiteRet) - Enterprise
    # =========================================================================
    "InventorySite": {
        "description": "Inventory locations (Enterprise)",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "ParentSiteRef": {"type": "REF"},
            "IsDefaultSite": {"type": "BOOLTYPE"},
            "Desc": {"type": "STRTYPE", "max_length": 200},
            "Contact": {"type": "STRTYPE", "max_length": 41},
            "Phone": {"type": "STRTYPE", "max_length": 21},
            "Fax": {"type": "STRTYPE", "max_length": 21},
            "Email": {"type": "STRTYPE", "max_length": 1023},
            "SiteAddress": {"type": "ADDRESS"},
        }
    },

    # =========================================================================
    # UNIT OF MEASURE SET (UnitOfMeasureSetRet)
    # =========================================================================
    "UnitOfMeasureSet": {
        "description": "Unit of measure definitions",
        "list_type": True,
        "id_field": "ListID",
        "fields": {
            "ListID": {"type": "IDTYPE", "readonly": True},
            "TimeCreated": {"type": "DATETIMETYPE", "readonly": True},
            "TimeModified": {"type": "DATETIMETYPE", "readonly": True},
            "EditSequence": {"type": "STRTYPE", "readonly": True},
            "Name": {"type": "STRTYPE", "max_length": 31, "required": True},
            "IsActive": {"type": "BOOLTYPE"},
            "UnitOfMeasureType": {"type": "ENUMTYPE", "values": ["Area", "Count", "Length", "Other", "Time", "Volume", "Weight"]},
            "BaseUnit": {"type": "OBJECT", "nested": {
                "Name": {"type": "STRTYPE", "max_length": 31},
                "Abbreviation": {"type": "STRTYPE", "max_length": 31},
            }},
            "RelatedUnit": {"type": "LIST", "nested": {
                "Name": {"type": "STRTYPE", "max_length": 31},
                "Abbreviation": {"type": "STRTYPE", "max_length": 31},
                "ConversionRatio": {"type": "FLOATTYPE"},
            }},
            "DefaultUnit": {"type": "OBJECT", "nested": {
                "UnitUsedFor": {"type": "ENUMTYPE", "values": ["Purchase", "Sales", "Shipping"]},
                "Unit": {"type": "STRTYPE"},
            }},
        }
    },
}

# =============================================================================
# DATA TYPES REFERENCE
# =============================================================================

QB_DATA_TYPES = {
    "IDTYPE": {
        "description": "QuickBooks unique identifier (GUID format)",
        "example": "80000001-1234567890",
        "python_type": "str"
    },
    "STRTYPE": {
        "description": "String value",
        "python_type": "str"
    },
    "BOOLTYPE": {
        "description": "Boolean value",
        "values": ["true", "false"],
        "python_type": "bool"
    },
    "INTTYPE": {
        "description": "Integer value",
        "python_type": "int"
    },
    "FLOATTYPE": {
        "description": "Floating point number",
        "python_type": "float"
    },
    "AMTTYPE": {
        "description": "Monetary amount (up to 2 decimal places)",
        "format": "XXXX.XX",
        "python_type": "Decimal"
    },
    "PRICETYPE": {
        "description": "Price value (up to 5 decimal places)",
        "format": "XXXX.XXXXX",
        "python_type": "Decimal"
    },
    "PERCENTTYPE": {
        "description": "Percentage value",
        "format": "XX.XX",
        "python_type": "Decimal"
    },
    "QUANTYPE": {
        "description": "Quantity value (up to 5 decimal places)",
        "format": "XXXX.XXXXX",
        "python_type": "Decimal"
    },
    "DATETYPE": {
        "description": "Date value",
        "format": "YYYY-MM-DD",
        "python_type": "date"
    },
    "DATETIMETYPE": {
        "description": "Date and time value",
        "format": "YYYY-MM-DDTHH:MM:SS",
        "python_type": "datetime"
    },
    "DURATIONTYPE": {
        "description": "Duration in format PT#H#M#S",
        "format": "PT8H30M0S",
        "python_type": "timedelta"
    },
    "GUIDTYPE": {
        "description": "External GUID for integration",
        "format": "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}",
        "python_type": "str"
    },
    "ENUMTYPE": {
        "description": "Enumeration value (one of predefined options)",
        "python_type": "str"
    },
    "REF": {
        "description": "Reference to another entity (contains ListID and/or FullName)",
        "python_type": "dict"
    },
    "ADDRESS": {
        "description": "Address structure with Addr1-5, City, State, PostalCode, Country, Note",
        "python_type": "dict"
    },
    "ADDRESSBLOCK": {
        "description": "Formatted address block for printing",
        "python_type": "dict"
    },
    "LIST": {
        "description": "List of items (can repeat)",
        "python_type": "list"
    },
    "OBJECT": {
        "description": "Nested object structure",
        "python_type": "dict"
    },
}


def print_schema_summary():
    """Print a summary of all entities and their field counts"""
    print("=" * 70)
    print("QUICKBOOKS DESKTOP - COMPLETE FIELD SCHEMA")
    print("qbXML SDK 16.0 for QuickBooks Enterprise")
    print("=" * 70)
    print()

    total_fields = 0
    for entity, data in QB_SCHEMA.items():
        field_count = len(data.get('fields', {}))
        total_fields += field_count
        entity_type = "List" if data.get('list_type') else "Transaction"
        id_field = data.get('id_field', 'N/A')
        print(f"{entity:25} | {entity_type:12} | ID: {id_field:8} | {field_count:3} fields")

    print("-" * 70)
    print(f"Total Entities: {len(QB_SCHEMA)}")
    print(f"Total Fields: {total_fields}")
    print()


def get_entity_schema(entity_name):
    """Get detailed schema for a specific entity"""
    return QB_SCHEMA.get(entity_name)


def export_schema_to_json():
    """Export the complete schema to JSON"""
    import json
    return json.dumps({
        "entities": QB_SCHEMA,
        "data_types": QB_DATA_TYPES
    }, indent=2)


if __name__ == "__main__":
    print_schema_summary()

    # Print detailed Customer schema as example
    print("\n" + "=" * 70)
    print("EXAMPLE: CUSTOMER ENTITY DETAILED SCHEMA")
    print("=" * 70)
    customer = QB_SCHEMA["Customer"]
    print(f"\nDescription: {customer['description']}")
    print(f"ID Field: {customer['id_field']}")
    print(f"\nFields ({len(customer['fields'])}):")
    for field_name, field_info in customer['fields'].items():
        field_type = field_info['type']
        max_len = field_info.get('max_length', '')
        desc = field_info.get('description', '')
        required = " [REQUIRED]" if field_info.get('required') else ""
        readonly = " [READONLY]" if field_info.get('readonly') else ""
        print(f"  {field_name:35} {field_type:15} {f'max:{max_len}' if max_len else '':10} {desc}{required}{readonly}")
