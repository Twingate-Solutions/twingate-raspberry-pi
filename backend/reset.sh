sudo apt remove twingate-connector
sudo rm /home/twingate/twingate-raspberry-pi/backend/store/.token_
sudo rm /home/twingate/twingate-raspberry-pi/backend/store/.tenant_
echo "{\"tenant\":\"\"}" > /home/twingate/twingate-raspberry-pi/frontend/tenantconf.json
./set_mode_ds.sh
cp ./set_mode_ds.sh ~
cp ./set_mode_pr.sh ~
cp ./reset.sh ~