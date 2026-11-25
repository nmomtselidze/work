Recommended Multi-File Directory StructureOrganize your library as a local package directory so both your main application and every test file in test/ can import it cleanly via relative paths:   Plaintextmy-goose-project/
├── .github/
│   └── workflows/
│       └── test.yml
├── app.goose               # Main application entry point
├── mylib/                  # Library package directory
│   ├── mylib.goose         # Package root module (must match directory name)
│   └── parser.goose        # Additional submodule
└── test/                   # Independent test entry points
    ├── test_mylib.goose
    └── test_parser.goose
#========================================================
LEVEL 0 — Prepare the laboratory
0.1 Go to your project
cd /media/user/dsk64/monowork/go-cicd-lab
pwd
ls -la
0.2 Check Go
go version
go env GOPATH
go env GOMOD
go mod init gitlab.com/nmomtselidze/go-cicd-lab
go env GOMOD
go version
go mod tidy
go test ./...

Level 1 — Step 1: Create project structure
cd /media/user/dsk64/monowork/go-cicd-lab
mkdir -p cmd/server
mkdir -p internal/handler
mkdir -p tests
mkdir -p docs
tree -L 3
.
├── cmd
│   └── server
├── Dockerfile
├── docs
├── DUO_LAB.md
├── experiments
├── go.mod
├── internal
│   └── handler
├── reports
├── tests
└── toDo.md
Step 2: Create Go application with Goose
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
2.4 Start Goose
ls -lah /usr/lib/goose/
goose
2.5 Prompt for Goose

