class IssueHandler():
	def __init__(self, repos):
		self.repos = repos


	def handle(self, channel, prefix, issue):
		repo = self.find_repo(prefix, channel)
		if repo is not None:
			return "https://github.com/" + repo + "/issues/" + issue


	def find_repo(self, prefix, channel):
		for repo in self.repos:
			if prefix in repo["prefixes"] or (prefix is "" and channel in repo["channels"]):
				return repo["name"]
