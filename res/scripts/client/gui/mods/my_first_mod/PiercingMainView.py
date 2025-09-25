import typing
import math
from ProjectileMover import EntityCollisionData
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.app_loader.settings import APP_NAME_SPACE
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.personality import ServicesLocator
from items.components.shared_components import MaterialInfo
from AvatarInputHandler import gun_marker_ctrl
from Vehicle import Vehicle as VehicleEntity
from DestructibleEntity import DestructibleEntity
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers import dependency

from .color import lerpColor

import BigWorld


MY_FIRST_MOD_PIERCING_MAIN_VIEW = "MY_FIRST_MOD_PIERCING_MAIN_VIEW"

RICOCHET_COLOR = 0xa85dfc
NOT_ARMOR_COLOR = 0xbbbbbb
GREEN_COLOR = 0x00FF00
SOFT_GREEN_COLOR = 0x48f32c
RED_COLOR = 0xFF0000
SOFT_RED_COLOR = 0xf32c2c

def penetrationProbability(piercing, totalArmor, piercingPowerRandomization):
  P0 = float(piercing)
  A  = float(totalArmor)
  x  = float(piercingPowerRandomization)

  # Границы клампа
  L = P0 * (1.0 - x)
  U = P0 * (1.0 + x)

  k = 3
  sigma = (x * P0) / k
  mu = P0

  # Быстрые случаи
  if A <= L: return 1.0
  if A >= U: return 0.0

  # Стандартная нормальная CDF через erf
  def Phi(z): return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

  zL = (L - mu) / sigma
  zU = (U - mu) / sigma
  zA = (A - mu) / sigma

  denom = Phi(zU) - Phi(zL)
  if denom <= 1e-15: return 1.0 if A <= mu else 0.0

  p = (Phi(zU) - Phi(zA)) / denom

  # Численная обрезка
  if p < 0.0: p = 0.0
  if p > 1.0: p = 1.0
  return p

