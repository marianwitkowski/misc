import boto3, time, random, logging, os

USER_DATA = '''#!/bin/bash

sudo su
apt-get update
apt-get upgrade
apt-get -y install tinyproxy
sed -i '/Allow 127.0.0.1/d' /etc/tinyproxy/tinyproxy.conf
service tinyproxy restart

'''

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION_NAME = os.getenv("REGION_NAME")
AMI_ID = 'ami-0874dad5025ca362c'
SG_ID = 'sg-0494b628da56640e1'


####################################################################
def check_instance_running(instance_id, timeout=60):
    logging.info(f"{instance_id} Waiting for instance running"),
    try:
        i = int(timeout / 5)
        if i <= 0:
            i = 1
        while i > 0:
            logging.info(f"{instance_id} check is running....")
            data = get_instance_data(instance_id)
            is_running = data["State"]["Name"] in ['running']
            if is_running:
                return True
            time.sleep(5)
            i -= 1
        return False
    except Exception as e:
        logging.error(f"{instance_id} Exception occurred", exc_info=True)
        return None
    finally:
        pass


####################################################################
def get_instance_data(instance_id):
    try:
        ec2client = boto3.client('ec2',
                                 aws_access_key_id=AWS_ACCESS_KEY,
                                 aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                 region_name=REGION_NAME)
        response = ec2client.describe_instances(InstanceIds=[instance_id])
        return response['Reservations'][0]['Instances'][0]
    except Exception as e:
        logging.error(f"{instance_id} Exception occurred", exc_info=True)
        return None


####################################################################
def terminate_ec2(instance_id):
    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        region_name=REGION_NAME)
        ec2 = session.resource('ec2')
        logging.info(f"{instance_id} Terminating instance")
        result = ec2.instances.filter(InstanceIds=[instance_id]).terminate()
        return result
    except Exception as e:
        logging.error("{instance_id} Exception occurred", exc_info=True)
        return None


####################################################################
def start_ec2(instance_id):
    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        region_name=REGION_NAME)
        ec2 = session.resource('ec2')
        logging.info(f"{instance_id} Starting instance")
        result = ec2.instances.filter(InstanceIds=[instance_id]).start()
        return result
    except Exception as e:
        logging.error(f"{instance_id} Exception occurred", exc_info=True)
        return None


####################################################################
def stop_ec2(instance_id):
    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        region_name=REGION_NAME)
        ec2 = session.resource('ec2')
        logging.info(f"{format(instance_id)} Stop instance")
        result = ec2.instances.filter(InstanceIds=[instance_id]).stop()
        return result
    except Exception as e:
        logging.error(f"{instance_id} Exception occurred", exc_info=True)
        return None


####################################################################
def create_ec2():
    blockdevmap = [
        {
            'DeviceName': '/dev/xvdb',
            'Ebs': {
                'VolumeSize': 8,
                'DeleteOnTermination': True,
            }
        }
    ]

    try:
        session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY,
                                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                        region_name=REGION_NAME)
        ec2 = session.resource('ec2')

        subnets = list(ec2.subnets.filter())
        secure_random = random.SystemRandom()
        subnet = secure_random.choice(subnets)

        result = ec2.create_instances(
            ImageId=AMI_ID,
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName='proxy-key',
            SubnetId=subnet.id,
            SecurityGroupIds=[SG_ID],
            InstanceInitiatedShutdownBehavior='terminate',
            UserData=USER_DATA,
            BlockDeviceMappings=blockdevmap
        )
        instance_id = result[0].id
        ec2.create_tags(Resources=[instance_id], Tags=[
            {'Key': 'Name', 'Value': 'PROXY-FARM'}])
        return instance_id
    except Exception as e:
        logging.error("Exception occurred", exc_info=True)
        return None


#########################################################################
if __name__ == "__main__":
    instance_id = create_ec2() # create EC2 instance with user data
    if instance_id:
        start_ec2(instance_id) # start instance
        details = get_instance_data(instance_id) # get details
        logging.info(f"IP: {details['PublicIpAddress']}") # public IP
        time.sleep(60)
        terminate_ec2(instance_id) # terminate instance
