import logging
import json
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from sym_api_client_python.processors.sym_elements_parser import SymElementsParser
from sym_api_client_python.listeners.elements_listener import ElementsActionListener

from .processors.action_processor import ActionProcessor

class ElementsListenerImpl(ElementsActionListener):
    """Example implementation of IMListener

        sym_bot_client: contains clients which respond to incoming events

    """
    def __init__(self, sym_bot_client, dazl_client, integration_party):
        self.bot_client = sym_bot_client
        self.dazl_client = dazl_client
        self.integration_party = integration_party
        self.action_processor = ActionProcessor(self.bot_client, self.dazl_client, self.integration_party)
    async def on_elements_action(self, action):
        stream_type = self.bot_client.get_stream_client().stream_info_v2(SymElementsParser().get_stream_id(action))
        if stream_type['streamType']['type'] == 'IM':
            await self.action_processor.process_im_action(action)

# class ElementsListenerImpl(ElementsActionListener):
#     def __init__(self, sym_bot_client):
#         self.bot_client = sym_bot_client
#
#     async def on_elements_action(self, action):
#         logging.debug('Elements Action Recieved: {}'.format(json.dumps(action, indent=4)))
