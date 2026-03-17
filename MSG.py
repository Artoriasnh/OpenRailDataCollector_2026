from Listener import *

topic_dict = {
    'TD' : '/topic/TD_ALL_SIG_AREA',
    'MVT' : '/topic/TRAIN_MVT_ALL_TOC',
    'VSTP': '/topic/VSTP_ALL',
    'TSR' : '/topic/TSR_ALL_ROUTE',
    'RTPPM' : '/topic/RTPPM_ALL',
    'SCHEDULE' : '/topic/CIF_ALL_FULL_DAILY'
}



##########################################
#MVT
##########################################
TM_MV_table_format = {
    'event_type':'TEXT',
    'gbtt_timestamp':'TEXT',
    'original_loc_stanox':'TEXT',
    'planned_timestamp':'TEXT',
    'timetable_variation':'TEXT',
    'original_loc_timestamp':'TEXT',
    'current_train_id':'TEXT',
    'delay_monitoring_point':'TEXT',
    'next_report_run_time':'TEXT',
    'reporting_stanox':'TEXT',
    'actual_timestamp':'TEXT',
    'correction_ind':'TEXT',
    'event_source':'TEXT',
    'train_file_address':'TEXT',
    'platform':'TEXT',
    'division_code':'TEXT',
    'train_terminated':'TEXT',
    'train_id':'TEXT',
    'offroute_ind':'TEXT',
    'variation_status':'TEXT',
    'train_service_code':'TEXT',
    'toc_id':'TEXT',
    'loc_stanox':'TEXT',
    'auto_expected':'TEXT',
    'direction_ind':'TEXT',
    'route':'TEXT',
    'planned_event_type':'TEXT',
    'next_report_stanox':'TEXT',
    'line_ind':'TEXT',
    'msg_queue_timestamp':'TEXT'
    }


TM_AC_table_format = {
        "schedule_source": 'TEXT',
        "train_file_address": 'TEXT',
        "schedule_end_date": 'TEXT',
        "train_id": 'TEXT',
        "tp_origin_timestamp": 'TEXT',
        "creation_timestamp": 'TEXT',
        "tp_origin_stanox": 'TEXT',
        "origin_dep_timestamp": 'TEXT',
        "train_service_code": 'TEXT',
        "toc_id": 'TEXT',
        "d1266_record_number": 'TEXT',
        "train_call_type": 'TEXT',
        "train_uid": 'TEXT',
        "train_call_mode": 'TEXT',
        "schedule_type": 'TEXT',
        "sched_origin_stanox": 'TEXT',
        "schedule_wtt_id": 'TEXT',
        "schedule_start_date": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}


TM_Cancel_table_format={
        "train_file_address": 'TEXT',
        "train_service_code": 'TEXT',
        "orig_loc_stanox": 'TEXT',
        "toc_id": 'TEXT',
        "dep_timestamp": 'TEXT',
        "division_code": 'TEXT',
        "loc_stanox": 'TEXT',
        "canx_timestamp": 'TEXT',
        "canx_reason_code": 'TEXT',
        "train_id": 'TEXT',
        "orig_loc_timestamp": 'TEXT',
        "canx_type": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}

TM_TR_table_format={
        "current_train_id": 'TEXT',
        "original_loc_timestamp": 'TEXT',
        "train_file_address": 'TEXT',
        "train_service_code": 'TEXT',
        "toc_id": 'TEXT',
        "dep_timestamp": 'TEXT',
        "division_code": 'TEXT',
        "loc_stanox": 'TEXT',
        "train_id": 'TEXT',
        "original_loc_stanox": 'TEXT',
        "reinstatement_timestamp": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}

TM_COO_table_format={
        "reason_code": 'TEXT',
        "current_train_id": 'TEXT',
        "original_loc_timestamp": 'TEXT',
        "train_file_address": 'TEXT',
        "train_service_code": 'TEXT',
        "toc_id": 'TEXT',
        "dep_timestamp": 'TEXT',
        "coo_timestamp": 'TEXT',
        "division_code": 'TEXT',
        "loc_stanox": 'TEXT',
        "train_id": 'TEXT',
        "original_loc_stanox": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}

TM_COI_table_format={
        "current_train_id": 'TEXT',
        "train_file_address": 'TEXT',
        "train_service_code": 'TEXT',
        "revised_train_id": 'TEXT',
        "train_id": 'TEXT',
        "event_timestamp": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}

TM_COL_table_format={
        "original_loc_timestamp": 'TEXT',
        "current_train_id": 'TEXT',
        "train_file_address": 'TEXT',
        "train_service_code": 'TEXT',
        "dep_timestamp": 'TEXT',
        "loc_stanox": 'TEXT',
        "train_id": 'TEXT',
        "original_loc_stanox": 'TEXT',
        "event_timestamp": 'TEXT',
        'msg_queue_timestamp':'TEXT'
}

MVT_table_format = {
    '0001':TM_AC_table_format,
    '0002':TM_Cancel_table_format,
    '0003':TM_MV_table_format,
    '0004':None,
    '0005':TM_TR_table_format,
    '0006':TM_COO_table_format,
    '0007':TM_COI_table_format,
    '0008':TM_COL_table_format,
    }

TM_MESSAGES = {
    "0001": "activation",
    "0002": "cancellation",
    "0003": "movement",
    "0004": "_unidentified",
    "0005": "reinstatement",
    "0006": "origin change",
    "0007": "identity change",
    "0008": "_location change"
    }








##########################################
#TD
##########################################
td_table_format ={
    'time':'TEXT',
    'area_id':'TEXT',
    'msg_type':'TEXT',
    'descr':'TEXT',
    'address':'TEXT',
    'data':'TEXT',
    'from_berth':'TEXT',
    'to_berth':'TEXT',
    'report_time':'TEXT',

    }

