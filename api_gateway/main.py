# api_gateway/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import grpc
import httpx # For SOAP calls
import logging
import os
import sys

# Configure logging for the Gateway
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- CRUCIAL: Adicionar a pasta 'python_client' diretamente ao sys.path ---
# Isso permite que o Python encontre 'tasks_pb2' e 'tasks_pb2_grpc' diretamente.
# O 'os.path.dirname(__file__)' obtém o diretório atual (api_gateway/)
# O 'os.path.join(..., '..')' sobe um nível para a raiz do projeto (lista_de_tarefas_rest_soap_api/)
python_client_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'python_client'))
if python_client_path not in sys.path:
    sys.path.append(python_client_path)
logging.info(f"Added '{python_client_path}' to sys.path.")


# Import gRPC generated modules
# AGORA QUE python_client_path ESTÁ NO sys.path, IMPORTAMOS DIRETAMENTE
try:
    import tasks_pb2 # Importa tasks_pb2 como se estivesse na raiz do sys.path
    import tasks_pb2_grpc # Importa tasks_pb2_grpc como se estivesse na raiz do sys.path
    logging.info("Successfully imported gRPC modules (tasks_pb2, tasks_pb2_grpc).")
except ImportError as e:
    logging.error(f"Failed to import gRPC modules. Please ensure: "
                  f"1. 'protoc' generated files are in 'python_client/'."
                  f"2. 'python_client/__init__.py' exists (though not strictly needed with this import method)."
                  f"3. You ran 'pip install grpcio grpcio-tools'. Error: {e}")
    sys.exit(1) # Exit if gRPC modules cannot be imported


app = FastAPI(
    title="API Gateway for Task and User Management",
    description="Unified API for managing tasks (gRPC) and users (SOAP), with HATEOAS.",
    version="1.0.0",
    docs_url="/swagger", # Swagger UI will be available at /swagger
    redoc_url="/redoc"
)

