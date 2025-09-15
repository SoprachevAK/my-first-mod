package my.first_mod
{
  import net.wg.infrastructure.base.AbstractWindowView;
  import flash.text.TextField;

  public class HelloWorldWindow extends AbstractWindowView
  {
    public function HelloWorldWindow()
    {
      super();
    }

    override protected function onPopulate():void
    {
      super.onPopulate();
      width = 400;
      height = 100;
      window.title = 'My First Mod Window';
      window.useBottomBtns = false;

      var text:TextField = new TextField();
      text.width = 384;
      text.height = 84;
      text.x = 8;
      text.y = 8;
      text.htmlText = "<font face='$FieldFont' size='14' color='#8C8C7E'>Мод работает! Ура!</font>";

      addChild(text);
    }
  }
}