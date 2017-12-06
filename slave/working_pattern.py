import queue
import helper
import threading


def do_pattern(pattern, q, local_dir, repo_dir):
    if pattern is 'master-slave':
        do_master_slave(q, local_dir, repo_dir)
    elif pattern is 'working-push':
        do_working_push(q, local_dir, repo_dir)

def do_master_slave(q, local_dir, repo_dir):

    """
    master slave process the queue in parallerl
    create a new thread for each file
    this allows application to run each file in a seperate process(master-slave)
    """
    complexities = queue.Queue()

    while not q.empty():
        (file, commit) = q.get()
        thread = threading.Thread(target=helper.compute_complexity, args=(file, local_dir, repo_dir, commit, complexities))
        thread.start()
        thread.join()

    return list(complexities.queue)


def do_working_push(q, local_dir, repo_dir):

    """
    master slave process the queue in parallerl
    create a new thread for each file
    this allows application to run each file in a seperate process(master-slave)
    """
    complexities = queue.Queue()

    # do not loop through the queue as we want to send back the result immediately
    if not q.empty():
        (file, commit) = q.get()
        helper.compute_complexity(file, local_dir, repo_dir, commit, complexities)

    return list(complexities.queue)