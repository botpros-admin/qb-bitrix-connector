"""
Sync Manager - Orchestrates bi-directional sync between QuickBooks and Bitrix24

This module determines what needs to be synced and coordinates the data flow.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from database import (
    init_db, get_last_sync_time, update_last_sync_time,
    get_bitrix_id, get_qb_list_id, save_id_mapping,
    get_pending_qb_queue, mark_queue_item_processed, log_sync
)
from qbxml_builder import (
    customer_query_all, customer_query_modified_since, customer_add,
    vendor_query_all, vendor_query_modified_since,
    invoice_query_all, invoice_query_modified_since,
    item_query_all, item_query_modified_since,
    estimate_query_all, estimate_query_modified_since,
    host_query, company_query
)
from qbxml_parser import parse_qbxml_response
from bitrix24_client import (
    Bitrix24Client,
    qb_customer_to_bitrix_contact, qb_customer_to_bitrix_company,
    bitrix_contact_to_qb_customer,
    qb_item_to_bitrix_product,
    qb_invoice_to_bitrix_deal
)
from config import BITRIX24_WEBHOOK

logger = logging.getLogger(__name__)


class SyncManager:
    """Manages synchronization between QuickBooks and Bitrix24"""

    def __init__(self):
        """Initialize the sync manager"""
        init_db()
        self.bitrix_client = None
        if BITRIX24_WEBHOOK:
            try:
                self.bitrix_client = Bitrix24Client(BITRIX24_WEBHOOK)
            except Exception as e:
                logger.warning(f"Could not initialize Bitrix24 client: {e}")

        # Define what entities to sync
        self.sync_entities = [
            'customers',
            'vendors',
            'items',
            'invoices',
            'estimates',
        ]

    def get_pending_requests(self) -> List[Dict]:
        """
        Get all pending qbXML requests that need to be sent to QuickBooks.

        This is called when Web Connector authenticates to build the request queue.

        Returns:
            List of request items with 'type' and 'qbxml' keys
        """
        requests = []

        # Always start with host query to verify connection
        requests.append({
            'type': 'host_query',
            'qbxml': host_query(),
            'action': 'query'
        })

        # Check for pending Bitrix24 -> QB items first (from webhook queue)
        pending_queue = get_pending_qb_queue()
        for item in pending_queue:
            qbxml = self._build_qbxml_for_queue_item(item)
            if qbxml:
                requests.append({
                    'type': f"{item['entity_type']}_{item['action']}",
                    'qbxml': qbxml,
                    'action': item['action'],
                    'queue_id': item['id'],
                    'bitrix_id': item['bitrix_id'],
                    'entity_type': item['entity_type']
                })

        # Query QuickBooks for changes to sync TO Bitrix24
        for entity in self.sync_entities:
            last_sync = get_last_sync_time(entity, 'qb_to_bitrix')

            if last_sync:
                # Incremental sync - only get modified records
                qbxml = self._get_modified_query(entity, last_sync)
            else:
                # Full sync - get all records
                qbxml = self._get_full_query(entity)

            if qbxml:
                requests.append({
                    'type': f'{entity}_query',
                    'qbxml': qbxml,
                    'action': 'query',
                    'entity_type': entity,
                    'is_incremental': bool(last_sync)
                })

        logger.info(f"Built {len(requests)} requests for Web Connector")
        return requests

    def _get_full_query(self, entity: str) -> Optional[str]:
        """Get qbXML for full query of an entity type"""
        query_map = {
            'customers': customer_query_all,
            'vendors': vendor_query_all,
            'items': item_query_all,
            'invoices': invoice_query_all,
            'estimates': estimate_query_all,
        }

        query_func = query_map.get(entity)
        if query_func:
            return query_func()
        return None

    def _get_modified_query(self, entity: str, from_date: str) -> Optional[str]:
        """Get qbXML for incremental query since last sync"""
        query_map = {
            'customers': customer_query_modified_since,
            'vendors': vendor_query_modified_since,
            'items': item_query_modified_since,
            'invoices': invoice_query_modified_since,
            'estimates': estimate_query_modified_since,
        }

        query_func = query_map.get(entity)
        if query_func:
            # Format date for qbXML (ISO format)
            return query_func(from_date)
        return None

    def _build_qbxml_for_queue_item(self, item: Dict) -> Optional[str]:
        """Build qbXML request for a queued Bitrix24 -> QB item"""
        entity_type = item['entity_type']
        action = item['action']
        data = json.loads(item['data']) if item['data'] else {}

        if entity_type == 'customer' and action == 'add':
            return customer_add(
                name=data.get('name', f"Bitrix Contact {item['bitrix_id']}"),
                company_name=data.get('company_name'),
                first_name=data.get('first_name'),
                last_name=data.get('last_name'),
                email=data.get('email'),
                phone=data.get('phone'),
                address=data.get('address')
            )

        # Add more entity types as needed
        logger.warning(f"Unknown queue item type: {entity_type}/{action}")
        return None

    def process_response(self, request_item: Dict, response_xml: str):
        """
        Process a qbXML response from QuickBooks.

        Args:
            request_item: The original request item with metadata
            response_xml: The qbXML response string
        """
        request_type = request_item.get('type', '')
        action = request_item.get('action', '')
        entity_type = request_item.get('entity_type', '')

        logger.info(f"Processing response for {request_type}")

        # Parse the response
        parsed = parse_qbxml_response(response_xml)

        if not parsed['success']:
            logger.error(f"QB Response error: {parsed['status_message']}")

            # If this was from the queue, mark it as failed
            if 'queue_id' in request_item:
                mark_queue_item_processed(
                    request_item['queue_id'],
                    status='failed',
                    error_message=parsed['status_message']
                )
            return

        data = parsed['data']

        # Handle host query (just log info)
        if 'host_query' in request_type:
            if data:
                logger.info(f"Connected to QuickBooks: {data[0].get('ProductName', 'Unknown')}")
            return

        # Handle queue items (Bitrix24 -> QB)
        if 'queue_id' in request_item:
            self._handle_queue_response(request_item, data)
            return

        # Handle query responses (QB -> Bitrix24)
        if action == 'query' and data:
            self._sync_to_bitrix24(entity_type, data)
            update_last_sync_time(entity_type, 'qb_to_bitrix')

    def _handle_queue_response(self, request_item: Dict, data: List[Dict]):
        """Handle response for a queued Bitrix24 -> QB item"""
        queue_id = request_item['queue_id']
        entity_type = request_item.get('entity_type', '')
        bitrix_id = request_item.get('bitrix_id', '')

        if data:
            # Successfully created/updated in QB
            qb_list_id = data[0].get('ListID') or data[0].get('TxnID')
            if qb_list_id:
                save_id_mapping(entity_type, qb_list_id, bitrix_id)
                log_sync('bitrix_to_qb', entity_type, qb_list_id, bitrix_id, 'add', 'success')

            mark_queue_item_processed(queue_id, status='completed')
            logger.info(f"Successfully synced {entity_type} from Bitrix24 to QB")
        else:
            mark_queue_item_processed(queue_id, status='failed', error_message='No data returned')

    def _sync_to_bitrix24(self, entity_type: str, data: List[Dict]):
        """Sync QuickBooks data to Bitrix24"""
        if not self.bitrix_client:
            logger.warning("Bitrix24 client not configured, skipping sync to Bitrix24")
            return

        logger.info(f"Syncing {len(data)} {entity_type} records to Bitrix24")

        for record in data:
            try:
                self._sync_single_record_to_bitrix24(entity_type, record)
            except Exception as e:
                logger.error(f"Error syncing {entity_type} to Bitrix24: {e}")
                qb_id = record.get('ListID') or record.get('TxnID')
                log_sync('qb_to_bitrix', entity_type, qb_id, None, 'sync', 'error', str(e))

    def _sync_single_record_to_bitrix24(self, entity_type: str, record: Dict):
        """Sync a single record to Bitrix24"""
        qb_id = record.get('ListID') or record.get('TxnID')
        existing_bitrix_id = get_bitrix_id(entity_type, qb_id)

        if entity_type == 'customers':
            self._sync_customer_to_bitrix24(record, existing_bitrix_id)
        elif entity_type == 'items':
            self._sync_item_to_bitrix24(record, existing_bitrix_id)
        elif entity_type == 'invoices':
            self._sync_invoice_to_bitrix24(record, existing_bitrix_id)
        # Add more entity types as needed

    def _sync_customer_to_bitrix24(self, qb_customer: Dict, existing_bitrix_id: str = None):
        """Sync a QuickBooks customer to Bitrix24"""
        qb_list_id = qb_customer.get('ListID')

        # Determine if this is a company or individual contact
        if qb_customer.get('CompanyName'):
            # Sync as company
            bitrix_data = qb_customer_to_bitrix_company(qb_customer)

            if existing_bitrix_id:
                result = self.bitrix_client.update_company(int(existing_bitrix_id), bitrix_data)
                action = 'update'
            else:
                result = self.bitrix_client.add_company(bitrix_data)
                action = 'add'

            if result.get('success'):
                bitrix_id = str(result.get('result', existing_bitrix_id))
                if bitrix_id and not existing_bitrix_id:
                    save_id_mapping('customers', qb_list_id, bitrix_id)
                log_sync('qb_to_bitrix', 'customers', qb_list_id, bitrix_id, action, 'success')
                logger.info(f"Synced customer {qb_customer.get('Name')} to Bitrix24 company {bitrix_id}")
            else:
                log_sync('qb_to_bitrix', 'customers', qb_list_id, existing_bitrix_id, action, 'error',
                        result.get('error'))
        else:
            # Sync as contact
            bitrix_data = qb_customer_to_bitrix_contact(qb_customer)

            if existing_bitrix_id:
                result = self.bitrix_client.update_contact(int(existing_bitrix_id), bitrix_data)
                action = 'update'
            else:
                result = self.bitrix_client.add_contact(bitrix_data)
                action = 'add'

            if result.get('success'):
                bitrix_id = str(result.get('result', existing_bitrix_id))
                if bitrix_id and not existing_bitrix_id:
                    save_id_mapping('customers', qb_list_id, bitrix_id)
                log_sync('qb_to_bitrix', 'customers', qb_list_id, bitrix_id, action, 'success')
                logger.info(f"Synced customer {qb_customer.get('Name')} to Bitrix24 contact {bitrix_id}")
            else:
                log_sync('qb_to_bitrix', 'customers', qb_list_id, existing_bitrix_id, action, 'error',
                        result.get('error'))

    def _sync_item_to_bitrix24(self, qb_item: Dict, existing_bitrix_id: str = None):
        """Sync a QuickBooks item to Bitrix24 product"""
        qb_list_id = qb_item.get('ListID')
        bitrix_data = qb_item_to_bitrix_product(qb_item)

        if existing_bitrix_id:
            result = self.bitrix_client.update_product(int(existing_bitrix_id), bitrix_data)
            action = 'update'
        else:
            result = self.bitrix_client.add_product(bitrix_data)
            action = 'add'

        if result.get('success'):
            bitrix_id = str(result.get('result', existing_bitrix_id))
            if bitrix_id and not existing_bitrix_id:
                save_id_mapping('items', qb_list_id, bitrix_id)
            log_sync('qb_to_bitrix', 'items', qb_list_id, bitrix_id, action, 'success')
            logger.info(f"Synced item {qb_item.get('Name')} to Bitrix24 product {bitrix_id}")
        else:
            log_sync('qb_to_bitrix', 'items', qb_list_id, existing_bitrix_id, action, 'error',
                    result.get('error'))

    def _sync_invoice_to_bitrix24(self, qb_invoice: Dict, existing_bitrix_id: str = None):
        """Sync a QuickBooks invoice to Bitrix24 deal"""
        qb_txn_id = qb_invoice.get('TxnID')
        bitrix_data = qb_invoice_to_bitrix_deal(qb_invoice)

        # Link to customer/company if we have a mapping
        customer_ref = qb_invoice.get('CustomerRef', {})
        if customer_ref.get('ListID'):
            customer_bitrix_id = get_bitrix_id('customers', customer_ref['ListID'])
            if customer_bitrix_id:
                bitrix_data['COMPANY_ID'] = customer_bitrix_id

        if existing_bitrix_id:
            result = self.bitrix_client.update_deal(int(existing_bitrix_id), bitrix_data)
            action = 'update'
        else:
            result = self.bitrix_client.add_deal(bitrix_data)
            action = 'add'

        if result.get('success'):
            bitrix_id = str(result.get('result', existing_bitrix_id))
            if bitrix_id and not existing_bitrix_id:
                save_id_mapping('invoices', qb_txn_id, bitrix_id)
            log_sync('qb_to_bitrix', 'invoices', qb_txn_id, bitrix_id, action, 'success')
            logger.info(f"Synced invoice {qb_invoice.get('RefNumber')} to Bitrix24 deal {bitrix_id}")
        else:
            log_sync('qb_to_bitrix', 'invoices', qb_txn_id, existing_bitrix_id, action, 'error',
                    result.get('error'))
