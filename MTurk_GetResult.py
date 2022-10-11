import json
import boto3
import xmltodict as xmltodict
import mysql.connector
import time

region_name = 'us-east-1'
aws_access_key_id = ''
aws_secret_access_key = ''

endpoint_url = 'https://mturk-requester.us-east-1.amazonaws.com'

mtc = boto3.client(
    'mturk',
    endpoint_url=endpoint_url,
    region_name=region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)

my_db = mysql.connector.connect(
    host="",
    user="",
    password="",
    database=""
)


while True:
    my_cursor = my_db.cursor()
    print("this will run after every 30 sec")


    my_cursor.execute("SELECT `HIT_number` FROM `HIT_Information` WHERE `Status` ='pending'")

    hit_ids = my_cursor.fetchall()
    temp_id = ""
    for x in hit_ids:
        for y in x:
            my_cursor.execute("SELECT `MTurk_HIT_ID` FROM `HIT_Information` WHERE `HIT_number`=" + str(y))
            MTurk_HIT_ID = my_cursor.fetchall()
            for z in MTurk_HIT_ID:
                for m in z:
                    temp_id = m
                    print(temp_id)
            if temp_id is not None:
                temp_id = temp_id.replace(" ", "")
                hit = mtc.get_hit(HITId=temp_id)
                print('Hit {} status: {}'.format(temp_id, hit['HIT']['HITStatus']))
                response = mtc.list_assignments_for_hit(
                    HITId=temp_id,
                    AssignmentStatuses=['Submitted', 'Approved'],
                    MaxResults=10,
                )

                assignments = response['Assignments']
                print('The number of submitted assignments is {}'.format(len(assignments)))
                for assignment in assignments:
                    worker_id = assignment['WorkerId']
                    assignment_id = assignment['AssignmentId']

                    # Approve the Assignment (if it hasn't already been approved)
                    if assignment['AssignmentStatus'] == 'Submitted':
                        print('Approving Assignment {}'.format(assignment_id))
                        mtc.approve_assignment(
                            AssignmentId=assignment_id,
                            RequesterFeedback='good',
                            OverrideRejection=False,
                        )

                results = []
                results.append(temp_id)

                for item in results:

                    assignmentsList = mtc.list_assignments_for_hit(
                        HITId=temp_id,
                        AssignmentStatuses=['Submitted', 'Approved'],
                        MaxResults=10
                    )
                    assignments = assignmentsList['Assignments']

                    answers = []
                    for assignment in assignments:

                        worker_id = assignment['WorkerId']
                        assignment_id = assignment['AssignmentId']

                        # Retrieve the value submitted by the Worker from the XML
                        answer_dict = xmltodict.parse(assignment['Answer'])
                        answer = answer_dict['QuestionFormAnswers']['Answer']['FreeText']

                        if assignment['AssignmentStatus'] == 'Submitted':
                            mtc.approve_assignment(
                                AssignmentId=assignment_id,
                                OverrideRejection=False
                            )
                if len(answer) != 0:
                    print('The Worker with ID {} submitted assignment {} and gave the answer "{}"'.format(worker_id,
                                                                                                          assignment_id,
                                                                                                          answer))

                sql_update = "Update HIT_Information set Status= 'Completed', Answer = %s , Worker_Name = %s where HIT_number = %s"
                tuple1 = (answer, worker_id, str(y))
                my_cursor.execute(sql_update, tuple1)

                my_db.commit()

                print("record(s) affected")
    time.sleep(300)
    my_cursor.close()
