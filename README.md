# homeassistant_resol_dl2  
converts the crappy json data from dl2 to a mqtt message. Config for homeassistant auto configure is done as well. 
create cron, or whatever:  
```
*/5 * * * * python3 resol2mqtt.py --ip <resolIP> --broker <mqtt_ip> --port <mqtt_port> --topic dl2/sensor/ --device_name dl2 --client_id python-mqtt-dl2 --username <mqtt_username>  --password <mqtt password> 2>&1
```
