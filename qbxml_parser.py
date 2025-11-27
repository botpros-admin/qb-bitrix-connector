"""
qbXML Response Parser for QuickBooks Desktop

This module parses qbXML responses from QuickBooks into Python dictionaries.
"""

from lxml import etree
from typing import List, Dict, Any, Optional


def parse_qbxml_response(xml_string: str) -> Dict[str, Any]:
    """
    Parse a qbXML response string into a Python dictionary.

    Returns a dict with:
    - 'success': bool
    - 'status_code': str
    - 'status_message': str
    - 'data': list of parsed entities
    """
    if not xml_string or not xml_string.strip():
        return {'success': False, 'status_code': '', 'status_message': 'Empty response', 'data': []}

    try:
        # Parse XML
        root = etree.fromstring(xml_string.encode('utf-8'))

        # Find the response element (e.g., CustomerQueryRs, InvoiceQueryRs)
        msgs_rs = root.find('.//QBXMLMsgsRs')
        if msgs_rs is None:
            return {'success': False, 'status_code': '', 'status_message': 'No QBXMLMsgsRs found', 'data': []}

        # Get the first response element
        response_elem = None
        for child in msgs_rs:
            if child.tag.endswith('Rs'):
                response_elem = child
                break

        if response_elem is None:
            return {'success': False, 'status_code': '', 'status_message': 'No response element found', 'data': []}

        # Get status
        status_code = response_elem.get('statusCode', '')
        status_message = response_elem.get('statusMessage', '')
        success = status_code == '0'

        # Parse data based on response type
        data = []
        response_type = response_elem.tag

        if 'CustomerQuery' in response_type or 'CustomerAdd' in response_type or 'CustomerMod' in response_type:
            data = parse_customers(response_elem)
        elif 'VendorQuery' in response_type or 'VendorAdd' in response_type:
            data = parse_vendors(response_elem)
        elif 'InvoiceQuery' in response_type or 'InvoiceAdd' in response_type:
            data = parse_invoices(response_elem)
        elif 'ItemQuery' in response_type or 'ItemInventoryQuery' in response_type:
            data = parse_items(response_elem)
        elif 'EstimateQuery' in response_type or 'EstimateAdd' in response_type:
            data = parse_estimates(response_elem)
        elif 'AccountQuery' in response_type:
            data = parse_accounts(response_elem)
        elif 'ClassQuery' in response_type:
            data = parse_classes(response_elem)
        elif 'CompanyQuery' in response_type:
            data = parse_company(response_elem)
        elif 'HostQuery' in response_type:
            data = parse_host(response_elem)
        else:
            # Generic parsing
            data = parse_generic(response_elem)

        return {
            'success': success,
            'status_code': status_code,
            'status_message': status_message,
            'data': data
        }

    except Exception as e:
        return {'success': False, 'status_code': '', 'status_message': str(e), 'data': []}


def element_to_dict(elem) -> Dict[str, Any]:
    """Convert an XML element and its children to a dictionary"""
    result = {}
    for child in elem:
        tag = child.tag
        if len(child) > 0:
            # Has children, recurse
            if tag.endswith('Ret') or tag.endswith('Ref') or tag.endswith('Line') or tag.endswith('Address'):
                value = element_to_dict(child)
            elif any(sibling.tag == tag for sibling in elem if sibling != child):
                # Multiple elements with same tag, make a list
                if tag not in result:
                    result[tag] = []
                result[tag].append(element_to_dict(child))
                continue
            else:
                value = element_to_dict(child)
        else:
            value = child.text
        result[tag] = value
    return result


def parse_customers(response_elem) -> List[Dict]:
    """Parse CustomerQueryRs / CustomerAddRs / CustomerModRs"""
    customers = []
    for customer_ret in response_elem.findall('.//CustomerRet'):
        customer = {
            'ListID': get_text(customer_ret, 'ListID'),
            'TimeCreated': get_text(customer_ret, 'TimeCreated'),
            'TimeModified': get_text(customer_ret, 'TimeModified'),
            'EditSequence': get_text(customer_ret, 'EditSequence'),
            'Name': get_text(customer_ret, 'Name'),
            'FullName': get_text(customer_ret, 'FullName'),
            'IsActive': get_text(customer_ret, 'IsActive'),
            'CompanyName': get_text(customer_ret, 'CompanyName'),
            'FirstName': get_text(customer_ret, 'FirstName'),
            'LastName': get_text(customer_ret, 'LastName'),
            'Email': get_text(customer_ret, 'Email'),
            'Phone': get_text(customer_ret, 'Phone'),
            'AltPhone': get_text(customer_ret, 'AltPhone'),
            'Fax': get_text(customer_ret, 'Fax'),
            'Balance': get_text(customer_ret, 'Balance'),
            'TotalBalance': get_text(customer_ret, 'TotalBalance'),
        }

        # Parse billing address
        bill_addr = customer_ret.find('.//BillAddress')
        if bill_addr is not None:
            customer['BillAddress'] = {
                'Addr1': get_text(bill_addr, 'Addr1'),
                'Addr2': get_text(bill_addr, 'Addr2'),
                'City': get_text(bill_addr, 'City'),
                'State': get_text(bill_addr, 'State'),
                'PostalCode': get_text(bill_addr, 'PostalCode'),
                'Country': get_text(bill_addr, 'Country'),
            }

        customers.append(customer)
    return customers


