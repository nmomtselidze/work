package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"time"
)

// OpenAI-compatible request structures for Hugging Face Router
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	MaxTokens   int       `json:"max_tokens,omitempty"`
	Temperature float64   `json:"temperature,omitempty"`
}

// OpenAI-compatible response structures
type ChatChoice struct {
	Message Message `json:"message"`
}

type ChatResponse struct {
	Choices []ChatChoice `json:"choices"`
	Error   *struct {
		Message string `json:"message"`
	} `json:"error,omitempty"`
}

func main() {
	apiURL := "https://router.huggingface.co/v1/chat/completions"
	modelID := "HuggingFaceTB/SmolLM2-1.7B-Instruct"

	// Supports HF_TOKEN (standard) or HUGGINGFACE_API_KEY
	apiKey := os.Getenv("HF_TOKEN")
	if apiKey == "" {
		apiKey = os.Getenv("HUGGINGFACE_API_KEY")
	}

	systemPrompt := "You are a medical AI assistant. Analyze the symptoms and identify the single most likely condition with the highest probability."
	userPrompt := "I have a high fever, dry cough, and severe fatigue."

	reqPayload := ChatRequest{
		Model: modelID,
		Messages: []Message{
			{Role: "system", Content: systemPrompt},
			{Role: "user", Content: userPrompt},
		},
		MaxTokens:   300,
		Temperature: 0.3,
	}

	jsonData, err := json.Marshal(reqPayload)
	if err != nil {
		fmt.Printf("Error marshaling request: %v\n", err)
		printFallback(systemPrompt, userPrompt)
		return
	}

	req, err := http.NewRequest("POST", apiURL, bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("Error creating request: %v\n", err)
		printFallback(systemPrompt, userPrompt)
		return
	}

	req.Header.Set("Content-Type", "application/json")
	if apiKey != "" {
		req.Header.Set("Authorization", "Bearer "+apiKey)
	}

	client := &http.Client{Timeout: 30 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		fmt.Printf("Error sending request: %v\n", err)
		printFallback(systemPrompt, userPrompt)
		return
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("Error reading response: %v\n", err)
		printFallback(systemPrompt, userPrompt)
		return
	}

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("API returned status %d: %s\n", resp.StatusCode, string(body))
		printFallback(systemPrompt, userPrompt)
		return
	}

	var chatResp ChatResponse
	if err := json.Unmarshal(body, &chatResp); err != nil {
		fmt.Printf("Error parsing JSON response: %v\n", err)
		printFallback(systemPrompt, userPrompt)
		return
	}

	if len(chatResp.Choices) == 0 {
		fmt.Println("No choices returned in API response.")
		printFallback(systemPrompt, userPrompt)
		return
	}

	fmt.Println("--- Hugging Face Router Response ---")
	fmt.Println(chatResp.Choices[0].Message.Content)
}

func printFallback(systemPrompt, userPrompt string) {
	fmt.Printf("\n\n--- Demo Mode: Fallback Response ---\n")
	fmt.Printf("<|im_start|>system\n%s\n<|im_end|>\n", systemPrompt)
	fmt.Printf("<|im_start|>user\n%s\n<|im_end|>\n", userPrompt)
	fmt.Println("<|im_start|>assistant")
	fmt.Println("Based on the symptoms you've provided, the most likely condition is:\n\nInfluenza (Flu): This is a viral infection that causes symptoms like fever, cough, and fatigue. It's highly contagious and can spread quickly, especially during flu season. The combination of high fever, dry cough, and severe fatigue strongly suggests influenza as the primary diagnosis.\n\nPlease remember that this is just a potential condition and it's important to consult with a healthcare professional for a proper diagnosis.")
}
