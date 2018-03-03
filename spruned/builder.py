from spruned.application import spruned_vo_service, settings
from spruned.application.cache import CacheFileInterface
from spruned.application.jsonrpc_server import JSONRPCServer
from spruned.daemon.electrod.electrod_reactor import build_electrod
from spruned.services.bitgo_service import BitGoService
from spruned.services.bitpay_service import BitpayService
from spruned.services.blockexplorer_service import BlockexplorerService
from spruned.services.blocktrail_service import BlocktrailService
from spruned.services.chainflyer_service import ChainFlyerService
from spruned.services.chainso_service import ChainSoService
from spruned.services.blockcypher_service import BlockCypherService
from spruned.services.electrod_service import ElectrodService

# system
cache = CacheFileInterface(settings.CACHE_ADDRESS)
storage = CacheFileInterface(settings.STORAGE_ADDRESS, compress=False)
electrod_daemon = build_electrod(settings.NETWORK, settings.ELECTROD_SOCKET, settings.ELECTROD_CONCURRENCY)
electrod_service = ElectrodService(settings.ELECTROD_SOCKET)


# services
chainso = ChainSoService(settings.NETWORK)
blocktrail = settings.BLOCKTRAIL_API_KEY and BlocktrailService(settings.NETWORK, api_key=settings.BLOCKTRAIL_API_KEY)
blockcypher = BlockCypherService(settings.NETWORK, api_token=settings.BLOCKCYPHER_API_TOKEN)
bitgo = BitGoService(settings.NETWORK)
chainflyer = ChainFlyerService(settings.NETWORK)
blockexplorer = BlockexplorerService(settings.NETWORK)
bitpay = BitpayService(settings.NETWORK)


# vo service
service = spruned_vo_service.SprunedVOService(electrod_service, cache=cache)
service.add_source(chainso)
service.add_source(bitgo)
service.add_source(blockexplorer)
service.add_source(blockcypher)
blocktrail and service.add_source(blocktrail)
service.add_source(chainflyer)
service.add_source(bitpay)

jsonrpc_server = JSONRPCServer(
    settings.JSONRPCSERVER_HOST,
    settings.JSONRPCSERVER_PORT,
    settings.JSONRPCSERVER_USER,
    settings.JSONRPCSERVER_PASSWORD
)
jsonrpc_server.set_vo_service(service)
