#
import os
import wakeonlan
from time import sleep
from random import randrange

TV_IP_ADDR = '192.168.0.38'
TV_MAC_ADDR = '00:7C:2D:06:89:40'
NETFLIX_APP_ID = '11101200001'

from samsungtvws import SamsungTVWS, SamsungTVShortcuts

token_file = os.path.dirname(os.path.realpath(__file__)) + '/token.txt'
tv = SamsungTVWS(host=TV_IP_ADDR, port=8002, token_file=token_file)
remote_ctrl: SamsungTVShortcuts = tv.shortcuts()

# Wake up TV Set
wakeonlan.send_magic_packet(TV_MAC_ADDR)

# check is Netfix app running and close it
tv.rest_app_close(NETFLIX_APP_ID)
while True:
    app = tv.rest_app_status(NETFLIX_APP_ID)
    if not app.get("running"):
        break
    sleep(1)

# run netflix
tv.run_app(NETFLIX_APP_ID)
sleep(10)

# run remote controller buttons sequence
remote_ctrl.enter()  # ENTER
remote_ctrl.left()  # LEFT
for _ in range(2): remote_ctrl.down()  # x2 RIGHT
remote_ctrl.enter()  # ENTER

rnd_item = randrange(0, 9)
if rnd_item>0:
    for _ in randrange(rnd_item): remote_ctrl.right()

remote_ctrl.enter()  # ENTER
