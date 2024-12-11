import socket  # Import socket module for network communication
import threading  # Import threading for handling multiple clients concurrently
import json  # Import json for data serialization
import signal  # Import signal to handle system signals (like shutdown)
import sys  # Import sys for system-specific parameters and functions
import time  # Import time for managing time-related functions like delays
from datetime import datetime  # Import datetime for working with date and time
from newsapi import NewsApiClient  # Import the NewsApiClient to interact with the NewsAPI

class NewsServer:
    def __init__(self):
        """Initialize the news server with all necessary configurations."""
        # Core server settings
        self.host = '127.0.0.1'  # Set the server's host address (127.0.0.1)
        self.port = 49999  # Set the server's listening port
        self.server_socket = None  # Initialize the server socket as None (will be created later)
        self.running = True  # Flag to keep track if the server is running
        self.active_connections = set()  # Set to track active client connections
        
        # Configuration constants
        self.SOCKET_TIMEOUT = 10  # Set socket timeout to 10 seconds
        self.BUFFER_SIZE = 4096  # Set buffer size for receiving data from clients
        self.MAX_RECONNECT_ATTEMPTS = 3  # Set the maximum reconnection attempts
        self.RECONNECT_DELAY = 1  # Delay between reconnection attempts (in seconds)
        
        # NewsAPI initialization
        self.newsapi = NewsApiClient(api_key="530444ab828a4f12bdcbb48ab8424304")  # Initialize the NewsAPI client with the API key
        
        # Cache settings
        self.cache = {}  # Initialize a dictionary to store cached data
        self.cache_duration = 300  # Set cache duration to 300 seconds (5 minutes)
        
        # Supported parameters for requests
        self.supported_countries = ['au', 'ca', 'jp', 'ae', 'sa', 'kr', 'us', 'ma']  # List of supported countries for search
        self.supported_languages = ['ar', 'en']  # List of supported languages for search
        self.supported_categories = ['business', 'general', 'health', 'science', 'sports', 'technology']  # List of supported categories

    def generate_filename(self, client_name, request_type):
        """Generate a unique filename for saving results."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Get current timestamp as a string
        return f"A12_{client_name}_{request_type}_{timestamp}.json"  # Return a unique filename based on client name, request type, and timestamp

    def cache_get(self, key):
        """Retrieve data from cache if it exists and is not expired."""
        if key in self.cache:  # Check if the cache has the requested key
            data, timestamp = self.cache[key]  # Retrieve cached data and its timestamp
            if time.time() - timestamp < self.cache_duration:  # Check if the cached data is still valid (not expired)
                return data  # Return cached data if valid
            del self.cache[key]  # If expired, remove the cached entry
        return None  # Return None if the key is not found or the cache has expired

    def cache_set(self, key, data):
        """Store data in cache with current timestamp."""
        self.cache[key] = (data, time.time())  # Store data along with the current timestamp in the cache

    def send_to_client(self, client_socket, data, encoding='ascii'):
        """Send data to client with proper error handling."""
        try:
            if isinstance(data, str):  # Check if the data is a string
                data = data.encode(encoding)  # Encode the string to bytes using the specified encoding
            # Add newline to signal end of transmission
            data = data + b'\n'
            total_sent = 0  # Initialize the total number of bytes sent
            while total_sent < len(data):  # Loop until all data is sent
                sent = client_socket.send(data[total_sent:])  # Send a portion of the data
                if sent == 0:  # If no data was sent, raise an error
                    raise RuntimeError("Socket connection broken")
                total_sent += sent  # Update the total sent counter
            return True  # Return True if data was sent successfully
        except Exception as e:
            print(f"Error sending data: {e}")  # Print error if sending data fails
            return False  # Return False if an error occurred

    def save_and_send_response(self, client_socket, data, filename):
        """Save data to file and send filename to client."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:  # Open file in write mode with UTF-8 encoding
                json.dump(data, f, ensure_ascii=False, indent=2)  # Write the data as JSON to the file
            return self.send_to_client(client_socket, filename)  # Send the filename to the client
        except Exception as e:
            print(f"Error saving/sending response: {e}")  # Print error if saving or sending response fails
            return False  # Return False if an error occurred

    def get_headlines(self, params=None):
        """Fetch headlines from NewsAPI with caching."""
        if params is None:
            params = {'country': 'us'}  # Set default country to 'us' if no parameters are provided
        
        cache_key = f"headlines_{json.dumps(params, sort_keys=True)}"  # Generate a unique cache key based on the parameters
        cached_data = self.cache_get(cache_key)  # Check if the data is available in cache
        if cached_data:
            return cached_data  # Return cached data if available

        try:
            response = self.newsapi.get_top_headlines(**params)  # Fetch headlines from NewsAPI using the provided parameters
            self.cache_set(cache_key, response)  # Cache the response for future use
            return response  # Return the fetched headlines
        except Exception as e:
            print(f"Error fetching headlines: {e}")  # Print error if fetching headlines fails
            return {"status": "error", "message": str(e), "articles": []}  # Return an error message if fetching fails

    def get_sources(self, params=None):
        """Fetch sources from NewsAPI with caching."""
        if params is None:
            params = {}  # Use an empty dictionary as default if no parameters are provided
        
        cache_key = f"sources_{json.dumps(params, sort_keys=True)}"  # Generate a unique cache key based on the parameters
        cached_data = self.cache_get(cache_key)  # Check if the data is available in cache
        if cached_data:
            return cached_data  # Return cached data if available

        try:
            response = self.newsapi.get_sources(**params)  # Fetch sources from NewsAPI using the provided parameters
            self.cache_set(cache_key, response)  # Cache the response for future use
            return response  # Return the fetched sources
        except Exception as e:
            print(f"Error fetching sources: {e}")  # Print error if fetching sources fails
            return {"status": "error", "message": str(e), "sources": []}  # Return an error message if fetching fails

    def handle_headlines_command(self, client_socket, client_name):
        """Handle headlines-related commands."""
        search_type = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the search type command from the client
        
        try:
            if search_type == "Search by keywords":  # Handle keyword search request
                keyword = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the keyword from the client
                data = self.get_headlines({'q': keyword})  # Fetch headlines using the keyword
                filename = self.generate_filename(client_name, "keyword_search")  # Generate filename for the search results
                
            elif search_type == "Search by category":  # Handle category search request
                category = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the category from the client
                if category not in self.supported_categories:  # Check if the category is supported
                    raise ValueError(f"Unsupported category: {category}")  # Raise an error if the category is unsupported
                data = self.get_headlines({'category': category})  # Fetch headlines by category
                filename = self.generate_filename(client_name, "category_search")  # Generate filename for the search results
                
            elif search_type == "Search by country":  # Handle country search request
                country = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the country code from the client
                if country not in self.supported_countries:  # Check if the country is supported
                    raise ValueError(f"Unsupported country: {country}")  # Raise an error if the country is unsupported
                data = self.get_headlines({'country': country})  # Fetch headlines by country
                filename = self.generate_filename(client_name, "country_search")  # Generate filename for the search results
                
            elif search_type == "List all new headlines":  # Handle all headlines request
                data = self.get_headlines()  # Fetch all new headlines
                filename = self.generate_filename(client_name, "all_headlines")  # Generate filename for the search results
                
            else:
                raise ValueError(f"Unknown search type: {search_type}")  # Raise an error if the search type is unknown
                
            self.save_and_send_response(client_socket, data, filename)  # Save and send the search results to the client
            
        except Exception as e:
            print(f"Error handling headlines command: {e}")  # Print error if any issues occur
            self.send_to_client(client_socket, f"error_{str(e)}")  # Send error message to the client

    def handle_sources_command(self, client_socket, client_name):
        """Handle sources-related commands."""
        search_type = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the search type command from the client
        
        try:
            if search_type == "Search by category":  # Handle category search request
                category = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the category from the client
                if category not in self.supported_categories:  # Check if the category is supported
                    raise ValueError(f"Unsupported category: {category}")  # Raise an error if the category is unsupported
                data = self.get_sources({'category': category})  # Fetch sources by category
                filename = self.generate_filename(client_name, "sources_category")  # Generate filename for the search results
                
            elif search_type == "Search by country":  # Handle country search request
                country = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the country code from the client
                if country not in self.supported_countries:  # Check if the country is supported
                    raise ValueError(f"Unsupported country: {country}")  # Raise an error if the country is unsupported
                data = self.get_sources({'country': country})  # Fetch sources by country
                filename = self.generate_filename(client_name, "sources_country")  # Generate filename for the search results
                
            elif search_type == "Search by language":  # Handle language search request
                language = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive the language code from the client
                if language not in self.supported_languages:  # Check if the language is supported
                    raise ValueError(f"Unsupported language: {language}")  # Raise an error if the language is unsupported
                data = self.get_sources({'language': language})  # Fetch sources by language
                filename = self.generate_filename(client_name, "sources_language")  # Generate filename for the search results
                
            elif search_type == "List all sources":  # Handle all sources request
                data = self.get_sources()  # Fetch all sources
                filename = self.generate_filename(client_name, "all_sources")  # Generate filename for the search results
                
            else:
                raise ValueError(f"Unknown search type: {search_type}")  # Raise an error if the search type is unknown
                
            self.save_and_send_response(client_socket, data, filename)  # Save and send the search results to the client
            
        except Exception as e:
            print(f"Error handling sources command: {e}")  # Print error if any issues occur
            self.send_to_client(client_socket, f"error_{str(e)}")  # Send error message to the client

    def handle_client(self, client_socket, addr):
        """Handle individual client connections."""
        client_name = None  # Initialize client_name variable
        try:
            client_socket.settimeout(self.SOCKET_TIMEOUT)  # Set timeout for the client socket
            self.active_connections.add(client_socket)  # Add the client socket to active connections
            
            client_name = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive client name from the client
            if not client_name:
                raise ValueError("Invalid client name received")  # Raise error if client name is invalid
            
            print(f"Connected to client: {client_name} from {addr}")  # Print client connection info
            
            while self.running:
                try:
                    command = client_socket.recv(self.BUFFER_SIZE).decode('ascii')  # Receive command from client
                    if not command or command == "Quit":  # If the command is 'Quit' or empty, exit the loop
                        break
                        
                    if command == "Search Headlines":  # If the command is to search headlines
                        self.handle_headlines_command(client_socket, client_name)  # Handle headlines search
                    elif command == "List of Sources":  # If the command is to list sources
                        self.handle_sources_command(client_socket, client_name)  # Handle sources list
                        
                except socket.timeout:  # If the socket times out, continue
                    continue
                except Exception as e:  # Handle any other errors that occur while processing commands
                    print(f"Error processing command from {client_name}: {e}")
                    break  # Exit the loop
                    
        except Exception as e:
            print(f"Error handling client {client_name if client_name else addr}: {e}")  # Print error if any issues occur with client handling
        finally:
            self.cleanup_client(client_socket, client_name)  # Clean up after client disconnects

    def cleanup_client(self, client_socket, client_name):
        """Clean up client resources."""
        try:
            self.active_connections.remove(client_socket)  # Remove client socket from active connections
        except KeyError:  # Ignore if client socket is not found
            pass
        try:
            client_socket.close()  # Close the client socket
        except:  # Ignore any error while closing socket
            pass
        print(f"Connection closed with {client_name}")  # Print when the connection with a client is closed

    def shutdown(self):
        """Shutdown the server gracefully."""
        print("\nInitiating server shutdown...")  # Print shutdown initiation message
        self.running = False  # Set the running flag to False to stop the server
        
        # Close all active connections
        for sock in self.active_connections.copy():  # Iterate over all active connections
            try:
                sock.close()  # Close each socket connection
            except:  # Ignore any error while closing socket
                pass
        self.active_connections.clear()  # Clear the set of active connections
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()  # Close the server socket
            except:  # Ignore any error while closing the server socket
                pass
            
        print("Server shutdown complete")  # Print when server shutdown is complete

    def signal_handler(self, sig, frame):
        """Handle shutdown signals."""
        self.shutdown()  # Trigger server shutdown
        sys.exit(0)  # Exit the program gracefully

    def start(self):
        """Start the server."""
        signal.signal(signal.SIGINT, self.signal_handler)  # Handle SIGINT (Ctrl+C) for graceful shutdown
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Create a new TCP socket
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reuse of address/port
            self.server_socket.bind((self.host, self.port))  # Bind the socket to the specified host and port
            self.server_socket.listen(5)  # Start listening for incoming connections (maximum 5 clients)
            self.server_socket.settimeout(1.0)  # Set the timeout for the server socket
            
            print(f"Server started on {self.host}:{self.port}")  # Print server start message
            print("Press Ctrl+C to shutdown server")  # Inform user on how to shut down the server
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()  # Accept a new incoming client connection
                    client_thread = threading.Thread(
                        target=self.handle_client,  # Start a new thread to handle the client
                        args=(client_socket, addr)  # Pass the client socket and address to the handler function
                    )
                    client_thread.daemon = True  # Make the thread a daemon thread (will terminate when the main program terminates)
                    client_thread.start()  # Start the client handler thread
                    
                except socket.timeout:  # Ignore timeout errors while waiting for new connections
                    continue
                except Exception as e:  # Print any other error that occurs while accepting connections
                    if self.running:
                        print(f"Error accepting connection: {e}")
                        time.sleep(1)  # Wait for a short time before trying again
                    continue
                    
        except Exception as e:
            print(f"Server error: {e}")  # Print error if the server encounters an issue
        finally:
            self.shutdown()  # Ensure proper server shutdown if any exception occurs

if __name__ == "__main__":
    server = NewsServer()  # Create an instance of NewsServer
    server.start()  # Start the server
