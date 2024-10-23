# START THE SSH SERVICE
/usr/sbin/sshd

# START THE REVERSE SSH TUNNEL
screen -dmS reverse_tunnel bash -c "sshpass -f /cluster/password.txt ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -R 2222:localhost:22 wickstjo@193.167.37.47"