import paramiko
import hashlib
import argparse
def create_ssh_client(host, username, password):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host,username=username,password=password)
        return client
    except paramiko.AuthenticationException:
        client.close()
        print('Authentication failed. Please check your SSH credentials.')
        quit()
        
def upload_file_to_server(src, dest, host, username, password):
    try:
        client = create_ssh_client(host, username, password)
        with client.open_sftp() as scp:
            dest_parts = dest.split('/')
            dest_folder = '/'.join(dest_parts[:-1])
            file_name = dest_parts[-1]
            if file_name.endswith('.zip'):
                if file_name in scp.listdir(dest_folder):
                    print("Step[Upload]: File already exists on the remote server")
                    client.close()
                    quit()
                else:
                    scp.put(src, dest)
                    sha256sum_local = hashlib.sha256(open(src, 'rb').read()).hexdigest()
                    stdin, stdout, stderr = client.exec_command(f'sha256sum {dest}')
                    sha256sum_remote = stdout.read().decode().split()[0]
                    if sha256sum_local == sha256sum_remote:
                        client.close()
                        print("Step[Upload]: File uploaded successfully")
                    else:
                        client.close()
                        print("Step[Upload]: File upload failed")
                        quit()
            else:
                print("Step[Upload]: Please specify a zip file as the destination")
                client.close()
                quit()
    except Exception as e:
        client.close()
        print(f"Step[Upload]: An error occurred: {str(e)}")
        quit()

def unzip_file_on_server(dest, host, username, password):
    src = dest
    dest = dest.rstrip('.zip')
    try:
        client = create_ssh_client(host, username, password)
        stdin, stdout, stderr = client.exec_command(f'unzip -o {src} -d {dest}')
        folder_name = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        if error:
            print(error)
            quit()
        else:
            print(f"Step[Unzip]: unzip {src} to {dest} successfully")
        client.close()
    except Exception as e:
        client.close()
        quit()

def copy_file_to_web_server(dest, host, username, password):
    dest = dest.rstrip('.zip')
    dest = '/'.join(dest.split('/'))
    try:
        client = create_ssh_client(host, username, password)
        stdin, stdout, stderr = client.exec_command(f'sudo rm -rf /usr/share/nginx/html/*')
        stdin, stdout, stderr = client.exec_command(f'sudo cp -r {dest}/* /usr/share/nginx/html')
        error = stderr.read().decode().strip()
        if error:
            print(error)
        else:
            print("Step[Copy]: Files copied to web server successfully")
        client.close()
    except Exception as e:
        print(f"Step[Copy]: An error occurred: {str(e)}")
        client.close()
        quit()

def check_service_status(service_name,host, username, password):
    try:
        client = create_ssh_client(host, username, password)
        stdin, stdout, stderr = client.exec_command(f'systemctl is-active {service_name}')
        status = stdout.read().decode().strip()
        if status == 'active':
            print(f"Step[Check]: The {service_name} service is running")
        else:
            print(f"Step[Check]: The {service_name} service is not running")
            quit()
        client.close() 
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        client.close()
        quit()

def restart_service(service_name,host, username, password):
    try:
        client = create_ssh_client(host, username, password)
        stdin, stdout, stderr = client.exec_command(f'sudo systemctl restart {service_name}')
        error = stderr.read().decode().strip()
        if error:
            print(error)
            client.close()
        else:
            print(f"Step[Restart]: The {service_name} service has been restarted successfully")
        client.close()  
    except Exception as e:
        print(f"Step[Restart]: An error occurred: {str(e)}")
        client.close()  
        quit()

def cleanup(dest, host, username, password):
    dest = dest.rstrip('.zip')
    try:
        client = create_ssh_client(host, username, password)
        stdin, stdout, stderr = client.exec_command(f'sudo rm -rf {dest}*')
        error = stderr.read().decode().strip()
        if error:
            print(error)
            quit()
        else:
            print("Step[Cleanup]: Cleaned up the remote server successfully")
        client.close()
    except Exception as e:
        print(f"Step[Cleanup]: An error occurred: {str(e)}")
        client.close()
        quit()

if __name__ == "__main__":
    service_name = 'nginx' 
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="Hostname or IP address of the remote server")
    parser.add_argument("--username", help="Username for SSH connection")
    parser.add_argument("--password", help="Password for SSH connection")
    parser.add_argument("--src", help="source zip file path")
    parser.add_argument("--dest", help="destination path to unzip")
    args = parser.parse_args()
    username = str(args.username)
    host = str(args.host)
    password = str(args.password)
    src = str(args.src)
    dest = str(args.dest)

    check_service_status(service_name,host, username, password)
    upload_file_to_server(src, dest, host, username, password)
    unzip_file_on_server(dest, host, username, password)
    copy_file_to_web_server(dest, host, username, password)
    check_service_status(service_name,host, username, password)
    restart_service(service_name,host, username, password)
    check_service_status(service_name,host, username, password)
    cleanup(dest, host, username, password)