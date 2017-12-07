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