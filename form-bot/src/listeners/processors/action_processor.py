import xml.etree.ElementTree as ET
import logging
import base64
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.sym_elements_parser import SymElementsParser
from ..simple_form.render import form_data, render_simple_form

class ActionProcessor:

    def __init__(self, bot_client, dazl_client, integration_party):
        self.bot_client = bot_client
        self.dazl_client = dazl_client
        self.integration_party = integration_party
        self.action_processed_message = MessageFormatter().format_message('Your action has been processed')

    async def process_im_action(self, action):

        logging.debug('action_processor/im_process')
        logging.debug(json.dumps(action, indent=4))
        form_id = SymElementsParser().get_form_id(action)
        id_split = form_id.split('::')
        form_id = id_split[0]

        processor = {
            'form_id': self.process_simple_form,
            'yes_no_id': self.process_yes_no,
            'proposal_form_id': self.process_proposal_form,
            'review_form_id': self.process_review_form
        }.get(form_id, self.process_default)

        await processor(action, id_split)

    async def process_simple_form(self, action, id_split):
        if SymElementsParser().get_form_values(action)['action'] == 'submit_button':
            self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.action_processed_message)
            form_contents = SymElementsParser().get_form_values(action)
            print(form_contents)
            self.response_message = MessageFormatter().format_message('Captured: {}'.format(form_contents))
            self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.response_message)

    async def process_yes_no(self, action, id_splitn):
        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.action_processed_message)
        button_action = SymElementsParser().get_action(action)

        if button_action == 'accept_button':
            self.response_message = MessageFormatter().format_message('Accepted!')

        elif button_action == 'reject_button':
            self.response_message = MessageFormatter().format_message('Rejected!')

        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.response_message)

    async def process_proposal_form(self, action, id_split):
        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.action_processed_message)
        button_action = SymElementsParser().get_action(action)
        stream_id = SymElementsParser().get_stream_id(action)
        form_contents = SymElementsParser().get_form_values(action)

        if button_action == 'submit_button':
            self.response_message = MessageFormatter().format_message('Accepted!')
            self.dazl_client.submit_create("Examples.Proposal:Proposal", {
                        'company': self.integration_party,
                        'employee': stream_id,
                        'proposalText': form_contents['proposal']
                    })
        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.response_message)

    async def process_review_form(self, action, id_split):
        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.action_processed_message)
        button_action = SymElementsParser().get_action(action)
        form_contents = SymElementsParser().get_form_values(action)
        cid = '690104a9c4161c1b7e5d2262f8c1747fbca7aaa7db8c6571c4e3b6932ee5b284'
        # id_split[1]
        # print(cid)

        if button_action == 'accept_button':
            self.dazl_client.submit_exercise(cid, 'Proposal_Accept')
            self.response_message = MessageFormatter().format_message('Accepted!')

        elif button_action == 'reject_button':
            self.dazl_client.submit_exercise(cid, 'Proposal_Reject')
            self.response_message = MessageFormatter().format_message('Rejected!')

        self.bot_client.get_message_client().send_msg(SymElementsParser().get_stream_id(action), self.response_message)

    async def process_default(self, action, id_split):
        logging.debug('Unknown form')

