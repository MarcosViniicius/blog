import re
import html

class NotionParser:
    def __init__(self):
        self.headers = [] # Store headers for Table of Contents

    def _slugify(self, text):
        """Creates a URL-friendly slug from text."""
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[-\s]+', '-', text).strip('-')

    def blocks_to_html(self, blocks):
        """Converts a list of Notion blocks to a single HTML string."""
        html_output = []
        in_list = False
        list_type = None

        self.headers = [] # Reset headers for each conversion
        for block in blocks:
            b_type = block.get("type")
            
            # Close list if block is not of a similar list type
            if in_list and b_type != list_type:
                html_output.append(f"</{'ul' if list_type == 'bulleted_list_item' else 'ol'}>")
                in_list = False
                list_type = None

            # Handle block types
            if b_type == "paragraph":
                text = self._rich_text_to_html(block.get("paragraph", {}).get("rich_text", []))
                html_output.append(f"<p>{text}</p>")
            
            elif b_type in ["heading_1", "heading_2", "heading_3"]:
                h_tag = "h1" if b_type == "heading_1" else "h2" if b_type == "heading_2" else "h3"
                text = self._rich_text_to_html(block.get(b_type, {}).get("rich_text", []))
                anchor_id = self._slugify(text)
                
                # Store metadata for ToC
                self.headers.append({
                    "text": text,
                    "id": anchor_id,
                    "level": int(h_tag[1])
                })
                
                html_output.append(f'<{h_tag} id="{anchor_id}">{text}</{h_tag}>')
            
            elif b_type in ["bulleted_list_item", "numbered_list_item"]:
                if not in_list:
                    html_output.append(f"<{'ul' if b_type == 'bulleted_list_item' else 'ol'}>")
                    in_list = True
                    list_type = b_type
                text = self._rich_text_to_html(block.get(b_type, {}).get("rich_text", []))
                html_output.append(f"<li>{text}</li>")
            
            elif b_type == "quote":
                text = self._rich_text_to_html(block.get("quote", {}).get("rich_text", []))
                html_output.append(f"<blockquote>{text}</blockquote>")
            
            elif b_type == "code":
                code_data = block.get("code", {})
                code_text = "".join([t.get("plain_text", "") for t in code_data.get("rich_text", [])])
                lang = code_data.get("language", "plaintext")
                html_output.append(f'<pre><code class="language-{lang}">{html.escape(code_text)}</code></pre>')
            
            elif b_type == "divider":
                html_output.append("<hr />")
            
            elif b_type == "image":
                img_data = block.get("image", {})
                url = img_data.get("external", {}).get("url") or img_data.get("file", {}).get("url")
                caption = self._rich_text_to_html(img_data.get("caption", []))
                if url:
                    html_output.append(f'<figure><img src="{url}" alt="{caption}" /><figcaption>{caption}</figcaption></figure>')
            
            elif b_type == "callout":
                callout_data = block.get("callout", {})
                text = self._rich_text_to_html(callout_data.get("rich_text", []))
                emoji = callout_data.get("icon", {}).get("emoji", "💡")
                html_output.append(f'<aside class="callout"><span class="icon">{emoji}</span><div class="content">{text}</div></aside>')

        # Final list closure
        if in_list:
            html_output.append(f"</{'ul' if list_type == 'bulleted_list_item' else 'ol'}>")

        return "\n".join(html_output)

    def _rich_text_to_html(self, rich_text_list):
        """Converts Notion rich text objects to HTML with formatting (bold, italic, etc.)."""
        html_parts = []
        for text_item in rich_text_list:
            content = html.escape(text_item.get("plain_text", ""))
            annotations = text_item.get("annotations", {})
            href = text_item.get("href")

            # Apply annotations
            if annotations.get("bold"):
                content = f"<strong>{content}</strong>"
            if annotations.get("italic"):
                content = f"<em>{content}</em>"
            if annotations.get("strikethrough"):
                content = f"<del>{content}</del>"
            if annotations.get("underline"):
                content = f"<u>{content}</u>"
            if annotations.get("code"):
                content = f"<code>{content}</code>"
            if annotations.get("color") and annotations.get("color") != "default":
                content = f'<span class="notion-color-{annotations.get("color")}">{content}</span>'

            # Apply links
            if href:
                content = f'<a href="{href}" target="_blank" rel="noopener noreferrer">{content}</a>'
            
            html_parts.append(content)
        
        return "".join(html_parts)
