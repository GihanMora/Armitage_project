import os, uuid
from azure.storage.queue import QueueServiceClient, QueueClient, QueueMessage

connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')

queue_name = "testqueue"
queue_client1 = QueueClient.from_connection_string(connect_str, "testqueue1")
queue_client2 = QueueClient.from_connection_string(connect_str, "testqueue2")
# Receive messages one-by-one
while(True):
    messages1 = queue_client1.receive_messages()
    messages2 = queue_client2.receive_messages()
    for msg in messages1:
        print(msg.content)
        # do the task
        queue_client1.delete_message(msg)
    for msg in messages2:
        print(msg.content)
        # do the task
        queue_client2.delete_message(msg)

