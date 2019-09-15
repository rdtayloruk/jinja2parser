import requests, json

GITEA_URL = "https://try.gitea.io/api/v1"
GITEA_AUTH_TOKEN = "" 

class GiteaAPI():
    def __init__(self, base_url, auth_token=None):
        self.base_url = base_url
        if auth_token:
            self.auth_token = auth_token

    def get(self, url):
        try:
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                return r.json()
            else:
                r.raise_for_status()
        except requests.exceptions.RequestException as error:
            pass
    
    def get_repos(self, org):
        url = "{0}/{1}/repos".format(self.base_url, org)
        return self.get(url)
    
    def get_branches(self, org, repo):
        url = "{0}/repos/{1}/{2}/branches".format(self.base_url, org, repo)
        return self.get(url)
    
    def get_releases(self, org, repo):
        url = "{0}/repos/{1}/{2}/releases".format(self.base_url, org, repo)
        return self.get(url)
    
    def get_contents(self, org, repo):
        url = "{0}/repos/{1}/{2}/contents".format(self.base_url, org, repo)
        return self.get(url)
    
    def get_contents_path(self, org, repo, path):
        url = "{0}/repos/{1}/{2}/contents/{3}".format(self.base_url, org, repo, path)
        return self.get(url)

org = "rttest"
gitea_api =  GiteaAPI(GITEA_URL)
repos = gitea_api.get_repos(org)
#repos = [i['name'] for i in items]

repo = "Test34"
path = "templatest/python"
contents = gitea_api.get_contents_path(org, repo, path)


#base64 decode
#base64.b64decode("dGVzdA==")
print(contents)

