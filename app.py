from flask import Flask, render_template, abort, Response, redirect, url_for
from services.notion_service import NotionService
from services.cache_service import cache
from utils.parser import NotionParser
from config import Config
from feedgen.feed import FeedGenerator
from datetime import datetime
import collections

app = Flask(__name__)
app.config.from_object(Config)

# Configure Flask-Caching
app.config['CACHE_TYPE'] = Config.CACHE_TYPE
app.config['CACHE_DIR'] = Config.CACHE_DIR
cache.init_app(app)

notion_service = NotionService()
notion_parser = NotionParser()

@app.context_processor
def inject_globals():
    """Injects global variables into all templates."""
    return {
        'now': datetime.now(),
        'config': Config
    }

def get_grouped_posts():
    """Fetches and groups posts by year and month for the index page."""
    posts = cache.get("all_posts")
    if posts is None:
        posts = notion_service.get_blog_posts()
        cache.set("all_posts", posts)
    
    # Group by year and then by month
    grouped = collections.defaultdict(lambda: collections.defaultdict(list))
    for post in posts:
        # Use date if available, otherwise fallback to last_edited time
        date_str = post.get('date')
        if not date_str and post.get('last_edited'):
            date_str = post['last_edited'][:10] # Get YYYY-MM-DD from ISO string
            
        if date_str:
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # Fallback for full ISO strings or malformed dates
                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            
            grouped[dt.year][dt.strftime('%B')].append(post)
        else:
            # Absolute fallback
            grouped['Other']['Unknown'].append(post)
    
    # Sort years descending, months chronological (but grouped in years descending)
    sorted_grouped = []
    for year in sorted(grouped.keys(), reverse=True):
        months = []
        for month_name in sorted(grouped[year].keys(), key=lambda m: datetime.strptime(m, '%B').month, reverse=True):
            months.append({
                'name': month_name,
                'posts': grouped[year][month_name]
            })
        sorted_grouped.append({
            'year': year,
            'months': months
        })
    
    return sorted_grouped

@app.route('/')
def index():
    """Home page showing a list of posts."""
    try:
        grouped_posts = get_grouped_posts()
        return render_template('index.html', grouped_posts=grouped_posts)
    except Exception as e:
        print(f"Error rendering index: {e}")
        return "Internal Server Error", 500

@app.route('/post/<slug>')
def post_detail(slug):
    """Specific blog post page."""
    cache_key = f"post_{slug}"
    post = cache.get(cache_key)
    
    if post is None:
        post = notion_service.get_post_by_slug(slug)
        if post:
            post['html_content'] = notion_parser.blocks_to_html(post['content'])
            cache.set(cache_key, post)
    
    if not post:
        abort(404)
        
    return render_template('post.html', post=post)

@app.route('/rss')
@cache.cached(timeout=Config.CACHE_LIST_TIMEOUT) # Cache the entire XML response
def rss():
    """Generates the RSS feed using optimized caching."""
    posts = notion_service.get_blog_posts()
    
    # Limit RSS to the last 15 posts
    latest_posts = posts[:15]
        
    fg = FeedGenerator()
    fg.id(Config.BASE_URL)
    fg.title(Config.BLOG_NAME)
    fg.description(Config.BLOG_DESCRIPTION)
    fg.link(href=Config.BASE_URL, rel='alternate')
    
    for post in latest_posts:
        # Use the intelligent cache from get_post_by_slug to avoid redundant Notion calls
        # We fetch by slug or use a dedicated cached method
        full_post = notion_service.get_post_by_slug(post['slug'])
        
        if not full_post:
            continue
            
        html_content = notion_parser.blocks_to_html(full_post['content'])
        
        fe = fg.add_entry()
        fe.id(f"{Config.BASE_URL}/post/{post['slug']}")
        fe.title(post['title'])
        fe.link(href=f"{Config.BASE_URL}/post/{post['slug']}")
        fe.content(html_content, type='html')
        
        if post['date']:
            try:
                dt = datetime.strptime(post['date'], '%Y-%m-%d')
                fe.published(dt.replace(tzinfo=None))
            except:
                pass
            
    return Response(fg.rss_str(pretty=True), mimetype='application/xml')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('base.html', content="<h1>404 - Page Not Found</h1><p>The post you are looking for does not exist.</p>"), 404

if __name__ == '__main__':
    app.run(debug=(Config.FLASK_ENV == 'development'))
