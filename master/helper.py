import glob
from pymongo import MongoClient
import datetime
from git import Repo
import os
import lizard

"""
file reading helper
"""

def get_file_in_dir(dir):
    return [file_name.replace(dir, '') for file_name in glob.glob(dir + "/**/*.*", recursive=True, )]

def get_worker_info(base="docker-compose.yml"):
    # ports = []
    # with open(base, 'r') as stream:
    #     try:
    #
    #         res = yaml.load(stream)
    #         print(yaml.load(stream))
    #         for k, v in res["services"].items():
    #             port = res["services"][k].get('environment')
    #             if port:
    #                 ports.append(port[0].split("=")[1])
    #
    #     except yaml.YAMLError as exc:
    #         print(exc)
    #
    # return ports
    return [("localhost", "5001"), ("localhost", "5002"), ("localhost", "5003")]


def retrieve_repository_tasks(repo, dir):

    """
    Parse the repository of the current commit and inserts all the files in each commit into the db
    Each files is a subtask and will be sent to the workers

    :param repo: repository
    :return:
    """
    for current_commit in repo.iter_commits():

        git_checkout(dir, current_commit.hexsha)
        items = get_file_in_dir(dir)

        for item in items:
            db_insert_single_task(file=item, commit=current_commit.hexsha)


"""
mongodb helper
"""


def db_get_expired_tasks(expire_minute=5):

    expire_tasks = []
    for task in db_get_incompleted_tasks():
        if task['start_time'] and (datetime.datetime.now() - task['start_time']).minute > expire_minute:
            expire_tasks.append(task)
    return expire_tasks


def db_insert_single_task(file, commit):
    post = {
        "file": file,
        "commit": commit,
        "start_time": None,
        "slave_address": None,
        "completed": False,
        "assigned": False
    }
    tasks_table().insert_one(post)


def db_start_task(file, commit, slave):
    db_get_all_tasks().find_one_and_update({"file": file, 'commit': commit},
                                           {"$set": {"slave": slave,
                                                     "start_time": datetime.datetime.now()}})


def db_end_task(file, commit):
    db_get_all_tasks().find_one_and_update({"file": file, 'commit': commit},
                                           {"$set": {"completed": True}})


def tasks_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-task')


def db_get_all_tasks():
    return tasks_table().find()


def db_get_incompleted_tasks():
    return tasks_table().find({"completed": False})


def db_get_unassigned_task():
    return tasks_table().find({"completed": False, "assigned": False})


def db_insert_single_slave(addr):
    post = {
        "addr": addr
    }
    slave_table().insert_one(post)


def db_get_all_slaves():
    return slave_table().find()


def slave_existed(addr):
    return slave_table().find({'addr': addr})


def slave_table():
    client = MongoClient("localhost", 27017)
    return client['test-database'].get_collection('test-collection-slave')


"""
git helper
"""


def git_checkout(dir, commit):
    repo = Repo(dir)
    git1 = repo.git
    git1.checkout(commit)


def git_clone_or_pull(repo_dir, local_dir):

    if not os.path.exists(local_dir):
        Repo.clone_from(repo_dir, local_dir)

    return Repo(local_dir)


"""
Complexity Computation helper
"""


def compute_complexity(file_dir, local_dir, repo_url, commit_hex, complexity):
    git_clone_or_pull(repo_url, local_dir)
    git_checkout(file_dir, commit_hex)
    complexity.put((lizard.analyze_file(file_dir).average_cyclomatic_complexity, file_dir, commit_hex))
