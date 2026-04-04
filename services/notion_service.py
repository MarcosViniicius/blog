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
        """Fetches posts from cache or Notion, grouped by 'Produção' status."""
        from services.cache_service import cache
        
        cache_key = "all_posts_metadata"
        posts = cache.get(cache_key)
        
        if posts is not None:
            return posts

        url = f"{self.api_base_url}/databases/{self.database_id}/query"
        payload = {}
        
        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            posts = []
            for item in data.get("results", []):
                post_metadata = self._parse_post_metadata(item)
                if "Produção" in post_metadata.get("status_values", []):
                    posts.append(post_metadata)
            
            # Cache the listing for a short duration (e.g. 5 mins)
            cache.set(cache_key, posts, timeout=Config.CACHE_LIST_TIMEOUT)
            return posts
        except Exception as e:
            print(f"Error fetching Notion posts: {e}")
            return []

    def get_post_by_slug(self, slug):
        """Finds a post by slug with intelligent cache invalidation based on last_edited_time."""
        from services.cache_service import cache
        
        # 1. Get current metadata from the (short-term) list to check for updates
        all_posts = self.get_blog_posts()
        current_meta = next((p for p in all_posts if p['slug'] == slug), None)
        
        if not current_meta:
            return None

        # 2. Check long-term content cache
        cache_key = f"post_full_{slug}"
        cached_post = cache.get(cache_key)
        
        if cached_post:
            # Check if the post was updated in Notion since it was cached
            if current_meta['last_edited'] == cached_post.get('last_edited'):
                return cached_post
            else:
                print(f"Post '{slug}' updated in Notion! Refreshing cache...")
                cache.delete(cache_key)

        # 3. Fetch fresh content if not cached or stale
        try:
            # We already have metadata from the list, just need the blocks
            current_meta['content'] = self.get_post_content(current_meta['id'])
            
            # Cache the full post for a long time (it will be invalidated by the check above)
            cache.set(cache_key, current_meta, timeout=Config.CACHE_POST_TIMEOUT)
            return current_meta
        except Exception as e:
            print(f"Error refreshing post '{slug}': {e}")
            
        return None

    def get_post_content(self, page_id):
        """Fetches blocks (content) for a given page ID with pagination support."""
        blocks = []
        url = f"{self.api_base_url}/blocks/{page_id}/children"
        
        try:
            while url:
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                blocks.extend(data.get("results", []))
                
                # Support pagination for articles > 100 blocks
                if data.get("has_more"):
                    url = f"{self.api_base_url}/blocks/{page_id}/children?start_cursor={data['next_cursor']}"
                else:
                    url = None
            return blocks
        except Exception as e:
            print(f"Error fetching blocks for {page_id}: {e}")
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

        # 4. Collect all status-like values for resilient filtering
        status_values = []
        for p_name, p_val in props.items():
            p_type = p_val.get("type")
            if p_type == "status" and p_val.get("status"):
                status_values.append(p_val["status"].get("name"))
            elif p_type == "select" and p_val.get("select"):
                status_values.append(p_val["select"].get("name"))
            elif p_type == "multi_select" and p_val.get("multi_select"):
                for s in p_val["multi_select"]:
                    status_values.append(s.get("name"))

        return {
            "id": item.get("id"),
            "title": title,
            "slug": slug,
            "date": publish_date,
            "tags": [tag.get("name") for tag in props.get("Tags", {}).get("multi_select", [])] if "Tags" in props else [],
            "status_values": status_values,
            "last_edited": item.get("last_edited_time")
        }
