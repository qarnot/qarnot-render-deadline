import qarnot
import logging
import random


class QarnotRenderDeadline:
    def __init__(self, client_token, cluster_url="https://api.qarnot.com"):
        """
        Initializes object with Qarnot connection information.

        Args:
            client_token: Qarnot API token
            cluster_url: Qarnot cluster URL
        """

        self.conn = None
        self.started_tasks = []

        self.client_token = client_token
        self.cluster_url = cluster_url
        ######## CONFIGURATION #########################################################
        self.license_server = ""
        self.license_mode = "Standard"
        # Your Deadline Remote Connection Server (RCS) in the form "hostname:port"
        self.repository = ""
        self.proxy_crt = "/opt/Thinkbox/Deadline10RemoteClient.pfx"
        self.proxy_ssl = "True"
        ######## CONFIGURATION #########################################################
        self.deadline_prefix = "deadline"
        self.resources_bucket = "deadline-input"
        self.results_bucket = "deadline-output"

        self.error_credentials = "Invalid credentials"

    def refresh_connection(self):
        """
        Refresh connection to Qarnot API.
        """

        if len(self.client_token) == 0:
            raise Exception(self.error_credentials)

        # init connection to API
        self.conn = qarnot.connection.Connection(
            client_token=self.client_token, cluster_url=self.cluster_url
        )

    def verify_access(self):
        """
        Verify if requests to Qarnot API are valid.

        Returns:
            True if valid
        """

        self.refresh_connection()
        if self.conn is None:
            return False

        try:
            self.conn.user_info
        except:
            logging.error("Error: Invalid credentials")
            return False

        return True

    def get_available_profiles(self):
        """
        Get available deadline profiles.

        Returns:
            available_profiles: Return list of available OSImages
                supported by this provider : correspond to API profiles
                Must be implemented for the Balancer to work.
        """

        if self.verify_access() is False:
            raise Exception(self.error_credentials)

        available_profiles = []
        profiles = self.conn.profiles()

        for profile in profiles:
            # add only profiles dedicated to deadline
            if self.deadline_prefix in profile.name:
                available_profiles.append(profile)

        return available_profiles

    def get_active_tasks(self):
        """
        Get active tasks.

        Returns:
            active_tasks: list of tasks objects that are currently active
        """

        active_tasks = []
        self.refresh_connection()

        if self.conn is not None:
            tasks = self.conn.tasks()
            excluded_states = [
                "UploadingResults",
                "DownloadingResults",
                "Cancelled",
                "Success",
                "Failure",
            ]

            for task in tasks:
                # add only active tasks dedicated to deadline
                logging.debug('Evaluating task "{}": {}'.format(task.name, task.state))
                if (
                    all(x not in task.state for x in excluded_states)
                    and self.deadline_prefix in task.name
                ):
                    active_tasks.append(task)
        else:
            raise Exception(self.error_credentials)

        logging.debug(
            'Active tasks: "{}"'.format([(x.name, x.uuid) for x in active_tasks])
        )
        return active_tasks

    def get_active_pools(self):
        """
        Get active pools.

        Returns:
            active_pools: list of tasks objects that are currently active
        """

        active_pools = []
        self.refresh_connection()

        if self.conn is not None:
            pools = self.conn.pools()
            excluded_states = ["Closed", "Closing", "PendingDelete", "Failure"]

            for pool in pools:
                # add only active pools dedicated to deadline
                logging.debug('Evaluating pool "{}": {}'.format(pool.name, pool.state))
                if (
                    all(x not in pool.state for x in excluded_states)
                    and self.deadline_prefix in pool.name
                ):
                    active_pools.append(pool)
        else:
            raise Exception(self.error_credentials)

        logging.debug(
            'Active pools: "{}"'.format([(x.name, x.uuid) for x in active_pools])
        )
        return active_pools

    def create_instances(
        self,
        profile,
        count,
    ):
        """
        Start instances and return list of started tasks.

        Args:
            profile: the profile of tasks to start
            count: the number of tasks to start

        Returns:
            started_tasks: list of tasks that were started
        """

        startedIDs = []
        self.refresh_connection()

        if self.verify_access() is False:
            raise Exception(self.error_credentials)

        # is random name good enough for uniqueness?
        def r():
            return random.randint(0, 255)

        def random_suffix(r):
            rand = "-%02X%02X%02X" % (
                r(),
                r(),
                r(),
            )
            # use a name with random 3byte hex value
            return rand

        pool_name = profile + random_suffix(r)
        pool = self.conn.create_pool(
            name=pool_name, profile=profile, instancecount=count
        )
        pool.submit()

        # name form: deadline-<profile>-<random>
        # name = self.deadline_prefix + "-" + profile + random_suffix(r)
        task_name = profile + random_suffix(r)
        task = self.conn.create_task(task_name, pool, count)
        bucketOut = self.conn.create_bucket(self.results_bucket)
        bucketIn = self.conn.create_bucket(self.resources_bucket)
        task.results = bucketOut
        task.resources = [bucketIn]

        task.constants["DEADLINE_REPOSITORY"] = self.repository
        task.constants["DEADLINE_SSL"] = self.proxy_ssl
        task.constants["DEADLINE_LICENSE_MODE"] = self.license_mode
        task.constants["DEADLINE_LICENSE_SERVER"] = self.license_server
        task.constants["DEADLINE_CRT"] = "".join(self.proxy_crt.splitlines())
        # TODO: specify docker repo
        # instance.task.constants['DOCKER_HOST'] = instance.Name
        # instance.task.constants['DOCKER_TAG'] = "2.100.106"

        task.submit()

        # take snapshots every 5 minutes
        task.snapshot(5 * 60)

        self.started_tasks.append(task)

        # self.StartInstances(startedIDs)
        return self.started_tasks

    def terminate_instances(self):
        """
        Stop instances and return list of stopped tasks.

        Returns:
            results: list of boolean values indicating which tasks
            terminated successfully
        """

        active_tasks = self.get_active_tasks()
        # TODO: return list of boolean values indicating which pools terminated
        # successfully
        active_pools = self.get_active_pools()

        if active_tasks is None or len(active_tasks) == 0:
            results = []

        results = [False] * len(active_tasks)
        self.refresh_connection()

        if self.verify_access() is False:
            raise Exception(self.error_credentials)

        terminated_tasks = []
        for active_task in active_tasks:
            try:
                task = self.conn.retrieve_task(active_task)
                task.instant()
                task.delete(False, False)
            except:
                logging.error("Error terminating Instance")

        for i in range(0, len(active_tasks)):
            active_task = active_tasks[i]
            if active_task in terminated_tasks:
                results[i] = True

        for active_pool in active_pools:
            try:
                pool = self.conn.retrieve_pool(active_pool.uuid)
                pool.close()
            except:
                logging.error("Error terminating Pool")

        return results
