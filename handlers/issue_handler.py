class IssueHandler:
	def __init__(self, repos):
		self.repos = repos

	def handle(self, channel, prefix, issue):
		repo = self.find_repo(prefix, channel)
		if repo is not None:
			return "https://github.com/" + repo + "/issues/" + issue

	def find_repo(self, prefix, channel):
		for repo in self.repos:
			if prefix is "" and channel in repo["channels"]:
				# "Look at #123"
				return repo["name"]
			if prefix in repo["prefixes"] or prefix.lower() in repo["prefixes"]:
				# "Look at bugs#123"
				return repo["name"]
