import boto3
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import HTMLQuestion

region_name = 'us-east-1'
aws_access_key_id = ''
aws_secret_access_key = '/FS'

endpoint_url = 'https://mturkmazonaws.com'

mtc = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

# This will return $10,000.00 in the MTurk Developer Sandbox
print(mtc.get_account_balance()['AvailableBalance'])

question_html_value = """
<html>
<head>
<meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
<script src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js' type='text/javascript'></script>
</head>
<body>
<!-- HTML to handle creating the HIT form -->
<form name='mturk_form' method='post' id='mturk_form' action='https://mturk-requester.us-east-1.amazonaws.com'>
<input type='hidden' value='' name='assignmentId' id='assignmentId'/>
<!-- This is where you define your question(s) --> 
<h1>Where is my Pepper robot? This is a test</h1>
<p><textarea name='answer' rows=3 cols=80></textarea></p>
<!-- HTML to handle submitting the HIT -->
<p><input type='submit' id='submitButton' value='Submit' /></p></form>
<script language='Javascript'>turkSetAssignmentID();</script>
</body>
</html>
"""

html_question = HTMLQuestion(question_html_value, 500)

html_layout = question_html_value
QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
        <HTMLContent><![CDATA[{}]]></HTMLContent>
        <FrameHeight>650</FrameHeight>
        </HTMLQuestion>"""
question_xml = QUESTION_XML.format(html_layout)

response = mtc.create_hit(Question=question_xml,
                          MaxAssignments=1,
                          Title="Answer a simple question to Pepper robot",
                          Description="Pepper robot",
                          Keywords="question, answer, research",
                          LifetimeInSeconds=60 * 60,
                          AssignmentDurationInSeconds=60 * 10,
                          Reward="0.01")

################
hit_type_id = response['HIT']['HITTypeId']
hit_id = response['HIT']['HITId']
print("\nCreated HIT: {}".format(hit_id))

print("\nYou can work the HIT here:")
# print (endpoint_url['preview'] + "?groupId={}".format(hit_id))

print("\nAnd see results here:")
# print (endpoint_url['manage'])

print("Your HIT has been created. You can see it at this link:")
print("https://mturk-requester.us-east-1.amazonaws.com={}".format(hit_type_id))
print("Your HIT ID is: {}".format(hit_id))
