import time
from gopigo import *
import iot_connect
from iot_topics import *
import camera, awsUtils, tweet
import PollyApi, RekognitionApi, RekognitionUtils

def callbackSee(client, userdata, message):
	print "Topic="+message.topic
	image = camera.takePicture()
	awsUtils.copyLocalFileToS3(image)
	print "Picture uploaded"
	labels = RekognitionApi.detectLabels(reko, image)
	RekognitionUtils.printLabelsInformation(labels)
	faces = RekognitionApi.detectFaces(reko, image)
	newImage, faceCounter = RekognitionUtils.generateOutputImage(image, faces)
	faceMessage, labelMessage = RekognitionUtils.generateMessages(faceCounter, labels)
	print "Face message: " + faceMessage
	print "Label message: " + labelMessage
	PollyApi.speak(polly, faceMessage)
    	PollyApi.speak(polly, labelMessage)
	if message.payload == "tweet":
		tweet.tweet(newImage, faceMessage)
		print "Tweet sent"

def callbackSpeak(client, userdata, message):
	print "Topic="+message.topic
	print "Message="+message.payload
	if not message.payload:
		msg = "Nothing to say, sorry"
	else:
		msg = message.payload
	PollyApi.speak(polly, msg)

def callbackMove(client, userdata, message):
	print "Topic="+message.topic
	print "Message="+message.payload
	cmd = message.payload
	if cmd=="forward":
		fwd()	# Move forward
	elif cmd=="left":
		left()	# Turn left
	elif cmd=="right":
		right()	# Turn Right
	elif cmd=="backward":
		bwd()	# Move back
	elif cmd=="stop":
		stop()	# Stop
	elif cmd=="faster":
		increase_speed()	# Increase speed
	elif cmd=="slower":
		decrease_speed()	# Decrease speed
	else:
		print "Wrong Command, Please Enter Again"
	time.sleep(1)
	stop()

def scan():
	dist=(str)(us_dist(15))
	message = "The object is "+dist+" centimeters away"
	return message

def callbackScan(client, userdata, message):
	print "Topic="+message.topic
	print "Message="+message.payload
	cmd = message.payload
	if cmd=="scan":
		message = scan()
        elif cmd=="left":
		angle = angle + 30
		if (angle > 180):
			angle = 180
                servo(angle)
        elif cmd=="right":
		angle = angle - 30
		if (angle < 0):
			angle = 0
                servo(angle)
        elif cmd=="reset":
                servo(90)
        else:
                print "Wrong Command, Please Enter Again"

global angle, polly, reko

# Reset servo to center position
enable_servo()
angle = 90
servo(angle)

# Connect to IoT Gateway and subscribe to topics
client = iot_connect.connectIot()
client.subscribe(topicMove, 1, callbackMove)
client.subscribe(topicScan, 1, callbackScan)
client.subscribe(topicSpeak, 1, callbackSpeak)
client.subscribe(topicSee, 1, callbackSee)

polly = PollyApi.connectToPolly()
reko = RekognitionApi.connectToRekognition()
while True:
	time.sleep(10)

client.unsubscribe(topicMove)
client.unsubscribe(topicScan)
client.unsubscribe(topicSpeak)
client.unsubscribe(topicSee)
iot_connect.disconnectIot(client)
disable_servo()

