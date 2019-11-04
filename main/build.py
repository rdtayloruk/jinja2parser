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
        log.info("creating repo: %s", self.name)
        if not os.path.isdir(self.working_dir):
            log.info("creating working_dir: %s", self.working_dir)
            os.makedirs(self.working_dir)
            
    def update(self):
        """Clone or update the repository."""
        if self.repo_exists():
            self.fetch()
        else:
            self.clone()
    
    def clean(self):
        log.info("removing workingdir: %s", self.working_dir)
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
            if branch.name == 'origin/HEAD':
                continue
            versions.append(branch.name)
        return versions
        
    def committed_date(self, version=None):
        repo = git.Repo(self.working_dir)
        if version:
            return repo.commit(version).committed_date
        else:
            return repo.head.object.committed_date
        
    def hexsha(self, version=None):
        repo = git.Repo(self.working_dir)
        if version:
            return repo.commit(version).hexsha
        else:
            return repo.head.object.hexsha
        
    
