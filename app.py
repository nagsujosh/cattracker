import os
from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
import requests
from datetime import datetime
from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-mpnet-base-v2')

# Flask App Initialization
app = Flask(__name__)

# Load secret key from environment variables for security reasons
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key')

# Deleted the production URLs and keys

# Use for local development
user_url = os.getenv('USER_API_URL', '  http://localhost:7071/api/user/')
ticket_url = os.getenv('TICKET_API_URL', '  http://localhost:7071/api/ticket/')
upload_url = os.getenv('UPLOAD_URL', '  http://localhost:7071/api/upload/')
func_key = os.getenv('FUNC_KEY', '')
upload_key = os.getenv('UPLOAD_KEY', '')

# Flask-Login Initialization
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


# Function to validate form data
def validate_form_data(data):
    return all(data.values())


def get_user_details():
    return {
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'user_id': current_user.id,
        'photo': current_user.photo
    }


# Index Route
@app.route('/')
def index():
    return render_template('index.html')


# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username_email = request.form.get('username_email')
    pw = request.form.get('password')

    if not validate_form_data({'username_email': username_email, 'password': pw}):
        flash('Both username/email and password are required', 'error')
        return redirect(url_for('login'))

    user = User.authenticate(username_email, pw)

    if user:
        login_user(user)
        flash('Logged in successfully', 'success')
        return redirect(url_for('home'))
    else:
        flash('Invalid login credentials', 'error')
        return redirect(url_for('login'))


# Logout Route
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    # Extract form data
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    pw = request.form.get('password')
    username = request.form.get('username')

    # Validate form data
    if not validate_form_data(
            {'first_name': first_name, 'last_name': last_name, 'email': email, 'password': pw, 'username': username}):
        flash("All fields are required", 'error')
        return redirect(url_for('signup'))

    # Create user via API
    try:
        res = requests.post(user_url, params={'code': func_key}, json={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': pw
        })

        if res.status_code == 201:
            flash("Account created successfully! Please log in.", 'success')
            return redirect(url_for('login'))
        else:
            flash(f"Error creating account: {res.text}", 'error')
            return redirect(url_for('signup'))
    except requests.exceptions.RequestException as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('signup'))


# Home Route
@app.route('/home')
@login_required
def home():
    res = requests.get(ticket_url, params={'code': func_key})
    tickets = res.json() if res.status_code == 200 else []
    user_details = get_user_details()
    return render_template('home.html', user=user_details, tickets=tickets)


# Found Route
@app.route('/found')
@login_required
def found():
    user_details = get_user_details()
    res = requests.get(ticket_url, params={'code': func_key, 'user_id': current_user.username})
    tickets = res.json() if res.status_code == 200 else []
    print(tickets)

    return render_template('found.html', tickets=tickets, user=user_details)


@app.route('/ticket/create', methods=['POST'])
@login_required
def create_ticket():
    # Validate form data
    if not all([
        request.form.get('lost_item'),
        request.form.get('description'),
        request.form.get('location_lost'),
        request.form.get('datetime')
    ]):
        flash("All fields are required.", 'error')
        return redirect(url_for('home'))

    # Handle file upload
    file_url = None
    if "photo" in request.files and request.files["photo"].filename:
        file = request.files["photo"]

        try:
            # Upload file
            file_response = requests.post(
                upload_url,
                params={'code': func_key},
                files={"file": file}
            )

            if file_response.status_code != 201:
                flash("Failed to upload photo.", 'error')
                return redirect(url_for('create_ticket'))

            # Get the file URL from the upload response
            file_url = file_response.json().get('file_url')

        except requests.exceptions.RequestException as e:
            flash(f"Photo upload error: {str(e)}", 'error')
            return redirect(url_for('create_ticket'))

    try:
        # Create ticket with optional photo URL
        ticket_data = {
            "user_id": str(current_user.id),
            "lost": request.form.get('lost', 'True'),
            "lost_item": request.form.get('lost_item'),
            "description": request.form.get('description'),
            "location_lost": request.form.get('location_lost'),
            "date": request.form.get('datetime'),
            "photo_url": file_url  # Optional photo URL
        }

        # Send ticket creation request
        res = requests.post(
            ticket_url,
            params={'code': func_key},
            json=ticket_data
        )

        if res.status_code == 201:
            flash("Ticket created successfully!", 'success')
            return redirect(url_for('home'))
        else:
            flash(f"Error creating ticket: {res.text}", 'error')
            return redirect(url_for('create_ticket'))

    except requests.exceptions.RequestException as e:
        flash(f"An error occurred: {str(e)}", 'error')
        return redirect(url_for('create_ticket'))


