import base64
import json
import requests
import sys
import os
import yaml
import helper

from git import Repo
from threading import Thread
from flask import Flask
from flask import jsonify
from flask import request
from itertools import chain, islice

"""
Repo
"""
TARGET_REPOSITORY = "https://github.com/yimk/scalable_golang_lab1.git"
TARGET_DIR = os.getcwd() + "/tmp"


"""
Pattern and Port
"""
port=sys.argv[1]
pattern=sys.argv[2]


"""
declare rest app
"""
app = Flask(__name__)


@app.route('/register', methods=['POST'])
def register():

    # allowing new slave join the system in real time
    slave_address = request.remote_addr + ':' + request.headers.get('port')

    # add slave to db
    # require slave to init git repo
    helper.db_insert_single_slave(slave_address)
    return jsonify({'git-repo': TARGET_REPOSITORY, 'pattern': pattern})


@app.route('/ask-for-work', methods=['POST'])
def distribute_work():

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

    return jsonify({'tasks': tasks_list})


@app.route('/result', methods=['POST'])
def listen_for_result():
    # retrieve essential information
    data = request.get_json(force=True)
    slave_address = request.remote_addr

    result = data.get('result')

    print(result)


if __name__ == '__main__':

    """
        The program will be implemented with the three possible pattern - master-slave, working-push and working-steal
        The only problem is the sharing of git data
        There are two options in turns of how master and slave sharing the git data

            1. master nodes sends the file needed to slave node in real time
            2. master node and slave node both keep a copy of the entire git repo

        I choose 2, as it will maximize the performance of the cloud system in following ways:

            1. Reducing the traffic between master node and slave node. - traffic between nodes are in fact
               one of the bottleneck of the state-of-art distributed file/computation system. This is because the transferring
               of data between nodes are slow and expensive. By making all the nodes have a copy of the git repo, we reduce the
               data transferring between the nodes(e.g master node only need to send the file name instead of the ENTIRE FILE!!)

        
        Problem:
            - The requirement is that we do the complexity computation for all commits.
            - This means that for different commit 
                - we need to checkout the local git repo to the specific commit before we can start to read the file data
                - checkout is very expensive
                - Hence, the design is that, the master will loop through every commit, and start the new commit if and 
                  only if the last commit has been processed
                   
            - Issue:
                - The BOTTLE-NECK of this implementation is that if we are implementing a traditional master slave
                - fast slave node might need to wait for slow slave node to completed their task for current commit in order to move to NEXT COMMIT
                
                Solution:
                    - As I am not required to implement all three solution, I will implement 
                        
                        - a working-steal-style master slave system
                        - a working-steal-style working-push system
            
            Traditional master-slave/working-push - slaves are reactive, they do the job when master ask them to do it
                                                  - all slaves get same amount of work which stays in their queue
            
            My master-slave/working-push - slave are proactive, they ask master for job
                                         - this allows me to give faster slave more job.
                                         
            e.g - Instead of split all the jobs and assign all these tasks to all the slaves in the very beginning, 
                - I only give each slave some job(3 files a time in here)
                - master slave handle it concurrently, working push handle it one by one
                - faster slave can then come back to me and ask for more job, he will end up do more work
                - this keeps all the nodes busy all the time
                - THIS ALSO allows me to handle real-time new slave member, 
                - e.g new slave can join the system at any time and my master can just assign it incompleted or expired tasks
    """

    # init git across cloud system, require all nodes to prepare a copy of the git repository
    repo = helper.git_clone_or_pull(TARGET_REPOSITORY, TARGET_DIR)

    # init tasks, parse the repository and insert all the files(sub-tasks) of each commit into the db
    helper.retrieve_repository_tasks(repo, TARGET_DIR)

    # run the rest api
    app.run(debug=True, use_reloader=False)
