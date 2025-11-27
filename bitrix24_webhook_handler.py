"""
Bitrix24 Webhook Handler

This module handles incoming webhooks from Bitrix24 to sync changes TO QuickBooks.
When contacts/deals/etc. change in Bitrix24, this queues them for the next Web Connector poll.

To set up webhooks in Bitrix24:
1. Go to Developer resources > Other > Outbound webhooks
2. Add a new webhook pointing to: http://YOUR_SERVER:8080/bitrix24/webhook
3. Select the events you want to track (e.g., ONCRMCONTACTADD, ONCRMCONTACTUPDATE)
"""

import json
import logging
from flask import Blueprint, request, jsonify

from database import add_to_qb_queue
from bitrix24_client import Bitrix24Client, bitrix_contact_to_qb_customer
from config import BITRIX24_WEBHOOK

logger = logging.getLogger(__name__)

bitrix_webhook_bp = Blueprint('bitrix_webhook', __name__)


@bitrix_webhook_bp.route('/bitrix24/webhook', methods=['POST'])
def handle_bitrix24_webhook():
    """
    Handle incoming webhook from Bitrix24.

    Bitrix24 sends webhooks when CRM entities are created/updated/deleted.
    We queue these changes for the next QuickBooks Web Connector poll.
    """
    try:
        # Bitrix24 can send form data or JSON
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        logger.info(f"Received Bitrix24 webhook: {data}")

        event = data.get('event', '')

        # Handle different event types
        if event.startswith('ONCRMCONTACT'):
            handle_contact_event(event, data)
        elif event.startswith('ONCRMCOMPANY'):
            handle_company_event(event, data)
        elif event.startswith('ONCRMDEAL'):
            handle_deal_event(event, data)
        elif event.startswith('ONCRMPRODUCT'):
            handle_product_event(event, data)
        else:
            logger.info(f"Unhandled event type: {event}")

        return jsonify({'status': 'ok'}), 200

    except Exception as e:
        logger.error(f"Error handling Bitrix24 webhook: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


def handle_contact_event(event: str, data: dict):
    """Handle contact-related events from Bitrix24"""
    contact_id = data.get('data[FIELDS][ID]') or data.get('data', {}).get('FIELDS', {}).get('ID')

    if not contact_id:
        logger.warning("No contact ID in webhook data")
        return

    if 'ADD' in event:
        action = 'add'
    elif 'UPDATE' in event:
        action = 'update'
    elif 'DELETE' in event:
        action = 'delete'
    else:
        logger.info(f"Unknown contact event: {event}")
        return

    logger.info(f"Contact {action}: ID {contact_id}")

    # Fetch full contact data from Bitrix24
    if action != 'delete' and BITRIX24_WEBHOOK:
        try:
            client = Bitrix24Client(BITRIX24_WEBHOOK)
            result = client.get_contact(int(contact_id))

            if result.get('success'):
                contact_data = result.get('result', {})
                qb_data = bitrix_contact_to_qb_customer(contact_data)

                add_to_qb_queue(
                    entity_type='customer',
                    bitrix_id=contact_id,
                    action=action,
                    data=json.dumps(qb_data)
                )
                logger.info(f"Queued contact {contact_id} for QB sync")
            else:
                logger.error(f"Failed to fetch contact {contact_id}: {result.get('error')}")
        except Exception as e:
            logger.error(f"Error processing contact webhook: {e}")
    else:
        # For delete, we just need the ID
        add_to_qb_queue(
            entity_type='customer',
            bitrix_id=contact_id,
            action=action,
            data=None
        )


def handle_company_event(event: str, data: dict):
    """Handle company-related events from Bitrix24"""
    company_id = data.get('data[FIELDS][ID]') or data.get('data', {}).get('FIELDS', {}).get('ID')

    if not company_id:
        logger.warning("No company ID in webhook data")
        return

    if 'ADD' in event:
        action = 'add'
    elif 'UPDATE' in event:
        action = 'update'
    elif 'DELETE' in event:
        action = 'delete'
    else:
        return

    logger.info(f"Company {action}: ID {company_id}")

    if action != 'delete' and BITRIX24_WEBHOOK:
        try:
            client = Bitrix24Client(BITRIX24_WEBHOOK)
            result = client.get_company(int(company_id))

            if result.get('success'):
                company_data = result.get('result', {})

                # Convert to QB customer format
                qb_data = {
                    'name': company_data.get('TITLE', f"Bitrix Company {company_id}"),
                    'company_name': company_data.get('TITLE', ''),
                }

                # Get phone/email if available
                phones = company_data.get('PHONE', [])
                if phones and isinstance(phones, list):
                    qb_data['phone'] = phones[0].get('VALUE', '') if isinstance(phones[0], dict) else phones[0]

                emails = company_data.get('EMAIL', [])
                if emails and isinstance(emails, list):
                    qb_data['email'] = emails[0].get('VALUE', '') if isinstance(emails[0], dict) else emails[0]

                add_to_qb_queue(
                    entity_type='customer',
                    bitrix_id=f"company_{company_id}",
                    action=action,
                    data=json.dumps(qb_data)
                )
                logger.info(f"Queued company {company_id} for QB sync")
        except Exception as e:
            logger.error(f"Error processing company webhook: {e}")


def handle_deal_event(event: str, data: dict):
    """Handle deal-related events from Bitrix24"""
    deal_id = data.get('data[FIELDS][ID]') or data.get('data', {}).get('FIELDS', {}).get('ID')

    if not deal_id:
        return

    if 'ADD' in event:
        action = 'add'
    elif 'UPDATE' in event:
        action = 'update'
    elif 'DELETE' in event:
        action = 'delete'
    else:
        return

    logger.info(f"Deal {action}: ID {deal_id}")

    # Note: Syncing deals to QB invoices requires more complex logic
    # For now, just log the event
    # TODO: Implement deal -> invoice sync if needed


def handle_product_event(event: str, data: dict):
    """Handle product-related events from Bitrix24"""
    product_id = data.get('data[FIELDS][ID]') or data.get('data', {}).get('FIELDS', {}).get('ID')

    if not product_id:
        return

    if 'ADD' in event:
        action = 'add'
    elif 'UPDATE' in event:
        action = 'update'
    elif 'DELETE' in event:
        action = 'delete'
    else:
        return

    logger.info(f"Product {action}: ID {product_id}")

    # Note: Syncing products to QB items requires more complex logic
    # For now, just log the event
    # TODO: Implement product -> item sync if needed
