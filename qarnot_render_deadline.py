import qarnot
import logging
import random
import base64


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
        # Path to your "Deadline10RemoteClient.pfx" file
        self.proxy_crt = r""
        # The optional certificate password
        self.proxy_crt_pwd = ""
        self.proxy_ssl = "True"
        ######## CONFIGURATION #########################################################
        self.deadline_prefix = "deadline"
        self.resources_bucket = ["deadline-input"]
        self.results_bucket = "deadline-output"

        self.error_credentials = "Invalid credentials"

    def refresh_connection(self):
        """
        Refresh connection to Qarnot API.
        """

        if len(self.client_token) == 0:
            raise Exception(self.error_credentials)

        # init connection to API
        try:
            self.conn = qarnot.connection.Connection(
                client_token=self.client_token, cluster_url=self.cluster_url
            )
        except Exception as e:
            logging.error("Connection error")
            raise

    def get_available_profiles(self):
        """
        Get available deadline profiles.

        Returns:
            available_profiles: list of available deadline profiles
        """

        available_profiles = []
        self.refresh_connection()

        profiles = self.conn.profiles()

        for profile in profiles:
            # add only profiles dedicated to deadline
            if self.deadline_prefix in profile.name:
                available_profiles.append(profile)

        logging.debug(
            'Available deadline profiles: "{}"'.format(
                [(x.name) for x in available_profiles]
            )
        )
        return available_profiles

    def get_active_tasks(self):
        """
        Get active tasks.

        Returns:
            active_tasks: list of task objects that are currently active
        """

        active_tasks = []
        self.refresh_connection()

        tasks = self.conn.tasks(summary=True)
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

        logging.debug(
            'Active tasks: "{}"'.format([(x.name, x.uuid) for x in active_tasks])
        )
        return active_tasks

    def get_active_pools(self):
        """
        Get active pools.

        Returns:
            active_pools: list of pool objects that are currently active
        """

        active_pools = []
        self.refresh_connection()

        pools = self.conn.pools(summary=True)
        excluded_states = ["Closed", "Closing", "PendingDelete", "Failure"]

        for pool in pools:
            # add only active pools dedicated to deadline
            logging.debug('Evaluating pool "{}": {}'.format(pool.name, pool.state))
            if (
                all(x not in pool.state for x in excluded_states)
                and self.deadline_prefix in pool.name
            ):
                active_pools.append(pool)

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

        suffix = random_suffix(r)
        pool_name = profile + suffix
        pool = self.conn.create_pool(
            name=pool_name, profile=profile, instancecount=count
        )
        pool.submit()

        task_name = profile + suffix + "-task"
        task = self.conn.create_task(task_name, pool, count)
        bucketOut = self.conn.create_bucket(self.results_bucket)
        bucketIn = []
        for new_bucket in self.resources_bucket:
            bucketIn.append(self.conn.create_bucket(new_bucket))
        task.results = bucketOut
        task.resources = bucketIn

        task.constants["DOCKER_HOST"] = "qarnot" + suffix + "-${INSTANCE_ID}"
        task.constants["DEADLINE_REPOSITORY"] = self.repository
        task.constants["DEADLINE_SSL"] = self.proxy_ssl
        task.constants["DEADLINE_LICENSE_MODE"] = self.license_mode
        task.constants["DEADLINE_LICENSE_SERVER"] = self.license_server
        with open(self.proxy_crt, "rb") as fin:
            deadline_certificate = base64.b64encode(fin.read())
        task.constants["DEADLINE_CRT"] = deadline_certificate.decode('ascii')
        task.constants["DEADLINE_CRT_PWD"] = self.proxy_crt_pwd

        # upload results when the task is manually cancelled
        task.upload_results_on_cancellation = True

        task.submit()

        # take snapshots every 5 minutes
        task.snapshot(5 * 60)

        self.started_tasks.append(task)

        return self.started_tasks

    def stop_instances(self, pool_uuid=None):
        """
        Stop instances for all active pools or one specific pool

        Args:
            pool: optional UUID of a specific pool to close
        """

        self.refresh_connection()

        if pool_uuid is None:
            active_pools = self.get_active_pools()

            for active_pool in active_pools:
                try:
                    pool_uuid = self.conn.retrieve_pool(active_pool.uuid)
                    pool_uuid.close()
                except:
                    logging.error("Error closing Pool {}".format(active_pool.name))
        else:
            try:
                pool_uuid = self.conn.retrieve_pool(pool_uuid)
                pool_uuid.close()
            except:
                logging.error("Error closing Pool with UUID {}".format(pool_uuid))