def parse_vendors(response_elem) -> List[Dict]:
    """Parse VendorQueryRs / VendorAddRs"""
    vendors = []
    for vendor_ret in response_elem.findall('.//VendorRet'):
        vendor = {
            'ListID': get_text(vendor_ret, 'ListID'),
            'TimeCreated': get_text(vendor_ret, 'TimeCreated'),
            'TimeModified': get_text(vendor_ret, 'TimeModified'),
            'EditSequence': get_text(vendor_ret, 'EditSequence'),
            'Name': get_text(vendor_ret, 'Name'),
            'IsActive': get_text(vendor_ret, 'IsActive'),
            'CompanyName': get_text(vendor_ret, 'CompanyName'),
            'FirstName': get_text(vendor_ret, 'FirstName'),
            'LastName': get_text(vendor_ret, 'LastName'),
            'Email': get_text(vendor_ret, 'Email'),
            'Phone': get_text(vendor_ret, 'Phone'),
            'Balance': get_text(vendor_ret, 'Balance'),
        }
        vendors.append(vendor)
    return vendors


def parse_invoices(response_elem) -> List[Dict]:
    """Parse InvoiceQueryRs / InvoiceAddRs"""
    invoices = []
    for invoice_ret in response_elem.findall('.//InvoiceRet'):
        invoice = {
            'TxnID': get_text(invoice_ret, 'TxnID'),
            'TimeCreated': get_text(invoice_ret, 'TimeCreated'),
            'TimeModified': get_text(invoice_ret, 'TimeModified'),
            'EditSequence': get_text(invoice_ret, 'EditSequence'),
            'TxnNumber': get_text(invoice_ret, 'TxnNumber'),
            'RefNumber': get_text(invoice_ret, 'RefNumber'),
            'TxnDate': get_text(invoice_ret, 'TxnDate'),
            'DueDate': get_text(invoice_ret, 'DueDate'),
            'Subtotal': get_text(invoice_ret, 'Subtotal'),
            'SalesTaxTotal': get_text(invoice_ret, 'SalesTaxTotal'),
            'AppliedAmount': get_text(invoice_ret, 'AppliedAmount'),
            'BalanceRemaining': get_text(invoice_ret, 'BalanceRemaining'),
            'Memo': get_text(invoice_ret, 'Memo'),
            'IsPaid': get_text(invoice_ret, 'IsPaid'),
        }

        # Customer reference
        customer_ref = invoice_ret.find('.//CustomerRef')
        if customer_ref is not None:
            invoice['CustomerRef'] = {
                'ListID': get_text(customer_ref, 'ListID'),
                'FullName': get_text(customer_ref, 'FullName'),
            }

        # Line items
        invoice['LineItems'] = []
        for line in invoice_ret.findall('.//InvoiceLineRet'):
            line_item = {
                'TxnLineID': get_text(line, 'TxnLineID'),
                'Description': get_text(line, 'Desc'),
                'Quantity': get_text(line, 'Quantity'),
                'Rate': get_text(line, 'Rate'),
                'Amount': get_text(line, 'Amount'),
            }
            item_ref = line.find('.//ItemRef')
            if item_ref is not None:
                line_item['ItemRef'] = {
                    'ListID': get_text(item_ref, 'ListID'),
                    'FullName': get_text(item_ref, 'FullName'),
                }
            invoice['LineItems'].append(line_item)

        invoices.append(invoice)
    return invoices


def parse_items(response_elem) -> List[Dict]:
    """Parse ItemQueryRs / ItemInventoryQueryRs"""
    items = []

    # Handle different item types
    for item_type in ['ItemServiceRet', 'ItemInventoryRet', 'ItemNonInventoryRet',
                      'ItemOtherChargeRet', 'ItemDiscountRet', 'ItemGroupRet']:
        for item_ret in response_elem.findall(f'.//{item_type}'):
            item = {
                'ListID': get_text(item_ret, 'ListID'),
                'TimeCreated': get_text(item_ret, 'TimeCreated'),
                'TimeModified': get_text(item_ret, 'TimeModified'),
                'EditSequence': get_text(item_ret, 'EditSequence'),
                'Name': get_text(item_ret, 'Name'),
                'FullName': get_text(item_ret, 'FullName'),
                'IsActive': get_text(item_ret, 'IsActive'),
                'ItemType': item_type.replace('Ret', ''),
                'Description': get_text(item_ret, 'SalesDesc') or get_text(item_ret, 'Desc'),
                'Price': get_text(item_ret, 'SalesPrice') or get_text(item_ret, 'Price'),
                'QuantityOnHand': get_text(item_ret, 'QuantityOnHand'),
                'AverageCost': get_text(item_ret, 'AverageCost'),
            }
            items.append(item)

    return items


