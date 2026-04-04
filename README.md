# Notion-Powered Blog (Akita Style)

A lightweight, secure, and high-performance blog that uses Notion as a CMS. The design is inspired by the minimalist, document-centric aesthetic of Fabio Akita's blog.

## Features

- **Notion Integration**: Write your posts in Notion, and they'll automatically appear on the site.
- **Minimalist Design**: High-fidelity typography (IBM Plex Serif) and layout, with a focus on readability.
- **RSS Feed**: Automatic generation of `/rss` compliant feed.
- **Simple Caching**: In-memory caching to minimize Notion API hits and speed up page loads.
- **High Performance**: Vanilla CSS and minimalist Python Flask backend.
- **Responsive**: Mobile-friendly design with dark/light mode support.

## Prerequisites

- [Notion Internal Integration Token](https://www.notion.so/my-integrations)
- Notion Database ID (with the required properties)
- Python 3.9+

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

3. **Notion Database Configuration**:
   The blog expects a database with the following properties:
   - `Title`: **Title** (Default)
   - `Slug`: **Rich text** (e.g., "my-first-post")
   - `Date`: **Date** (Publication date)
   - `Status`: **Status** (Set to "Published" to show on the blog)
   - `Tags`: **Multi-select** (Optional)

4. **Run the App**:
   ```bash
   python app.py
   ```

## Project Structure

- `app.py`: Main entry point and routes.
- `services/`:
  - `notion_service.py`: Handles all communication with the Notion API.
  - `cache_service.py`: Simple in-memory caching logic.
- `utils/`:
  - `parser.py`: Converts Notion blocks to semantic HTML.
- `static/`: CSS and assets.
- `templates/`: Jinja2 HTML templates.

## Security

- All API tokens are stored in environment variables.
- Direct Notion blocks are sanitized and escaped where appropriate.
- Minimal dependencies to reduce attack surface.

## License

MIT
