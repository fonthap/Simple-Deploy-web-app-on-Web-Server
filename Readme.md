## Simple Deploy web app on Web Server 
options

```
  -h, --help       show this help message and exit  
  --host string          Hostname or IP address of the remote server  
  --username string  Username for SSH connection   
  --password string  Password for SSH connection   
  --src string            source zip file path   
  --dest string          destination path to unzip ```  

  ```
## Command Exaple
  ```
  python.exe .\deploy.py --host 192.168.10.21 --username vagrant --password vagrant --src .\zip_file.zip --dest /home/vagrant/test.zip
  ```