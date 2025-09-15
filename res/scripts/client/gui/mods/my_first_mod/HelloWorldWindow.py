
from frameworks.wulf.gui_constants import WindowLayer
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.application import AppEntry

class HelloWorldWindow(AbstractWindowView):
  def onWindowClose(self):
    self.destroy()

HELLO_WORLD_WINDOW = "MY_MOD_HELLO_WORLD_WINDOW"

def setup():
  settingsViewSettings = ViewSettings(
    HELLO_WORLD_WINDOW,
    HelloWorldWindow,
    "my.first_mod.HelloWorldWindow.swf",
    WindowLayer.TOP_WINDOW,
    None,
    ScopeTemplates.VIEW_SCOPE,
  )
  g_entitiesFactories.addSettings(settingsViewSettings)
  

def show():
  appLoader = dependency.instance(IAppLoader) # type: IAppLoader
  app = appLoader.getApp() # type: AppEntry
  app.loadView(SFViewLoadParams(HELLO_WORLD_WINDOW))