from flask import Flask
import queue
import json
import helper
import os
import requests
import sys
import working_pattern


"""
Constants
"""
headers = {'Content-type': 'application/json'}
TARGET_DIR = os.getcwd() + "/tmp_slave" + sys.argv[1]
MASTER_HOST = 'localhost'
MASTER_PORT = '5000'


"""
The task queue
"""

work_queue = queue.Queue()


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


def register():

    try:
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

        # clone the git repo
        helper.git_clone_or_pull(git_repo, TARGET_DIR)  

        # init git repo
        # repo_url = response.headers.get('git-repo')
        # helper.git_clone_or_pull(repo_url, TARGET_DIR)

        print("Registration is Successful")
    except requests.exceptions.RequestException as e:
        register() #should I also sys.exit(1) after this?


def quit():

    try:
        # require master to register slave
        link = "http://{}/quit".format(MASTER_HOST + ':' + MASTER_PORT)
        headers = {'host': 'localhost', 'port': sys.argv[1]}
        response = requests.post(link, data=json.dumps({}), headers=headers)
    except requests.exceptions.RequestException as e:
        quit() #should I also sys.exit(1) after this?


def ask_for_work():

    # require master to give slave work
    link = "http://{}/ask-for-work".format(MASTER_HOST + ':' + MASTER_PORT)
    headers = {'host': 'localhost', 'port': sys.argv[1]}
    try:
        response = requests.post(link, data=json.dumps({}), headers=headers)
        json_data = json.loads(response.text)
        for task in json_data['tasks']:
            commit_hex = task['commit']
            file = task['file']
            work_queue.put(item=(file, commit_hex))

        if work_queue.empty():
            print("Work Done")
            quit()
            sys.exit()
    except requests.exceptions.RequestException as e:
        print("connection failed") #should I also sys.exit(1) after this?


def do_work():
    if not work_queue.empty():
        # get the work from the queue{TypeError}empty() missing 1 required positional argument: 'self'
        complexities = working_pattern.do_pattern(pattern, work_queue, TARGET_DIR, git_repo)

        # do work
        print("Do Work")
        link = "http://{}/result".format(MASTER_HOST + ':' + MASTER_PORT)
        headers = {'host': 'localhost', 'port': sys.argv[1]}
        requests.post(link, data=json.dumps(complexities), headers=headers)
    else:
        ask_for_work()


if __name__ == '__main__':

    print("Register Slave Node")
    register()

    while True:
        do_work()
