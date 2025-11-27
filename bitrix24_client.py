"""
Bitrix24 REST API Client

Handles all communication with Bitrix24 on-premise at https://hartzell.app
"""

import requests
import json
import logging
from typing import List, Dict, Any, Optional
from config import BITRIX24_URL, BITRIX24_WEBHOOK

logger = logging.getLogger(__name__)


class Bitrix24Client:
    """Client for Bitrix24 REST API"""

    def __init__(self, webhook_url: str = None):
        """
        Initialize the Bitrix24 client.

        Args:
            webhook_url: Full webhook URL like https://hartzell.app/rest/1/abc123xyz/
        """
        self.webhook_url = webhook_url or BITRIX24_WEBHOOK
        if not self.webhook_url:
            raise ValueError("Bitrix24 webhook URL is required. Set BITRIX24_WEBHOOK in config.py")

        # Ensure webhook URL ends with /
        if not self.webhook_url.endswith('/'):
            self.webhook_url += '/'

    def _call(self, method: str, params: Dict = None) -> Dict:
        """Make an API call to Bitrix24"""
        url = f"{self.webhook_url}{method}"

        try:
            response = requests.post(url, json=params or {}, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                logger.error(f"Bitrix24 API error: {result['error']} - {result.get('error_description', '')}")
                return {'success': False, 'error': result['error'], 'error_description': result.get('error_description')}

            return {'success': True, 'result': result.get('result'), 'total': result.get('total')}

        except requests.exceptions.RequestException as e:
            logger.error(f"Bitrix24 request failed: {e}")
            return {'success': False, 'error': str(e)}

    # ============== CONTACTS (maps to QB Customers) ==============

    def get_contacts(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """
        Get contacts from Bitrix24 CRM

        Args:
            filter_params: Filter criteria (e.g., {'>DATE_MODIFY': '2024-01-01'})
            select: Fields to return
        """
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        return self._call('crm.contact.list', params)

    def get_contact(self, contact_id: int) -> Dict:
        """Get a single contact by ID"""
        return self._call('crm.contact.get', {'id': contact_id})

    def add_contact(self, fields: Dict) -> Dict:
        """
        Add a new contact

        Args:
            fields: Contact fields like NAME, LAST_NAME, EMAIL, PHONE, etc.
        """
        return self._call('crm.contact.add', {'fields': fields})

    def update_contact(self, contact_id: int, fields: Dict) -> Dict:
        """Update an existing contact"""
        return self._call('crm.contact.update', {'id': contact_id, 'fields': fields})

    # ============== COMPANIES (maps to QB Customers with CompanyName) ==============

    def get_companies(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """Get companies from Bitrix24 CRM"""
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        return self._call('crm.company.list', params)

    def get_company(self, company_id: int) -> Dict:
        """Get a single company by ID"""
        return self._call('crm.company.get', {'id': company_id})

    def add_company(self, fields: Dict) -> Dict:
        """Add a new company"""
        return self._call('crm.company.add', {'fields': fields})

    def update_company(self, company_id: int, fields: Dict) -> Dict:
        """Update an existing company"""
        return self._call('crm.company.update', {'id': company_id, 'fields': fields})

    # ============== DEALS (can map to QB Invoices/Estimates) ==============

    def get_deals(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """Get deals from Bitrix24 CRM"""
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        return self._call('crm.deal.list', params)

    def get_deal(self, deal_id: int) -> Dict:
        """Get a single deal by ID"""
        return self._call('crm.deal.get', {'id': deal_id})

    def add_deal(self, fields: Dict) -> Dict:
        """Add a new deal"""
        return self._call('crm.deal.add', {'fields': fields})

    def update_deal(self, deal_id: int, fields: Dict) -> Dict:
        """Update an existing deal"""
        return self._call('crm.deal.update', {'id': deal_id, 'fields': fields})

    # ============== PRODUCTS (maps to QB Items) ==============

    def get_products(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """Get products from Bitrix24 catalog"""
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        return self._call('crm.product.list', params)

    def get_product(self, product_id: int) -> Dict:
        """Get a single product by ID"""
        return self._call('crm.product.get', {'id': product_id})

    def add_product(self, fields: Dict) -> Dict:
        """Add a new product"""
        return self._call('crm.product.add', {'fields': fields})

    def update_product(self, product_id: int, fields: Dict) -> Dict:
        """Update an existing product"""
        return self._call('crm.product.update', {'id': product_id, 'fields': fields})

    # ============== INVOICES ==============

    def get_invoices(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """Get invoices from Bitrix24"""
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        # Try the new smart invoice first, fall back to old invoice
        result = self._call('crm.item.list', {
            'entityTypeId': 31,  # Smart Invoice entity type
            **params
        })

        if not result.get('success'):
            # Fall back to old invoice API
            return self._call('crm.invoice.list', params)

        return result

    def add_invoice(self, fields: Dict) -> Dict:
        """Add a new invoice"""
        return self._call('crm.invoice.add', {'fields': fields})

    # ============== LEADS ==============

    def get_leads(self, filter_params: Dict = None, select: List[str] = None) -> Dict:
        """Get leads from Bitrix24 CRM"""
        params = {}
        if filter_params:
            params['filter'] = filter_params
        if select:
            params['select'] = select

        return self._call('crm.lead.list', params)

    def add_lead(self, fields: Dict) -> Dict:
        """Add a new lead"""
        return self._call('crm.lead.add', {'fields': fields})

    # ============== UTILITY METHODS ==============

    def test_connection(self) -> Dict:
        """Test the connection to Bitrix24"""
        return self._call('app.info')

    def get_current_user(self) -> Dict:
        """Get the current user info"""
        return self._call('user.current')

    def get_fields(self, entity_type: str) -> Dict:
        """
        Get available fields for an entity type

        Args:
            entity_type: One of 'contact', 'company', 'deal', 'lead', 'product', 'invoice'
        """
        method_map = {
            'contact': 'crm.contact.fields',
            'company': 'crm.company.fields',
            'deal': 'crm.deal.fields',
            'lead': 'crm.lead.fields',
            'product': 'crm.product.fields',
            'invoice': 'crm.invoice.fields',
        }

        method = method_map.get(entity_type.lower())
        if not method:
            return {'success': False, 'error': f'Unknown entity type: {entity_type}'}

        return self._call(method)


# ============== MAPPING FUNCTIONS ==============

def qb_customer_to_bitrix_contact(qb_customer: Dict) -> Dict:
    """Convert a QuickBooks customer to Bitrix24 contact fields"""
    fields = {
        'NAME': qb_customer.get('FirstName') or qb_customer.get('Name', '').split()[0] if qb_customer.get('Name') else '',
        'LAST_NAME': qb_customer.get('LastName') or (qb_customer.get('Name', '').split()[-1] if len(qb_customer.get('Name', '').split()) > 1 else ''),
        'COMPANY_TITLE': qb_customer.get('CompanyName', ''),
        'SOURCE_DESCRIPTION': f"QB ListID: {qb_customer.get('ListID', '')}",
    }

    # Email
    if qb_customer.get('Email'):
        fields['EMAIL'] = [{'VALUE': qb_customer['Email'], 'VALUE_TYPE': 'WORK'}]

    # Phone
    if qb_customer.get('Phone'):
        fields['PHONE'] = [{'VALUE': qb_customer['Phone'], 'VALUE_TYPE': 'WORK'}]

    # Address
    if qb_customer.get('BillAddress'):
        addr = qb_customer['BillAddress']
        address_parts = [
            addr.get('Addr1', ''),
            addr.get('Addr2', ''),
            f"{addr.get('City', '')}, {addr.get('State', '')} {addr.get('PostalCode', '')}",
            addr.get('Country', '')
        ]
        fields['ADDRESS'] = '\n'.join(filter(None, address_parts))

    return fields


def qb_customer_to_bitrix_company(qb_customer: Dict) -> Dict:
    """Convert a QuickBooks customer to Bitrix24 company fields"""
    fields = {
        'TITLE': qb_customer.get('CompanyName') or qb_customer.get('Name', ''),
        'COMMENTS': f"QB ListID: {qb_customer.get('ListID', '')}",
    }

    # Email
    if qb_customer.get('Email'):
        fields['EMAIL'] = [{'VALUE': qb_customer['Email'], 'VALUE_TYPE': 'WORK'}]

    # Phone
    if qb_customer.get('Phone'):
        fields['PHONE'] = [{'VALUE': qb_customer['Phone'], 'VALUE_TYPE': 'WORK'}]

    return fields


def bitrix_contact_to_qb_customer(bitrix_contact: Dict) -> Dict:
    """Convert a Bitrix24 contact to QuickBooks customer fields"""
    name_parts = []
    if bitrix_contact.get('NAME'):
        name_parts.append(bitrix_contact['NAME'])
    if bitrix_contact.get('LAST_NAME'):
        name_parts.append(bitrix_contact['LAST_NAME'])

    qb_data = {
        'name': ' '.join(name_parts) or f"Bitrix Contact {bitrix_contact.get('ID', '')}",
        'first_name': bitrix_contact.get('NAME', ''),
        'last_name': bitrix_contact.get('LAST_NAME', ''),
        'company_name': bitrix_contact.get('COMPANY_TITLE', ''),
    }

    # Email (Bitrix stores as array)
    emails = bitrix_contact.get('EMAIL', [])
    if emails and isinstance(emails, list) and len(emails) > 0:
        qb_data['email'] = emails[0].get('VALUE', '') if isinstance(emails[0], dict) else emails[0]

    # Phone (Bitrix stores as array)
    phones = bitrix_contact.get('PHONE', [])
    if phones and isinstance(phones, list) and len(phones) > 0:
        qb_data['phone'] = phones[0].get('VALUE', '') if isinstance(phones[0], dict) else phones[0]

    return qb_data


def qb_item_to_bitrix_product(qb_item: Dict) -> Dict:
    """Convert a QuickBooks item to Bitrix24 product fields"""
    fields = {
        'NAME': qb_item.get('Name') or qb_item.get('FullName', ''),
        'DESCRIPTION': qb_item.get('Description', ''),
        'PRICE': float(qb_item.get('Price', 0) or 0),
        'CURRENCY_ID': 'USD',
        'XML_ID': f"QB_{qb_item.get('ListID', '')}",
    }

    return fields


def qb_invoice_to_bitrix_deal(qb_invoice: Dict) -> Dict:
    """Convert a QuickBooks invoice to Bitrix24 deal fields"""
    fields = {
        'TITLE': f"Invoice {qb_invoice.get('RefNumber', qb_invoice.get('TxnID', ''))}",
        'OPPORTUNITY': float(qb_invoice.get('Subtotal', 0) or 0),
        'CURRENCY_ID': 'USD',
        'COMMENTS': f"QB TxnID: {qb_invoice.get('TxnID', '')}\n{qb_invoice.get('Memo', '')}",
    }

    # Set stage based on payment status
    if qb_invoice.get('IsPaid') == 'true':
        fields['STAGE_ID'] = 'WON'
    elif float(qb_invoice.get('BalanceRemaining', 0) or 0) > 0:
        fields['STAGE_ID'] = 'EXECUTING'
    else:
        fields['STAGE_ID'] = 'NEW'

    return fields
