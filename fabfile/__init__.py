import os

from fabric.api import task, run, env, cd, require
from fabric.utils import puts, abort
from fabric.main import list_commands
from fabric.contrib.files import exists

# fixme: add error if doesn't exist yet
import host


env.mercury_git = "git://github.com/techcollective/mercury.git"
require_hosts = {"provided_by": "host.HOST (run 'fab usage' for more help)"}


# TODO

# add init task to setup host.py?

# add task: delete *.pyc files

# add pre-install task to check dependencies (e.g. pg_config on path implies
# that postgresql headers are most likely available)

# add task to create local settings. prompt for values? (after #161)

# add task to run syncdb, load fixtures etc

# add install_centos task that will add gunicorn initscript and nginx config

# update calls to install_dependencies to allow setting deps arg

# add tasks to start/stop/reload gunicorn (maybe look at supervisord)

# success message from install saying "now run deploy if this is a production
# server"? because it doesn't do collectstatic.


@task(default=True)
def usage():
    """
    Prints this usage information
    """
    puts("usage: fab host.HOST TASK[:OPTIONS]")
    puts("See the list below for available host.HOST and TASK choices.")
    puts("Use fab -d TASK for a list of that task's available options.")
    puts("\n".join(list_commands("", "normal")))


@task
def install_src(branch="master"):
    """
    Install the mercury source code
    Options: branch=BRANCH_NAME (default: master)
    """
    require("mercury_src", **require_hosts)
    if not exists(env.mercury_src):
        run("git clone %(mercury_git)s %(mercury_src)s" % env)
        with cd("%(mercury_src)s" % env):
            run("git checkout %s" % branch)
    else:
        abort("%(mercury_src)s already exists. Try using update_src." % env)


@task
def install_virtualenv():
    """
    Creates the virtualenv directory.
    To change the path, edit host.py
    """
    require("mercury_virtualenv", "python", **require_hosts)
    if not exists(env.mercury_virtualenv):
        run("virtualenv --no-site-packages -p %(python)s"
            " %(mercury_virtualenv)s" % env)
    else:
        puts("%(mercury_virtualenv)s exists. "
             "Try using install_dependencies" % env)


def virtualenv_run(command):
    activate = os.path.join(env.mercury_virtualenv, "bin/activate")
    run("source %s" % activate + " && " + command)


@task
def install_dependencies(deps="production"):
    """
    Install dependencies
    Options: deps={production,development} (default: production)
    """
    require("mercury_src", "mercury_virtualenv", **require_hosts)
    reqs = os.path.join(env.mercury_src, "requirements/%s-frozen.txt" % deps)
    virtualenv_run("pip install -r %s" % reqs)


@task
def install(branch="master"):
    """
    Install source, virtualenv, and dependencies
    Options: branch=BRANCH_NAME (default: master)
    """
    require("mercury_src", "mercury_virtualenv", "python", **require_hosts)
    install_src(branch)
    install_virtualenv()
    install_dependencies()


@task
def update_src(branch="master"):
    """
    Update source to latest version
    Options: branch=BRANCH_NAME (default: master)
    """
    require("mercury_src", **require_hosts)
    with cd("%(mercury_src)s" % env):
        run("git fetch")
        run("git checkout %s" % branch)
        run("git merge origin/%s" % branch)


@task
def deploy(branch="master"):
    """
    Update source and install latest dependencies
    Options: branch=BRANCH_NAME (default: master)
    """
    require("mercury_src", "mercury_virtualenv", **require_hosts)
    update_src(branch)
    install_dependencies()
    manage = os.path.join("%(mercury_src)s" % env, "manage.py")
    virtualenv_run(manage + " collectstatic --noinput "
                   "--settings=mercury.settings_production")