class PiercingMainView(View):

  sessionProvider = dependency.descriptor(IBattleSessionProvider) # type: IBattleSessionProvider
  
  def __init__(self, *args, **kwargs):
    super(PiercingMainView, self).__init__(*args, **kwargs)
    self.shotResultResolver = gun_marker_ctrl.createShotResultResolver() # type: gun_marker_ctrl._CrosshairShotResults
    self.sessionProvider.shared.crosshair.onGunMarkerStateChanged += self.onGunMarkerStateChanged

  def computeTotalEffectiveArmor(self, hitPoint, collision, direction, shell):
    # type: (Math.Vector3, typing.Optional[EntityCollisionData], Math.Vector3, Shell) -> (float, Boolean)

    if collision is None: return (0.0, False)

    entity = collision.entity
    collisionsDetails = self.shotResultResolver._getAllCollisionDetails(hitPoint, direction, entity) # type: typing.List[SegmentCollisionResultExt]
    if not collisionsDetails: return (0.0, False)

    totalArmor = 0.0
    ignoredMaterials = set()
    isRicochet = False
    hitArmor = False
    jetStartDist = None
    jetLoss = 0.0
    jetLossPPByDist = self.shotResultResolver._SHELL_EXTRA_DATA[shell.kind].jetLossPPByDist # сколько теряет кумулятивная струя в воздухе на метр

    for c in collisionsDetails:
      if not self.shotResultResolver._CrosshairShotResults__isDestructibleComponent(entity, c.compName): break

      material = c.matInfo # type: MaterialInfo
      if material is None or material.armor is None: continue

      key = (c.compName, material.kind)
      if key in ignoredMaterials: continue

      hitAngleCos = c.hitAngleCos if material.useHitAngle else 1.0
      totalArmor += self.shotResultResolver._computePenetrationArmor(shell, hitAngleCos, material)

      isRicochet |= self.shotResultResolver._shouldRicochet(shell, hitAngleCos, material)
      hitArmor |= material.vehicleDamageFactor > 0

      if material.collideOnceOnly: ignoredMaterials.add(key)
      if material.vehicleDamageFactor:
        # вычисляем потери кумулятивной струи в воздухе ПЕРЕД основным слоем
        if jetStartDist: jetLoss = (c.dist - jetStartDist) * jetLossPPByDist
        break

      if jetStartDist is None and jetLossPPByDist > 0.0:
        jetStartDist = c.dist + material.armor * 0.001 # точка старта за бронёй

    return (float(totalArmor), isRicochet, hitArmor, jetLoss)

  def computeResult(self, hitPoint, direction, collision):
    if not collision: return None

    entity = collision.entity
    if not isinstance(entity, (VehicleEntity, DestructibleEntity)): return None

    player = BigWorld.player()
    if player is None: return None

    vDesc = player.getVehicleDescriptor()
    shell = vDesc.shot.shell
    ppDesc = vDesc.shot.piercingPower
    maxDist = vDesc.shot.maxDistance
    piercingPowerRandomization = shell.piercingPowerRandomization
    dist = (hitPoint - player.getOwnVehiclePosition()).length
    

    # Актуальное пробитие на дистанции
    distPiercingPower = self.shotResultResolver._computePiercingPowerAtDist(ppDesc, dist, maxDist, 1)

    # Список всех столкновений с колиженом танка
    collisionsDetails = self.shotResultResolver._getAllCollisionDetails(hitPoint, direction, entity)
    if collisionsDetails is None: return (distPiercingPower, None, None, None, None, None)

    totalArmor, isRicochet, hitArmor, jetLoss = self.computeTotalEffectiveArmor(hitPoint, collision, direction, shell)

    return (distPiercingPower, totalArmor, isRicochet, hitArmor, jetLoss, piercingPowerRandomization)

  def onGunMarkerStateChanged(self, markerType, hitPoint, direction, collision):
    result = self.computeResult(hitPoint, direction, collision)
    if result is None: return self.as_setText('', 0)

    piercing, totalArmor, isRicochet, hitArmor, jetLoss, piercingPowerRandomization = result

    if piercing is None: return self.as_setText('', 0)
    if totalArmor is None: return self.as_setText('%d/-' % round(piercing), GREEN_COLOR)

    realPiercing = piercing * max(0, (1 - jetLoss))

    targetColor = GREEN_COLOR
    prob = 0
    if isRicochet: targetColor = RICOCHET_COLOR
    elif not hitArmor: targetColor = NOT_ARMOR_COLOR
    elif realPiercing <= 0.0: targetColor = RED_COLOR
    elif totalArmor <= 0.0: targetColor = GREEN_COLOR
    else:
      prob = penetrationProbability(realPiercing, totalArmor, piercingPowerRandomization)
      if prob <= 0: targetColor = RED_COLOR
      elif prob >= 1: targetColor = GREEN_COLOR
      else: targetColor = lerpColor(SOFT_RED_COLOR, SOFT_GREEN_COLOR, prob, mid_L_shift=+10.0, mid_C_boost=1.15)

    self.as_setText('%d/%d' % (round(realPiercing), round(totalArmor)), targetColor)

  def as_setText(self, text, color):
    self.flashObject.as_setText(text, color)

def setup():
  settingsViewSettings = ViewSettings(
    MY_FIRST_MOD_PIERCING_MAIN_VIEW,
    PiercingMainView,
    "my.first_mod.PiercingMainView.swf",
    WindowLayer.WINDOW,
    None,
    ScopeTemplates.DEFAULT_SCOPE,
  )
  g_entitiesFactories.addSettings(settingsViewSettings)

  def onAppInitialized(event):
    if event.ns == APP_NAME_SPACE.SF_BATTLE:
      app = ServicesLocator.appLoader.getApp(event.ns) # type: AppEntry
      app.loadView(SFViewLoadParams(MY_FIRST_MOD_PIERCING_MAIN_VIEW))

  g_eventBus.addListener(events.AppLifeCycleEvent.INITIALIZED, onAppInitialized, EVENT_BUS_SCOPE.GLOBAL)