# Lost and Found Service App

## **Overview**
The Lost and Found Service App is a user-friendly platform that helps university students find and report lost items on campus. Users can create, update, and delete tickets for lost and found items, search for items using detailed descriptions, and upload photos for better identification. With features like real-time chat and advanced semantic search, the app simplifies the process of reconnecting students with their belongings.

## **Key Features**

- **User Authentication**: Sign up, log in, and manage user profiles securely.
- **Ticket Management**: Easily create, update, and delete tickets for lost and found items.
- **Real-time Chat**: Communicate with other users in real time using Flask-SocketIO. *(Feature in development)*
- **Photo Upload**: Upload and store item images in Azure Blob Storage for better item identification.
- **Semantic Search**: Use AI-powered semantic search from `sentence-transformers` to locate items quickly based on descriptive queries.
- **Responsive Design**: Enjoy a smooth experience on desktop, tablet, and mobile devices.

## **Tech Stack**
- **Backend**: Flask (web framework) with Flask-SocketIO for real-time communication.
- **Storage**: Azure Blob Storage for securely storing images.
- **AI/ML**: Pre-trained models from `sentence-transformers` for semantic search.
- **Containerization**: Docker for environment consistency across development and production.

## **Azure Services Used**
- **Azure Blob Storage**: Stores uploaded photos of lost and found items.
- **Azure Functions**: Handles backend processes like user authentication and service logic.

## **Docker Integration**
The project is containerized using Docker, ensuring a consistent development and production environment. Here’s a breakdown of the `Dockerfile` configuration:

### **Dockerfile Highlights**
1. **Base Image**: Uses a lightweight Python 3.9.6 image.
2. **Environment Variables**: Sets essential environment variables to optimize Python behavior.
3. **Working Directory**: Establishes `/app` as the working directory.
4. **Non-root User**: Runs the application using a non-root user for security.
5. **Dependency Installation**: Installs the required Python packages from `requirements.txt`.
6. **File Copying**: Copies application files into the container.
7. **Port Exposure**: Exposes port 80 for external access.
8. **Run Command**: Executes the Flask application.

### **Docker Commands**
- **Build the Docker Image**:
  ```sh
  docker build -t lost-and-found-service-app .
  ```
- **Run the Docker Container**:
  ```sh
  docker run -p 80:80 lost-and-found-service-app
  ```

## **Installation & Setup**
To get started, follow these steps:

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/yourusername/lost-and-found-service-app.git
   cd lost-and-found-service-app
   ```

2. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   - Create a `.env` file.
   - Add required environment variables for Azure Blob Storage and other configurations.

4. **Run the Application**:
   ```sh
   flask run
   ```

## **Usage Instructions**
- **Creating a Ticket**: Navigate to the "Create Ticket" page, fill in item details, and submit the form.
- **Searching for Items**: Use the search bar to find items by entering descriptive keywords.
- **Chatting**: Access the chat feature to communicate with other users in real time. *(Feature in development)*

## **Contributing**
We welcome contributions to improve the app. Follow these steps to contribute:

1. **Fork the Repository**: Click the "Fork" button at the top-right corner of the repository.
2. **Create a Branch**: Create a new branch for your feature or bug fix.
3. **Make Changes**: Implement your feature or bug fix.
4. **Push Changes**: Push your changes to your forked repository.
5. **Submit a Pull Request**: Create a pull request with a clear description of your changes.

## **Authors & Acknowledgments**
- **Sujosh Nag**: Development
- **Tyler Norcross**: Initial Design

## **License**
This project is licensed under the **MIT License**. Feel free to use, modify, and distribute it according to the license terms.

## **Project Status**
The project is actively being developed, with several features in progress. New enhancements and improvements are planned for future releases.