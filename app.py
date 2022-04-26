#!python
import logging
from flask import Flask, request, abort
from telegram_send import send
import json
import datetime

app = Flask(__name__)
with open("allowed.json", 'r') as f:
    allowed_ids = json.load(f) 

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print(request.args)
        logging.info("POST request")
        rq = request.json
        logging.info(rq)
        dt = datetime.datetime.strptime(rq["received_at"].split(".")[0], "%Y-%m-%dT%H:%M:%S")
        msg = "Received at " + dt.strftime("%H:%M:%S %Y-%m-%d") + "\n"
        dev_id=(rq["end_device_ids"]["device_id"])
        location=None
        if(dev_id in allowed_ids.keys()):
            dev_name = allowed_ids[dev_id]
            if("join_accept" in rq.keys()):
                logging.info("Join request")
                msg = msg + f"{dev_name} has joined"
            if("uplink_message" in rq.keys()):
                logging.info("Uplink message")
                data = rq["uplink_message"]["decoded_payload"]
                if (dev_name == "tracker"):
                    msg=msg + f'{dev_name}: Alarm = {data["ALARM_status"]}\nBattery={data["BatV"]}'
                    location = (str(data["latitude"]),str(data["longitude"]))
                if (dev_name == "door"):
                    msg=msg+f'{dev_name}: Open={data["DOOR_OPEN_STATUS"]}\nAlarm={data["ALARM"]}\nBattery={data["BAT_V"]}'
            if(msg):
                logging.info(msg)
                if(location):
                    logging.info(location)
                send(messages=[msg], locations=location)
        else:
            logging.error(f"{dev_id} not allowed")
            abort(401)
        return 'success', 200
    else:
        logging.error("Upsupported request")
        abort(400)

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', datefmt='%Y/%m/%d %H:%M:%S', level=logging.INFO, filename='/root/webhooktest/iot.log')
    logging.getLogger().addHandler(logging.StreamHandler())
    app.run(host="0.0.0.0")

