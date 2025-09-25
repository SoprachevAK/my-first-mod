from adisp import adisp_process, adisp_async
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from post_progression_common import TankSetupGroupsId
from gui.shared.gui_items.items_actions import factory as ActionsFactory

itemsCache = dependency.instance(IItemsCache) # type: IItemsCache

@adisp_async
@adisp_process
def getInstalledSlotIdx(vehicleCD, moduleIntCD, callback):

    def checkDevices():
        vehicle = itemsCache.items.getItemByCD(vehicleCD)
        for idx, op in enumerate(vehicle.optDevices.installed):
            if op is not None and moduleIntCD == op.intCD:
                callback(idx)
                return True
        return False

    # Проверяем текущий комплект
    if checkDevices(): return

    # Меняем комплект на противоположный
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    targetIndex = 1 if vehicle.optDevices.setupLayouts.layoutIndex == 0 else 0
    action = ActionsFactory.getAction(
        ActionsFactory.CHANGE_SETUP_EQUIPMENTS_INDEX,
        vehicle,
        TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS,
        targetIndex
    )
    # Дожидаемся смены
    result = yield ActionsFactory.asyncDoAction(action)
    
    # Проверяем новый текущий комплект
    if checkDevices(): return
    
    # Ничего не нашли
    callback(-1)


@adisp_process
def demount(vehicleCD, deviceCD):
    item = itemsCache.items.getItemByCD(deviceCD)
    vehicle = itemsCache.items.getItemByCD(vehicleCD)

    slotId = yield getInstalledSlotIdx(vehicleCD, deviceCD)
    if slotId == -1:
        print('Device not found on vehicle')
        return
    
    action = ActionsFactory.getAction(
        ActionsFactory.REMOVE_OPT_DEVICE,
        vehicle,
        item,
        slotId,
        False,
        forFitting=False,
        everywhere=True
    )
    result = yield ActionsFactory.asyncDoAction(action)