import base64
import json
import requests
import sys
import os
import helper

from git import Repo
from threading import Thread
from flask import Flask
from flask import jsonify
from flask import request
from itertools import chain, islice
import datetime

"""
Repo
"""
TARGET_REPOSITORY = "https://github.com/yimk/scalable_golang_lab1.git"
TARGET_DIR = os.getcwd() + "/tmp"


"""
Pattern and Port
"""
port = sys.argv[1]
pattern = sys.argv[2]


"""
declare rest app
"""
app = Flask(__name__)


"""
Start time
"""
start_time = None


@app.route('/register', methods=['POST'])
def register():

    # allowing new slave join the system in real time
    slave_address = request.remote_addr + ':' + request.headers.get('port')

    # add slave to db
    # require slave to init git repo
    helper.db_insert_single_slave(slave_address)
    return jsonify({'git-repo': TARGET_REPOSITORY, 'pattern': pattern})


@app.route('/quit', methods=['POST'])
def request_to_quit():

    # allowing new slave join the system in real time
    slave_address = request.remote_addr + ':' + request.headers.get('port')

    # add slave to db
    # require slave to init git repo
    helper.db_remove_single_slave(slave_address)
    return jsonify({'Success': 'True'})

@app.route('/ask-for-work', methods=['POST'])
def distribute_work():

    global start_time

    # retrieve essential information
    data = request.get_json(force=True)
    slave_address = request.remote_addr + ':' + request.headers.get('port')

    # ensure slave is registered, e.g ensure it holds the git repo
    if not helper.slave_existed(slave_address):
        return jsonify({'result': 'Please Register'})

    # get tasks, both unassigned_task and expired task
    tasks = chain(helper.db_get_unassigned_task(), helper.db_get_expired_tasks())

    # assign five tasks a time
    tasks_list = []
    for task in islice(tasks, 5):
        print(task)
        tasks_list.append({'file': task['file'], 'commit': task['commit']})
        helper.db_start_task(task['file'], task['commit'], slave_address)

    if not start_time:
        start_time = datetime.datetime.now()



    return jsonify({'tasks': tasks_list})


@app.route('/result', methods=['POST'])
def listen_for_result():

    # retrieve essential information
    results = request.get_json(force=True)
    for result in results:
        helper.db_complete_task(result['file'], result['commit'], result['complexity'])

    if helper.db_get_incomplete_tasks().count() == 0:
        print("Task Completed------------------------------------------------------------------------------------------")
        print("The average cyclomatic complexity is: " + str(helper.db_get_avg_complexity_result()))
        print("Time Taken: " + str((datetime.datetime.now() - start_time).microseconds))
    else:
        print("Number of task remain: " + str(helper.db_get_incomplete_tasks().count()))
        

if __name__ == '__main__':

    # init git in the master node
    repo = helper.git_clone_or_pull(TARGET_REPOSITORY, TARGET_DIR)

    # init tasks, parse the repository and insert all the files(sub-tasks) of each commit into the db
    helper.retrieve_repository_tasks(repo, TARGET_DIR)

    # run the rest api
    app.run(debug=True, use_reloader=False, port=5000)