# CORS configuration to allow requests from your web client
# Adjust origins based on where your web client is hosted (e.g., http://localhost:8080)
origins = [
    "http://localhost",
    "http://localhost:8000", # If web client is served from the same port as gateway (unlikely)
    "http://localhost:8080", # Common port for local web servers (e.g., Python http.server)
    "http://127.0.0.1:8080",
    "http://localhost:5500", # Common for VS Code Live Server
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- gRPC Client Setup (for Task Service) ---
GRPC_SERVER_ADDRESS = "localhost:50051" # Address of your Go gRPC server
try:
    grpc_channel = grpc.insecure_channel(GRPC_SERVER_ADDRESS)
    grpc_task_stub = tasks_pb2_grpc.TaskServiceStub(grpc_channel)
    # Test connection to gRPC server
    # This test might fail if the gRPC server is not yet running, but the Gateway will still start.
    # The actual RPC calls will then fail with 503 if the gRPC server is down.
    # grpc_task_stub.ListTasks(tasks_pb2.ListTasksRequest(), timeout=2) # Removed aggressive startup test
    logging.info(f"Gateway: Attempting to connect to gRPC Task Service at {GRPC_SERVER_ADDRESS}")
except grpc.RpcError as e:
    logging.warning(f"Gateway: Failed to connect to gRPC Task Service at {GRPC_SERVER_ADDRESS} during startup. Error: {e.details}")
    logging.warning("This might be normal if the gRPC server starts after the Gateway. RPC calls will fail until it's up.")
except Exception as e:
    logging.error(f"Gateway: Unexpected error during gRPC Task Service setup: {e}")


# --- SOAP Client Setup (for User Service) ---
SOAP_SERVICE_ADDRESS = "http://localhost:8001/" # Address of your Python SOAP service
# For SOAP, we'll construct the XML request manually or use a library like 'suds-pyc' or 'zeep' if needed
# For this example, we'll use httpx to send XML directly.

# --- HATEOAS Helper ---
def add_hateoas_links(request: Request, resource_type: str, resource_id: int = None):
    base_url = str(request.base_url).rstrip('/')
    links = {
        "self": {"href": f"{base_url}/{resource_type}" + (f"/{resource_id}" if resource_id else ""), "method": "GET"}
    }
    if resource_type == "tasks":
        links["create"] = {"href": f"{base_url}/tasks", "method": "POST"}
        if resource_id:
            links["update"] = {"href": f"{base_url}/tasks/{resource_id}", "method": "PUT"}
            links["delete"] = {"href": f"{base_url}/tasks/{resource_id}", "method": "DELETE"}
            links["get_by_id"] = {"href": f"{base_url}/tasks/{resource_id}", "method": "GET"}
    elif resource_type == "users":
        links["create"] = {"href": f"{base_url}/users", "method": "POST"}
        if resource_id:
            links["get_by_id"] = {"href": f"{base_url}/users/{resource_id}", "method": "GET"}
    return links

# --- Task Endpoints (REST -> gRPC) ---

@app.post("/tasks", status_code=201)
async def create_task(request_data: dict, request: Request):
    logging.info(f"Gateway: Received REST POST /tasks request: {request_data}")
    try:
        grpc_request = tasks_pb2.CreateTaskRequest(
            title=request_data.get("title"),
            description=request_data.get("description"),
            created_by=request_data.get("created_by")
        )
        grpc_response = grpc_task_stub.CreateTask(grpc_request, timeout=5)
        response_content = {
            "task": {
                "id": grpc_response.task.id,
                "title": grpc_response.task.title,
                "description": grpc_response.task.description,
                "status": grpc_response.task.status,
                "created_by": grpc_response.task.created_by,
            },
            "message": grpc_response.message,
            "_links": add_hateoas_links(request, "tasks", grpc_response.task.id)
        }
        logging.info(f"Gateway: Sent gRPC CreateTask, received response: {grpc_response.message}")
        return JSONResponse(content=response_content)
    except grpc.RpcError as e:
        logging.error(f"Gateway: gRPC CreateTask failed: {e.details}")
        raise HTTPException(status_code=503, detail=f"gRPC Task Service Error: {e.details}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in create_task: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/tasks")
async def list_tasks(request: Request):
    logging.info("Gateway: Received REST GET /tasks request")
    try:
        grpc_request = tasks_pb2.ListTasksRequest()
        grpc_response = grpc_task_stub.ListTasks(grpc_request, timeout=5)
        tasks_list = []
        for task in grpc_response.tasks:
            tasks_list.append({
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "created_by": task.created_by,
                "_links": add_hateoas_links(request, "tasks", task.id) # HATEOAS for each task
            })
        response_content = {
            "tasks": tasks_list,
            "message": grpc_response.message,
            "_links": add_hateoas_links(request, "tasks") # HATEOAS for the collection
        }
        logging.info(f"Gateway: Sent gRPC ListTasks, found {len(tasks_list)} tasks.")
        return JSONResponse(content=response_content)
    except grpc.RpcError as e:
        logging.error(f"Gateway: gRPC ListTasks failed: {e.details}")
        raise HTTPException(status_code=503, detail=f"gRPC Task Service Error: {e.details}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in list_tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/tasks/{task_id}")
async def get_task_by_id(task_id: int, request: Request):
    logging.info(f"Gateway: Received REST GET /tasks/{task_id} request")
    try:
        grpc_request = tasks_pb2.GetTaskRequest(id=task_id)
        grpc_response = grpc_task_stub.GetTask(grpc_request, timeout=5)
        if not grpc_response.task.id: # Check if task was actually found
             raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")

        response_content = {
            "task": {
                "id": grpc_response.task.id,
                "title": grpc_response.task.title,
                "description": grpc_response.task.description,
                "status": grpc_response.task.status,
                "created_by": grpc_response.task.created_by,
            },
            "message": grpc_response.message,
            "_links": add_hateoas_links(request, "tasks", grpc_response.task.id)
        }
        logging.info(f"Gateway: Sent gRPC GetTask for ID {task_id}, received response: {grpc_response.message}")
        return JSONResponse(content=response_content)
    except grpc.RpcError as e:
        logging.error(f"Gateway: gRPC GetTask failed for ID {task_id}: {e.details}")
        if e.code() == codes.NotFound:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
        raise HTTPException(status_code=503, detail=f"gRPC Task Service Error: {e.details}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in get_task_by_id for ID {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


@app.put("/tasks/{task_id}")
async def update_task(task_id: int, request_data: dict, request: Request):
    logging.info(f"Gateway: Received REST PUT /tasks/{task_id} request: {request_data}")
    try:
        grpc_request = tasks_pb2.UpdateTaskRequest(
            id=task_id,
            title=request_data.get("title", ""),
            description=request_data.get("description", ""),
            status=request_data.get("status", "")
        )
        grpc_response = grpc_task_stub.UpdateTask(grpc_request, timeout=5)
        response_content = {
            "task": {
                "id": grpc_response.task.id,
                "title": grpc_response.task.title,
                "description": grpc_response.task.description,
                "status": grpc_response.task.status,
                "created_by": grpc_response.task.created_by,
            },
            "message": grpc_response.message,
            "_links": add_hateoas_links(request, "tasks", grpc_response.task.id)
        }
        logging.info(f"Gateway: Sent gRPC UpdateTask for ID {task_id}, received response: {grpc_response.message}")
        return JSONResponse(content=response_content)
    except grpc.RpcError as e:
        logging.error(f"Gateway: gRPC UpdateTask failed for ID {task_id}: {e.details}")
        if e.code() == codes.NotFound:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
        raise HTTPException(status_code=503, detail=f"gRPC Task Service Error: {e.details}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in update_task for ID {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: int):
    logging.info(f"Gateway: Received REST DELETE /tasks/{task_id} request")
    try:
        grpc_request = tasks_pb2.DeleteTaskRequest(id=task_id)
        grpc_response = grpc_task_stub.DeleteTask(grpc_request, timeout=5)
        if not grpc_response.success:
            logging.warning(f"Gateway: gRPC DeleteTask failed for ID {task_id}: {grpc_response.message}")
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found: {grpc_response.message}")
        logging.info(f"Gateway: Sent gRPC DeleteTask for ID {task_id}, received success.")
        return # 204 No Content
    except grpc.RpcError as e:
        logging.error(f"Gateway: gRPC DeleteTask failed for ID {task_id}: {e.details}")
        if e.code() == codes.NotFound:
            raise HTTPException(status_code=404, detail=f"Task with ID {task_id} not found.")
        raise HTTPException(status_code=503, detail=f"gRPC Task Service Error: {e.details}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in delete_task for ID {task_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# --- User Endpoints (REST -> SOAP) ---

@app.post("/users", status_code=201)
async def create_user(request_data: dict, request: Request):
    logging.info(f"Gateway: Received REST POST /users request: {request_data}")
    name = request_data.get("name")
    email = request_data.get("email")

    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required for user creation.")

    # Construct SOAP XML request
    soap_request_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:tns="urn:user.service.soap">
      <soap:Body>
        <tns:createUser>
          <tns:name>{name}</tns:name>
          <tns:email>{email}</tns:email>
        </tns:createUser>
      </soap:Body>
    </soap:Envelope>"""

    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SOAP_SERVICE_ADDRESS, headers=headers, content=soap_request_xml, timeout=5)
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            
            soap_response_xml = response.text
            logging.info(f"Gateway: Received SOAP response for create_user: {soap_response_xml}")

            # Simple parsing of SOAP response (for demonstration)
            # In a real app, use an XML parser like lxml or defusedxml
            user_id_start = soap_response_xml.find('<user_id>') + len('<user_id>')
            user_id_end = soap_response_xml.find('</user_id>')
            user_id = int(soap_response_xml[user_id_start:user_id_end]) if user_id_start != -1 and user_id_end != -1 else None

            user_name_start = soap_response_xml.find('<name>') + len('<name>')
            user_name_end = soap_response_xml.find('</name>')
            user_name = soap_response_xml[user_name_start:user_name_end] if user_name_start != -1 and user_name_end != -1 else ""

            user_email_start = soap_response_xml.find('<email>') + len('<email>')
            user_email_end = soap_response_xml.find('</email>')
            user_email = soap_response_xml[user_email_start:user_email_end] if user_email_start != -1 and user_email_end != -1 else ""

            response_content = {
                "user": {
                    "user_id": user_id,
                    "name": user_name,
                    "email": user_email,
                },
                "message": "User created successfully via SOAP.",
                "_links": add_hateoas_links(request, "users", user_id)
            }
            return JSONResponse(content=response_content)

    except httpx.RequestError as e:
        logging.error(f"Gateway: SOAP create_user request failed: {e}")
        raise HTTPException(status_code=503, detail=f"SOAP User Service Error: Cannot connect to service. {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Gateway: SOAP create_user returned HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=502, detail=f"SOAP User Service returned error: {e.response.text}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in create_user (SOAP): {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/users")
async def list_users(request: Request):
    logging.info(f"Gateway: Received REST GET /users request")
    # Construct SOAP XML request for list_users
    soap_request_xml = """<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:tns="urn:user.service.soap">
      <soap:Body>
        <tns:list_users/>
      </soap:Body>
    </soap:Envelope>"""

    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SOAP_SERVICE_ADDRESS, headers=headers, content=soap_request_xml, timeout=5)
            response.raise_for_status()
            
            soap_response_xml = response.text
            logging.info(f"Gateway: Received SOAP response for list_users: {soap_response_xml}")

            # Simple parsing of SOAP response for multiple users
            users_list = []
            # This parsing is very basic and fragile. A robust XML parser is recommended.
            user_elements = soap_response_xml.split('<User>')
            for user_element in user_elements[1:]: # Skip the part before the first <User>
                user_id_start = user_element.find('<user_id>') + len('<user_id>')
                user_id_end = user_element.find('</user_id>')
                user_id = int(user_element[user_id_start:user_id_end]) if user_id_start != -1 and user_id_end != -1 else None

                user_name_start = user_element.find('<name>') + len('<name>')
                user_name_end = user_element.find('</name>')
                user_name = user_element[user_name_start:user_name_end] if user_name_start != -1 and user_name_end != -1 else ""

                user_email_start = user_element.find('<email>') + len('<email>')
                user_email_end = user_element.find('</email>')
                user_email = user_element[user_email_start:user_email_end] if user_email_start != -1 and user_email_end != -1 else ""
                
                if user_id is not None:
                    users_list.append({
                        "user_id": user_id,
                        "name": user_name,
                        "email": user_email,
                        "_links": add_hateoas_links(request, "users", user_id) # HATEOAS for each user
                    })

            response_content = {
                "users": users_list,
                "message": f"{len(users_list)} users found via SOAP.",
                "_links": add_hateoas_links(request, "users") # HATEOAS for the collection
            }
            return JSONResponse(content=response_content)

    except httpx.RequestError as e:
        logging.error(f"Gateway: SOAP list_users request failed: {e}")
        raise HTTPException(status_code=503, detail=f"SOAP User Service Error: Cannot connect to service. {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Gateway: SOAP list_users returned HTTP error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=502, detail=f"SOAP User Service returned error: {e.response.text}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in list_users (SOAP): {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

@app.get("/users/{user_id}")
async def get_user_by_id(user_id: int, request: Request):
    logging.info(f"Gateway: Received REST GET /users/{user_id} request")
    # Construct SOAP XML request for get_user
    soap_request_xml = f"""<?xml version="1.0" encoding="utf-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"
                   xmlns:tns="urn:user.service.soap">
      <soap:Body>
        <tns:get_user>
          <tns:user_id>{user_id}</tns:user_id>
        </tns:get_user>
      </soap:Body>
    </soap:Envelope>"""

    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(SOAP_SERVICE_ADDRESS, headers=headers, content=soap_request_xml, timeout=5)
            response.raise_for_status()
            
            soap_response_xml = response.text
            logging.info(f"Gateway: Received SOAP response for get_user: {soap_response_xml}")

            # Simple parsing of SOAP response for a single user
            user_id_parsed = None
            user_name_parsed = ""
            user_email_parsed = ""

            user_id_start = soap_response_xml.find('<user_id>') + len('<user_id>')
            user_id_end = soap_response_xml.find('</user_id>')
            if user_id_start != -1 and user_id_end != -1:
                user_id_parsed = int(soap_response_xml[user_id_start:user_id_end])

            user_name_start = soap_response_xml.find('<name>') + len('<name>')
            user_name_end = soap_response_xml.find('</name>')
            if user_name_start != -1 and user_name_end != -1:
                user_name_parsed = soap_response_xml[user_name_start:user_name_end]

            user_email_start = soap_response_xml.find('<email>') + len('<email>')
            user_email_end = soap_response_xml.find('</email>')
            if user_email_start != -1 and user_email_end != -1:
                user_email_parsed = soap_response_xml[user_email_start:user_email_end]
            
            if user_id_parsed is not None:
                response_content = {
                    "user": {
                        "user_id": user_id_parsed,
                        "name": user_name_parsed,
                        "email": user_email_parsed,
                    },
                    "message": f"User with ID {user_id} found via SOAP.",
                    "_links": add_hateoas_links(request, "users", user_id_parsed)
                }
                return JSONResponse(content=response_content)
            else:
                raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found via SOAP.")

    except httpx.RequestError as e:
        logging.error(f"Gateway: SOAP get_user request failed: {e}")
        raise HTTPException(status_code=503, detail=f"SOAP User Service Error: Cannot connect to service. {e}")
    except httpx.HTTPStatusError as e:
        logging.error(f"Gateway: SOAP get_user returned HTTP error: {e.response.status_code} - {e.response.text}")
        if e.response.status_code == 500 and "not found" in e.response.text.lower(): # Basic check for "not found" fault
             raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found via SOAP.")
        raise HTTPException(status_code=502, detail=f"SOAP User Service returned error: {e.response.text}")
    except Exception as e:
        logging.error(f"Gateway: Unexpected error in get_user (SOAP): {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")


# Root endpoint for API Gateway documentation
@app.get("/")
async def root():
    return JSONResponse(content={
        "message": "Welcome to the API Gateway!",
        "documentation": "/swagger",
        "endpoints": {
            "tasks": "/tasks",
            "users": "/users"
        }
    })
