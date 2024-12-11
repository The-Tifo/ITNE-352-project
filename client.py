import tkinter as tk
from tkinter import messagebox, ttk
import socket
import json
import datetime
import time

class NewsApp:
    def __init__(self, root):
    
        # Initialize main window properties
        self.window = root                              # Store the root window
        self.window.title("News Browser")               # Set window title
        self.window.geometry("800x600")                 # Set initial window size
        self.window.resizable(True, True)               # Allow window resizing

        # Configure server connection settings
        self.server = ('127.0.0.1', 49999)              # Server address and port
        self.socket = None                              # Socket connection object
        self.user = None                                # Store username
        self.timeout = 10                               # Connection timeout in seconds

        # Available filters 
        self.countries = {
            'Australia': 'au', 'Canada': 'ca', 'Japan': 'jp',
            'UAE': 'ae', 'Saudi Arabia': 'sa', 'Korea': 'kr',
            'USA': 'us', 'Morocco': 'ma'
        }
        self.languages = {'Arabic': 'ar', 'English': 'en'}
        self.categories = ['business', 'general', 'health', 'science', 'sports', 'technology']

        self.setup_ui()

    def setup_ui(self):
            """Set up the main UI components"""
            self.main_frame = tk.Frame(self.window)
            self.main_frame.pack(expand=True, fill="both", padx=20, pady=20)

            self.title = tk.Label(self.main_frame, text="News Browser", font=("Arial", 16))
            self.title.pack(pady=10)

            self.content = tk.Frame(self.main_frame)
            self.content.pack(expand=True, fill="both")

            self.show_login()
            
    def show_login(self):
        """Show the login screen"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Enter your name:", font=("Arial", 14))
        label.pack(pady=10)

        self.name_input = tk.Entry(self.content, font=("Arial", 12))
        self.name_input.pack(pady=5)

        connect_btn = tk.Button(self.content, text="Connect", font=("Arial", 12),
                                command=self.connect)
        connect_btn.pack(pady=10)

    def connect(self):
        """Connect to news server"""
        name = self.name_input.get()                                                 # Retrieve entered name
        if not name:
            messagebox.showwarning("Missing Name", "Please enter your name")         # Check if name is empty Show warning popup Warning title Warning message

            return      # Exit if no name entered

        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)          # Initialize TCP socket Use IPv4 Use TCP protocol
            self.socket.settimeout(self.timeout)                                     # Set connection timeout
            self.socket.connect(self.server)                                         # Connect to news server
            self.socket.sendall(name.encode('ascii'))                                # Send data to server Convert name to ASCII bytes
            
            self.user = name
            messagebox.showinfo("Success", "Connected!")                             # Save username Show success popup  Success title Success message
            self.show_main_menu()                                                    # Display main menu
        except Exception as e:
            messagebox.showerror("Connection Failed", f"Couldn't connect: {e}")
            self.socket = None

    def show_main_menu(self):
        """Show main menu options"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="What would you like to do?", font=("Arial", 14))
        label.pack(pady=10)

        buttons = [
            ("Browse Headlines", self.headlines_menu),
            ("View News Sources", self.sources_menu),
            ("Exit", self.quit)
        ]

        for text, action in buttons:
            btn = tk.Button(self.content, text=text, font=("Arial", 12),
                            command=action, width=20)
            btn.pack(pady=5)

    def headlines_menu(self):
        """Show headlines search options"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Headlines Search", font=("Arial", 14))
        label.pack(pady=10)

        buttons = [
            ("Search by Keywords", self.keyword_search),
            ("Browse by Category", lambda: self.category_search("headlines")),
            ("Browse by Country", lambda: self.country_search("headlines")), 
            ("Latest Headlines", self.get_latest),
            ("Back", self.show_main_menu)
        ]

        for text, action in buttons:
            btn = tk.Button(self.content, text=text, font=("Arial", 12),
                            command=action, width=20)
            btn.pack(pady=5)

    def sources_menu(self):
        """Show news sources search options"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="News Sources", font=("Arial", 14))
        label.pack(pady=10)

        buttons = [
            ("Browse by Category", lambda: self.category_search("sources")),
            ("Browse by Country", lambda: self.country_search("sources")),
            ("Browse by Language", self.language_search),
            ("All Sources", self.get_sources),
            ("Back", self.show_main_menu)
        ]

        for text, action in buttons:
            btn = tk.Button(self.content, text=text, font=("Arial", 12),
                            command=action, width=20)
            btn.pack(pady=5)

    def keyword_search(self):
        """Search headlines by keywords"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Enter search terms:", font=("Arial", 14))
        label.pack(pady=10)

        search_input = tk.Entry(self.content, font=("Arial", 12))
        search_input.pack(pady=5)

        search_btn = tk.Button(self.content, text="Search", font=("Arial", 12),
                                command=lambda: self.search_news(search_input.get()))
        search_btn.pack(pady=10)

        back_btn = tk.Button(self.content, text="Back", font=("Arial", 12),
                            command=self.headlines_menu)
        back_btn.pack(pady=5)

    def category_search(self, mode):
        """Search by category"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Select category:", font=("Arial", 14))
        label.pack(pady=10)

        selected = tk.StringVar(value=self.categories[0])
        
        for cat in self.categories:
            rb = tk.Radiobutton(self.content, text=cat.title(),
                                variable=selected, value=cat,
                                font=("Arial", 12))
            rb.pack(anchor=tk.W, pady=2)

        search_btn = tk.Button(self.content, text="Search", font=("Arial", 12),
                                command=lambda: self.search_category(selected.get(), mode))
        search_btn.pack(pady=10)

        back_cmd = self.headlines_menu if mode == "headlines" else self.sources_menu
        back_btn = tk.Button(self.content, text="Back", font=("Arial", 12),
                            command=back_cmd)
        back_btn.pack(pady=5)

    def country_search(self, mode):
        """Search by country"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Select country:", font=("Arial", 14))
        label.pack(pady=10)

        selected = tk.StringVar(value=list(self.countries.keys())[0])
        
        for country in self.countries:
            rb = tk.Radiobutton(self.content, text=country,
                                variable=selected, value=country,
                                font=("Arial", 12))
            rb.pack(anchor=tk.W, pady=2)

        search_btn = tk.Button(self.content, text="Search", font=("Arial", 12),
                                command=lambda: self.search_country(selected.get(), mode))
        search_btn.pack(pady=10)

        back_cmd = self.headlines_menu if mode == "headlines" else self.sources_menu
        back_btn = tk.Button(self.content, text="Back", font=("Arial", 12),
                            command=back_cmd)
        back_btn.pack(pady=5)

    def language_search(self):
        """Search sources by language"""
        self.clear_screen()
        
        label = tk.Label(self.content, text="Select language:", font=("Arial", 14))
        label.pack(pady=10)

        selected = tk.StringVar(value=list(self.languages.keys())[0])
        
        for lang in self.languages:
            rb = tk.Radiobutton(self.content, text=lang,
                                variable=selected, value=lang,
                                font=("Arial", 12))
            rb.pack(anchor=tk.W, pady=2)

        search_btn = tk.Button(self.content, text="Search", font=("Arial", 12),
                                command=lambda: self.search_language(selected.get()))
        search_btn.pack(pady=10)

        back_btn = tk.Button(self.content, text="Back", font=("Arial", 12),
                            command=self.sources_menu)
        back_btn.pack(pady=5)

    def search_news(self, query):
        """Search headlines by keywords"""
        if not query:
            messagebox.showwarning("Empty Search", "Please enter search terms")
            return
            
        try:
            self.send_command("Search Headlines")
            self.send_command("Search by keywords")
            self.send_command(query.strip())
            self.show_results("headlines")
            
        except Exception as e:
            messagebox.showerror("Search Failed", f"Couldn't perform search: {e}")
            self.headlines_menu()

    def search_category(self, category, mode):
        """Search by category"""
        try:
            cmd = "Search Headlines" if mode == "headlines" else "List of Sources"
            self.send_command(cmd)
            self.send_command("Search by category")
            self.send_command(category.lower())
            self.show_results(mode)
            
        except Exception as e:
            messagebox.showerror("Search Failed", f"Couldn't search category: {e}")
            if mode == "headlines":
                self.headlines_menu()
            else:
                self.sources_menu()

    def search_country(self, country, mode):
        """Search by country"""
        try:
            if country not in self.countries:
                raise ValueError(f"Invalid country: {country}")
            
            cmd = "Search Headlines" if mode == "headlines" else "List of Sources"
            self.send_command(cmd)
            self.send_command("Search by country")
            self.send_command(self.countries[country])
            self.show_results(mode)
            
        except Exception as e:
            messagebox.showerror("Search Failed", f"Couldn't search country: {e}")
            if mode == "headlines":
                self.headlines_menu()
            else:
                self.sources_menu()

    def search_language(self, language):
        """Search sources by language"""
        try:
            self.send_command("List of Sources")
            self.send_command("Search by language")
            self.send_command(self.languages[language])
            self.show_results("sources")
        except Exception as e:
            messagebox.showerror("Search Failed", f"Couldn't search language: {e}")
            self.sources_menu()

    def get_latest(self):
        """Get latest headlines"""
        try:
            self.send_command("Search Headlines")
            self.send_command("List all new headlines")
            self.show_results("headlines")
        except Exception as e:
            messagebox.showerror("Failed", f"Couldn't get headlines: {e}")
            self.headlines_menu()

    def get_sources(self):
        """Get all news sources"""
        try:
            self.send_command("List of Sources")
            self.send_command("List all sources")
            self.show_results("sources")
        except Exception as e:
            messagebox.showerror("Failed", f"Couldn't get sources: {e}")
            self.sources_menu()

    def send_command(self, cmd):
        """Send command to server"""
        try:
            if not self.socket:
                raise ConnectionError("Not connected")
            
            if not cmd or not isinstance(cmd, str):
                raise ValueError("Invalid command")
            
            self.socket.sendall(cmd.encode('ascii'))
            time.sleep(0.1)
            
        except Exception as e:
            raise ConnectionError(f"Command failed: {e}")

    def show_results(self, result_type):
        """Show search results"""
        try:
            response = self.socket.recv(1024).decode('ascii').strip()
            
            if response.startswith("error_"):
                raise Exception(response[6:])
            
            with open(response, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if result_type == "headlines" and "articles" not in data:
                raise ValueError("Invalid headlines data")
            if result_type == "sources" and "sources" not in data:
                raise ValueError("Invalid sources data")
            
            self.display_results(data, result_type)
            
        except Exception as e:
            raise Exception(f"Couldn't get results: {e}")

    def display_results(self, data, result_type):
        """Display results in UI"""
        self.clear_screen()

        if not data:
            messagebox.showerror("Error", "No results found")
            return

        # Create scrollable container
        container = tk.Frame(self.content)
        container.pack(expand=True, fill="both")

        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Add results
        title = "Headlines" if result_type == "headlines" else "Sources"
        tk.Label(frame, text=f"{title} Results", font=("Arial", 14, "bold")).pack(pady=10)

        if result_type == "headlines" and "articles" in data:
            self.show_articles(frame, data["articles"])
        elif result_type == "sources" and "sources" in data:
            self.show_sources(frame, data["sources"]) 
        else:
            tk.Label(frame, text="No results found", font=("Arial", 12)).pack(pady=20)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        back_cmd = self.headlines_menu if result_type == "headlines" else self.sources_menu
        tk.Button(frame, text="Back", font=("Arial", 12),
                    command=back_cmd).pack(pady=10)

    def show_articles(self, frame, articles):
        """Display article results"""
        if not articles:
            tk.Label(frame, text="No articles found", font=("Arial", 12)).pack(pady=20)
            return

        for i, article in enumerate(articles[:15], 1):
            article_frame = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
            article_frame.pack(fill=tk.X, padx=5, pady=5)
            
            def on_click(a=article):
                self.show_article_preview(a)
            
            article_frame.bind("<Button-1>", lambda e, a=article: on_click(a))

            # Title
            title = article.get('title', 'No Title')
            tk.Label(article_frame, text=f"{i}. {title}",
                    font=("Arial", 12, "bold"), wraplength=700).pack(anchor=tk.W, padx=5, pady=2)

            # Source 
            source = article.get('source', {}).get('name', 'Unknown Source')
            tk.Label(article_frame, text=f"Source: {source}",
                    font=("Arial", 10)).pack(anchor=tk.W, padx=5)

            # Description preview
            if article.get('description'):
                desc = article['description'][:150]
                if len(article['description']) > 150:
                    desc += "... (Click for more)"
                tk.Label(article_frame, text=desc, wraplength=700,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=5, pady=2)

        if len(articles) > 15:
            tk.Label(frame, text="Showing first 15 results",
                    font=("Arial", 10, "italic")).pack(pady=5)

    def show_article_preview(self, article):
        """Show detailed article preview"""
        preview = tk.Toplevel(self.window)
        preview.title("Article Preview") 
        preview.geometry("800x600")

        # Create scrollable frame
        canvas = tk.Canvas(preview)
        scrollbar = tk.Scrollbar(preview, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Title
        title = article.get('title', 'No Title')
        tk.Label(frame, text=title, font=("Arial", 16, "bold"),
                wraplength=750).pack(anchor=tk.W, padx=20, pady=10)

        # Metadata
        meta_frame = tk.Frame(frame)
        meta_frame.pack(fill=tk.X, padx=20, pady=5)

        # Source & author
        source = article.get('source', {}).get('name', 'Unknown Source')
        tk.Label(meta_frame, text=f"Source: {source}",
                font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 20))

        if article.get('author'):
            tk.Label(meta_frame, text=f"Author: {article['author']}",
                    font=("Arial", 10)).pack(side=tk.LEFT)

        # Date
        if article.get('publishedAt'):
            try:
                date = datetime.datetime.strptime(article['publishedAt'],
                                                "%Y-%m-%dT%H:%M:%SZ")
                date_str = date.strftime("%B %d, %Y at %I:%M %p")
                tk.Label(frame, text=f"Published on {date_str}",
                        font=("Arial", 10)).pack(anchor=tk.W, padx=20, pady=5)
            except ValueError:
                pass

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=10)

        # Content
        content_frame = tk.Frame(frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        if article.get('description'):
            tk.Label(content_frame, text=article['description'],
                    wraplength=750, justify=tk.LEFT,
                    font=("Arial", 12)).pack(anchor=tk.W, pady=10)

        if article.get('content'):
            content = article['content']
            if '[+' in content:
                content = content.split('[+')[0]
            
            tk.Label(content_frame, text=content, wraplength=750,
                    justify=tk.LEFT, font=("Arial", 12)).pack(anchor=tk.W, pady=10)

        tk.Button(frame, text="Close Preview", font=("Arial", 11),
                    command=preview.destroy, width=20).pack(pady=20)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        preview.transient(self.window)
        preview.grab_set()

    def show_sources(self, frame, sources):
        """Display source results"""
        if not sources:
            tk.Label(frame, text="No sources found", font=("Arial", 12)).pack(pady=20)
            return

        for i, source in enumerate(sources[:15], 1):
            source_frame = tk.Frame(frame, relief=tk.RAISED, borderwidth=1)
            source_frame.pack(fill=tk.X, padx=5, pady=5)

            def on_click(s=source):
                self.show_source_details(s)

            source_frame.bind("<Button-1>", lambda e, s=source: on_click(s))

            # Name
            name = source.get('name', 'Unknown Source')
            tk.Label(source_frame, text=f"{i}. {name}",
                    font=("Arial", 12, "bold"), wraplength=700).pack(anchor=tk.W, padx=5, pady=2)

            # Description preview
            if source.get('description'):
                desc = source['description'][:100]
                if len(source['description']) > 100:
                    desc += "... (Click for more)"
                tk.Label(source_frame, text=desc, wraplength=700,
                        font=("Arial", 10)).pack(anchor=tk.W, padx=5, pady=2)

            # Basic info
            info_frame = tk.Frame(source_frame)
            info_frame.pack(fill=tk.X, padx=5)

            if source.get('category'):
                tk.Label(info_frame, text=f"Category: {source['category'].title()}",
                        font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

            if source.get('country'):
                tk.Label(info_frame, text=f"Country: {source['country'].upper()}",
                        font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        if len(sources) > 15:
            tk.Label(frame, text="Showing first 15 results",
                    font=("Arial", 10, "italic")).pack(pady=5)

    def show_source_details(self, source):
        """Show detailed source information"""
        details = tk.Toplevel(self.window)
        details.title("Source Details")
        details.geometry("800x600")

        canvas = tk.Canvas(details)
        scrollbar = tk.Scrollbar(details, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor="nw")

        # Name
        name = source.get('name', 'Unknown Source')
        tk.Label(frame, text=name, font=("Arial", 16, "bold"),
                wraplength=750).pack(anchor=tk.W, padx=20, pady=10)

        # Metadata
        meta_frame = tk.Frame(frame)
        meta_frame.pack(fill=tk.X, padx=20, pady=5)

        if source.get('category'):
            tk.Label(meta_frame, text=f"Category: {source['category'].title()}",
                    font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 20))

        if source.get('language'):
            tk.Label(meta_frame, text=f"Language: {source['language'].upper()}",
                    font=("Arial", 10)).pack(side=tk.LEFT, padx=(0, 20))

        if source.get('country'):
            tk.Label(meta_frame, text=f"Country: {source['country'].upper()}",
                    font=("Arial", 10)).pack(side=tk.LEFT)

        ttk.Separator(frame, orient='horizontal').pack(fill='x', padx=20, pady=10)

        if source.get('description'):
            tk.Label(frame, text="About:", font=("Arial", 12, "bold")).pack(anchor=tk.W, padx=20, pady=5)
            tk.Label(frame, text=source['description'], wraplength=750,
                    justify=tk.LEFT, font=("Arial", 12)).pack(anchor=tk.W, padx=20, pady=5)

        tk.Button(frame, text="Close", font=("Arial", 11),
                    command=details.destroy, width=20).pack(pady=20)

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        details.transient(self.window)
        details.grab_set()

    def clear_screen(self):
        """Clear the content frame"""
        for widget in self.content.winfo_children():
            widget.destroy()

    def quit(self):
        """Exit the application"""
        if self.socket:
            try:
                self.send_command("Quit")
                self.socket.close()
            except:
                pass
        self.window.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NewsApp(root)
    root.mainloop()