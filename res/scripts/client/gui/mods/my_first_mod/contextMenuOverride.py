from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.opt_device import OptDeviceItemContextMenu
from gui.shared.utils.requesters import REQ_CRITERIA

from .demount import demount

itemsCache = dependency.instance(IItemsCache) # type: IItemsCache

# ==== Переопределение _generateOptions ====
orig_generateOptions = OptDeviceItemContextMenu._generateOptions

def new_generateOptionsRealVehicles(obj, *a, **k):
    original_result = orig_generateOptions(obj, *a, **k)

    inventoryVehicles = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
    installedVehicles = obj._getItem().getInstalledVehicles(inventoryVehicles.itervalues())
    
    submenuItems = [
        obj._makeItem('demountFrom:%d' % v.intCD, v.userName) for v in installedVehicles
    ]
    
    if len(submenuItems) == 0: return original_result
    
    original_result.append(obj._makeSeparator())
    original_result.append(obj._makeItem('demount', 'Демонтировать с танка:', optSubMenu=submenuItems))
    return original_result
    
OptDeviceItemContextMenu._generateOptions = new_generateOptionsRealVehicles


# ==== Переопределение onOptionSelect ====
orig_onOptionSelect = OptDeviceItemContextMenu.onOptionSelect

def new_onOptionSelect(obj, optionId):
    if optionId.startswith('demountFrom:'):
        veh_id = optionId.split(':')[1]
        demount(int(veh_id), obj._getItem().intCD) # вызов демонтажа
        return

    return orig_onOptionSelect(obj, optionId)

OptDeviceItemContextMenu.onOptionSelect = new_onOptionSelect