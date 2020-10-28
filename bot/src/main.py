import os
import sys
import asyncio
import logging
from pathlib import Path
from sym_api_client_python.configure.configure import SymConfig
from sym_api_client_python.auth.auth import Auth
from sym_api_client_python.auth.rsa_auth import SymBotRSAAuth
from sym_api_client_python.clients.sym_bot_client import SymBotClient
from listeners.im_listener_impl import IMListenerImpl
from listeners.room_listener_impl import RoomListenerImpl
from listeners.elements_listener_impl import ElementsListenerImpl

# DAZL
import dazl
from dazl import exercise

dazl.setup_default_logger(logging.INFO)

class SYMPHONY:
    InboundDirectMessage = 'SymphonyIntegration.InboundDirectMessage.InboundDirectMessage'
    OutboundMessage = 'SymphonyIntegration.OutboundMessage:OutboundMessage'

def configure_logging():
    log_dir = os.path.join(os.path.dirname(__file__), "logs")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        filename=os.path.join(log_dir, 'bot.log'),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filemode='w', level=logging.DEBUG
    )
    logging.getLogger("urllib3").setLevel(logging.WARNING)

def main():
    # load DAZL
    integration_party = 'Integration'
    url = os.getenv('DAML_LEDGER_URL')
    network = dazl.Network()
    network.set_config(url=url)
    # Configure log
    configure_logging()

    # Load configuration
    configure = SymConfig('../resources/config.json')
    configure.load_config()

    # Authenticate based on authType in config
    if ('authType' not in configure.data or configure.data['authType'] == 'rsa'):
        print('Python Client runs using RSA authentication')
        auth = SymBotRSAAuth(configure)
    else:
        print('Python Client runs using certificate authentication')
        auth = Auth(configure)
    auth.authenticate()

    # Initialize SymBotClient with auth and configure objects
    bot_client = SymBotClient(auth, configure)

    # Initialize datafeed service
    datafeed_event_service = bot_client.get_async_datafeed_event_service()

    async_client = makeClient(network, integration_party, bot_client)

    # Initialize listener objects and append them to datafeed_event_service
    # Datafeed_event_service polls the datafeed and the event listeners
    # respond to the respective types of events
    datafeed_event_service.add_im_listener(IMListenerImpl(bot_client, integration_party, async_client))
    datafeed_event_service.add_room_listener(RoomListenerImpl(bot_client))
    datafeed_event_service.add_elements_listener(ElementsListenerImpl(bot_client))


    # network.run_forever()

    # Create and read the datafeed
    print('Starting datafeed')
    # message = '<messageML>Hello {first_name}, hope you are doing well!</messageML>'
    # stream_id = 'JrsGM0ecerH87Bek5Evcgn___oqaZ0pOdA'
    # bot_client.get_message_client().send_msg(stream_id, dict(message=message))
    # datafeed_event_service.start_datafeed()
    try:
        # async network.aio_run()
        loop = asyncio.get_event_loop()
        # loop.run_until_complete(datafeed_event_service.start_datafeed())
        # session_task = asyncio.create_task(request_session(env.apiKey, env.secret))

        # group = asyncio.gather(*[datafeed_event_service.start_datafeed(), network.aio_run()])
        group = asyncio.gather(*[datafeed_event_service.start_datafeed(), network.aio_run()])
        loop.run_until_complete(group)
        # network.run_forever()
        print ('try')
    except (KeyboardInterrupt, SystemExit):
        None
    except:
        raise

def makeClient(network, party, bot_client):
    client = network.aio_party(party)

    @client.ledger_ready()
    def say_hello(event):
        logging.info("DA Marketplace matching engine is ready!")

    @client.ledger_created(SYMPHONY.OutboundMessage)
    def handle_outbound_message(event):
        cid = event.cid
        message = event.cdata['messageText']
        stream_id = event.cdata['symphonyStreamId']
        bot_client.get_message_client().send_msg(stream_id, dict(message=message))
        return [exercise(event.cid, 'Archive', {})]

    return client



if __name__ == "__main__":
    main()
