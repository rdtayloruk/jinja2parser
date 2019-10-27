import subprocess, logging
import git
from git.exc import BadName, InvalidGitRepositoryError

log = logging.getLogger(__name__)

class Repo():

    def __init__(self, name, url, working_dir):
        self.name = name
        self.url = url
        self.working_dir = working_dir

    def update(self):
        """Clone or update the repository."""
        if self.repo_exists():
            return self.fetch()
        else:
            return self.clone()
    
    def fetch(self):
        cmd = ['git', 'fetch', '--tags']
        subprocess.check_call(cmd, cwd=self.working_dir)
    
    def checkout_version(self, version='master'):
        cmd = ['git', 'checkout', version ]
        subprocess.check_call(cmd, cwd=self.working_dir)
        pass
    
    def clone(self):
        cmd = ['git', 'clone', self.url, self.working_dir]
        subprocess.check_call(cmd)
    
    def repo_exists(self):
        try:
            git.Repo(self.working_dir)
        except InvalidGitRepositoryError:
            return False
        return True
    
    @property
    def tags(self):
        versions = []
        repo = git.Repo(self.working_dir)
        for tag in repo.tags:
            try:
                versions.append(tag.name)
            except ValueError:
                log.warning('Git tag skipped: %s', tag)
                continue
        return versions

    @property
    def branches(self):
        repo = git.Repo(self.working_dir)
        versions = []
        branches = []

        if repo.remotes:
            branches += repo.remotes.origin.refs

        for branch in branches:
            verbose_name = branch.name
            if verbose_name.startswith('origin/'):
                verbose_name = verbose_name.replace('origin/', '')
            if verbose_name == 'HEAD':
                continue
            versions.append(verbose_name)
        return versions
        
def build(project):
    pass
    # creat VCS object
   # project = 
    #repo = Repo()
    # update
    # get revisions
    # for each revision
    #    if revision in project.revisions
    #       if revision.sha chnaged: 
    #           update
    #    else:
    #       add new revision
    # sort revisions by age
    # keep X most recent