@app.route('/ticket/claim/<ticket_id>', methods=['PUT'])
@login_required
def claim_ticket(ticket_id):
    try:
        res = requests.put(
            f"{ticket_url}{ticket_id}",
            params={'code': func_key},
            json={'claimer_id': current_user.username, 'claimed': True}
        )

        if res.status_code == 200:
            flash("Ticket claimed successfully", "success")
            return jsonify({"success": True, "redirect": url_for('index')})
        else:
            flash(f"Error claiming ticket: {res.text}", "error")
            return jsonify({"success": False, "message": res.text}), res.status_code

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/ticket/status/<ticket_id>', methods=['PUT'])
@login_required
def update_ticket_status(ticket_id):
    try:
        data = request.get_json()
        if 'status' not in data:
            flash("Status parameter is required", "error")
            return jsonify({"success": False, "message": "Status parameter is required"}), 400

        status = data['status']

        res = requests.put(
            f"{ticket_url}status/{ticket_id}",
            params={'code': func_key},
            json={'status': status}
        )

        if res.status_code == 200:
            flash("Ticket status updated successfully", "success")
            return jsonify({"success": True, "message": "Ticket status updated successfully"})
        else:
            flash(f"Error updating ticket status: {res.text}", "error")
            return jsonify({"success": False, "message": res.text}), res.status_code

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/ticket/delete/<ticket_id>', methods=['DELETE'])
@login_required
def delete_ticket(ticket_id):
    try:
        # Fetch the ticket details
        ticket_res = requests.get(f"{ticket_url}{ticket_id}", params={'code': func_key})

        if ticket_res.status_code != 200:
            flash(f"Error fetching ticket: {ticket_res.text}", "error")
            return jsonify({"success": False, "message": ticket_res.text}), ticket_res.status_code

        ticket = ticket_res.json()

        # Check if the current user is the creator of the ticket
        if ticket['user_id'] != str(current_user.username):

            flash("Unauthorized to delete this ticket", "error")
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        # Proceed with deletion
        res = requests.delete(f"{ticket_url}/{ticket_id}", params={"code": func_key})

        if res.status_code == 200:
            flash("Ticket deleted successfully", "success")
            return jsonify({"success": True, "message": "Ticket deleted successfully"})
        else:
            flash(f"Error deleting ticket: {res.text}", "error")
            return jsonify({"success": False, "message": res.text}), res.status_code

    except Exception as e:
        flash(f"An error occurred: {str(e)}", "error")
        return jsonify({"success": False, "message": str(e)}), 500


# Lost Route
@app.route('/lost')
@login_required
def lost():
    res = requests.get(ticket_url, params={'code': func_key, 'user_id': current_user.username})
    tickets = res.json() if res.status_code == 200 else []
    user_details = get_user_details()
    return render_template('lost.html', user=user_details, tickets=tickets)


@app.route('/home-found')
@login_required
def home_found():
    user_details = get_user_details()
    res = requests.get(ticket_url, params={'code': func_key})
    tickets = res.json() if res.status_code == 200 else []
    return render_template('home-found.html', tickets=tickets, user=user_details)


