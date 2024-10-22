# IN THE CONTAINER -- CREATE REVERSE TUNNEL TO CPU MACHINE

# UBUNTU BASE
# service ssh start && ssh -R 2222:localhost:22 wickstjo@193.167.37.47

# ALPINE BASE
screen -S reverse_tunnel
/usr/sbin/sshd && ssh -R 2222:localhost:22 wickstjo@193.167.37.47