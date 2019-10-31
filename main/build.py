import os, subprocess, logging, shutil
import git
from git.exc import BadName, InvalidGitRepositoryError

log = logging.getLogger(__name__)

class Repo():

    def __init__(self, name, url, working_dir):
        """Create Repo object, create working dir if it does not exist"""
        self.name = name
        self.url = url
        self.working_dir = working_dir
        if not os.path.isdir(self.working_dir):
            os.makedirs(self.working_dir)
            
    def update(self):
        """Clone or update the repository."""
        if self.repo_exists():
            self.fetch()
        else:
            self.clone()
    
    def clean(self):
        shutil.rmtree(self.working_dir)
        
            
    def __call(self, cmd):
        try:
            subprocess.check_call(cmd, cwd=self.working_dir)
        except CalledProcessError as e:
            log.exception("%s. Error calling: %s", self.name, cmd)
    
    def fetch(self):
        cmd = ['git', 'fetch', '--tags']
        self.__call(cmd)
    
    def checkout_version(self, version='master'):
        cmd = ['git', 'checkout', version ]
        self.__call(cmd)
    
    def clone(self):
        cmd = ['git', 'clone', self.url, self.working_dir]
        self.__call(cmd)
    
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
        
    def hexsha(self, version=None):
        repo = git.Repo(self.working_dir)
        if version:
            return repo.commit(version).hexsha
        else:
            return repo.head.object.hexsha
        

def update_build(project):
    repo = Repo(
        name = project.name,
        url =  project.url,
        working_dir = project.working_dir )
    repo.update()
    # get revisions
    new_versions = repo.branches + repo.tags
    old_versions = project.versions
    for version in old_versions:
        if version.name in new_versions:
            if version.hexsha != repo.hexsha(version.name):
            """rebuild version"""
        else:
            """cleanup old version"""
    for version in new_versions:
        if version not in old_versions:
            """add new version"""
    #       add new revision
    # sort revisions by age
    # keep X most recent
    
def delete_build(project):
    pass
