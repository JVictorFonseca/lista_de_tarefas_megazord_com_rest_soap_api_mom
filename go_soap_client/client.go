package main

import (
	"fmt"
	"log"
	"strings"

	"github.com/tiaguinho/gosoap"
)

// WSDL_URL is the address of the SOAP service's WSDL
const WSDL_URL = "http://localhost:8001/?wsdl"

func main() {
	log.Println("Starting Go SOAP Client...")

	// Create a new SOAP client
	client, err := gosoap.SoapClient(WSDL_URL, nil)
	if err != nil {
		log.Fatalf("Failed to create SOAP client: %v", err)
	}

	// --- Create User Example ---
	fmt.Println("\n--- Creating a new user via SOAP ---")
	name := "Alice"
	email := "alice@example.com"
	paramsCreate := gosoap.Params{
		"name":  name,
		"email": email,
	}

	resCreate, err := client.Call("createUser", paramsCreate)
	if err != nil {
		log.Printf("Error calling createUser: %v", err)
	} else {
		responseXML := string(resCreate.Body)
		fmt.Printf("SOAP Create User Raw Response: \n%s\n", responseXML)
		if strings.Contains(responseXML, "<user_id>") {
			fmt.Printf("User '%s' created successfully!\n", name)
		} else {
			fmt.Printf("Failed to create user '%s'.\n", name)
		}
	}

	// --- List Users Example ---
	fmt.Println("\n--- Listing all users via SOAP ---")
	paramsList := gosoap.Params{}

	resList, err := client.Call("list_users", paramsList)
	if err != nil {
		log.Printf("Error calling list_users: %v", err)
	} else {
		responseXML := string(resList.Body)
		fmt.Printf("SOAP List Users Raw Response: \n%s\n", responseXML)
		if strings.Contains(responseXML, "<User>") {
			fmt.Println("Users listed successfully!")
			users := strings.Split(responseXML, "<User>")
			if len(users) > 1 {
				fmt.Println("--- Users Found ---")
				for _, userStr := range users[1:] {
					idStart := strings.Index(userStr, "<user_id>")
					idEnd := strings.Index(userStr, "</user_id>")
					nameStart := strings.Index(userStr, "<name>")
					nameEnd := strings.Index(userStr, "</name>")
					emailStart := strings.Index(userStr, "<email>")
					emailEnd := strings.Index(userStr, "</email>")

					if idStart != -1 && idEnd != -1 && nameStart != -1 && nameEnd != -1 && emailStart != -1 && emailEnd != -1 {
						id := userStr[idStart+len("<user_id>") : idEnd]
						name := userStr[nameStart+len("<name>") : nameEnd]
						email := userStr[emailStart+len("<email>") : emailEnd]
						fmt.Printf("ID: %s, Name: %s, Email: %s\n", id, name, email)
					}
				}
				fmt.Println("-------------------")
			} else {
				fmt.Println("No users found.")
			}
		} else {
			fmt.Println("Failed to list users.")
		}
	}

	// --- Get User Example ---
	fmt.Println("\n--- Getting a user by ID via SOAP ---")
	userIDToGet := 1
	paramsGet := gosoap.Params{
		"user_id": userIDToGet,
	}

	resGet, err := client.Call("get_user", paramsGet)
	if err != nil {
		log.Printf("Error calling get_user: %v", err)
	} else {
		responseXML := string(resGet.Body)
		fmt.Printf("SOAP Get User Raw Response: \n%s\n", responseXML)
		if strings.Contains(responseXML, "<user_id>") {
			fmt.Printf("User with ID %d found successfully!\n", userIDToGet)
		} else {
			fmt.Printf("User with ID %d not found.\n", userIDToGet)
		}
	}

	fmt.Println("\nGo SOAP Client finished.")
}
