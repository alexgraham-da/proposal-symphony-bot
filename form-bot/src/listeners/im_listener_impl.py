import logging
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.listeners.im_listener import IMListener
from sym_api_client_python.processors.sym_message_parser import SymMessageParser

from .processors.im_processor import IMProcessor

from dazl import create

class SYMPHONY:
    InboundDirectMessage = 'SymphonyIntegration.InboundDirectMessage.InboundDirectMessage'
    OutboundMessage = 'SymphonyIntegration.OutboundMessage:OutboundMessage'

class IMListenerImpl(IMListener):
    def __init__(self, sym_bot_client, integration_party, dazl_client):
        self.bot_client = sym_bot_client
        self.message_parser = SymMessageParser()
        self.integration_party = integration_party
        self.dazl_client = dazl_client

        self.im_processor = IMProcessor(self.bot_client, self.dazl_client)

    async def on_im_message(self, im_message):
        logging.debug('IM Message Received')

        msg_text = self.message_parser.get_text(im_message)
        first_name = self.message_parser.get_im_first_name(im_message)
        stream_id = self.message_parser.get_stream_id(im_message)
        username = im_message['user']['username']
        print(username)

        message = f'<messageML>Message received, storing on ledger...</messageML>'

        # Store in DAML ledger
        self.dazl_client.submit_create(SYMPHONY.InboundDirectMessage, {
                    'integrationParty': self.integration_party,
                    'symphonyChannel': first_name,
                    'symphonyUser': first_name,
                    'symphonyStreamId': stream_id,
                    'messageText': msg_text})

        self.dazl_client.submit_create(SYMPHONY.OutboundMessage, {
                    'integrationParty': self.integration_party,
                    'symphonyStreamId':stream_id,
                    'messageText': message,
                    'attemptCount': 0})

        self.im_processor.process(im_message)

        # await self.bot_client.get_message_client().send_msg_async(stream_id, dict(message=message))

    async def on_im_created(self, im_created):
        logging.debug('IM created %s', im_created)
