import pymongo
from bson import ObjectId
from datetime import datetime
from database.user import get_username


# Initialization and reset
def connect(conn_str: str):
    """Connect to the client and initialize the ticket collection."""
    global ticket_col
    client = pymongo.MongoClient(conn_str)
    db = client['CS518']
    ticket_col = db['ticket']
    return None


def reset():
    """Reset the ticket collection."""
    global ticket_col
    ticket_col.drop()
    return None


# CRUD operations
def create_ticket(user_id: str, lost: bool, item_name: str, location: str, description: str, date_found: str,
                  photo: str) -> str:
    """Create a new ticket for a lost or found item and return its ID."""
    global ticket_col
    username = get_username(user_id)
    ticket_data = {
        "user_id": username,
        "lost": lost,
        "lost_item": item_name,
        "location": location,
        "description": description,
        "date": date_found,
        "issue_date": datetime.now().isoformat(),
        "claimed": False,  # Default to unclaimed
        "status": True,  # Default to active / status true means the ticket is open
        "claimer_id": None,
        "photo_url": photo
    }

    result = ticket_col.insert_one(ticket_data)
    return str(result.inserted_id)


def read_ticket(ticket_id: str) -> dict:
    """Retrieve a specific ticket by its ID."""
    global ticket_col
    ticket = ticket_col.find_one({"_id": ObjectId(ticket_id)})
    if ticket:
        ticket["_id"] = str(ticket["_id"])  # Convert ObjectId to string for easier handling
    return ticket


def read_all_tickets(query: dict) -> dict:
    """Retrieve all tickets based on query."""
    global ticket_col
    cursor = ticket_col.find(query)
    tickets = list(cursor)
    for ticket in tickets:
        ticket["_id"] = str(ticket["_id"])  # Convert ObjectId to string
    total_tickets = ticket_col.count_documents(query)
    return {
        "tickets": tickets,
        "total_tickets": total_tickets
    }


def update_ticket(ticket_id: str, update: dict) -> dict:
    """Update details of a specific ticket."""
    global ticket_col
    result = ticket_col.update_one({"_id": ObjectId(ticket_id)}, {"$set": update})
    return {"success": result.modified_count > 0, "message": "Ticket updated successfully."}


def delete_ticket(ticket_id: str) -> dict:
    """Delete a ticket if the provided credentials match."""
    global ticket_col
    try:
        ticket = ticket_col.find_one({"_id": ObjectId(ticket_id)})
        if not ticket:
            return {"success": False, "message": "Ticket not found."}

        result = ticket_col.delete_one({"_id": ObjectId(ticket_id)})
        return {"success": result.deleted_count > 0, "message": "Ticket deleted successfully."}
    except ValueError:
        return {"success": False, "message": "Invalid input."}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}


def get_user_tickets(user_id: str) -> dict:
    """Retrieve all tickets created by a specific user."""
    return read_all_tickets({"user_id": user_id})


def get_tickets_except_user(user_id: str) -> dict:
    """Retrieve all tickets except those created by a specific user."""
    return read_all_tickets({"user_id": {"$ne": user_id}})


def claim_ticket(ticket_id: str, claimer_id: str, claim_details: str, found_location: str) -> dict:
    """Claim a ticket for a found item."""
    global ticket_col
    update = {
        "claimer_id": claimer_id,
        "claim_details": claim_details,
        "found_location": found_location,
        "claimed": True
    }
    result = ticket_col.update_one({"_id": ObjectId(ticket_id)}, {"$set": update})
    return {"success": result.modified_count > 0, "message": "Claim submitted successfully."}
