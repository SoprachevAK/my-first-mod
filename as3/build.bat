@echo off

rem ==== настройки ====
set "MXML_PATH=C:\apache-royale"

rem ==== компиляция ====
"%MXML_PATH%\royale-asjs\js\bin\mxmlc" -load-config+=build-config.xml --output=bin/my.first_mod.HelloWorldWindow.swf src/my/first_mod/HelloWorldWindow.as
