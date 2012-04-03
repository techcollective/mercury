from fabric.api import task, env

# This file defines the servers you are deploying to.
# Set the paths to correspond to your desired setup.
# Copy and paste the block below to create additional
# configurations. See http://www.fabfile.org


@task
def production():
    """
    Run task on the production server
    """
    env.hosts = ["mercury@mercury.mydomain.com"]
    env.mercury_src = "/srv/mercury/src/mercury"
    env.mercury_virtualenv = "/srv/mercury/virtualenv"
    env.python = "/usr/bin/python26"
