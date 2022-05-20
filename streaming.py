import asyncio
import pprint

from td.client import TDClient
from websockets import client  # Fixes a bug in websockets 10

from config import *


def authenticateAPI() -> TDClient:
    """Creates an authenticated API connection object

    Returns:
        TDClient: API object
    """
    TDSession = TDClient(client_id=CONSUMER_KEY, redirect_uri=REDIRECT_URL,
                         credentials_path=CREDENTIALS_PATH)
    TDSession.login()
    TDStreamingClient = TDSession.create_streaming_session()
    return TDStreamingClient


TDStreamingClient = authenticateAPI()
TDStreamingClient.level_one_futures(symbols=['/ES'], fields=list(range(0, 3)))


async def dataPipeline():
    await TDStreamingClient.build_pipeline()

    while True:
        data = await TDStreamingClient.start_pipeline()
        if 'data' in data:
            print('-'*20)
            content = data['data'][0]['content']
            pprint.pprint(content, indent=4)

        if False:
            await TDStreamingClient.unsubscribe(service='LEVELONE_FUTURES')
            await TDStreamingClient.close_stream()
            break

asyncio.run(dataPipeline())
