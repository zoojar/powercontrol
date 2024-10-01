 net stop pwrcon
 SC DELETE pwrcon
 pip install -r .\requirements.txt
 .\venv\Scripts\pyinstaller.exe -F .\pwrcon.py      
 nssm install pwrcon C:\pwrcon\dist\pwrcon.exe    