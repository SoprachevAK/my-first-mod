package my.first_mod
{
  import flash.display.Sprite;
  import flash.display.DisplayObject;
  import net.wg.infrastructure.base.AbstractView;
  import net.wg.data.constants.generated.LAYER_NAMES;
  import net.wg.gui.components.containers.MainViewContainer;
  import net.wg.gui.battle.views.BaseBattlePage;
  import net.wg.infrastructure.interfaces.IView;
  import flash.text.TextField;
  import flash.text.TextFormat;
  import flash.filters.DropShadowFilter;
  import flash.text.TextFormatAlign;
  import flash.text.AntiAliasType;
  import flash.events.Event;

  public class PiercingMainView extends AbstractView
  {

    private var infoBox:Sprite = new Sprite();
    private var infoText:TextField = new TextField();

    public function PiercingMainView()
    {
      super();

      // Закрашиваем прямоугольник 150x20 полупрозрачным зеленым цветом
      infoBox.graphics.beginFill(0, 0);
      infoBox.graphics.drawRect(0, 0, 150, 20);
      infoBox.graphics.endFill();

      // Двигаем на центр экрана
      infoBox.x = App.appWidth * 0.5 - infoBox.width / 2;
      infoBox.y = App.appHeight * 0.55;

      // Настраиваем текст
      var format:TextFormat = new TextFormat();
      format.size = 18;
      format.color = 0xFFFFFF;
      format.font = "$FieldFont";
      format.align = TextFormatAlign.CENTER;

      var filter:DropShadowFilter = new DropShadowFilter();
      filter.distance = 0;
      filter.angle = 0;
      filter.color = 0x000000;
      filter.alpha = 0.9;
      filter.blurX = filter.blurY = 2;
      filter.strength = 2;
      filter.quality = 10;

      infoText.selectable = false;
      infoText.mouseEnabled = false;
      infoText.antiAliasType = flash.text.AntiAliasType.ADVANCED;
      infoText.defaultTextFormat = format;
      infoText.setTextFormat(format);
      infoText.filters = [filter];

      infoBox.addChild(infoText);
      infoText.width = infoBox.width;
      infoText.height = infoBox.height;
      infoText.x = 0;
      infoText.y = 0;

      App.instance.addEventListener(Event.RESIZE, onAppResize);

    }

    override protected function configUI():void
    {
      super.configUI();

      // Получаем основной контейнер игры
      var viewContainer:MainViewContainer = App.containerMgr.getContainer(
          LAYER_NAMES.LAYER_ORDER.indexOf(LAYER_NAMES.VIEWS)
        ) as MainViewContainer;

      // Перебираем все дочерние компоненты и ищем BaseBattlePage
      for (var i:int = 0; i < viewContainer.numChildren; i++)
      {
        var child:DisplayObject = viewContainer.getChildAt(i);
        if (child is BaseBattlePage)
        {

          // Нашли BaseBattlePage, добавляем в него наш прямоугольник
          (child as IView).addChild(infoBox);
        }
      }
    }

    public function as_setText(value:String, color:uint):void
    {
      infoText.text = value;
      infoText.textColor = color;
    }

    private function onAppResize(event:Event):void
    {
      infoBox.x = App.appWidth * 0.5 - infoBox.width / 2;
      infoBox.y = App.appHeight * 0.55;
    }
  }
}