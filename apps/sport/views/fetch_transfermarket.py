# It's better to get these from settings
from .update_players_transfermarket import AdminTransferMarketPlayersGetData as UpdateTransferMarketData


def AdminTransferMarketPlayersGetData(request):
    """Wrapper for the new TransferMarket update functionality"""
    return UpdateTransferMarketData(request)

