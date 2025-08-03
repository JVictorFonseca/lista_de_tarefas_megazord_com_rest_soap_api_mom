package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"net/smtp"
	"strings"
	"sync"

	// IMPORTANTE: O caminho abaixo deve corresponder ao nome da sua pasta principal
	// e à estrutura do seu projeto.
	pb "lista_de_tarefas_megazord_com_rest_soap_api_mom/go_server/pb" // Ajustado para o nome correto da pasta

	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

// server is the struct that implements the TaskServiceServer interface
type server struct {
	pb.UnimplementedTaskServiceServer
	mu     sync.Mutex
	tasks  map[int32]*pb.Task // Map to store tasks in memory
	nextID int32              // Next available ID for a new task
}

// NewServer creates a new instance of the server
func NewServer() *server {
	return &server{
		tasks:  make(map[int32]*pb.Task),
		nextID: 1, // Start with ID 1
	}
}

// Implementation of the CreateTask method
func (s *server) CreateTask(ctx context.Context, req *pb.CreateTaskRequest) (*pb.CreateTaskResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Log incoming request
	log.Printf("Received CreateTask request: Title='%s', Description='%s', CreatedBy='%s'",
		req.GetTitle(), req.GetDescription(), req.GetCreatedBy())

	newTask := &pb.Task{
		Id:          s.nextID,
		Title:       req.GetTitle(),
		Description: req.GetDescription(),
		Status:      "pendente", // Default initial status
		CreatedBy:   req.GetCreatedBy(),
	}
	s.tasks[s.nextID] = newTask
	s.nextID++

	response := &pb.CreateTaskResponse{
		Task:    newTask,
		Message: "Task created successfully!",
	}

	// Log outgoing response
	log.Printf("Sending CreateTask response: ID=%d, Title='%s'", newTask.GetId(), newTask.GetTitle())
	return response, nil
}

// Implementation of the ListTasks method
func (s *server) ListTasks(ctx context.Context, req *pb.ListTasksRequest) (*pb.ListTasksResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Log incoming request
	log.Println("Received ListTasks request")

	var tasks []*pb.Task
	for _, task := range s.tasks {
		tasks = append(tasks, task)
	}

	response := &pb.ListTasksResponse{
		Tasks:   tasks,
		Message: fmt.Sprintf("%d tasks found.", len(tasks)),
	}

	// Log outgoing response
	log.Printf("Sending ListTasks response: %d tasks.", len(tasks))
	return response, nil
}

// Implementation of the UpdateTask method
func (s *server) UpdateTask(ctx context.Context, req *pb.UpdateTaskRequest) (*pb.UpdateTaskResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Log incoming request
	log.Printf("Received UpdateTask request for ID=%d", req.GetId())

	task, exists := s.tasks[req.GetId()]
	if !exists {
		log.Printf("Error UpdateTask: Task with ID %d not found.", req.GetId())
		return nil, status.Errorf(codes.NotFound, "Task with ID %d not found", req.GetId())
	}

	// Update fields if provided in the request
	if req.GetTitle() != "" {
		task.Title = req.GetTitle()
	}
	if req.GetDescription() != "" {
		task.Description = req.GetDescription()
	}
	if req.GetStatus() != "" {
		task.Status = req.GetStatus()
	}

	response := &pb.UpdateTaskResponse{
		Task:    task,
		Message: "Task updated successfully!",
	}

	// Log outgoing response
	log.Printf("Sending UpdateTask response for ID=%d, updated Title='%s', Status='%s'",
		task.GetId(), task.GetTitle(), task.GetStatus())
	return response, nil
}

// Implementation of the DeleteTask method
func (s *server) DeleteTask(ctx context.Context, req *pb.DeleteTaskRequest) (*pb.DeleteTaskResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Log incoming request
	log.Printf("Received DeleteTask request for ID=%d", req.GetId())

	_, exists := s.tasks[req.GetId()]
	if !exists {
		log.Printf("Error DeleteTask: Task with ID %d not found.", req.GetId())
		return nil, status.Errorf(codes.NotFound, "Task with ID %d not found", req.GetId())
	}

	delete(s.tasks, req.GetId())

	response := &pb.DeleteTaskResponse{
		Success: true,
		Message: fmt.Sprintf("Task with ID %d deleted successfully!", req.GetId()),
	}

	// Log outgoing response
	log.Printf("Sending DeleteTask response for ID=%d", req.GetId())
	return response, nil
}

