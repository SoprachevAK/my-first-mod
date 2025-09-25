@echo off

rem ==== настройки ====
set "MXML_PATH=C:\apache-royale"

rem ==== компиляция ====
set "MXMLC=%MXML_PATH%\royale-asjs\bin\mxmlc"

call "%MXMLC%" -load-config+=build-config.xml --output=bin/my.first_mod.PiercingMainView.swf src/my/first_mod/PiercingMainView.as
call "%MXMLC%" -load-config+=build-config.xml --output=bin/my.first_mod.HelloWorldWindow.swf src/my/first_mod/HelloWorldWindow.as
