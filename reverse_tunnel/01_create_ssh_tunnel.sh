# START THE SSH SERVICE -- WAIT A FEW SECONDS FOR THE SERVICE TO BOOT UP
/usr/sbin/sshd
sleep 2

# READ NODE NUMBER FROM DOCKER ENV
# CLASSROOM MACHINES FOLLOW PATTERN "F365-0XX"
echo "SETTING UP PORT FORWARDS FOR CLUSTER NODE #$NTH_CLUSTER_NODE"

#############################################################
#############################################################

# TUNNEL SSH TO CPU MACHINE
REAL_SSH_PORT="22"
SSH_PREFIX="222"
MIRRORED_SSH_PORT="$SSH_PREFIX$NTH_CLUSTER_NODE"

screen -dmS ssh_tunnel bash -c "sshpass -f /cluster/password.txt ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -R $MIRRORED_SSH_PORT:localhost:$REAL_SSH_PORT wickstjo@193.167.37.47"
echo "TUNNELING SSH ON PORT $MIRRORED_SSH_PORT"

#############################################################
#############################################################

# BOOT UP NODE SERVICES FROM COMPOSE FILE
screen -dmS docker_services bash -c "docker compose -f /cluster/node_services.yml up --force-recreate --renew-anon-volumes --remove-orphans"
echo "STARTED DOCKER COMPOSE SERVICES"

#############################################################
#############################################################

# TUNNEL NODE EXPORTER TO CPU MACHINE
REAL_NODE_PORT="9100"
NODE_PREFIX="333"
MIRRORED_NODE="$NODE_PREFIX$NTH_CLUSTER_NODE"

# REMEMBER: THIS REQUIRES "GatewayPorts: yes" in /etc/ssh/sshd_config
screen -dmS node_exporter_tunnel bash -c "sshpass -f /cluster/password.txt ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -g -R $MIRRORED_NODE:localhost:$REAL_NODE_PORT wickstjo@193.167.37.47"
echo "TUNNELING NODE_EXPORTER ON PORT $MIRRORED_NODE"