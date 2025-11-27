"""
qbXML Request Builder for QuickBooks Desktop

This module builds qbXML requests for various QuickBooks operations.
Reference: https://developer.intuit.com/app/developer/qbdesktop/docs/api-reference/qbdesktop
"""

from datetime import datetime


def wrap_qbxml(request_body, on_error="stopOnError"):
    """Wrap a request body in the standard qbXML envelope"""
    return f'''<?xml version="1.0" encoding="utf-8"?>
<?qbxml version="16.0"?>
<QBXML>
    <QBXMLMsgsRq onError="{on_error}">
        {request_body}
    </QBXMLMsgsRq>
</QBXML>'''


# ============== CUSTOMER QUERIES ==============

def customer_query_all():
    """Query all customers"""
    return wrap_qbxml('''
        <CustomerQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </CustomerQueryRq>
    ''')


def customer_query_modified_since(from_date):
    """Query customers modified since a given date"""
    return wrap_qbxml(f'''
        <CustomerQueryRq requestID="1">
            <FromModifiedDate>{from_date}</FromModifiedDate>
            <ActiveStatus>All</ActiveStatus>
        </CustomerQueryRq>
    ''')


def customer_query_by_list_id(list_id):
    """Query a specific customer by ListID"""
    return wrap_qbxml(f'''
        <CustomerQueryRq requestID="1">
            <ListID>{list_id}</ListID>
        </CustomerQueryRq>
    ''')


def customer_add(name, company_name=None, first_name=None, last_name=None,
                 email=None, phone=None, address=None):
    """Add a new customer"""
    address_xml = ""
    if address:
        address_xml = f'''
            <BillAddress>
                <Addr1>{address.get('addr1', '')}</Addr1>
                <Addr2>{address.get('addr2', '')}</Addr2>
                <City>{address.get('city', '')}</City>
                <State>{address.get('state', '')}</State>
                <PostalCode>{address.get('postal_code', '')}</PostalCode>
                <Country>{address.get('country', '')}</Country>
            </BillAddress>
        '''

    return wrap_qbxml(f'''
        <CustomerAddRq requestID="1">
            <CustomerAdd>
                <Name>{name}</Name>
                {f'<CompanyName>{company_name}</CompanyName>' if company_name else ''}
                {f'<FirstName>{first_name}</FirstName>' if first_name else ''}
                {f'<LastName>{last_name}</LastName>' if last_name else ''}
                {f'<Email>{email}</Email>' if email else ''}
                {f'<Phone>{phone}</Phone>' if phone else ''}
                {address_xml}
            </CustomerAdd>
        </CustomerAddRq>
    ''')


def customer_mod(list_id, edit_sequence, **fields):
    """Modify an existing customer"""
    field_xml = ""
    for key, value in fields.items():
        if value is not None:
            tag = ''.join(word.capitalize() for word in key.split('_'))
            field_xml += f"<{tag}>{value}</{tag}>\n"

    return wrap_qbxml(f'''
        <CustomerModRq requestID="1">
            <CustomerMod>
                <ListID>{list_id}</ListID>
                <EditSequence>{edit_sequence}</EditSequence>
                {field_xml}
            </CustomerMod>
        </CustomerModRq>
    ''')


# ============== VENDOR QUERIES ==============

def vendor_query_all():
    """Query all vendors"""
    return wrap_qbxml('''
        <VendorQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </VendorQueryRq>
    ''')


def vendor_query_modified_since(from_date):
    """Query vendors modified since a given date"""
    return wrap_qbxml(f'''
        <VendorQueryRq requestID="1">
            <FromModifiedDate>{from_date}</FromModifiedDate>
            <ActiveStatus>All</ActiveStatus>
        </VendorQueryRq>
    ''')


def vendor_add(name, company_name=None, first_name=None, last_name=None,
               email=None, phone=None):
    """Add a new vendor"""
    return wrap_qbxml(f'''
        <VendorAddRq requestID="1">
            <VendorAdd>
                <Name>{name}</Name>
                {f'<CompanyName>{company_name}</CompanyName>' if company_name else ''}
                {f'<FirstName>{first_name}</FirstName>' if first_name else ''}
                {f'<LastName>{last_name}</LastName>' if last_name else ''}
                {f'<Email>{email}</Email>' if email else ''}
                {f'<Phone>{phone}</Phone>' if phone else ''}
            </VendorAdd>
        </VendorAddRq>
    ''')


# ============== INVOICE QUERIES ==============

def invoice_query_all():
    """Query all invoices"""
    return wrap_qbxml('''
        <InvoiceQueryRq requestID="1">
            <IncludeLineItems>true</IncludeLineItems>
        </InvoiceQueryRq>
    ''')


def invoice_query_modified_since(from_date):
    """Query invoices modified since a given date"""
    return wrap_qbxml(f'''
        <InvoiceQueryRq requestID="1">
            <ModifiedDateRangeFilter>
                <FromModifiedDate>{from_date}</FromModifiedDate>
            </ModifiedDateRangeFilter>
            <IncludeLineItems>true</IncludeLineItems>
        </InvoiceQueryRq>
    ''')


