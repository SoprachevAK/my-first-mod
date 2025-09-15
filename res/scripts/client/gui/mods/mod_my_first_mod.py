from gui import SystemMessages
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from .my_first_mod.HelloWorldWindow import setup, show

MOD_VERSION = '{{VERSION}}'

# получаем ссылку на IHangarSpace
hangarSpace = dependency.instance(IHangarSpace) # type: IHangarSpace

# Мод загрузился
def init():
  print("[MY_FIRST_MOD] Hello, World! Mod version is %s" % MOD_VERSION)
  setup()

  # Подписываемся на загрузку ангара
  hangarSpace.onSpaceCreate += onHangarSpaceCreate

def onHangarSpaceCreate():
  # Отписываемся от загрузки ангара
  hangarSpace.onSpaceCreate -= onHangarSpaceCreate

  # Выводим уведомление в ангаре
  SystemMessages.pushMessage(
    text='Привет мир! Версия мода: %s' % MOD_VERSION,
    type=SystemMessages.SM_TYPE.InformationHeader,
    messageData={ 'header': 'MY_FIRST_MOD' }
  )

  show()