td_DY_table_format ={
    'time':'TEXT',
    'area_id':'TEXT',
    'msg_type':'TEXT',
    'descr':'TEXT',
    'address':'TEXT',
    'data':'TEXT',
    'from_berth':'TEXT',
    'to_berth':'TEXT',
    'report_time':'TEXT',
    'Type':'TEXT',
    'ID':'TEXT',
    'State':'TEXT',
    }

TD = {
    'C_BERTH_STEP':'CA',                      # Berth step      - description moves from "from" berth into "to", "from" berth is erased
    'C_BERTH_CANCEL':'CB',                    # Berth cancel    - description is erased from "from" berth
    'C_BERTH_INTERPOSE':'CC',                 # Berth interpose - description is inserted into the "to" berth, previous contents erased
    'C_HEARTBEAT':'CT',                       # Heartbeat       - sent periodically by a train describer
    'S_SIGNALLING_UDPATE':'SF',               # Signalling update
    'S_SIGNALLING_REFRESH':'SG',              # Signalling refresh
    'S_SIGNALLING_REFRESH_FINISHED':'SH',     # Signalling refresh finished
}



##########################################
#VSTP
##########################################
vstp_schedule_table_format = {
    "schedule_id": "TEXT",
    "transaction_type": "TEXT",
    "schedule_start_date": "TEXT",
    "schedule_end_date": "TEXT",
    "schedule_days_runs": "TEXT",
    "applicable_timetable": "TEXT",
    "CIF_bank_holiday_running": "TEXT",
    "CIF_train_uid": "TEXT",
    "train_status": "TEXT",
    "CIF_stp_indicator": "TEXT",
    "timestamp" : "TEXT"
}

vstp_schedule_segment_table_format = {
    "signalling_id": "TEXT",
    "uic_code": "TEXT",
    "atoc_code": "TEXT",
    "CIF_train_category": "TEXT",
    "CIF_headcode": "TEXT",
    "CIF_course_indicator": "TEXT",
    "CIF_train_service_code": "TEXT",
    "CIF_business_sector": "TEXT",
    "CIF_power_type": "TEXT",
    "CIF_timing_load": "TEXT",
    "CIF_speed": "TEXT",
    "CIF_operating_characteristics": "TEXT",
    "CIF_train_class": "TEXT",
    "CIF_sleepers": "TEXT",
    "CIF_reservations": "TEXT",
    "CIF_connection_indicator": "TEXT",
    "CIF_catering_code": "TEXT",
    "CIF_service_branding": "TEXT",
    "CIF_traction_class": "TEXT",
    "CIF_train_uid": "TEXT",
    "timestamp" : "TEXT"
}

vstp_schedule_location_table_format = {
    "scheduled_arrival_time": "TEXT",
    "scheduled_departure_time": "TEXT",
    "scheduled_pass_time": "TEXT",
    "public_arrival_time": "TEXT",
    "public_departure_time": "TEXT",
    "CIF_platform": "TEXT",
    "CIF_line": "TEXT",
    "CIF_path": "TEXT",
    "CIF_activity": "TEXT",
    "CIF_engineering_allowance": "TEXT",
    "CIF_pathing_allowance": "TEXT",
    "CIF_performance_allowance": "TEXT",
    "tiploc_id": "TEXT",
    "CIF_train_uid": "TEXT",
    "timestamp" : "TEXT"
}

vstp_table_format = {
    'schedule':vstp_schedule_table_format,
    'segment':vstp_schedule_segment_table_format,
    'location':vstp_schedule_location_table_format
}



##########################################
#RTPPM
##########################################
rtppm_OR_table_format = {
    "code": "TEXT",
    "keySymbol": "TEXT",
    "name": "TEXT",
    "Total": "TEXT",
    "OnTime": "TEXT",
    "Late": "TEXT",
    "CancelVeryLate": "TEXT",
    "PPM_rag": "TEXT",
    "PPM_text": "TEXT",
    "RollingPPM_trendInd": "TEXT",
    "RollingPPM_displayFlag": "TEXT",
    "RollingPPM_rag": "TEXT",
    "RollingPPM_text": "TEXT",
    "timestamp" : "TEXT"
}

rtppm_NS_table_format = {
    "sectorDesc": "TEXT",
    "sectorCode": "TEXT",
    "SectorPPM_Total": "TEXT",
    "SectorPPM_OnTime": "TEXT",
    "SectorPPM_Late": "TEXT",
    "SectorPPM_CancelVeryLate": "TEXT",
    "SectorPPM_PPM_rag": "TEXT",
    "SectorPPM_PPM_text": "TEXT",
    "SectorPPM_RollingPPM_trendInd": "TEXT",
    "SectorPPM_RollingPPM_rag": "TEXT",
    "SectorPPM_RollingPPM_text": "TEXT",
    "timestamp" : "TEXT"
}

rtppm_table_format = {
    'NationalPage_Operator':rtppm_OR_table_format,
    'NationalPage_Sector':rtppm_NS_table_format,
    'OOCPage':rtppm_OR_table_format,
    'OperatorPage':rtppm_OR_table_format,
    }




###################
table_format = {
    'TD_All': td_table_format,
    'TD':td_DY_table_format,
    'MVT': MVT_table_format,
    'VSTP':vstp_table_format,
    'RTPPM':rtppm_table_format
}


###################
Listener_dict = {
    'TD':TD_Listener,
    'MVT':TM_MVT_Listener,
    'VSTP':VSTP_Listener,
    'RTPPM':RTPPM_Listener
}



