def invoice_query_by_txn_id(txn_id):
    """Query a specific invoice by TxnID"""
    return wrap_qbxml(f'''
        <InvoiceQueryRq requestID="1">
            <TxnID>{txn_id}</TxnID>
            <IncludeLineItems>true</IncludeLineItems>
        </InvoiceQueryRq>
    ''')


def invoice_add(customer_list_id, line_items, ref_number=None, txn_date=None, memo=None):
    """
    Add a new invoice

    line_items should be a list of dicts with keys:
    - item_list_id: ListID of the item
    - description: Line description
    - quantity: Quantity (optional)
    - rate: Unit price (optional)
    - amount: Line total (optional, if not using quantity*rate)
    """
    lines_xml = ""
    for item in line_items:
        lines_xml += f'''
            <InvoiceLineAdd>
                {f'<ItemRef><ListID>{item["item_list_id"]}</ListID></ItemRef>' if item.get('item_list_id') else ''}
                {f'<Desc>{item.get("description", "")}</Desc>' if item.get('description') else ''}
                {f'<Quantity>{item["quantity"]}</Quantity>' if item.get('quantity') else ''}
                {f'<Rate>{item["rate"]}</Rate>' if item.get('rate') else ''}
                {f'<Amount>{item["amount"]}</Amount>' if item.get('amount') else ''}
            </InvoiceLineAdd>
        '''

    return wrap_qbxml(f'''
        <InvoiceAddRq requestID="1">
            <InvoiceAdd>
                <CustomerRef>
                    <ListID>{customer_list_id}</ListID>
                </CustomerRef>
                {f'<RefNumber>{ref_number}</RefNumber>' if ref_number else ''}
                {f'<TxnDate>{txn_date}</TxnDate>' if txn_date else ''}
                {f'<Memo>{memo}</Memo>' if memo else ''}
                {lines_xml}
            </InvoiceAdd>
        </InvoiceAddRq>
    ''')


# ============== ITEM QUERIES ==============

def item_query_all():
    """Query all items (inventory, service, etc.)"""
    return wrap_qbxml('''
        <ItemQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </ItemQueryRq>
    ''')


def item_inventory_query_all():
    """Query all inventory items specifically"""
    return wrap_qbxml('''
        <ItemInventoryQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </ItemInventoryQueryRq>
    ''')


def item_query_modified_since(from_date):
    """Query items modified since a given date"""
    return wrap_qbxml(f'''
        <ItemQueryRq requestID="1">
            <FromModifiedDate>{from_date}</FromModifiedDate>
            <ActiveStatus>All</ActiveStatus>
        </ItemQueryRq>
    ''')


def item_service_add(name, description=None, price=None):
    """Add a service item"""
    return wrap_qbxml(f'''
        <ItemServiceAddRq requestID="1">
            <ItemServiceAdd>
                <Name>{name}</Name>
                {f'<SalesOrPurchase><Desc>{description}</Desc><Price>{price}</Price></SalesOrPurchase>' if description or price else ''}
            </ItemServiceAdd>
        </ItemServiceAddRq>
    ''')


# ============== ESTIMATE QUERIES ==============

def estimate_query_all():
    """Query all estimates"""
    return wrap_qbxml('''
        <EstimateQueryRq requestID="1">
            <IncludeLineItems>true</IncludeLineItems>
        </EstimateQueryRq>
    ''')


def estimate_query_modified_since(from_date):
    """Query estimates modified since a given date"""
    return wrap_qbxml(f'''
        <EstimateQueryRq requestID="1">
            <ModifiedDateRangeFilter>
                <FromModifiedDate>{from_date}</FromModifiedDate>
            </ModifiedDateRangeFilter>
            <IncludeLineItems>true</IncludeLineItems>
        </EstimateQueryRq>
    ''')


# ============== ACCOUNT QUERIES ==============

def account_query_all():
    """Query all accounts (Chart of Accounts)"""
    return wrap_qbxml('''
        <AccountQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </AccountQueryRq>
    ''')


# ============== CLASS QUERIES (for Contractor Edition) ==============

def class_query_all():
    """Query all classes (job costing categories)"""
    return wrap_qbxml('''
        <ClassQueryRq requestID="1">
            <ActiveStatus>All</ActiveStatus>
        </ClassQueryRq>
    ''')


# ============== COMPANY INFO ==============

def company_query():
    """Query company information"""
    return wrap_qbxml('''
        <CompanyQueryRq requestID="1">
        </CompanyQueryRq>
    ''')


# ============== HOST INFO ==============

def host_query():
    """Query host (QuickBooks) version info"""
    return wrap_qbxml('''
        <HostQueryRq requestID="1">
        </HostQueryRq>
    ''')
