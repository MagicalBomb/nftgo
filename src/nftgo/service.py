import datetime
import time

from nftgo import api


class TradeTracker:
    def __init__(self, trade_api):
        self._trade_api = trade_api
        self._initialized = False

    async def get(self, *args, **kwargs):
        if not self._initialized:
            await self._init_last_cursor()

        async for trade in self._iter():
            yield trade

    async def _iter(self):
        now = time.time()
        async for trade in self._iter_trade(self._latest_trade_time, now):
            self._latest_trade_time = max(self._latest_trade_time, trade['time'] / 1000)

            # if (trade.get('action') or trade.get('event')) not in ['buy', 'sell', 'sale']:
            #     continue

            yield trade

    async def _init_last_cursor(self):
        latest_trade = await (self._iter_trade(time.time() - 3600 * 24, time.time()).__aiter__()).__anext__()
        self._latest_trade_time = latest_trade['time'] / 1000
        self._initialized = True

    async def _iter_trade(self, start_s, end_s):
        """
        @return: iterable or empty list
        """
        jesponse = (await self._trade_api(end_s))["data"]

        while True:
            # If jseponse is empty list or None, break
            if not jesponse:
                break

            # Ensure ascending order
            trade_list = sorted(jesponse, reverse=True, key=lambda x: x["time"])

            # Yield trade
            for trade in filter(lambda t: t["time"] > start_s * 1000, trade_list):
                yield trade

            # If time of last trade greater than start_s, continue
            if trade_list[-1]["time"] > start_s * 1000:
                jesponse = (await self._trade_api(trade_list[-1]["time"] / 1000))["data"]
            else:
                break


class WhaleTradesTracker(TradeTracker):
    def __init__(self, ):
        super(WhaleTradesTracker, self).__init__(api.whale_trades)


class BlockTradesTracker(TradeTracker):
    def __init__(self):
        super(BlockTradesTracker, self).__init__(api.block_trades)


async def all_drops():
    start_time_s = time.time()
    offset = 0
    limit = 100
    jesponse = await api.drops(start_time_s, limit, offset)

    if jesponse["data"]["total"] > limit:
        drop_list = jesponse["data"]["projects"]
        for i in range(1, jesponse["data"]["total"] // limit + 1):
            drop_list += await api.drops(time.time(), limit, i * limit)["data"]["projects"]
        return drop_list
    else:
        return jesponse["data"]["projects"]


async def today_drops():
    all_drops_ = await all_drops()

    today_drops_ = []

    today = datetime.datetime.today().date()
    for drop in all_drops_:
        start_date = datetime.datetime.fromtimestamp(drop['startTime'] // 1000).date()
        if start_date == today:
            today_drops_.append(drop)
    return today_drops_


async def tommorrow_drops():
    all_drops_ = await all_drops()

    tommorrow_drops_ = []

    today = datetime.datetime.today().date()
    for drop in all_drops_:
        start_date = datetime.datetime.fromtimestamp(drop['startTime'] // 1000).date()
        if start_date == today + datetime.timedelta(days=1):
            tommorrow_drops_.append(drop)
    return tommorrow_drops_


async def all_whale_mint_coll(time_rank, order_by, is_asc: bool, only_listed: bool):
    """
    Almost same as api.whale_mint_coll, but this function would return all collections
    """
    limit = 100
    offset = 0

    jesponse = await api.whale_mint_coll(time_rank, order_by, is_asc, only_listed, limit, offset)
    if jesponse['errorCode'] != 0:
        raise ValueError("{}".format(jesponse))

    data = jesponse["data"]
    if len(data) > limit:
        return data + await all_whale_mint_coll(time_rank, order_by, is_asc, only_listed, limit, offset + limit)
    else:
        return data


async def search_slug(slug):
    jesponse = await api.search_collection(slug, 0, 100)
    return list(map(lambda e: e['slug'], jesponse["data"]['collections']))


async def all_collection_slug():
    batch_count = 200

    jesponse = await api.search_collection('', 0, batch_count)
    total = jesponse['data']['total']

    if total < batch_count:
        return list(map(lambda e: e['slug'], jesponse["data"]['collections']))
    else:
        result_list = list(map(lambda e: e['slug'], jesponse["data"]['collections']))
        for i in range(1, total // batch_count + 2):
            jesponse = await api.search_collection('', i * batch_count, batch_count)
            result_list += list(map(lambda e: e['slug'], jesponse["data"]['collections']))
        return result_list


async def resolve_blockchain_domain(domain, blockchain="ETH") -> str or None:
    """
    @return: blockchain address corresponding to domain, or None if not found
    """
    async with aiohttp.ClientSession() as session:
        jesponse = await (await session.get("https://api.nftgo.io/api/v1/account/resolve-name", params={"domain": domain, "bc": blockchain})).json()
    return jesponse.get("data", {}).get("address")


async def rarity(contract_address, token_id, blockchain='ETH'):
    """
    :return: rarity of token, or None if not found
    """
    nft_basic_info = await api.nft(contract_address, token_id, blockchain)
    return nft_basic_info['data'].get('rarity')
