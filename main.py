"""
QB-Bitrix24 Connector - Main Entry Point

This is the main application that runs the connector service.
It hosts:
1. SOAP endpoint for QuickBooks Web Connector (/soap/)
2. Webhook endpoint for Bitrix24 (/bitrix24/webhook)
3. Status/admin UI (/)

Usage:
    python main.py

The service will start on http://localhost:8080 by default.
"""

import logging
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template_string
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from spyne import Application
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from config import SOAP_HOST, SOAP_PORT, LOG_FILE, LOG_LEVEL, BITRIX24_WEBHOOK
from database import init_db
from webconnector_service import QuickBooksWebConnectorService
from bitrix24_webhook_handler import bitrix_webhook_bp

# Set up logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# HTML template for the admin UI
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>QB-Bitrix24 Connector</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; border-bottom: 2px solid #4CAF50; padding-bottom: 10px; }
        h2 { color: #666; margin-top: 30px; }
        .status { padding: 10px 20px; border-radius: 4px; display: inline-block; margin: 10px 0; }
        .status.running { background: #4CAF50; color: white; }
        .status.warning { background: #ff9800; color: white; }
        .status.error { background: #f44336; color: white; }
        .info-box { background: #e3f2fd; padding: 15px; border-radius: 4px; margin: 15px 0; }
        code { background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace; }
        .endpoint { margin: 10px 0; padding: 10px; background: #fafafa; border-left: 3px solid #4CAF50; }
        a { color: #1976d2; }
        ul { line-height: 1.8; }
    </style>
</head>
<body>
    <div class="container">
        <h1>QB-Bitrix24 Connector</h1>

        <div class="status running">Service Running</div>

        <h2>Endpoints</h2>
        <div class="endpoint">
            <strong>SOAP Service (for Web Connector):</strong><br>
            <code>http://{{ host }}:{{ port }}/soap/</code><br>
            <a href="/soap/?wsdl">View WSDL</a>
        </div>
        <div class="endpoint">
            <strong>Bitrix24 Webhook Handler:</strong><br>
            <code>http://{{ host }}:{{ port }}/bitrix24/webhook</code>
        </div>
        <div class="endpoint">
            <strong>Status API:</strong><br>
            <a href="/status">/status</a>
        </div>

        <h2>Setup Instructions</h2>

        <div class="info-box">
            <strong>Step 1: Configure Bitrix24 Webhook</strong>
            <ol>
                <li>Go to your Bitrix24: <a href="{{ bitrix_url }}" target="_blank">{{ bitrix_url }}</a></li>
                <li>Navigate to: <strong>Developer resources → Webhooks → Add inbound webhook</strong></li>
                <li>Copy the webhook URL (looks like: <code>https://hartzell.app/rest/1/abc123xyz/</code>)</li>
                <li>Edit <code>config.py</code> and set <code>BITRIX24_WEBHOOK</code> to this URL</li>
            </ol>
        </div>

        <div class="info-box">
            <strong>Step 2: Install QuickBooks Web Connector</strong>
            <ol>
                <li>Open QuickBooks Enterprise</li>
                <li>Open the Web Connector (usually in QB menu: File → App Management → Update Web Services)</li>
                <li>Click "Add Application"</li>
                <li>Select the file: <code>C:\\Users\\max\\qb-bitrix-connector\\qb_bitrix_connector.qwc</code></li>
                <li>When prompted in QuickBooks, authorize the connector</li>
                <li>In Web Connector, enter password: <code>change_this_password</code> (change this in config.py!)</li>
                <li>Set the sync interval (default: 5 minutes)</li>
            </ol>
        </div>

        <div class="info-box">
            <strong>Step 3: (Optional) Set up Bitrix24 Outbound Webhooks</strong>
            <p>To sync changes FROM Bitrix24 TO QuickBooks:</p>
            <ol>
                <li>In Bitrix24, go to: <strong>Developer resources → Webhooks → Add outbound webhook</strong></li>
                <li>Set handler URL to: <code>http://YOUR_PUBLIC_IP:8080/bitrix24/webhook</code></li>
                <li>Select events: ONCRMCONTACTADD, ONCRMCONTACTUPDATE, etc.</li>
            </ol>
            <p><em>Note: For outbound webhooks, this server must be accessible from the internet.</em></p>
        </div>

        <h2>Current Configuration</h2>
        <ul>
            <li><strong>SOAP Host:</strong> {{ host }}</li>
            <li><strong>SOAP Port:</strong> {{ port }}</li>
            <li><strong>Bitrix24 URL:</strong> {{ bitrix_url }}</li>
            <li><strong>Bitrix24 Webhook:</strong> {{ 'Configured' if bitrix_webhook else 'Not configured' }}</li>
        </ul>
    </div>
</body>
</html>
'''


def create_app():
    """Create and configure the Flask application"""

    # Initialize database
    init_db()

    # Create Flask app
    flask_app = Flask(__name__)

    # Register Bitrix24 webhook blueprint
    flask_app.register_blueprint(bitrix_webhook_bp)

    # Create SOAP application
    soap_app = Application(
        [QuickBooksWebConnectorService],
        tns='http://developer.intuit.com/',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )
    wsgi_soap_app = WsgiApplication(soap_app)

    # Mount SOAP app at /soap
    flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
        '/soap': wsgi_soap_app
    })

    @flask_app.route('/')
    def index():
        """Admin UI"""
        from config import BITRIX24_URL
        return render_template_string(
            ADMIN_TEMPLATE,
            host=SOAP_HOST,
            port=SOAP_PORT,
            bitrix_url=BITRIX24_URL,
            bitrix_webhook=bool(BITRIX24_WEBHOOK)
        )

    @flask_app.route('/status')
    def status():
        """Status API endpoint"""
        import sqlite3
        from config import DATABASE_PATH

        # Get some stats from database
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM id_mappings')
            mappings_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM sync_log WHERE created_at > datetime("now", "-24 hours")')
            recent_syncs = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM bitrix_to_qb_queue WHERE status = "pending"')
            pending_queue = cursor.fetchone()[0]

            conn.close()
        except:
            mappings_count = 0
            recent_syncs = 0
            pending_queue = 0

        return {
            'status': 'running',
            'version': '1.0.0',
            'active_sessions': len(QuickBooksWebConnectorService.sessions),
            'id_mappings': mappings_count,
            'syncs_last_24h': recent_syncs,
            'pending_queue': pending_queue,
            'bitrix24_configured': bool(BITRIX24_WEBHOOK)
        }

    return flask_app


def main():
    """Main entry point"""
    print("=" * 60)
    print("QB-Bitrix24 Connector")
    print("=" * 60)
    print(f"Starting service on http://{SOAP_HOST}:{SOAP_PORT}")
    print(f"SOAP endpoint: http://{SOAP_HOST}:{SOAP_PORT}/soap/")
    print(f"WSDL: http://{SOAP_HOST}:{SOAP_PORT}/soap/?wsdl")
    print(f"Bitrix24 webhook: http://{SOAP_HOST}:{SOAP_PORT}/bitrix24/webhook")
    print("=" * 60)

    if not BITRIX24_WEBHOOK:
        print("\nWARNING: BITRIX24_WEBHOOK not configured in config.py")
        print("The connector will sync FROM QuickBooks but not TO Bitrix24")
        print("Please configure the webhook URL to enable bi-directional sync.\n")

    app = create_app()
    app.run(host=SOAP_HOST, port=SOAP_PORT, debug=False, threaded=True)


if __name__ == '__main__':
    main()
