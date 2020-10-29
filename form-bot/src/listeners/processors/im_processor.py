import xml.etree.ElementTree as ET
import logging
import json
from sym_api_client_python.processors.message_formatter import MessageFormatter
from sym_api_client_python.processors.sym_message_parser import SymMessageParser

from ..simple_form.render import form_data, render_simple_form, render_review_form
from model import SYMPHONY, EXAMPLES

class IMProcessor:
    def __init__(self, bot_client, dazl_client):
        self.bot_client = bot_client
        self.dazl_client = dazl_client
        self.message_formatter = MessageFormatter()
        self.sym_message_parser = SymMessageParser()

    #reads message and processes it
    #look inside logs/example.log to see the payload (metadata representing event coming over the datafeed)
    def process(self, msg):
        logging.debug('im_processor/process_im_message()')
        logging.debug(json.dumps(msg, indent=4))
        self.help_message = dict(message = """<messageML>
                                    <h3>Type '/elements' to render a form</h3>
                                              </messageML>
                                           """)

        commands = self.sym_message_parser.get_text(msg)
        stream_id = self.sym_message_parser.get_stream_id(msg)

        if commands[0] == '/elements':
            self.message_to_send = render_simple_form('listeners/simple_form/html/simple_form.html')
        elif commands[0] == '/yes':
            self.message_to_send = render_simple_form('listeners/simple_form/html/yes_no_form.html')
        elif commands[0] == '/propose':
            self.message_to_send = render_simple_form('listeners/simple_form/html/proposal_form.html')
        elif commands[0] == '/review':
            proposals = self.dazl_client.find_active(EXAMPLES.Proposal)
            self.message_to_send = dict(message='<messageML>Listing proposals...</messageML>')
            # logging.debug(proposals)
            for cid, cdata in proposals.items():
                current_form = render_review_form('listeners/simple_form/html/review_form.html', cdata['proposalText'], cid)
                self.bot_client.get_message_client().send_msg(stream_id, current_form)
        else:
            self.message_to_send = self.help_message

        self.bot_client.get_message_client().send_msg(stream_id, self.message_to_send)
