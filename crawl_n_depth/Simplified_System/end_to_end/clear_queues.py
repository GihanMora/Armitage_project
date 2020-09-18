import os
import sys

from azure.storage.queue import QueueClient

from os.path import dirname as up


three_up = up(up(up(__file__)))
# sys.path.insert(0, three_up)
sys.path.insert(0,'F:/from git/Armitage_project/crawl_n_depth')
from Simplified_System.end_to_end.execute_pipeline_via_queues import query_state_update_via_queue
from Simplified_System.end_to_end.execute_pipeline_via_queues import project_state_update_via_queue


def clear_all_queues():
    connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    avention_client = QueueClient.from_connection_string(connect_str, "avention-extraction-queue")
    c_page_client = QueueClient.from_connection_string(connect_str, "c-page--queue")
    crunchbase_client = QueueClient.from_connection_string(connect_str, "crunchbase-extraction-queue")
    deep_crawl_client = QueueClient.from_connection_string(connect_str, "deep-crawlinig-queue")
    dnb_client = QueueClient.from_connection_string(connect_str, "dnb-extraction-queue")
    feature_ex_client = QueueClient.from_connection_string(connect_str, "feature-extraction-queue")
    google_ad_client = QueueClient.from_connection_string(connect_str, "google-address-queue")
    google_cp_client = QueueClient.from_connection_string(connect_str, "google-cp-queue")
    google_tp_client = QueueClient.from_connection_string(connect_str, "google-tp-queue")
    initial_cr_client = QueueClient.from_connection_string(connect_str, "initial-crawling-queue")
    li_cp_client = QueueClient.from_connection_string(connect_str, "li-cp-extraction-queue")
    oc_client = QueueClient.from_connection_string(connect_str, "opencorporates-extraction-queue")
    owler_client = QueueClient.from_connection_string(connect_str, "owler-qa-queue")
    proj_comp_client = QueueClient.from_connection_string(connect_str, "project-completion-queue")
    proj_client = QueueClient.from_connection_string(connect_str, "projects-queue")
    simp_dump_client = QueueClient.from_connection_string(connect_str, "simplified-dump-queue")
    type_pred_client = QueueClient.from_connection_string(connect_str, "type-predict-queue")
    query_client = QueueClient.from_connection_string(connect_str, "query-queue")

    avention_client.Clear()
    c_page_client.Clear()
    crunchbase_client.Clear()
    deep_crawl_client.Clear()
    dnb_client.clear()
    feature_ex_client.clear()
    google_ad_client.clear()
    google_cp_client.clear()
    google_tp_client.clear()
    initial_cr_client.clear()
    li_cp_client.clear()
    oc_client.clear()
    owler_client.clear()
    proj_comp_client.clear()
    proj_client.clear()
    simp_dump_client.clear()
    type_pred_client.clear()
    query_client.clear()


# clear_all_queues()
# query_state_update_via_queue()
project_state_update_via_queue()
