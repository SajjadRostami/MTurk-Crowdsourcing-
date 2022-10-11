from oocsi import OOCSI
import mysql.connector
from mysql.connector import errorcode
import boto3
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import HTMLQuestion
import datetime
from webbrowser import open_new_tab


def receiveEvent(sender, recipant, event):
    print('from ', sender, ' -> ', event)

    # this will convert unicode string to plain string
    msg = str(event['message'])
    last_hit_id = str(event['username'])
    sender = str(sender)

    x, y = sender.split('_')

    connect_to_DB(last_hit_id)


def connect_to_DB(last_hit_id):
    hit_info = []

    my_db = stablish_database()

    my_cursor = my_db.cursor()

    my_cursor.execute("SELECT * FROM HIT_Information where HIT_number = " + last_hit_id)

    hit_information = my_cursor.fetchall()
    my_cursor.close()
    for x in hit_information:
        for y in x:
            hit_info.append(y)
    print(hit_info[3])
    create_HIT(hit_info)


def update_hit_database(hit_id, hit_information):
    my_db = stablish_database()

    my_cursor = my_db.cursor()

    sql = "UPDATE HIT_Information SET MTurk_HIT_ID =' " + str(hit_id) + " ' WHERE HIT_number =" + str(
        hit_information[9])

    my_cursor.execute(sql)

    my_db.commit()

    print("record(s) affected")


def stablish_database():
    my_db = mysql.connector.connect(
        host="..",
        user="",
        password="",
        database=""
    )
    return my_db


def create_HIT(hit_information):
    region_name = 'us-east-1'
    aws_access_key_id = ''
    aws_secret_access_key = '/FS'

    endpoint_url = 'https://mteast-1.amazonaws.com'

    mtc = boto3.client(
        'mturk',
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    print(mtc.get_account_balance()['AvailableBalance'])

    question_html_value = create_live_html(hit_information)

    html_question = HTMLQuestion(question_html_value, 500)

    QUESTION_XML = """<HTMLQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd">
            <HTMLContent><![CDATA[{}]]></HTMLContent>
            <FrameHeight>650</FrameHeight>
            </HTMLQuestion>"""
    question_xml = QUESTION_XML.format(question_html_value)
    reward_str = str(hit_information[3])
    title_str = str(hit_information[0])
    description_str = str(hit_information[8])
    keywords_str = str(hit_information[5]) + "," + str(hit_information[6]) + "," + str(hit_information[7])
    response = mtc.create_hit(Question=question_xml,
                              MaxAssignments=1,
                              Title=title_str,
                              Description=description_str,
                              Keywords=keywords_str,
                              LifetimeInSeconds=60 * 60,
                              AssignmentDurationInSeconds=60 * 10,
                              Reward=reward_str)

    hit_type_id = response['HIT']['HITTypeId']
    hit_id = response['HIT']['HITId']
    print("\nCreated HIT: {}".format(hit_id))

    print("Your HIT has been created. You can see it at this link:")
    print("https://mturk-requester.us-east-1.amazonaws.com={}".format(hit_type_id))
    print("Your HIT ID is: {}".format(hit_id))

    update_hit_database(str(hit_id), hit_information)


def create_live_html(hit_information):
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
    <h1> Please answer to the below question </h1>
   
    
    
     <p><img src=\"%s\" alt="no-image"> </p>
      <h1>  %s </h1>
    <!-- HTML to handle submitting the HIT -->
    <p>Please add the name of your current location at the end of your answer. For example Crow + Montreal, Canada.</p>
    <p>Please write no image if the image does not load for you. No image+ your location name</p>
    <p>We need to know your location to know the location diversity of the workers.</p>
    <p><textarea name='answer' rows=3 cols=80></textarea></p>
    
    <p><input type='submit' id='submitButton' value='Submit' /></p></form>
    <script language='Javascript'>turkSetAssignmentID();</script>
    </body>
    </html>
    """

    generated_dynamic_page = question_html_value % (hit_information[12],hit_information[4])
    return generated_dynamic_page


if __name__ == "__main__":
    o = OOCSI('pepper_receiver1', 'oocsi.id.tue.nl')
    o.subscribe('__test123__', receiveEvent)
