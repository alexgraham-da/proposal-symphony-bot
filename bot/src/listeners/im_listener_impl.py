import logging
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.listeners.im_listener import IMListener
from sym_api_client_python.processors.sym_message_parser import SymMessageParser

from dazl import create

class SYMPHONY:
    InboundDirectMessage = 'SymphonyIntegration.InboundDirectMessage.InboundDirectMessage'
    OutboundDirectMessage = 'SymphonyIntegration.OutboundDirectMessage:OutboundDirectMessage'

class IMListenerImpl(IMListener):
    def __init__(self, sym_bot_client, integration_party, dazl_client):
        self.bot_client = sym_bot_client
        self.message_parser = SymMessageParser()
        self.integration_party = integration_party
        self.dazl_client = dazl_client

    async def on_im_message(self, im_message):
        logging.debug('IM Message Received')

        msg_text = self.message_parser.get_text(im_message)
        first_name = self.message_parser.get_im_first_name(im_message)
        stream_id = self.message_parser.get_stream_id(im_message)

        message = f'<messageML>Hello {first_name}, hope you are doing well!</messageML>'

        # Store in DAML ledger
        self.dazl_client.submit_create(SYMPHONY.InboundDirectMessage, {
                    'integrationParty': self.integration_party,
                    'symphonyChannel': first_name,
                    'symphonyUser': first_name,
                    'messageText': msg_text})

        # self.dazl_client.submit(commands)

        await self.bot_client.get_message_client().send_msg_async(stream_id, dict(message=message))

    async def on_im_created(self, im_created):
        logging.debug('IM created', im_created)