@app.route('/home-claim')
@login_required
def home_claim():
    user_details = get_user_details()
    res = requests.get(ticket_url, params={'code': func_key})
    tickets = res.json() if res.status_code == 200 else []
    return render_template('home-claim.html', tickets=tickets, user=user_details)


# Claim Route
@app.route('/claim')
@login_required
def claim():
    user_details = get_user_details()

    # Fetch all tickets from other users
    res = requests.get(ticket_url, params={'code': func_key, 'not_user_id': current_user.username})
    tickets_all = res.json().get('tickets', []) if res.status_code == 200 else []
    # Fetch the user's tickets
    res = requests.get(ticket_url, params={'code': func_key, 'user_id': current_user.username})
    tickets_user = res.json().get('tickets', []) if res.status_code == 200 else []

    # Extract descriptions
    user_descriptions = [ticket['description'] for ticket in tickets_user]
    other_descriptions = [ticket['description'] for ticket in tickets_all]

    # Encode descriptions to embeddings
    user_embeddings = model.encode(user_descriptions, convert_to_tensor=True)
    other_embeddings = model.encode(other_descriptions, convert_to_tensor=True)

    # Find matches using cosine similarity
    matches = []
    for idx, user_emb in enumerate(user_embeddings):
        similarities = util.cos_sim(user_emb, other_embeddings)
        for j, score in enumerate(similarities.tolist()[0]):
            if score > 0.8:
                matches.append(tickets_all[j])

    filtered_matches = [ticket for ticket in matches if ticket.get('claimed') is False and ticket.get('lost') is False]
    unique_filtered_matches = list({ticket['_id']: ticket for ticket in filtered_matches}.values())
    print(unique_filtered_matches)
    return render_template('claim.html', tickets=tickets_user, user=user_details,
                           matched_tickets=unique_filtered_matches)


@app.route('/claim-found')
@login_required
def claim_found():
    user_details = get_user_details()

    # Fetch all tickets from other users
    res = requests.get(ticket_url, params={'code': func_key, 'not_user_id': current_user.username})
    tickets_all = res.json().get('tickets', []) if res.status_code == 200 else []

    # Fetch the user's tickets
    res = requests.get(ticket_url, params={'code': func_key, 'user_id': current_user.username})
    tickets_user = res.json().get('tickets', []) if res.status_code == 200 else []

    # Extract descriptions
    user_descriptions = [ticket['description'] for ticket in tickets_user]
    other_descriptions = [ticket['description'] for ticket in tickets_all]

    # Encode descriptions to embeddings
    user_embeddings = model.encode(user_descriptions, convert_to_tensor=True)
    other_embeddings = model.encode(other_descriptions, convert_to_tensor=True)

    # Find matches using cosine similarity
    matches = []
    for idx, user_emb in enumerate(user_embeddings):
        similarities = util.cos_sim(user_emb, other_embeddings)
        for j, score in enumerate(similarities.tolist()[0]):
            if score > 0.8:
                matches.append(tickets_all[j])

    filtered_matches = [ticket for ticket in matches if ticket.get('claimed') is False and ticket.get('lost') is True]
    unique_filtered_matches = list({ticket['_id']: ticket for ticket in filtered_matches}.values())
    return render_template('claim-found.html', tickets=tickets_user, user=user_details,
                           matched_tickets=unique_filtered_matches)


