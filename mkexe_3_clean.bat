rd /s /q exeFile
mkdir exeFile
copy dist\*.exe exeFile\.

rd /s /q dist
rd /s /q build
del Pipfile
del Pipfile.lock
del PlcLogger.spec
del PlcViewer.spec
