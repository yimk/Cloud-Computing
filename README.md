## Rest Cyclomatic Complexity Computation
I have implemented master-slave pattern and working-push pattern of working-steal pattern.

One of the bottleneck of master-slave pattern and working-push pattern is the sharing of data:

There are two options in turns of how master and slave sharing the git data

    1. master nodes sends the file needed to slave node in real time
    2. master node and slave node both keep a copy of the entire git repo

I have implemented 2 in my implmentation, as this is reducing the traffics between the master node and the slave node, e.g master node do not have to send big size data to slave in real time.


Another Problem with traditional master-slave and working-push pattern is the waiting issue:

    - Traditional master-slave/working-push pattern are reactive, slave do the job when master ask them to do it(it is often decided at the very start of the task. 
    - This means all slaves get same amount of work which stays in their queue
    - When one slave is much faster then the other(different hardware or maybe the task assigned is actually small, e.g we dont know the size of file need to be parsed). The faster slave will need to wait other slave.

    - My master-slave/working-push implementation - slave are proactive, they ask master for job
                                                  - this allows me to give faster slave more job.

    e.g - Instead of split all the jobs and assign all these tasks to all the slaves in the very beginning,
        - I only give each slave some job(3 files a time in here)
        - master slave handle it concurrently, working push handle it one by one
        - faster slave can then come back to me and ask for more job, he will end up do more work
        - this keeps all the nodes busy all the time
        - THIS ALSO allows me to handle real-time new slave member,
        - e.g new slave can join the system at any time and my master can just assign it incompleted or expired tasks

## Run Application
