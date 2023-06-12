#!/bin/bash

# SSH connection parameters
remote_user="esroot"
remote_host="16.182.31.122"

# File to be copied
files=(
    "main.py"
    "details.yaml"
)
remote_directory="sachinthra/automation-test/"

scp_command="scp"

for file in "${files[@]}"; do
    scp_command+=" \"$file\""
done

scp_command+=" \"$remote_user@$remote_host:$remote_directory/\""

echo "copy"
# Copy the files to the remote host
eval "$scp_command"