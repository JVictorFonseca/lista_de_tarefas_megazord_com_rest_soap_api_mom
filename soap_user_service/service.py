# soap_user_service/service.py
from spyne import Application, rpc, ServiceBase, Integer, Unicode, Iterable
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from wsgiref.simple_server import make_server
import logging
import threading # For thread-safe in-memory storage

# NEW: Import ComplexModel for data types
from spyne.model.complex import ComplexModel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# In-memory storage for users
users_db = {}
next_user_id = 1
users_lock = threading.Lock() # For thread-safe access in case of multiple requests

# Define the User object (Spyne will convert this to WSDL types)
# CHANGED: Inherit from ComplexModel instead of ServiceBase
class User(ComplexModel):
    __type_name__ = 'User' # Optional: name for the WSDL type

    user_id = Integer
    name = Unicode
    email = Unicode

# Define the SOAP service
class UserService(ServiceBase):
    @rpc(Unicode, Unicode, _returns=User)
    def create_user(ctx, name, email):
        """
        Creates a new user.
        """
        global next_user_id
        with users_lock:
            user_id = next_user_id
            next_user_id += 1
            user = User(user_id=user_id, name=name, email=email)
            users_db[user_id] = user
            logging.info(f"User created: ID={user_id}, Name='{name}', Email='{email}'")
            return user

    @rpc(_returns=Iterable(User))
    def list_users(ctx):
        """
        Lists all registered users.
        """
        logging.info("Received request to list users.")
        with users_lock:
            users = list(users_db.values())
            logging.info(f"Returning {len(users)} users.")
            return users

    @rpc(Integer, _returns=User)
    def get_user(ctx, user_id):
        """
        Gets a user by ID.
        """
        logging.info(f"Received request to get user by ID: {user_id}")
        with users_lock:
            user = users_db.get(user_id)
            if user:
                logging.info(f"User found: ID={user_id}, Name='{user.name}'")
                return user
            else:
                logging.warning(f"User with ID {user_id} not found.")
                # Spyne can return SOAP Faults for errors
                raise ValueError(f"User with ID {user_id} not found.")

# Create the Spyne application
application = Application([UserService],
                          tns='urn:user.service.soap', # Target Namespace
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11())

# Create the WSGI application
wsgi_app = WsgiApplication(application)

if __name__ == '__main__':
    host = '0.0.0.0'
    port = 8001
    logging.info(f"SOAP User Service listening on http://{host}:{port}/")
    logging.info(f"WSDL available at http://{host}:{port}/?wsdl")
    server = make_server(host, port, wsgi_app)
    server.serve_forever()

