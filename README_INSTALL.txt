In administrator PowerShell:
	Set-ExecutionPolicy RemoteSigned

Activate Kivy venv:
	.\kivy_env\Scripts\Activate.ps1

Install MS build tools from here:
	https://visualstudio.microsoft.com/visual-cpp-build-tools/

Install all requirements:
	pip install git+https://github.com/kivy/kivy
	#pip install git+https://github.com/denczo/kivy_examples
	pip install -r requirements.txt

Download .json confidentials from here:
	https://console.cloud.google.com/apis/credentials?pli=1&project=kitchendisplay-444122
and put them in ~/.credentials

Go to todoist.com => Click Avatar => Settings => Integrations => Developer and copy api key.
At terminal:
	keyring set todoist_api aarondeno11@gmai.com
	<paste api key when asked>