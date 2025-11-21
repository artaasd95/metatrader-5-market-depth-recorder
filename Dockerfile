# escape=`
FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["powershell", "-Command"]

RUN $ProgressPreference = 'SilentlyContinue'; `
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.12.1/python-3.12.1-amd64.exe" -OutFile "C:\\python-installer.exe"; `
    Start-Process -FilePath "C:\\python-installer.exe" -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' -Wait; `
    Remove-Item "C:\\python-installer.exe" -Force

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY .env ./.env

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["python", "src/orderbook_loader.py"]

