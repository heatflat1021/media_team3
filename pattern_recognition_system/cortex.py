from typing import List
import websocket #'pip install websocket-client' for install
from datetime import datetime
import json
import ssl
import time
import sys
import math
from collections import Counter

import numpy as np
import tensorflow as tf

# define request id
QUERY_HEADSET_ID                    =   1
CONNECT_HEADSET_ID                  =   2
REQUEST_ACCESS_ID                   =   3
AUTHORIZE_ID                        =   4
CREATE_SESSION_ID                   =   5
SUB_REQUEST_ID                      =   6
SETUP_PROFILE_ID                    =   7
QUERY_PROFILE_ID                    =   8
TRAINING_ID                         =   9
DISCONNECT_HEADSET_ID               =   10
CREATE_RECORD_REQUEST_ID            =   11
STOP_RECORD_REQUEST_ID              =   12
EXPORT_RECORD_ID                    =   13
INJECT_MARKER_REQUEST_ID            =   14
SENSITIVITY_REQUEST_ID              =   15
MENTAL_COMMAND_ACTIVE_ACTION_ID     =   16
MENTAL_COMMAND_BRAIN_MAP_ID         =   17
MENTAL_COMMAND_TRAINING_THRESHOLD   =   18

DATA_LENGTH = 640
MOTION_SENSING_FREQUENCY = 32
REFERENCE_SENSING_SECONDS = 8
THRESHOLD_ANGLE = 20
EEG_COMMAND_GENERATION_SKIP_RATE = 16
COMMAND_CASH_LENGTH = 10

mot_file_path = './../mot.txt'
eeg_file_path = './../eeg.txt'
eeg_commands = ['NEUTRAL', 'STRAIGHT', 'SWORD', 'MAGIC1', 'MAGIC2']

class DataCashQueue():
    def __init__(self, queue_length):
        self.queue = []
        self.queue_length = queue_length
    
    def __str__(self):
        return str(self.queue)

    def isFulfilled(self):
        return (len(self.queue) == self.queue_length)

    def update(self, new_data):
        if self.isFulfilled():
            del self.queue[0]
        self.queue.append(new_data)
    
    def reshape(self):
        X = np.array(self.queue, dtype="float32")
        mean = np.mean(X)
        std = np.std(X, ddof=1)
        X = (X - mean) / std
        X = X.reshape(1, X.shape[0], X.shape[1], 1)
        return X
    
    def getMostCommon(self):
        counter = Counter(self.queue)
        most_common = counter.most_common()[0][0]
        most_command_counter = 0
        for item in self.queue:
            if item == most_common:
                most_command_counter += 1
        if most_command_counter < 8:
            return "NEUTRAL"
        else:
            return most_common