# Settings Route
@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'profile':
            first_name = request.form.get('firstName')
            last_name = request.form.get('lastName')
            update_data = {'first_name': first_name, 'last_name': last_name}

        elif action == 'email_username':
            new_email = request.form.get('newEmail')
            new_username = request.form.get('newUsername')
            update_data = {'email': new_email, 'username': new_username}

        elif action == 'password':
            current_password = request.form.get('currentPassword')
            new_password = request.form.get('newPassword')

            if not current_user.check_password(current_password):
                flash('Incorrect current password.', 'error')
                return redirect(url_for('settings'))

            update_data = {'password': new_password}

        elif action == 'upload_photo':
            if 'profile_photo' in request.files and request.files['profile_photo'].filename:
                file = request.files['profile_photo']

                try:
                    # Upload file
                    file_response = requests.post(
                        upload_url,
                        params={'code': func_key},
                        files={'file': file}
                    )

                    if file_response.status_code != 201:
                        flash('Failed to upload photo.', 'error')
                        return redirect(url_for('settings'))

                    # Get the file URL from the upload response
                    file_url = file_response.json().get('file_url')
                    update_data = {'photo': file_url}

                except requests.exceptions.RequestException as e:
                    flash(f'Photo upload error: {str(e)}', 'error')
                    return redirect(url_for('settings'))

        else:
            flash('Invalid form submission.', 'error')
            return redirect(url_for('settings'))

        try:
            res = requests.put(
                f"{user_url}{current_user.id}",
                params={'code': func_key},
                json=update_data
            )
            if res.status_code == 200:
                if action == 'password':
                    flash('Password updated successfully!', 'success')
                elif action == 'profile':
                    flash('Profile updated successfully!', 'success')
                elif action == 'email_username':
                    flash('Email and Username updated successfully!', 'success')
                elif action == 'upload_photo':
                    flash('Profile photo updated successfully!', 'success')
            else:
                flash(f"Error updating profile: {res.text}", 'error')
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {str(e)}", 'error')

        return redirect(url_for('settings'))

    return render_template('settings.html', user=current_user)


@app.route('/users/<user_id>/delete', methods=['POST'])
@login_required
def user_delete(user_id):
    confirm_username = request.form.get('confirm_username')

    if confirm_username != current_user.username:
        flash("User ID confirmation failed. Please enter the correct ID.")
        return redirect(url_for('settings'))

    delete_res = requests.delete(user_url + user_id, params={"code": func_key})

    if delete_res.status_code == 200:
        flash(f"User {user_id} deleted successfully.")
        return redirect(url_for('index'))
    else:
        flash(f"Error deleting user {user_id}.")
        return redirect(url_for('settings'))


@app.route('/search', methods=['GET'])
@login_required
def search():
    query = request.args.get('query')
    if not query:
        flash('Please enter a search term.', 'error')
        return redirect(url_for('home'))

    # Fetch all tickets from the external API
    res = requests.get(ticket_url, params={'code': func_key})
    tickets = res.json().get('tickets', []) if res.status_code == 200 else []

    # Extract relevant fields from the tickets and combine them
    combined_texts = [
        f"{ticket['description']} {ticket['location']} {ticket['issue_date']} {ticket['lost_item']}"
        for ticket in tickets
    ]

    # Encode the search query and combined texts
    query_embedding = model.encode(query, convert_to_tensor=True)
    ticket_embeddings = model.encode(combined_texts, convert_to_tensor=True)

    # Compute cosine similarity between the query embedding and ticket embeddings
    similarities = util.cos_sim(query_embedding, ticket_embeddings).tolist()[0]

    # Filter and sort the results based on similarity scores
    search_results = [
        ticket for _, ticket in sorted(zip(similarities, tickets), key=lambda pair: pair[0], reverse=True)
        if _ > 0.3
    ]

    return render_template('search_results.html', query=query, results=search_results)


# Error Handlers
@app.errorhandler(401)
def unauthorized(error):
    flash('You must be logged in to access this page', 'error')
    return redirect(url_for('login'))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


# Custom Error Page for 500
@app.errorhandler(500)
def internal_error(error):
    flash('An internal server error occurred. Please try again later.', 'error')
    return render_template('500.html'), 500


@app.template_filter()
def format_datetime(value):
    if not value:
        return ''

    value = str(value)

    try:
        return datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f').strftime('%B %d, %Y %I:%M %p')
    except ValueError:
        try:
            return datetime.strptime(value, '%Y-%m-%dT%H:%M').strftime('%B %d, %Y %I:%M %p')
        except ValueError:
            return value


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
