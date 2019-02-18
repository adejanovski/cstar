from aloe import before, step, world, before, after
import json
import logging
import os
import re
import uuid
import subprocess

@before.each_feature
def before_feature(feature):
    logging.info("Running before each feature")
    logging.info("Collect seed node from tlp-cluster")
    world.seed_node = "127.0.0.1"
    world.cstar_job_dir = os.path.join(os.path.expanduser("~"), ".cstar", "jobs")


@step(r'I run "([^"]*)" on the cluster with strategy "([^"]*)"')
def _i_run_nodetool_status_on_the_cluster(self, command, strategy):
    logging.info("Running {} command with strategy {}...".format(command, strategy))
    world.last_job_id = str(uuid.uuid4())
    cstar_output = subprocess.check_output(["cstar", "run", "--command",command,"--seed-host",world.seed_node, "--enforced-job-id", world.last_job_id,"--strategy",strategy])
    logging.info(cstar_output)
    assert os.path.isdir(os.path.join(world.cstar_job_dir, world.last_job_id))
    world.job = get_job_json()

@step(r'there are (\d+) nodes reported by nodetool')
def _there_are_x_nodes_reported_by_nodetool(self, node_count):
    logging.info("Checking nodetool status reported nodes...")
    _ip_re = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", re.MULTILINE)
    first_node = next(os.walk(os.path.join(world.cstar_job_dir, world.last_job_id)))[1][0]
    nodetool_status_output = ''
    with open(os.path.join(world.cstar_job_dir, world.last_job_id, first_node, "out"), 'r') as f:
        nodetool_status_output = f.read()
    logging.info(nodetool_status_output)
    nodes = re.findall(_ip_re, nodetool_status_output)
    logging.info("Nodes in the cluster: {}".format(nodes))
    logging.info("Number of nodes in the cluster: {}".format(len(nodes)))
    logging.info("Expected: {}".format(node_count))
    assert len(nodes) == int(node_count)

@step(r'there are no errors in the job')
def _there_are_no_errors_in_the_job(self):
    assert len(world.job['errors']) == 0

@step(r'the job fails')
def _the_job_fails(self):
    assert len(world.job['errors']) > 0

@after.each_feature
def tear_down(feature):
    print("Running after each feature")
    print("Destroy cluster")


def spin_up_cluster(cassandra_version):
    pass

def get_job_json():
    with open(os.path.join(world.cstar_job_dir, world.last_job_id, "job.json"), 'r') as f:
        job_json = f.read()
        return json.loads(job_json)
