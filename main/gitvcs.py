import subprocess, logging
from git import Repo
from git.exc import BadName, InvalidGitRepositoryError

log = logging.getLogger(__name__)

class GitVCS():

    def __init__(self, project):
        self.repo_url = project.url
        self.name = project.name
        self.working_dir = project.working_dir

    def update(self):
        """Clone or update the repository."""
        if self.repo_exists():
            return self.fetch()
        else:
            return self.clone()
    
    def fetch(self):
        cmd = ['git', 'fetch', '--tags']
        subprocess.call(cmd)
    
    def checkout_version(self, version='master')
        pass
    
    
    def clone(self):
        cmd = ['git', 'clone', self.repo_url]
        subprocess.call(cmd)
    
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
                versions.append(VCSVersion(self, str(tag.commit), str(tag)))
            except ValueError:
                # ValueError: Cannot resolve commit as tag TAGNAME points to a
                # blob object - use the `.object` property instead to access it
                # This is not a real tag for us, so we skip it
                # https://github.com/rtfd/readthedocs.org/issues/4440
                log.warning('Git tag skipped: %s', tag, exc_info=True)
                continue
        return versions



    @property
    def branches(self):
        repo = git.Repo(self.working_dir)
        versions = []
        branches = []

        # ``repo.remotes.origin.refs`` returns remote branches
        if repo.remotes:
            branches += repo.remotes.origin.refs

        for branch in branches:
            verbose_name = branch.name
            if verbose_name.startswith('origin/'):
                verbose_name = verbose_name.replace('origin/', '')
            if verbose_name == 'HEAD':
                continue
            versions.append(VCSVersion(self, str(branch), verbose_name))
        return versions
