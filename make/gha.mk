include ../.env
export

######################################
### GHA setup
######################################

setup-gh-cli:
	brew install gh
	gh auth-login

add-secrets-gh:
	gh secret set SVC_KEY < ~/.gcp/$(SVC_ACCT)-key.json
