newtenant=$1

echo "tenant current set:"
cat /home/twingate/twingate-raspberry-pi/frontend/tenantconf.json

echo "setting new tenant: ${newtenant}.."
echo "{\"tenant\":\"${newtenant}\"}" > /home/twingate/twingate-raspberry-pi/frontend/tenantconf.json
echo "tenant is now:"
cat /home/twingate/twingate-raspberry-pi/frontend/tenantconf.json