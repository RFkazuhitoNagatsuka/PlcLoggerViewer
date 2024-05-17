pipenv  install datetime
pipenv  install pandas
pipenv  install xlsxwriter
pipenv  install schedule
pip install pyinstaller

pyinstaller PlcLogger.py --onefile --clean
pyinstaller PlcViewer.py --onefile --clean

exit
pipenv --rm