class Cortex():
    def __init__(self, user, debug_mode=True):
        url = "wss://localhost:6868"
        self.ws = websocket.create_connection(url,
                                            sslopt={"cert_reqs": ssl.CERT_NONE})
        self.user = user
        self.debug = debug_mode

    def query_headset(self):
        print('query headset --------------------------------')        
        query_headset_request = {
            "jsonrpc": "2.0", 
            "id": QUERY_HEADSET_ID,
            "method": "queryHeadsets",
            "params": {}
        }

        self.ws.send(json.dumps(query_headset_request, indent=4))
        result = self.ws.recv()
        result_dic = json.loads(result)

        self.headset_id = result_dic['result'][0]['id']
        if self.debug:
            # print('query headset result', json.dumps(result_dic, indent=4))            
            print(self.headset_id)

    def connect_headset(self):
        print('connect headset --------------------------------')        
        connect_headset_request = {
            "jsonrpc": "2.0", 
            "id": CONNECT_HEADSET_ID,
            "method": "controlDevice",
            "params": {
                "command": "connect",
                "headset": self.headset_id
            }
        }

        self.ws.send(json.dumps(connect_headset_request, indent=4))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('connect headset result', json.dumps(result_dic, indent=4))


    def request_access(self):
        print('request access --------------------------------')
        request_access_request = {
            "jsonrpc": "2.0", 
            "method": "requestAccess",
            "params": {
                "clientId": self.user['client_id'], 
                "clientSecret": self.user['client_secret']
            },
            "id": REQUEST_ACCESS_ID
        }

        self.ws.send(json.dumps(request_access_request, indent=4))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))


    def authorize(self):
        print('authorize --------------------------------')
        authorize_request = {
            "jsonrpc": "2.0",
            "method": "authorize", 
            "params": { 
                "clientId": self.user['client_id'], 
                "clientSecret": self.user['client_secret'], 
                "license": self.user['license'],
                "debit": self.user['debit']
            },
            "id": AUTHORIZE_ID
        }

        if self.debug:
            print('auth request \n', json.dumps(authorize_request, indent=4))

        self.ws.send(json.dumps(authorize_request))
        
        while True:
            result = self.ws.recv()
            result_dic = json.loads(result)
            if 'id' in result_dic:
                if result_dic['id'] == AUTHORIZE_ID:
                    if self.debug:
                        print('auth result \n', json.dumps(result_dic, indent=4))
                    self.auth = result_dic['result']['cortexToken']
                    break


    def create_session(self, auth, headset_id):
        print('create session --------------------------------')
        create_session_request = { 
            "jsonrpc": "2.0",
            "id": CREATE_SESSION_ID,
            "method": "createSession",
            "params": {
                "cortexToken": self.auth,
                "headset": self.headset_id,
                "status": "active"
            }
        }
        
        if self.debug:
            print('create session request \n', json.dumps(create_session_request, indent=4))

        self.ws.send(json.dumps(create_session_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('create session result \n', json.dumps(result_dic, indent=4))

        self.session_id = result_dic['result']['id']


    def close_session(self):
        print('close session --------------------------------')
        close_session_request = { 
            "jsonrpc": "2.0",
            "id": CREATE_SESSION_ID,
            "method": "updateSession",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "status": "close"
            }
        }

        self.ws.send(json.dumps(close_session_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('close session result \n', json.dumps(result_dic, indent=4))


    def get_cortex_info(self):
        print('get cortex version --------------------------------')
        get_cortex_info_request = {
            "jsonrpc": "2.0",
            "method": "getCortexInfo",
            "id":100
        }

        self.ws.send(json.dumps(get_cortex_info_request))        
        result = self.ws.recv()
        if self.debug:
            print(json.dumps(json.loads(result), indent=4))

    def do_prepare_steps(self):
        self.query_headset()
        self.connect_headset()
        self.request_access()
        self.authorize()
        self.create_session(self.auth, self.headset_id)


    def disconnect_headset(self):
        print('disconnect headset --------------------------------')
        disconnect_headset_request = {
            "jsonrpc": "2.0", 
            "id": DISCONNECT_HEADSET_ID,
            "method": "controlDevice",
            "params": {
                "command": "disconnect",
                "headset": self.headset_id
            }
        }

        self.ws.send(json.dumps(disconnect_headset_request))

        # wait until disconnect completed
        while True:
            time.sleep(1)
            result = self.ws.recv()
            result_dic = json.loads(result)
            
            if self.debug:
                print('disconnect headset result', json.dumps(result_dic, indent=4))

            if 'warning' in result_dic:
                if result_dic['warning']['code'] == 1:
                    break
    
    def get_magnetic_field_range(self):
        SENSING_SECONDS = 10

        sub_request_json = {
            "jsonrpc": "2.0", 
            "method": "subscribe", 
            "params": { 
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": ['mot']
            }, 
            "id": SUB_REQUEST_ID
        }

        self.ws.send(json.dumps(sub_request_json))

        minY = minZ = sys.float_info.max
        maxY = maxZ = -sys.float_info.max
        for i in range(SENSING_SECONDS * MOTION_SENSING_FREQUENCY):
            new_data = self.ws.recv()
            new_data = json.loads(new_data)
            print(new_data)
            if 'mot' in new_data:
                y, z = new_data['mot'][10], new_data['mot'][11]

                if y < minY:
                    minY = y
                if y > maxY:
                    maxY = y
                if z < minZ:
                    minZ = z
                if z > maxZ:
                    maxZ = z
        
        return minY, maxY, minZ, maxZ
    
    # -1~1の間に値を正規化する
    def normalize_to_plus_minus_one(self, val, min, max):
        return (val - min) / (max - min) * 2 - 1

    def get_reference_direction_vector(self, minY, maxY, minZ, maxZ):
        SENSING_SECONDS = 10

        sub_request_json = {
            "jsonrpc": "2.0", 
            "method": "subscribe", 
            "params": { 
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": ['mot']
            }, 
            "id": SUB_REQUEST_ID
        }

        self.ws.send(json.dumps(sub_request_json))

        y_data = [0]*SENSING_SECONDS * MOTION_SENSING_FREQUENCY
        z_data = [0]*SENSING_SECONDS * MOTION_SENSING_FREQUENCY
        for i in range(SENSING_SECONDS * MOTION_SENSING_FREQUENCY):
            new_data = self.ws.recv()
            new_data = json.loads(new_data)
            print(new_data)
            if 'mot' in new_data:
                y, z = new_data['mot'][10], new_data['mot'][11]
            
                y_data[i] = self.normalize_to_plus_minus_one(y, minY, maxY)
                z_data[i] = self.normalize_to_plus_minus_one(z, minZ, maxZ)
        
        refY, refZ = (sum(y_data) / len(y_data)), (sum(z_data) / len(z_data))
        return refY, refZ
    
    def normalize(x):
        min = x.min()
        max = x.max()
        result = (x-min)/(max-min)
        return result

    def sub_request_and_realtime_process(self, minY, maxY, minZ, maxZ, refY, refZ):
        model = tf.keras.models.load_model('./../model.h5', compile=True)

        sub_request_json = {
            "jsonrpc": "2.0", 
            "method": "subscribe", 
            "params": { 
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": ['eeg', 'mot']
            }, 
            "id": SUB_REQUEST_ID
        }

        self.ws.send(json.dumps(sub_request_json))
        
        eeg_cache = DataCashQueue(DATA_LENGTH)
        eeg_command_cache = DataCashQueue(COMMAND_CASH_LENGTH)

        skip_counter = 0
        while True:
            new_data = self.ws.recv()
            new_data = json.loads(new_data)

            # EEGによるコマンド生成
            if 'eeg' in new_data:
                eeg_cache.update(new_data['eeg'][2:16])
                print(new_data['eeg'][2:16])
                skip_counter += 1
                if eeg_cache.isFulfilled() and skip_counter % EEG_COMMAND_GENERATION_SKIP_RATE == 0:
                    eeg_command = eeg_commands[np.argmax(model.predict(eeg_cache.reshape()))]
                    eeg_command_cache.update(eeg_command)

                    most_common = eeg_command_cache.getMostCommon()

                    print(eeg_command)
                    print("[EEG] {}".format(most_common))
                    try:
                        f = open(eeg_file_path, mode='w')
                        f.write(most_common)
                    except PermissionError as e:
                        print("PermissionErrorが発生")
                    finally:
                        f.close()
                    try:
                        f = open("./../cacs.txt", mode='a')
                        f.write(most_common)
                        f.write("\n")
                    except PermissionError as e:
                        print("PermissionErrorが発生")
                    finally:
                        f.close()

            # モーションによるコマンド生成
            if 'mot' in new_data:
                y = self.normalize_to_plus_minus_one(new_data['mot'][10], minY, maxY)
                z = self.normalize_to_plus_minus_one(new_data['mot'][11], minZ, maxZ)
            
                angle = math.degrees(math.atan2(z, y))\
                        - math.degrees(math.atan2(refZ , refY))
                
                # 角度を-180~180の範囲に変換
                angle = angle % 360
                angle = angle if angle <= 180 else angle - 360

                mot_command = ""
                if abs(angle) < THRESHOLD_ANGLE:
                    mot_command = 'STRAIGHT'
                elif 0 < angle:
                    mot_command = 'RIGHT'
                else:
                    mot_command = 'LEFT'

                # print("[MOT] {}".format(mot_command))
                try:
                    f = open(mot_file_path, mode='w')
                    f.write(mot_command)
                except PermissionError as e:
                    print("PermissionErrorが発生")
                finally:
                    f.close()

    def sub_request(self, stream):
        print('subscribe request --------------------------------')
        sub_request_json = {
            "jsonrpc": "2.0", 
            "method": "subscribe", 
            "params": { 
                "cortexToken": self.auth,
                "session": self.session_id,
                "streams": stream
            }, 
            "id": SUB_REQUEST_ID
        }

        self.ws.send(json.dumps(sub_request_json))
        
        if 'sys' in stream:
            new_data = self.ws.recv()
            print(json.dumps(new_data, indent=4))
            print('\n')
        else:
            while True:
                new_data = self.ws.recv()        
                print(new_data)

    def query_profile(self):
        print('query profile --------------------------------')
        query_profile_json = {
            "jsonrpc": "2.0",
            "method": "queryProfile",
            "params": {
              "cortexToken": self.auth,
            },
            "id": QUERY_PROFILE_ID
        }

        if self.debug:
            print('query profile request \n', json.dumps(query_profile_json, indent=4))
            print('\n')

        self.ws.send(json.dumps(query_profile_json))

        result = self.ws.recv()
        result_dic = json.loads(result)

        print('query profile result\n',result_dic)
        print('\n')

        profiles = []
        for p in result_dic['result']:
            profiles.append(p['name'])

        print('extract profiles name only')        
        print(profiles)
        print('\n')

        return profiles


    def setup_profile(self, profile_name, status):
        print('setup profile --------------------------------')
        setup_profile_json = {
            "jsonrpc": "2.0",
            "method": "setupProfile",
            "params": {
              "cortexToken": self.auth,
              "headset": self.headset_id,
              "profile": profile_name,
              "status": status
            },
            "id": SETUP_PROFILE_ID
        }
        
        if self.debug:
            print('setup profile json:\n', json.dumps(setup_profile_json, indent=4))
            print('\n')

        self.ws.send(json.dumps(setup_profile_json))

        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('result \n', json.dumps(result_dic, indent=4))
            print('\n')


    def train_request(self, detection, action, status):
        # print('train request --------------------------------')
        train_request_json = {
            "jsonrpc": "2.0", 
            "method": "training", 
            "params": {
              "cortexToken": self.auth,
              "detection": detection,
              "session": self.session_id,
              "action": action,
              "status": status
            }, 
            "id": TRAINING_ID
        }

        # print('training request:\n', json.dumps(train_request_json, indent=4))
        # print('\n')

        self.ws.send(json.dumps(train_request_json))
        
        if detection == 'mentalCommand':
            start_wanted_result = 'MC_Succeeded'
            accept_wanted_result = 'MC_Completed'

        if detection == 'facialExpression':
            start_wanted_result = 'FE_Succeeded'
            accept_wanted_result = 'FE_Completed'

        if status == 'start':
            wanted_result = start_wanted_result
            print('\n YOU HAVE 8 SECONDS FOR TRAIN ACTION {} \n'.format(action.upper()))

        if status == 'accept':
            wanted_result = accept_wanted_result

        # wait until success
        while True:
            result = self.ws.recv()
            result_dic = json.loads(result)

            print(json.dumps(result_dic, indent=4))

            if 'sys' in result_dic:
                # success or complete, break the wait
                if result_dic['sys'][1]==wanted_result:
                    break


    def create_record(self,
                    record_name,
                    record_description):
        print('create record --------------------------------')
        create_record_request = {
            "jsonrpc": "2.0", 
            "method": "createRecord",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id,
                "title": record_name,
                "description": record_description
            }, 

            "id": CREATE_RECORD_REQUEST_ID
        }

        self.ws.send(json.dumps(create_record_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('start record request \n',
                    json.dumps(create_record_request, indent=4))
            print('start record result \n',
                    json.dumps(result_dic, indent=4))

        self.record_id = result_dic['result']['record']['uuid']



    def stop_record(self):
        print('stop record --------------------------------')
        stop_record_request = {
            "jsonrpc": "2.0", 
            "method": "stopRecord",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id
            }, 

            "id": STOP_RECORD_REQUEST_ID
        }
        
        self.ws.send(json.dumps(stop_record_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('stop request \n',
                json.dumps(stop_record_request, indent=4))
            print('stop result \n',
                json.dumps(result_dic, indent=4))


    def export_record(self, 
                    folder, 
                    export_types, 
                    export_format,
                    export_version,
                    record_ids):
        print('export record --------------------------------')
        export_record_request = {
            "jsonrpc": "2.0",
            "id":EXPORT_RECORD_ID,
            "method": "exportRecord", 
            "params": {
                "cortexToken": self.auth, 
                "folder": folder,
                "format": export_format,
                "streamTypes": export_types,
                "recordIds": record_ids
            }
        }

        # "version": export_version,
        if export_format == 'CSV':
            export_record_request['params']['version'] = export_version

        if self.debug:
            print('export record request \n',
                json.dumps(export_record_request, indent=4))
        
        self.ws.send(json.dumps(export_record_request))

        # wait until export record completed
        while True:
            time.sleep(1)
            result = self.ws.recv()
            result_dic = json.loads(result)

            if self.debug:            
                print('export record result \n',
                    json.dumps(result_dic, indent=4))

            if 'result' in result_dic:
                if len(result_dic['result']['success']) > 0:
                    break

    def inject_marker_request(self, marker):
        print('inject marker --------------------------------')
        inject_marker_request = {
            "jsonrpc": "2.0",
            "id": INJECT_MARKER_REQUEST_ID,
            "method": "injectMarker", 
            "params": {
                "cortexToken": self.auth, 
                "session": self.session_id,
                "label": marker['label'],
                "value": marker['value'], 
                "port": marker['port'],
                "time": marker['time']
            }
        }

        self.ws.send(json.dumps(inject_marker_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print('inject marker request \n', json.dumps(inject_marker_request, indent=4))
            print('inject marker result \n',
                json.dumps(result_dic, indent=4))

    def get_mental_command_action_sensitivity(self, profile_name):
        print('get mental command sensitivity ------------------')
        sensitivity_request = {
            "id": SENSITIVITY_REQUEST_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActionSensitivity",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "status": "get"
            }
        }

        self.ws.send(json.dumps(sensitivity_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic


    def set_mental_command_action_sensitivity(self, 
                                            profile_name, 
                                            values):
        print('set mental command sensitivity ------------------')
        sensitivity_request = {
                                "id": SENSITIVITY_REQUEST_ID,
                                "jsonrpc": "2.0",
                                "method": "mentalCommandActionSensitivity",
                                "params": {
                                    "cortexToken": self.auth,
                                    "profile": profile_name,
                                    "session": self.session_id,
                                    "status": "set",
                                    "values": values
                                }
                            }

        self.ws.send(json.dumps(sensitivity_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_active_action(self, profile_name):
        print('get mental command active action ------------------')
        command_active_request = {
            "id": MENTAL_COMMAND_ACTIVE_ACTION_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandActiveAction",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "status": "get"
            }
        }

        self.ws.send(json.dumps(command_active_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_brain_map(self, profile_name):
        print('get mental command brain map ------------------')
        brain_map_request = {
            "id": MENTAL_COMMAND_BRAIN_MAP_ID,
            "jsonrpc": "2.0",
            "method": "mentalCommandBrainMap",
            "params": {
                "cortexToken": self.auth,
                "profile": profile_name,
                "session": self.session_id
            }
        }

        self.ws.send(json.dumps(brain_map_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

    def get_mental_command_training_threshold(self, profile_name):
        print('get mental command training threshold -------------')
        training_threshold_request = {
            "id": MENTAL_COMMAND_TRAINING_THRESHOLD,
            "jsonrpc": "2.0",
            "method": "mentalCommandTrainingThreshold",
            "params": {
                "cortexToken": self.auth,
                "session": self.session_id
            }
        }

        self.ws.send(json.dumps(training_threshold_request))
        result = self.ws.recv()
        result_dic = json.loads(result)

        if self.debug:
            print(json.dumps(result_dic, indent=4))

        return result_dic

# -------------------------------------------------------------------
# -------------------------------------------------------------------
# -------------------------------------------------------------------
