import azure.functions as func
import logging
from bson import ObjectId, json_util
from database import user, ticket
import json
from azure.storage.blob import BlobServiceClient
import uuid
import os

# Connect to the database
conn_str = 'not showing this time production hahaha'
user.connect(conn_str)
ticket.connect(conn_str)
app = func.FunctionApp()

# Blob Storage connection string and container
BLOB_CONNECTION_STRING = "not showing this time production hahaha"
BLOB_CONTAINER_NAME = "not showing this time production hahaha"
ACCOUNT_NAME = "not showing this time production hahaha"
ACCOUNT_KEY = "not showing this time production hahaha"

# Initialize BlobServiceClient
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)


# ------------------- User-related functions ------------------- #
@app.route(route="user", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def create_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid input", status_code=400)

    first_name = req_body.get('first_name')
    last_name = req_body.get('last_name')
    email = req_body.get('email')
    password = req_body.get('password')
    username = req_body.get('username')

    if not (username and password and first_name and last_name and email):
        return func.HttpResponse("All fields are required", status_code=400)

    uid = user.create_user(username, password, first_name, last_name, email)
    return func.HttpResponse(str(uid), status_code=201)


@app.route(route="user/{_id?}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def read_user(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Extract parameters
        _id = req.route_params.get('_id')
        username = req.params.get('username')
        password = req.params.get('password')
        email = req.params.get('email')

        if _id:
            # Handle fetching user by ID
            user_data = user.read_user(_id)
            if not user_data:
                return func.HttpResponse("User not found", status_code=404)

            user_json = json_util.dumps(user_data)
            return func.HttpResponse(user_json, mimetype="application/json")

        elif username and password:
            # Handle fetching user by username and password
            matching_users = list(user.read_users({'username': username, 'password': password}))
            if matching_users:
                user_json = json_util.dumps(matching_users[0])  # Return the first matching user
                return func.HttpResponse(user_json, mimetype="application/json")
            else:
                return func.HttpResponse("User not found", status_code=404)

        elif email and password:
            # Handle fetching user by email and password
            matching_users = list(user.read_users({'email': email, 'password': password}))
            if matching_users:
                user_json = json_util.dumps(matching_users[0])  # Return the first matching user
                return func.HttpResponse(user_json, mimetype="application/json")
            else:
                return func.HttpResponse("User not found", status_code=404)

        else:
            # If no parameters are provided, return all users
            all_users = list(user.read_all_users())
            if all_users:
                users_json = json_util.dumps(all_users)
                return func.HttpResponse(users_json, mimetype="application/json")
            else:
                return func.HttpResponse("No users found", status_code=404)

    except Exception as e:
        # Handle unexpected errors
        return func.HttpResponse(f"An unexpected error occurred: {str(e)}", status_code=500)


@app.route(route="user/{_id}", methods=['PUT'], auth_level=func.AuthLevel.FUNCTION)
def update_user(req: func.HttpRequest) -> func.HttpResponse:
    _id = req.route_params.get('_id')
    logging.info(f"ID: {_id}")
    if not _id:
        return func.HttpResponse("User ID is required", status_code=400)

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid input", status_code=400)

    update = req_body
    result = user.update_users(_id, update)
    return func.HttpResponse(str(result))


@app.route(route="user/{_id}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_user(req: func.HttpRequest) -> func.HttpResponse:
    _id = req.route_params.get('_id')
    logging.info(f"ID: {_id}")
    if not _id:
        return func.HttpResponse("User ID is required", status_code=400)

    result = user.delete_user(_id)
    return func.HttpResponse(str(result))


# ------------------- Ticket-related functions ------------------- #
# Create Ticket: Handles both 'lost' and 'found' tickets
@app.route(route="ticket", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def create_ticket_route(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON input", status_code=400)

    required_fields = ["lost", "lost_item", "description"]
    if not all(field in req_body for field in required_fields):
        missing_fields = [field for field in required_fields if field not in req_body]
        logging.error(f"Missing required fields: {missing_fields}")
        return func.HttpResponse(f"Missing required fields: {', '.join(missing_fields)}", status_code=400)

    lost = req_body.get("lost")
    date_found = req_body.get("date")
    photo_url = req_body.get("photo_url", None)
    if lost == "True":
        if "location_lost" not in req_body:
            return func.HttpResponse("location_lost is required for lost items", status_code=400)
        location = req_body.get("location_lost")
    else:
        if "location_lost" not in req_body:
            return func.HttpResponse("location_found is required for found items", status_code=400)
        location = req_body.get("location_lost")
    # Call the create_ticket function with the correct parameters
    ticket_id = ticket.create_ticket(
        user_id=req_body.get("user_id"),
        lost=lost == "True",
        item_name=req_body.get("lost_item"),
        location=location,
        description=req_body.get("description"),
        date_found=date_found,
        photo=photo_url
    )

    return func.HttpResponse(json.dumps({"ticket_id": ticket_id}), status_code=201)


# Retrieve a Specific Ticket
@app.route(route="ticket/{ticket_id}", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def get_ticket(req: func.HttpRequest) -> func.HttpResponse:
    ticket_id = req.route_params.get('ticket_id')
    if not ticket_id:
        return func.HttpResponse("Ticket ID is required", status_code=400)

    ticket_data = ticket.read_ticket(ticket_id)
    if not ticket_data:
        return func.HttpResponse("Ticket not found", status_code=404)

    return func.HttpResponse(json_util.dumps(ticket_data), mimetype="application/json")


# Retrieve Tickets with Filters
@app.route(route="ticket", methods=['GET'], auth_level=func.AuthLevel.FUNCTION)
def get_tickets(req: func.HttpRequest) -> func.HttpResponse:
    user_id = req.params.get('user_id')
    not_user_id = req.params.get('not_user_id')
    if user_id:
        tickets_data = ticket.get_user_tickets(user_id)
    elif not_user_id:
        tickets_data = ticket.get_tickets_except_user(not_user_id)
    else:
        tickets_data = ticket.read_all_tickets({})

    if not tickets_data["tickets"]:
        return func.HttpResponse("No tickets found", status_code=404)

    return func.HttpResponse(json_util.dumps(tickets_data), mimetype="application/json")


# Update a Ticket
@app.route(route="ticket/{ticket_id}", methods=['PUT'], auth_level=func.AuthLevel.FUNCTION)
def update_ticket(req: func.HttpRequest) -> func.HttpResponse:
    try:
        ticket_id = req.route_params.get('ticket_id')
        update_data = req.get_json()

        result = ticket.update_ticket(ticket_id, update_data)

        return func.HttpResponse(json.dumps(result),
                                 status_code=200 if result['success'] else 404,
                                 mimetype='application/json')
    except ValueError:
        return func.HttpResponse(json.dumps({
            "success": False,
            "message": "Invalid JSON input"
        }), status_code=400, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(json.dumps({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), status_code=500, mimetype='application/json')


# Update a Ticket
@app.route(route="ticket/status/{ticket_id}", methods=['PUT'], auth_level=func.AuthLevel.FUNCTION)
def update_ticket_status(req: func.HttpRequest) -> func.HttpResponse:
    ticket_id = req.route_params.get('ticket_id')

    if not ticket_id:
        return func.HttpResponse(json.dumps({
            "success": False,
            "message": "Ticket ID is required"
        }), status_code=400, mimetype='application/json')

    try:
        update_data = req.get_json()

        # Validate required fields
        if not update_data or 'status' not in update_data:
            return func.HttpResponse(json.dumps({
                "success": False,
                "message": "Invalid input: status is required"
            }), status_code=400, mimetype='application/json')

        result = ticket.update_ticket(ticket_id, update_data)

        return func.HttpResponse(json.dumps(result),
                                 status_code=200 if result['success'] else 404,
                                 mimetype='application/json')

    except ValueError:
        return func.HttpResponse(json.dumps({
            "success": False,
            "message": "Invalid JSON input"
        }), status_code=400, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(json.dumps({
            "success": False,
            "message": f"Unexpected error: {str(e)}"
        }), status_code=500, mimetype='application/json')


# Delete a Ticket
@app.route(route="ticket/{ticket_id}", methods=['DELETE'], auth_level=func.AuthLevel.FUNCTION)
def delete_ticket(req: func.HttpRequest) -> func.HttpResponse:
    ticket_id = req.route_params.get('ticket_id')
    if not ticket_id:
        return func.HttpResponse("Ticket ID is required", status_code=400)

    try:
        result = ticket.delete_ticket(ticket_id)
        return func.HttpResponse(result["message"], status_code=200 if result["success"] else 404)
    except ValueError:
        return func.HttpResponse("Invalid input", status_code=400)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)


@app.route(route="upload", methods=['POST'], auth_level=func.AuthLevel.FUNCTION)
def upload_file(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Retrieve the file from the request
        file = req.files.get('file')
        if not file:
            return func.HttpResponse("No file provided", status_code=400)

        # Generate a unique file name and get the file content
        file_ext = os.path.splitext(file.filename)[1]  # Get original file extension
        unique_filename = f"{str(uuid.uuid4())}{file_ext}"

        file_content = file.read()

        # Upload the file to Blob Storage
        blob_client = blob_service_client.get_blob_client(
            container=BLOB_CONTAINER_NAME,
            blob=unique_filename
        )
        blob_client.upload_blob(file_content, overwrite=True)

        # Generate the file URL
        file_url = blob_client.url
        return func.HttpResponse(json.dumps({"file_url": file_url}), status_code=201)

    except Exception as e:
        logging.error(f"Error uploading file: {e}")
        return func.HttpResponse(f"Error uploading file: {str(e)}", status_code=500)
