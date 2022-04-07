#!/usr/bin/python3
import paramiko
import sys

router_ip = sys.argv[1]
numberInterface = sys.argv[2]
router_username = "net"
router_password = "net"

ssh = paramiko.SSHClient()


def run_command_on_device(ip_address, username, password, command):
    """ Connect to a device, run a command, and return the output."""

    # Load SSH host keys.
    ssh.load_system_host_keys()
    # Add SSH host key when missing.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    total_attempts = 3
    for attempt in range(total_attempts):
        try:
            #print("Attempt to connect: %s towards %s" % (attempt, router_ip))
            # Connect to router using username/password authentication.
            ssh.connect(router_ip,
                        username=router_username,
                        password=router_password,
                        look_for_keys=False )
            # Run command.
            #print(command)
            ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(command)
            #print(command)
            # Read output from command.
            output = ssh_stdout.read().decode().strip("\n")
            #sys.stdout.write(output)
            # Close connection.
            ssh.close()
            return output

        except Exception as error_message:
            print("Unable to connect")
            print(error_message)


# Run function
numberInterface2 = int(numberInterface)
entireCommand = f'ip a | grep {numberInterface2}:{" "} | cut -d " " -f 2 | cut -d "@" -f 1'
#print(entireCommand)
nameInterface = run_command_on_device(router_ip, router_username, router_password, entireCommand)
print(nameInterface)