def parse_estimates(response_elem) -> List[Dict]:
    """Parse EstimateQueryRs / EstimateAddRs"""
    estimates = []
    for estimate_ret in response_elem.findall('.//EstimateRet'):
        estimate = {
            'TxnID': get_text(estimate_ret, 'TxnID'),
            'TimeCreated': get_text(estimate_ret, 'TimeCreated'),
            'TimeModified': get_text(estimate_ret, 'TimeModified'),
            'EditSequence': get_text(estimate_ret, 'EditSequence'),
            'TxnNumber': get_text(estimate_ret, 'TxnNumber'),
            'RefNumber': get_text(estimate_ret, 'RefNumber'),
            'TxnDate': get_text(estimate_ret, 'TxnDate'),
            'Subtotal': get_text(estimate_ret, 'Subtotal'),
            'Memo': get_text(estimate_ret, 'Memo'),
            'IsActive': get_text(estimate_ret, 'IsActive'),
        }

        # Customer reference
        customer_ref = estimate_ret.find('.//CustomerRef')
        if customer_ref is not None:
            estimate['CustomerRef'] = {
                'ListID': get_text(customer_ref, 'ListID'),
                'FullName': get_text(customer_ref, 'FullName'),
            }

        estimates.append(estimate)
    return estimates


def parse_accounts(response_elem) -> List[Dict]:
    """Parse AccountQueryRs"""
    accounts = []
    for account_ret in response_elem.findall('.//AccountRet'):
        account = {
            'ListID': get_text(account_ret, 'ListID'),
            'TimeCreated': get_text(account_ret, 'TimeCreated'),
            'TimeModified': get_text(account_ret, 'TimeModified'),
            'EditSequence': get_text(account_ret, 'EditSequence'),
            'Name': get_text(account_ret, 'Name'),
            'FullName': get_text(account_ret, 'FullName'),
            'IsActive': get_text(account_ret, 'IsActive'),
            'AccountType': get_text(account_ret, 'AccountType'),
            'AccountNumber': get_text(account_ret, 'AccountNumber'),
            'Balance': get_text(account_ret, 'Balance'),
            'TotalBalance': get_text(account_ret, 'TotalBalance'),
        }
        accounts.append(account)
    return accounts


def parse_classes(response_elem) -> List[Dict]:
    """Parse ClassQueryRs"""
    classes = []
    for class_ret in response_elem.findall('.//ClassRet'):
        cls = {
            'ListID': get_text(class_ret, 'ListID'),
            'TimeCreated': get_text(class_ret, 'TimeCreated'),
            'TimeModified': get_text(class_ret, 'TimeModified'),
            'EditSequence': get_text(class_ret, 'EditSequence'),
            'Name': get_text(class_ret, 'Name'),
            'FullName': get_text(class_ret, 'FullName'),
            'IsActive': get_text(class_ret, 'IsActive'),
        }
        classes.append(cls)
    return classes


def parse_company(response_elem) -> List[Dict]:
    """Parse CompanyQueryRs"""
    companies = []
    for company_ret in response_elem.findall('.//CompanyRet'):
        company = {
            'CompanyName': get_text(company_ret, 'CompanyName'),
            'LegalCompanyName': get_text(company_ret, 'LegalCompanyName'),
            'Email': get_text(company_ret, 'Email'),
            'Phone': get_text(company_ret, 'Phone'),
            'Fax': get_text(company_ret, 'Fax'),
            'Website': get_text(company_ret, 'Website'),
        }

        address = company_ret.find('.//Address')
        if address is not None:
            company['Address'] = {
                'Addr1': get_text(address, 'Addr1'),
                'Addr2': get_text(address, 'Addr2'),
                'City': get_text(address, 'City'),
                'State': get_text(address, 'State'),
                'PostalCode': get_text(address, 'PostalCode'),
                'Country': get_text(address, 'Country'),
            }

        companies.append(company)
    return companies


def parse_host(response_elem) -> List[Dict]:
    """Parse HostQueryRs"""
    hosts = []
    for host_ret in response_elem.findall('.//HostRet'):
        host = {
            'ProductName': get_text(host_ret, 'ProductName'),
            'MajorVersion': get_text(host_ret, 'MajorVersion'),
            'MinorVersion': get_text(host_ret, 'MinorVersion'),
            'Country': get_text(host_ret, 'Country'),
            'QBFileMode': get_text(host_ret, 'QBFileMode'),
        }
        hosts.append(host)
    return hosts


def parse_generic(response_elem) -> List[Dict]:
    """Generic parser for unknown response types"""
    results = []
    for child in response_elem:
        if child.tag.endswith('Ret'):
            results.append(element_to_dict(child))
    return results


def get_text(elem, tag) -> Optional[str]:
    """Get text content of a child element"""
    child = elem.find(f'.//{tag}')
    return child.text if child is not None else None
