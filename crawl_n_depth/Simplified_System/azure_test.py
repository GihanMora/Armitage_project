import base64
import os, uuid
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage

# try:
#     print("Azure Queue storage v12 - Python quickstart sample")
#     # Quick start code goes here
# except Exception as ex:
#     print('Exception:')
#     print(ex)

# Retrieve the connection string for use with the application. The storage
# connection string is stored in an environment variable on the machine
# running the application called AZURE_STORAGE_CONNECTION_STRING. If the
# environment variable is created after the application is launched in a
# console or with Visual Studio, the shell or application needs to be
# closed and reloaded to take the environment variable into account.
from gensim.utils import unicode

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
print(connect_str)


# Create a unique name for the queue
# queue_name = "quickstartqueues-" + str(uuid.uuid4())
queue_name = "company_names"
print("Creating queue: " + queue_name)

# Instantiate a QueueClient which will be
# used to create and manipulate the queue
initial_crawling_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
deep_crawling_client = QueueClient.from_connection_string(connect_str, "deep-crawling-queue")
feature_extraction_client = QueueClient.from_connection_string(connect_str, "feature-extraction-queue")
cp_extraction_client_dnb_oc_li = QueueClient.from_connection_string(connect_str, "cp-extraction-queue-dnb-oc-li")
type_predict_client = QueueClient.from_connection_string(connect_str, "type-predict-queue")
crunchbase_extraction_client = QueueClient.from_connection_string(connect_str, "crunchbase-extraction-queue")
linkedin_extraction_client = QueueClient.from_connection_string(connect_str, "linkedin-extraction-queue")
opencorporates_extraction_client = QueueClient.from_connection_string(connect_str, "opencorporates-extraction-queue")
dnb_extraction_client = QueueClient.from_connection_string(connect_str, "dnb-extraction-queue")
google_address_client = QueueClient.from_connection_string(connect_str, "google-address-queue")
google_cp_client = QueueClient.from_connection_string(connect_str, "google-cp-queue")
google_tp_client = QueueClient.from_connection_string(connect_str, "google-tp-queue")
owler_qa_client = QueueClient.from_connection_string(connect_str, "owler-qa-queue")
# initial_crawl_completed_client = QueueClient.from_connection_string(connect_str, "incrawldone")
# queue_client2 = QueueClient.from_connection_string(connect_str, "testqueue2")
# queue_client1 = QueueClient.from_connection_string(connect_str, "testqueue1")
# Create the queue
# initial_crawl_completed_client.create_queue()
initial_crawling_client.create_queue()
deep_crawling_client.create_queue()
feature_extraction_client.create_queue()
cp_extraction_client_dnb_oc_li.create_queue()
type_predict_client.create_queue()
crunchbase_extraction_client.create_queue()
linkedin_extraction_client.create_queue()
opencorporates_extraction_client.create_queue()
dnb_extraction_client.create_queue()
google_address_client.create_queue()
google_cp_client.create_queue()
google_tp_client.create_queue()
owler_qa_client.create_queue()

print("\nAdding messages to the queue...")
# comp_list=[u'2 and 2',u'Answers Portals',u'aludo',u'Assignment Help Services',u'Atomi',u'School App Solution',u'Australian assignments help',u'Australian Help',u'Beauty Courses Online','Brain Pump','Careercake','CompNow','Convincely','CourseLink','Courses Direct','Cuberider','Devika','EDflix','EdPotential','Edquire','Edval','eMarking Assistant','Equilibrium','Essay Assignment Help','Fitzroy Academy','Foundr Magazine','Funnelback','Navitas','Gradchat','Gradconnection','Guiix','Heropa','Ignia','Inkerz','JR Academy','Kindersay','LabTech Training','Learnable','Literatu Pty Limited','LiveWebTutors','Logitrain','Management Tutors','MathsRepublic','Me3D','Medis Media','Milliped','Minded','NetSpot','Newcomb Digital','Omnium','OpenLearning','OpenSTEM Pty Ltd','Paddl Co.','Pallas ALS','ProgrammingHomeworkTutors','Prosper Education','Tutor On Demand','Vericus','Vidversity','Workstar','Compass','Seqta','Synergetic','Axcelerate','passtab','Schoolbox','Bibliotech','Edumate','Simon Schools','PC School']
comp_list = [u"caltex"]*10
# print(comp_list)
# for c in comp_list:
#     comp_name_client.send_message(c)
# Send several messages to the queue
# queue_client.send_message(u"First message")
# queue_client.send_message(u"Second message")
# saved_message = queue_client.send_message(u"Third message")
# for i in range(1):
#     queue_client2.send_message(u"Second queue message"+str(i))

# for i in range(10):
#     queue_client1.send_message(u"First queue message"+str(i))
# print("\nPeek at the messages in the queue...")
#
#     # Peek at messages in the queue
# peeked_messages = queue_client.peek_messages(max_messages=5)
#
# for peeked_message in peeked_messages:
#     # Display the message
#     print("Message: " + peeked_message.content)
#
# print("\nUpdating the third message in the queue...")
#
# # Update a message using the message saved when calling send_message earlier
# queue_client.update_message(saved_message, pop_receipt=saved_message.pop_receipt, \
#     content="Third message has been updated")
#
#
# print("\nReceiving messages from the queue...")
#
# # Get messages from the queue
# messages = queue_client.receive_messages(messages_per_page=5)