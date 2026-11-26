package goose

import (
	"context"
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"
)

type Executor interface {
	ExecuteTask(task string) error
}

type gooseExecutor struct {
	config *Config
}

func NewExecutor(cfg *Config) Executor {
	return &gooseExecutor{config: cfg}
}

func (e *gooseExecutor) ExecuteTask(task string) error {
	if e.config == nil {
		return fmt.Errorf("Goose configuration is nil")
	}

	if strings.TrimSpace(task) == "" {
		return fmt.Errorf("task cannot be empty")
	}

	command := e.config.Command
	if command == "" {
		command = "goose"
	}

	timeout := time.Duration(e.config.Timeout) * time.Second
	if timeout <= 0 {
		timeout = 60 * time.Second
	}

	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()

	path, err := exec.LookPath(command)
	if err != nil {
		return fmt.Errorf("cannot find Goose executable: %w", err)
	}

	cmd := exec.CommandContext(ctx, path, task)

	if e.config.WorkingDir != "" {
		cmd.Dir = e.config.WorkingDir
	}

	cmd.Env = os.Environ()
	cmd.Stdin = os.Stdin
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	fmt.Printf("Starting Goose task: %s\n", task)

	if err := cmd.Run(); err != nil {
		if ctx.Err() == context.DeadlineExceeded {
			return fmt.Errorf("Goose task timed out after %s", timeout)
		}
		return fmt.Errorf("Goose execution failed: %w", err)
	}

	fmt.Println("Goose process finished.")
	return nil
}
