import paramiko
import time

hostname="10.14.144.67"
port=22
username="cliadmin"
password="onpremccs@123"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy() )
ssh.connect(hostname, port, username, password)


# stdin = ssh.exec_command("")
def displayOutput(conn):
    output = str(conn.recv(10000))
    print(output.replace("\\r", "").replace("\\n", "\n"))
    # print(output.replace("\\r", "").replace("\\n", "\n").replace("\\x1b[H\\x1b[J",""))

conn = ssh.invoke_shell()
print("Connect done")

displayOutput(conn)

conn.send("3\n")
time.sleep(1)
displayOutput(conn)

conn.send("1\n")
time.sleep(1)
displayOutput(conn)