ls -la
docker build -t go-cicd-lab .
docker images | grep go-cicd-lab
docker run --rm -it go-cicd-lab
go version
golangci-lint --version
git --version
# Now test GitLab Duo CLI
cd /media/user/dsk64/monowork/go-cicd-lab
mkdir -p experiments reports
touch DUO_LAB.md
ls -la

duo run --help
//Personal access tokens
https://gitlab.com/-/user_settings/personal_access_tokens?state=active&sort=expires_asc
