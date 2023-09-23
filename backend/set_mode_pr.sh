echo "tenant mode set:"
cat /home/twingate/twingate-raspberry-pi/backend/active_profile.json

echo "setting new mode: DS.."
echo "{\"active_profile\":\"PR\"}" > /home/twingate/twingate-raspberry-pi/backend/active_profile.json
echo "mode is now:"
cat /home/twingate/twingate-raspberry-pi/backend/active_profile.json