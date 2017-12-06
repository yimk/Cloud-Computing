from flask import Flask
from flask import jsonify
from flask import request
from pymongo import MongoClient
import threading
import queue
import base64
import json
import radon
import helper
import os
import requests
import sys
import working_pattern

slave = Flask(__name__)

"""
Constants
"""
headers = {'Content-type': 'application/json'}
TARGET_DIR = os.getcwd() + "/tmp"
MASTER_HOST = 'localhost'
MASTER_PORT = '5000'


"""
The task queue
"""

work_queue = queue.Queue


"""
The git repo, should get it when register
"""

git_repo = None


"""
The Working Pattern, should get it when register
"""
pattern = None


# @slave.route('/init-git')
# def listen_for_init_git():
#     data = request.get_json(force=True)
#     repo_url = data.get('git-repo')
#     repo = helper.git_clone_or_pull(repo_url, TARGET_DIR)
#
#     return jsonify({'result': 'success'})
#

def ask_for_work():
    data = request.get_json(force=True)
    commit_hex = data.get('commit')
    file = data.get('file')
    work_queue.put(item=(file, commit_hex))

    return jsonify({'result': 'success'})


def register():

    # require master to register slave
    link = "http://{}/register".format(MASTER_HOST + ':' + MASTER_PORT)
    headers = {'host': 'localhost', 'port': sys.argv[1]}
    response = requests.post(link, data=json.dumps({}), headers=headers)

    # get data
    json_data = json.loads(response.text)

    # get git repo
    global git_repo
    git_repo = json_data['git-repo']

    # get pattern
    global pattern
    pattern = json_data['pattern']

    # if response didn't contain git repo then we assume registration failed
    if not git_repo or not pattern:
        register()

    # init git repo
    # repo_url = response.headers.get('git-repo')
    # helper.git_clone_or_pull(repo_url, TARGET_DIR)


def do_work():
    if not work_queue.empty():
        # get the work from the queue
        complexities = working_pattern.do_pattern(pattern, queue, TARGET_DIR, git_repo)

        # require master to register slave
        link = "http://{}/result".format(MASTER_HOST + ':' + MASTER_PORT)
        headers = {'host': 'localhost', 'port': sys.argv[1]}
        requests.post(link, data=json.dumps({complexities}), headers=headers)
    else:
        ask_for_work()


if __name__ == '__main__':
    slave.run(debug=True, use_reloader=False, port=sys.argv[1])
    register()

    while True:
        do_work()