// Implementation of the GetTask method
func (s *server) GetTask(ctx context.Context, req *pb.GetTaskRequest) (*pb.GetTaskResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Log incoming request
	log.Printf("Received GetTask request for ID=%d", req.GetId())

	task, exists := s.tasks[req.GetId()]
	if !exists {
		log.Printf("Error GetTask: Task with ID %d not found.", req.GetId())
		return nil, status.Errorf(codes.NotFound, "Task with ID %d not found", req.GetId())
	}

	response := &pb.GetTaskResponse{
		Task:    task,
		Message: fmt.Sprintf("Task with ID %d found.", req.GetId()),
	}

	// Log outgoing response
	log.Printf("Sending GetTask response for ID=%d, Title='%s'", task.GetId(), task.GetTitle())
	return response, nil
}

// Implementation of the SendTasksByEmail method
func (s *server) SendTasksByEmail(ctx context.Context, req *pb.SendTasksByEmailRequest) (*pb.SendTasksByEmailResponse, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	recipientEmail := req.GetRecipientEmail()
	log.Printf("Received SendTasksByEmail request for: %s", recipientEmail)

	if recipientEmail == "" {
		log.Println("Error SendTasksByEmail: Recipient email is empty.")
		return &pb.SendTasksByEmailResponse{
			Success: false,
			Message: "Recipient email cannot be empty.",
		}, nil
	}

	// --- EMAIL CONFIGURATION ---
	// **ATTENTION:** For real tests, you will need to configure these variables
	// with credentials from a real SMTP server (e.g., Gmail, Outlook, SendGrid).
	// DO NOT PUT REAL CREDENTIALS IN PUBLIC REPOSITORIES!
	// For Gmail, you might need to generate an App Password.
	// Refer to your email provider's documentation.

	senderEmail := "your_email@example.com"           // YOUR SENDER EMAIL
	senderPassword := "your_password_or_app_password" // YOUR PASSWORD OR APP PASSWORD
	smtpHost := "smtp.example.com"                    // E.g., "smtp.gmail.com"
	smtpPort := "587"                                 // Standard port for TLS/STARTTLS

	// --- BUILD EMAIL BODY ---
	var body strings.Builder
	body.WriteString("Subject: Your Task List\r\n")
	body.WriteString("MIME-version: 1.0;\r\n")
	body.WriteString("Content-Type: text/plain; charset=\"UTF-8\";\r\n")
	body.WriteString(fmt.Sprintf("\r\nHello!\r\n\r\nHere is your task list:\r\n\r\n"))

	if len(s.tasks) == 0 {
		body.WriteString("No tasks registered at the moment.\r\n")
	} else {
		for _, task := range s.tasks {
			body.WriteString(fmt.Sprintf("ID: %d\r\n", task.GetId()))
			body.WriteString(fmt.Sprintf("Title: %s\r\n", task.GetTitle()))
			body.WriteString(fmt.Sprintf("Description: %s\r\n", task.GetDescription()))
			body.WriteString(fmt.Sprintf("Status: %s\r\n", task.GetStatus()))
			body.WriteString(fmt.Sprintf("Created by: %s\r\n", task.GetCreatedBy()))
			body.WriteString("---\r\n")
		}
	}
	body.WriteString("\r\nSincerely,\r\nYour gRPC Task Manager")

	msg := []byte(body.String())

	// --- ATTEMPT TO SEND EMAIL ---
	auth := smtp.PlainAuth("", senderEmail, senderPassword, smtpHost)
	err := smtp.SendMail(smtpHost+":"+smtpPort, auth, senderEmail, []string{recipientEmail}, msg)

	if err != nil {
		log.Printf("Error sending email to %s: %v", recipientEmail, err)
		return &pb.SendTasksByEmailResponse{
			Success: false,
			Message: fmt.Sprintf("Failed to send email: %v", err),
		}, nil
	}

	log.Printf("Email with tasks sent successfully to: %s", recipientEmail)
	return &pb.SendTasksByEmailResponse{
		Success: true,
		Message: "Email with task list sent successfully!",
	}, nil
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	s := grpc.NewServer()
	taskServer := NewServer()
	pb.RegisterTaskServiceServer(s, taskServer)

	log.Printf("gRPC server listening on %v", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
