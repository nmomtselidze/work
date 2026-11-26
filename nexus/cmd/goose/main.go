package main

import (
	"fmt"
	"log"

	"multi-agent-graph/integrations/goose"
)

func main() {
	// 1. Load the configuration
	cfg, err := goose.LoadConfig()
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	fmt.Println("Configuration loaded successfully.")

	// 2. Create a new executor with the loaded config
	executor := goose.NewExecutor(cfg)

	fmt.Println("Executor created.")

	// 3. Execute a sample task
	err = executor.ExecuteTask("process-incoming-data")
	if err != nil {
		log.Fatalf("Task execution failed: %v", err)
	}

	fmt.Println("Sample task completed successfully.")
}
