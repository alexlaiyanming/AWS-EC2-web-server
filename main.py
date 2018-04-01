#!/usr/bin/python

from flask import Flask
from flask import render_template , request
import boto3
import os
import botocore
from werkzeug import secure_filename
from flask import jsonify
app = Flask(__name__)
client = boto3.client(
    'ec2', 'ap-northeast-1'
)
@app.route("/")
def index():
    return render_template('index.html')
@app.route("/ec2/")
def ec2_list():
    response = client.describe_instances()
    instances = []
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instances.append(instance['InstanceId'])
    return render_template('ec2.html' , r1 = instances)      
@app.route("/ec2/start/", methods=['POST'])
def ec2_start():
    ec2_id = request.form['ec2_id']
    response = client.start_instances(
        InstanceIds=[
            ec2_id,
        ],
    )
    return "Running!!!"
@app.route("/ec2/stop/", methods=['POST'])
def ec2_stop():
    ec2_id = request.form['ec2_id']
    response = client.stop_instances(
        InstanceIds=[
           ec2_id,
        ],
    )
    return "Stopping!!"
@app.route("/ec2/snapshot/", methods=['POST'])
def ec2_snapshot():
    ec2_id = request.form['ec2_id']
    ec2 = boto3.resource('ec2' , region_name='ap-northeast-1')
    instance = ec2.Instance(ec2_id)
    volumes = instance.volumes.all()
    for v in volumes:
        vid = v.id
    response = client.create_snapshot(
        Description='test',
        VolumeId=vid,
    )
    return "Snapshotting!!"
@app.route("/s3/")
def s3():
    client2 = boto3.client('s3')
    r1 = client2.list_buckets()
    buckets = []
    for bucket in r1['Buckets']:
        buckets.append(bucket['Name'])
    return render_template('s3.html' , s3_buckets = buckets)
@app.route("/s3/list/", methods=['POST'])
def s3_list():
    bucket_name = request.form['s3_list']
    s3 = boto3.resource('s3')
    result = []
    mybucket = s3.Bucket(bucket_name)
    for object in mybucket.objects.all():
        result.append(object.key)
    return render_template('s3_list.html' , s3_list = result)
UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = set(['txt'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
@app.route("/s3/upload/", methods=['POST'])
def s3_upload():
    s3 = boto3.resource('s3')
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            s3_bucket = request.form['s3_bucket']
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            response =s3.meta.client.upload_file('/tmp/'+ filename, s3_bucket, filename)
    return 'Upload is complete!!!'
#@app.route("/demo/")
#def demo():
#    return render_template('demo.html')                     
if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=80)
