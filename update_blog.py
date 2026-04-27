import requests
import re

# Hashnode GraphQL API Endpoint
URL = "https://gql.hashnode.com"

PUBLICATION_HOST = "tiff-explores.hashnode.dev"
POST_COUNT = 3

QUERY = f"""
{{
  publication(host: \"{PUBLICATION_HOST}\") {{
    posts(first: {POST_COUNT}) {{
      edges {{
        node {{
          title
          url
          publishedAt
        }}
      }}
    }}
  }}
}}
"""

START_MARKER = "<!-- BLOG-POST-LIST:START -->"
END_MARKER = "<!-- BLOG-POST-LIST:END -->"


def fetch_posts():
    response = requests.post(URL, json={"query": QUERY}, timeout=30)
    response.raise_for_status()
    data = response.json()

    edges = (
        data.get("data", {})
        .get("publication", {})
        .get("posts", {})
        .get("edges", [])
    )

    posts = []
    for e in edges:
        node = e.get("node") or {}
        title = node.get("title")
        url = node.get("url")
        published_at = (node.get("publishedAt") or "")[:10]
        if title and url:
            # keep it clean in README (no extra metadata unless you want it)
            suffix = f" — {published_at}" if published_at else ""
            posts.append(f"* [{title}]({url}){suffix}")

    return posts


def update_readme(new_posts):
    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    if START_MARKER not in content or END_MARKER not in content:
        raise SystemExit(
            "README.md is missing blog markers. Add these lines where you want posts inserted:\n"
            "<!-- BLOG-POST-LIST:START -->\n<!-- BLOG-POST-LIST:END -->"
        )

    # Replace only the content between the markers
    pattern = re.compile(
        rf"({re.escape(START_MARKER)})([\s\S]*?)({re.escape(END_MARKER)})",
        re.MULTILINE,
    )

    replacement = (
        f"{START_MARKER}\n" + "\n".join(new_posts) + f"\n{END_MARKER}"
    )

    new_content, count = pattern.subn(replacement, content)
    if count != 1:
        raise SystemExit(
            f"Expected to update exactly 1 blog section, but updated {count}."
        )

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    latest_posts = fetch_posts()
    if latest_posts:
        update_readme(latest_posts)
        print("README updated with latest posts.")
    else:
        print("No posts fetched; README not modified.")
