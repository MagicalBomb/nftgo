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
        return await (await session.get(api(path=f"/api/v1/collection/slug/{slug}")).json()


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
