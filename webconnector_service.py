"""
QuickBooks Web Connector SOAP Service

This implements the SOAP interface that the QuickBooks Web Connector polls.
The Web Connector calls these methods in sequence:
1. authenticate() - Verify credentials
2. sendRequestXML() - Get qbXML request to process
3. receiveResponseXML() - Receive QB's response
4. getLastError() - If there was an error
5. closeConnection() - Session complete

Reference: https://developer.intuit.com/app/developer/qbdesktop/docs/develop/web-connector
"""

import logging
import uuid
from datetime import datetime
from typing import Optional

from spyne import Application, Service, Unicode, Integer, rpc
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from config import SOAP_USERNAME, SOAP_PASSWORD
from sync_manager import SyncManager

logger = logging.getLogger(__name__)


class QuickBooksWebConnectorService(Service):
    """
    SOAP Service implementing the QuickBooks Web Connector interface.

    The Web Connector polls this service at regular intervals.
    """

    # Class-level storage for session state (in production, use Redis or similar)
    sessions = {}
    sync_manager = None

    @classmethod
    def get_sync_manager(cls):
        if cls.sync_manager is None:
            cls.sync_manager = SyncManager()
        return cls.sync_manager

    @rpc(Unicode, Unicode, _returns=Unicode(max_occurs=2))
    def authenticate(ctx, strUserName, strPassword):
        """
        Called first by Web Connector to authenticate.

        Returns:
        - [0]: Session ticket (GUID) if authenticated, empty string if failed
        - [1]: Empty string = use currently open company file
                "nvu" = no valid user (invalid credentials)
                "none" = no work to do
                Company file path = open specific company
        """
        logger.info(f"Authentication attempt from user: {strUserName}")

        # Verify credentials
        if strUserName != SOAP_USERNAME or strPassword != SOAP_PASSWORD:
            logger.warning(f"Authentication failed for user: {strUserName}")
            return ["", "nvu"]

        # Create session ticket
        ticket = str(uuid.uuid4())

        # Initialize session
        sync_mgr = QuickBooksWebConnectorService.get_sync_manager()
        requests = sync_mgr.get_pending_requests()

        QuickBooksWebConnectorService.sessions[ticket] = {
            'user': strUserName,
            'created': datetime.now(),
            'request_queue': requests,
            'current_request_index': 0,
            'last_error': '',
        }

        if not requests:
            logger.info("No work to do")
            return [ticket, "none"]

        logger.info(f"Authenticated. Session: {ticket}, Pending requests: {len(requests)}")

        # Return empty string to use currently open company file
        return [ticket, ""]

    @rpc(Unicode, Unicode, Unicode, Unicode, Integer, Integer, _returns=Unicode)
    def sendRequestXML(ctx, ticket, strHCPResponse, strCompanyFileName,
                       qbXMLCountry, qbXMLMajorVers, qbXMLMinorVers):
        """
        Called by Web Connector to get the next qbXML request.

        Args:
            ticket: Session ticket from authenticate()
            strHCPResponse: Host query response (first call) or empty
            strCompanyFileName: Path to company file
            qbXMLCountry: Country code (e.g., "US")
            qbXMLMajorVers: QB XML major version
            qbXMLMinorVers: QB XML minor version

        Returns:
            qbXML request string, or empty string if no more requests
        """
        session = QuickBooksWebConnectorService.sessions.get(ticket)
        if not session:
            logger.error(f"Invalid session ticket: {ticket}")
            return ""

        logger.info(f"sendRequestXML called. Company: {strCompanyFileName}, "
                   f"QB Version: {qbXMLMajorVers}.{qbXMLMinorVers}")

        # Get next request from queue
        queue = session['request_queue']
        index = session['current_request_index']

        if index >= len(queue):
            logger.info("No more requests in queue")
            return ""

        request_item = queue[index]
        qbxml_request = request_item.get('qbxml', '')

        logger.info(f"Sending request {index + 1}/{len(queue)}: {request_item.get('type', 'unknown')}")

        return qbxml_request

    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Integer)
    def receiveResponseXML(ctx, ticket, response, hresult, message):
        """
        Called by Web Connector with QB's response to our request.

        Args:
            ticket: Session ticket
            response: qbXML response from QuickBooks
            hresult: HRESULT (0 = success)
            message: Error message if hresult != 0

        Returns:
            Percentage complete (0-100), or negative for error
        """
        session = QuickBooksWebConnectorService.sessions.get(ticket)
        if not session:
            logger.error(f"Invalid session ticket: {ticket}")
            return -1

        queue = session['request_queue']
        index = session['current_request_index']

        logger.info(f"Received response for request {index + 1}/{len(queue)}")

        if hresult != "0" and hresult != 0:
            logger.error(f"QB Error - HRESULT: {hresult}, Message: {message}")
            session['last_error'] = f"HRESULT: {hresult} - {message}"
            return -1

        # Process the response
        if index < len(queue):
            request_item = queue[index]
            try:
                sync_mgr = QuickBooksWebConnectorService.get_sync_manager()
                sync_mgr.process_response(request_item, response)
            except Exception as e:
                logger.error(f"Error processing response: {e}")
                session['last_error'] = str(e)

        # Move to next request
        session['current_request_index'] = index + 1

        # Calculate progress percentage
        if len(queue) > 0:
            progress = int(((index + 1) / len(queue)) * 100)
        else:
            progress = 100

        logger.info(f"Progress: {progress}%")
        return progress

    @rpc(Unicode, _returns=Unicode)
    def getLastError(ctx, ticket):
        """
        Called by Web Connector when there's an error.

        Returns:
            Error message string
        """
        session = QuickBooksWebConnectorService.sessions.get(ticket)
        if not session:
            return "Invalid session"

        error = session.get('last_error', 'Unknown error')
        logger.error(f"getLastError called: {error}")
        return error

    @rpc(Unicode, _returns=Unicode)
    def closeConnection(ctx, ticket):
        """
        Called by Web Connector when session is complete.

        Returns:
            Status message
        """
        session = QuickBooksWebConnectorService.sessions.get(ticket)
        if session:
            completed = session['current_request_index']
            total = len(session['request_queue'])
            del QuickBooksWebConnectorService.sessions[ticket]
            logger.info(f"Connection closed. Processed {completed}/{total} requests")
            return f"OK - Processed {completed} requests"

        return "OK"

    @rpc(_returns=Unicode)
    def serverVersion(ctx):
        """Returns server version string"""
        return "QB-Bitrix24 Connector v1.0"

    @rpc(Unicode, _returns=Unicode)
    def clientVersion(ctx, strVersion):
        """
        Called with Web Connector version.

        Returns:
            Empty string to proceed, "W:message" for warning, "E:message" for error
        """
        logger.info(f"Web Connector version: {strVersion}")
        return ""  # Accept all versions


