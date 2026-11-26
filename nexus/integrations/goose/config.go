package goose

import (
	"fmt"
	"os"
	"strconv"
)

// Config contains configuration for the local Goose CLI.
type Config struct {
	// Path to the Goose executable.
	// Normally just "goose", allowing PATH lookup.
	Command string `json:"command" yaml:"command"`

	// Maximum time allowed for one Goose task.
	Timeout int `json:"timeout" yaml:"timeout"`

	// Working directory where Goose will operate.
	WorkingDir string `json:"working_dir" yaml:"working_dir"`
}

// LoadConfig loads Goose configuration from environment variables.
//
// Environment variables:
//
//	GOOSE_COMMAND
//	GOOSE_TIMEOUT
//	GOOSE_WORKING_DIR
func LoadConfig() (*Config, error) {
	cfg := &Config{
		Command:    "goose",
		Timeout:    60,
		WorkingDir: ".",
	}

	if value := os.Getenv("GOOSE_COMMAND"); value != "" {
		cfg.Command = value
	}

	if value := os.Getenv("GOOSE_TIMEOUT"); value != "" {
		timeout, err := strconv.Atoi(value)
		if err != nil {
			return nil, fmt.Errorf(
				"invalid GOOSE_TIMEOUT: %w",
				err,
			)
		}

		if timeout <= 0 {
			return nil, fmt.Errorf(
				"GOOSE_TIMEOUT must be greater than zero",
			)
		}

		cfg.Timeout = timeout
	}

	if value := os.Getenv("GOOSE_WORKING_DIR"); value != "" {
		cfg.WorkingDir = value
	}

	return cfg, nil
}
