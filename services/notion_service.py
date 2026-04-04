import requests
from config import Config

class NotionService:
    def __init__(self):
        self.token = Config.NOTION_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        self.database_id = Config.DATABASE_ID
        self.api_base_url = "https://api.notion.com/v1"
        
        if not self.token or "your_notion" in self.token:
            print("WARNING: Notion Token is missing or using placeholder (check .env file)")
        if not self.database_id or "your_notion" in self.database_id:
            print("WARNING: Notion Database ID is missing or using placeholder (check .env file)")

    def get_blog_posts(self):
        """Fetches all posts from the Notion database without strict filtering to avoid 400 errors."""
        url = f"{self.api_base_url}/databases/{self.database_id}/query"
        
        # We start with an empty body to fetch everything, avoiding property name/type conflicts
        payload = {}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data.get("results", []):
                posts.append(self._parse_post_metadata(item))
            return posts
        except Exception as e:
            # Enhanced error logging for debugging
            if hasattr(e, 'response') and e.response is not None:
                print(f"Notion API Error: {e.response.status_code} - {e.response.text}")
            else:
                print(f"Error fetching Notion posts: {e}")
            return []

    def get_post_by_slug(self, slug):
        """Finds a post by its slug or directly by ID if the slug looks like a UUID."""
        # 1. Try querying the database by Slug property
        url = f"{self.api_base_url}/databases/{self.database_id}/query"
        payload = {
            "filter": {
                "property": "Slug",
                "rich_text": {
                    "equals": slug
                }
            }
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            if response.status_code == 200:
                results = response.json().get("results", [])
                if results:
                    post_metadata = self._parse_post_metadata(results[0])
                    post_metadata['content'] = self.get_post_content(results[0]['id'])
                    return post_metadata
            
            # 2. If query fails (e.g. no 'Slug' column) or not found, try fetching by ID directly
            # Notion IDs are 32 chars, often with dashes (total 36)
            clean_slug = slug.replace("-", "")
            if len(clean_slug) == 32:
                page_url = f"{self.api_base_url}/pages/{slug}"
                response = requests.get(page_url, headers=self.headers)
                if response.status_code == 200:
                    page_data = response.json()
                    post_metadata = self._parse_post_metadata(page_data)
                    post_metadata['content'] = self.get_post_content(page_data['id'])
                    return post_metadata
                    
        except Exception as e:
            print(f"Error fetching post by slug/id '{slug}': {e}")
            
        return None

    def get_post_content(self, page_id):
        """Fetches all blocks (content) for a given page ID."""
        url = f"{self.api_base_url}/blocks/{page_id}/children"
        
        try:
            # Note: Notion API paginates blocks, simple implementation for now
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json().get("results", [])
        except Exception as e:
            print(f"Error fetching post content for page {page_id}: {e}")
            return []

    def _parse_post_metadata(self, item):
        """Extracts and cleans metadata from a Notion database item, searching by type if names don't match."""
        props = item.get("properties", {})
        
        # 1. Find the TITLE (it's the only one with type "title")
        title = "Untitled"
        for p_name, p_val in props.items():
            if p_val.get("type") == "title":
                title_prop = p_val.get("title", [])
                title = "".join([t.get("plain_text", "") for t in title_prop])
                break

        # 2. Find the SLUG (prefer "Slug" name, then look for first rich_text)
        slug = item.get("id") # Fallback to page ID if no slug
        slug_prop = props.get("Slug", {})
        if slug_prop.get("type") == "rich_text":
            val = slug_prop.get("rich_text", [])
            slug = "".join([t.get("plain_text", "") for t in val])
            if not slug: # if Slug prop exists but is empty, fallback
                slug = item.get("id")

        # 3. Find the DATE (prefer "Date" name, then look for first date type)
        publish_date = None
        date_prop = props.get("Date", {})
        if date_prop.get("type") == "date" and date_prop.get("date"):
            publish_date = date_prop.get("date").get("start")
        else:
            # Fallback: look for ANY date property
            for p_name, p_val in props.items():
                if p_val.get("type") == "date" and p_val.get("date"):
                    publish_date = p_val.get("date").get("start")
                    break

        return {
            "id": item.get("id"),
            "title": title,
            "slug": slug,
            "date": publish_date,
            "tags": [tag.get("name") for tag in props.get("Tags", {}).get("multi_select", [])] if "Tags" in props else [],
            "last_edited": item.get("last_edited_time")
        }
