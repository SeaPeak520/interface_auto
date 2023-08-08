#!/bin/bash

#
useradd -d /home/jenkins jenkins

expect <<EOF
set timeout 10
spawn passwd jenkins
expect {
    "New password" {send "123456\r";exp_continue;}
    "Retype new password" {set timeout 500;send "123456\r";}
}
expect eof
EOF

chmod 755 /home/jenkins
