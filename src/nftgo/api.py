import aiohttp
import furl

DOMAIN_PRODUCTION = 'api.nftgo.io'
DOMAIN_DEV = ''
DOMAIN_DEFAULT = DOMAIN_PRODUCTION


def api(path, params={}, domain=DOMAIN_DEFAULT, scheme="https"):
    return furl.furl(scheme=scheme, host=domain, path=path, args=params).url


async def search_collection(slug):
    slug = slug.lower()

    async with aiohttp.ClientSession() as session:
        return await (await session.get(api(path="/api/v1/collections", params={"keyword": slug.lower()}))).json()


async def collection(slug):
    slug = slug.lower()

    async with aiohttp.ClientSession() as session:
        return await (await session.get(api(path=f"/api/v1/collection/slug/{slug}"))).json()


async def nft(contract_address, token_id, blockchain='ETH'):
    blockchain = blockchain.upper()

    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(api(path=f"/api/v1/asset/{blockchain}/{contract_address}/{token_id}"))
        ).json()


async def whale_trades(time_s):
    time_ms = time_s * 1000

    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(api(path="/api/v1/bot/whales/activities", params={"cid": "all", "action": "all", "scroll": time_ms}))
        ).json()


async def block_trades(time_s):
    time_ms = time_s * 1000
    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(api(path="/api/v1/bot/whales/activities", params={"cid": "all", "action": "all", "scroll": time_ms}))
        ).json()


async def drops(start_time_s, limit, offset):
    start_time_ms = start_time_s * 1000

    async with aiohttp.ClientSession() as session:
        return await (await session.get(api(path="/api/v1/drop/projects", params={"startTime": start_time_ms, "limit": limit, "offset": offset}))).json()


class TimeRankEnum:
    _15M = "15m"
    _30M = "30m"
    _1H = "1h"
    _6H = "6h"
    _12H = "12h"
    _24H = "24h"
    _7D = "7d"
    _30D = "30d"


class OrderByEnum:
    MINT_NUM = "MintNum"
    MINT_VOLUME = "MintVolume"
    MINTER_NUM = "MinterNum"
    WHALE_NUM = "WhaleNum"
    TOTAL_GAS_FEE = "TotalGasFee"
    FIRST_MINT_TIME = "FirstMintTime"
    FOMO = "Fomo"


async def top_mint(time_rank: TimeRankEnum, order_by: OrderByEnum, is_asc: bool, only_listed, offset=0, limit=None):
    """
    :param offset:
    :param only_listed:
    :param limit:
    :param order_by:
    :param time_rank:
    :param is_asc: True for ASC, False for DESC
    """
    asc = 1 if is_asc else -1
    only_listed = 1 if only_listed else -1

    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(
                api(path="/api/v1/ranking/top-mint", params={'timeRank': time_rank, 'by': order_by, 'asc': asc, 'isListed': only_listed, 'limit': limit, 'offset': offset}))
        ).json()


async def mint_whale(time_rank: TimeRankEnum, order_by: OrderByEnum, is_asc: bool, offset=0, limit=None):
    """
    :param offset:
    :param limit:
    :param order_by:
    :param time_rank:
    :param is_asc: True for ASC, False for DESC
    """
    asc = 1 if is_asc else -1

    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(
                api(path="/api/v1/whales/data/list/mintWhale", params={'timeRank': time_rank, 'by': order_by, 'asc': asc, 'limit': limit, 'offset': offset}))
        ).json()


async def whale_mint_coll(time_rank: TimeRankEnum, order_by: OrderByEnum, is_asc: bool, only_listed: bool, offset=0, limit=None):
    """
    Get a list of collections that minted by whales in the specified time range.
    There is possibility that the list returned by api is incomplete, so you should call this function again with offset and limit to get the rest of the list.
    """
    asc = 1 if is_asc else -1
    only_listed = 1 if only_listed else -1

    async with aiohttp.ClientSession() as session:
        return await (
            await session.get(
                api(path="/api/v1/whales/data/list/whaleMintColl", params={'timeRank': time_rank, 'by': order_by, 'asc': asc, 'isListed': only_listed, 'limit': limit, 'offset': offset}))
        ).json()
