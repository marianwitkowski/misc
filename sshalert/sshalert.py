import time
import subprocess, select
from smsapi.client import SmsApiPlClient

def poll_logfile(filename):
    f = subprocess.Popen(["tail", "-F", "-n", "0", filename], encoding="utf8", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        if p.poll(1):
            process_log_entry(f.stdout.readline())
        time.sleep(1)


def process_log_entry(logline): 
    # Look for phrases in log file
    if all(x in logline for x in ["ssh", "Accepted"]):
        send_sms(logline)
    return


def send_sms(msg):
    # Send SMS with SMSAPI.pl
    start = msg.find("for") + len("for")
    end = msg.find("from")
    substring = "Logged user: " + msg[start:end].strip()
    print(msg)
    token = "XXXXXXXXXXXXXXXX"
    client = SmsApiPlClient(access_token=token)
    send_results = client.sms.send(to="48XXXYYYZZZ", message=substring, normalize=True, nounicode=True)
    for result in send_results:
        print(result.id, result.points, result.error)


if __name__ == "__main__":
    poll_logfile("/var/log/secure") # CentOS location for log file