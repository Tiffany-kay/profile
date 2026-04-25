import requests
import re

# Hashnode GraphQL API Endpoint
URL = "https://gql.hashnode.com"
# Your specific blog handle
QUERY = """
{
  publication(host: "tiff-explores.hashnode.dev") {
    posts(first: 3) {
      edges {
        node {
          title
          url
          publishedAt
        }
      }
    }
  }
}
"""

def fetch_posts():
    response = requests.post(URL, json={'query': QUERY})
    if response.status_code == 200:
        data = response.json()
        posts = data['data']['publication']['posts']['edges']
        return [f"* [{p['node']['title']}]({p['node']['url']}) - {p['node']['publishedAt'][:10]}" for p in posts]
    return []

def update_readme(new_posts):
    with open("README.md", "r") as f:
        content = f.read()
    
    # Logic to find the anchors and inject the list
    pattern = r"[\s\S]*"
    replacement = f"\n" + "\n".join(new_posts) + "\n"
    
    new_content = re.sub(pattern, replacement, content)
    
    with open("README.md", "w") as f:
        f.write(new_content)

if __name__ == "__main__":
    latest_posts = fetch_posts()
    if latest_posts:
        update_readme(latest_posts)
        print("Architecture updated with latest posts.")
    else:
        print("Gateway failed: No posts fetched.")
