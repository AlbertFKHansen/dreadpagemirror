from requests_tor import RequestsTor
from bs4 import BeautifulSoup
from time import sleep

class DreadSession(RequestsTor):
    """
    A wrapper class to handle Dread requests through Tor with cookie management.
    Inherits from RequestsTor to manage Tor connections and requests.
    This class is specifically designed to interact with the Dread site.
    It provides methods to perform GET requests to various endpoints,
    including subpages and posts, while managing cookies for session
    persistence and CAPTCHA handling.
    
    Attributes:
        cookies (dict): Dictionary to store cookies.
    """
    def __init__(self, cookies=None):
        # Initialize the RequestsTor part
        super().__init__(   tor_ports=(9050,), 
                            tor_cport=9051,
                            password=None,
                            autochange_id=10)
        
        # Initialize a cookie jar
        self.cookies = cookies

        # base url
        self.base_url = "http://dreadytofatroptsdj6io7l3xptbet6onoyno2yv7jicoxknyazubrad.onion"
        
    def status(self, verbose=False):
        """
        1. Check if session is configured to use Tor.
        2. Check if the connection to Dread is successful.
        
        Check the status of the connection to Dread.
        Returns:
            bool: True if Tor is configured, False otherwise.
            bool: True if Dread is reachable, False otherwise.
        """
        tor, dread = False, False
        if verbose:
            print("\nChecking Tor configuration...", end="")
        try:
            response = super().get("http://check.torproject.org/")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                if title.text.strip() == "Congratulations. This browser is configured to use Tor.":
                    if verbose:
                        print("\033[92m[OK]\033[0m Tor is configured correctly.")
                    tor = True
                else:
                    if verbose:
                        print(f"\033[93m[WARN]\033[0m {title.text.strip()}")
            else:
                if verbose:
                    print(f"\033[93m[WARN]\033[0m Unexpected status code from Tor: {response.status_code}")
        except Exception as e:
            if verbose:
                print("\033[91m[ERROR]\033[0m Failed to connect to Tor.")
                print(f"        {type(e)}")
        
        if verbose:
            print("\nChecking Dread access...", end="")
        try:
            response = self.get('/')
            if response.status_code == 200:
                if verbose:
                    print("\033[92m[OK]\033[0m Connected to Dread successfully.")
                dread = True
            else:
                if verbose:
                    print("\033[93m[WARN]\033[0m Unexpected status code from Dread: {}".format(response.status_code))
        except Exception as e:
            if verbose:
                print("\033[91m[ERROR]\033[0m Failed to connect to Dread.")
                print(f"        {type(e)}")
        
        return tor, dread

    def set_cookie(self, name, value):
        """
        Set a cookie for the Dread session.
        There are two cookies that are needed for Dread to work:
        1. dcap: CAPTCHA token
        2. dread: session ID
        These cookies are set manually from the browser after waiting
        for the queue and maybe a CAPTCHA.
        Args:
            name (str): The name of the cookie.
            value (str): The value of the cookie.
        """
        self.cookies.set(name, value, domain=None)

    def get(self, path, Verbrose=False, **kwargs):
        """
        Perform a GET request to the specified path on the Dread site.
        Args:
            path (str): The path to append to the base URL.
            Verbrose (bool): If True, prints the connection status.
            **kwargs: Additional arguments to pass to the get request.
        Returns:
            response: The response object from the GET request.
        """

        # Override the get method to include cookies
        kwargs['cookies'] = self.cookies
        try:
            response = super().get(self.base_url+path, **kwargs)
        except Exception as e:
            sleep(5)
            try:
                response = super().get(self.base_url+path, **kwargs)
            except Exception as e:
                if Verbrose:
                    print("Attempted connection: {}".format(self.base_url+path))
                    if response.status_code == 111:
                        print("Connection refused. Check if Tor is running." \
                        " or extend the sleep time.")
                    elif response.status_code == 400:
                        print("Bad request. Check the URL.")
                    elif response.status_code == 403:
                        print("Access forbidden. You may need to set cookies.")
                    elif response.status_code == 404:
                        print("Page not found.")
                    elif response.status_code == 500:
                        print("Internal server error.")
                    elif response.status_code == 503:
                        print("Service unavailable.")
                    elif response.status_code == 504:
                        print("Gateway timeout.")
                    elif response.status_code == 200:
                        print("Successfully connected.")
                    else:
                        print(f"Request succeeded but received status code: {response.status_code}")
                    print("\n")

        return response
    
    def get_subpage(self, subpage, Verbrose=False, **kwargs):
        """
        Perform a GET request to the specified subpage on the Dread site.
        Args:
            subpage (str): The subpage to append to the base URL.
            Verbrose (bool): If True, prints the connection status.
            **kwargs: Additional arguments to pass to the get request.
        Returns:
            response: The response object from the GET request.
        """
        return self.get("/d/" + subpage, Verbrose=Verbrose, **kwargs)
    
    def get_post_ids(self,subpage,start_from=1,sort="new",pagination=False,Verbrose=False, **kwargs):
        """
        Perform a GET request to the specified posts subpage on the Dread site.
        Args:
            subpage (str): The subpage to append to the base URL.
            sort (str): Sorting method for posts.
            pagination (bool): If True, enable pagination.
            Verbrose (bool): If True, prints the progress status.
            **kwargs: Additional arguments to pass to the get request.
        Returns:
            postID: The list if ID's corresponding to .onion/post/ID
        """
        postIDs = []
        response = self.get_subpage(subpage+f"?p={start_from}&sort={sort}", **kwargs)

        while True:
            # Check if the response is valid
            if response.status_code == 200:
                # Parse the response to extract post IDs
                soup = BeautifulSoup(response.text, 'html.parser')
                posts = soup.find_all('a', class_='title')
                for post in posts:
                    post_url = post.get('href')
                    if post_url and post_url.startswith('/post/'):
                        # Extract the post ID from the URL
                        post_id = post_url.split('/')[-1]
                        postIDs.append(post_id)
                
                # Check for pagination and a next page
                next_page = soup.find('a', class_='next')
                if next_page and pagination:
                    next_page_args = next_page.get('href')
                    if next_page_args:
                        if Verbrose:
                            print(f"\r\033[KPosts found: {len(postIDs)}     Next page: {subpage+next_page_args}", end="")

                        sleep(1) # Sleep to avoid getting blocked
                        try:
                            response = self.get_subpage(subpage+next_page_args, **kwargs)
                        except Exception as e:
                            print(f"tried to get: {subpage+next_page_args}")
                            print(f"Error while trying to get the page: {e}")
                            print("Sleeping for 5 seconds before retrying...")
                            sleep(5)
                            try:
                                response = self.get_subpage(subpage+next_page_args, **kwargs)
                                print("Success... continuing\n")
                            except Exception as e:
                                print("error persisting, returning the postIDs")
                                break

                    else:
                        break
                else:
                    break
        
        if Verbrose:
            print(f"\r\033[KPosts found: {len(postIDs)}")

        return postIDs

    def get_post_content(self, post_id, Verbrose=False, **kwargs):
        """
        Perform a GET request to the specified post ID on the Dread site.
        Args:
            post_id (str): The post ID to append to the base URL.
            Verbrose (bool): If True, prints the connection status.
            **kwargs: Additional arguments to pass to the get request.
        Returns:
            response: The response object from the GET request.
            post_data: A dictionary containing the useful post data.
        """
        response = self.get("/post/" + post_id, **kwargs)
        if Verbrose:
            print(f"Post ID: {post_id}      Status code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract the data
        post_title = soup.find('a', class_='title').text.strip()
        post_author = soup.find('div', class_='author').find_all('a')[0].get('href').split('/')[-1]
        post_content = soup.find('div', class_='postContent').text.strip().replace("\n", " ")
        
        # return the data as a list of dictionaries
        data = [{
            'type': 'post',
            'id': post_id,
            'parent_id': None,
            'title': post_title,
            'author': post_author,
            'content': post_content
        }]

        # Extract the comments
        comments_div = soup.find('div', class_='postComments')
        if comments_div:
            comments = comments_div.find_all('div', class_='comment', recursive=False)

        if Verbrose and not comments_div:
            print(f"No comments found for post ID: {post_id}")
        elif Verbrose:
            print(f"Extracting comments for post/comment ID: {post_id}")
            data = self.__extract_comment_data(comments, post_id, data, Verbrose=Verbrose)
        elif comments_div:
            data = self.__extract_comment_data(comments, post_id, data, Verbrose=Verbrose)

        return response, data
    

    def __extract_comment_data(self, soup, parent_id, data, Verbrose=False):
        """
        Extract comment data from the HTML soup object.
        Args:
            soup (BeautifulSoup): The soup object containing the comments.
            comments (list): List to store the extracted comments.
        Returns:
            comments: A list of dictionaries containing comment data.
        """
        for comment in soup:
            comment_id = comment.get('id')
            comment_author = comment.find('a', class_='username').get('href').split('/')[-1]
            comment_content = comment.find('div', class_='commentBody').text.strip().replace("\n", " ")

            # Check for nested comments
            if Verbrose:
                print(f"Extracting comments for post/comment ID: {comment_id}")
            nested_comments = comment.find_all('div', class_='comment', recursive=False)
            if nested_comments:
                data = self.__extract_comment_data(nested_comments, comment_id, data, Verbrose=Verbrose)
            if Verbrose:
                print(f"Comment ID: {comment_id}     Author: {comment_author}     Parent ID: {parent_id}")

            # Append the comment data to the list
            data.append({
                'type': 'comment',
                'id': comment_id,
                'parent_id': parent_id,
                'title': None,
                'author': comment_author,
                'content': comment_content
            })
        
        return data


if __name__ == "__main__":
    # Example usage
    session = DreadSession()

    """
    session and CAPTCHA cookies are needed for dread to work
    you have to set them manually from the browser after wating
    for the queue and maybe a CAPTCHA
    """
    cookies = {
    "dread": "session_ID_here", # session ID
    "dcap": "captcha_token_here" # CAPTCHA token
    }
    session.cookies = cookies

    # or initialize with cookies
    # session = DreadSession(cookies=cookies)

    """
    We can check the status of the session
    """
    session.status(verbose=True)

    # Get post IDs from a specific subpage
    post_ids = session.get_post_ids("sub_dread_here", start_from=1, sort="new", pagination=True, Verbrose=True)
    print(post_ids)

    # Get post content for a specific post ID
    response, post_data = session.get_post_content("post_id_here", Verbrose=True)
    print(post_data)