def create_wsgi_app():
    """Create the WSGI application for the SOAP service"""
    app = Application(
        [QuickBooksWebConnectorService],
        tns='http://developer.intuit.com/',
        in_protocol=Soap11(validator='lxml'),
        out_protocol=Soap11()
    )

    return WsgiApplication(app)


# For running directly with Flask
def create_flask_app():
    """Create Flask app with SOAP endpoint"""
    from flask import Flask
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from werkzeug.serving import run_simple

    flask_app = Flask(__name__)
    wsgi_app = create_wsgi_app()

    @flask_app.route('/')
    def index():
        return '''
        <h1>QB-Bitrix24 Connector</h1>
        <p>QuickBooks Web Connector SOAP service is running.</p>
        <p>WSDL: <a href="/soap/?wsdl">/soap/?wsdl</a></p>
        '''

    @flask_app.route('/status')
    def status():
        return {
            'status': 'running',
            'sessions': len(QuickBooksWebConnectorService.sessions),
            'version': '1.0'
        }

    # Mount SOAP app at /soap
    flask_app.wsgi_app = DispatcherMiddleware(flask_app.wsgi_app, {
        '/soap': wsgi_app
    })

    return flask_app


if __name__ == '__main__':
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    from config import SOAP_HOST, SOAP_PORT

    print(f"Starting QB-Bitrix24 Connector SOAP service on {SOAP_HOST}:{SOAP_PORT}")
    print(f"WSDL available at: http://{SOAP_HOST}:{SOAP_PORT}/soap/?wsdl")

    app = create_flask_app()
    app.run(host=SOAP_HOST, port=SOAP_PORT, debug=True)
