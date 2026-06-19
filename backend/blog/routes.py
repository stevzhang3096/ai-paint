"""博客路由 — 列表页 + 详情页 + Sitemap + RSS + SEO 优化"""
import datetime
from flask import render_template, request, abort, Response, jsonify
from blog import blog_bp
import blog.models as m


@blog_bp.route("/blog")
@blog_bp.route("/blog/")
def blog_index():
    """博客文章列表页"""
    page = request.args.get("page", 1, type=int)
    per_page = 10
    posts, total = m.get_published_posts(page, per_page)
    total_pages = max(1, (total + per_page - 1) // per_page)

    return render_template(
        "blog/index.html",
        posts=posts,
        page=page,
        total_pages=total_pages,
        total=total,
        meta_title="AiCanvas Blog — AI Image Generation Tips, Tutorials & News",
        meta_description=(
            "Learn how to generate stunning AI images on a budget. "
            "Tutorials, comparisons, and tips for CogView-4, DALL-E alternatives, "
            "and cheap AI image generation."
        ),
    )


@blog_bp.route("/blog/<slug>")
def blog_post(slug):
    """文章详情页"""
    post = m.get_post_by_slug(slug)
    if not post or not post.get("published"):
        abort(404)

    return render_template(
        "blog/post.html",
        post=post,
        meta_title=f"{post['title']} — AiCanvas Blog",
        meta_description=post.get("meta_description") or post.get("excerpt") or "",
        meta_keywords=post.get("meta_keywords") or "",
    )


@blog_bp.route("/sitemap.xml")
def sitemap():
    """Sitemap XML — 让 Google 快速收录"""
    pages = []
    base_url = "https://paint.deepapi.pro"

    # 首页
    pages.append({"loc": base_url, "priority": "1.0", "changefreq": "weekly"})
    # 博客首页
    pages.append({"loc": f"{base_url}/blog/", "priority": "0.9", "changefreq": "daily"})

    # 所有文章
    posts = m.get_all_published_posts()
    for p in posts:
        updated = p.get("updated_at") or p.get("published_at") or datetime.datetime.now()
        pages.append({
            "loc": f"{base_url}/blog/{p['slug']}",
            "lastmod": updated.strftime("%Y-%m-%d"),
            "priority": "0.8",
            "changefreq": "monthly",
        })

    xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        xml += "  <url>\n"
        xml += f"    <loc>{p['loc']}</loc>\n"
        if "lastmod" in p:
            xml += f"    <lastmod>{p['lastmod']}</lastmod>\n"
        xml += f"    <priority>{p['priority']}</priority>\n"
        xml += f"    <changefreq>{p['changefreq']}</changefreq>\n"
        xml += "  </url>\n"
    xml += "</urlset>"

    return Response(xml, mimetype="application/xml")


@blog_bp.route("/feed.xml")
@blog_bp.route("/rss.xml")
def rss_feed():
    """RSS Feed — 让用户订阅博客更新"""
    base_url = "https://paint.deepapi.pro"
    posts = m.get_all_published_posts()

    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:content="http://purl.org/rss/1.0/modules/content/"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>AiCanvas Blog — AI Image Generation</title>
    <link>{base_url}/blog/</link>
    <description>Tips, tutorials, and news about affordable AI image generation with CogView-4 and other models.</description>
    <language>en</language>
    <lastBuildDate>{datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>
"""
    for p in posts[:20]:
        pub_date = p.get("published_at") or datetime.datetime.now()
        rss += f"""    <item>
      <title>{p['title']}</title>
      <link>{base_url}/blog/{p['slug']}</link>
      <guid>{base_url}/blog/{p['slug']}</guid>
      <pubDate>{pub_date.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate>
      <description>{p.get('meta_description', '') or p['title']}</description>
    </item>
"""
    rss += """  </channel>
</rss>"""

    return Response(rss, mimetype="application/rss+xml")


# ── 自动生成脚本的 API（只在 debug 模式或通过定时任务调用） ──

@blog_bp.route("/blog/api/posts", methods=["GET"])
def api_list_posts():
    """（内部用）获取所有文章列表"""
    posts, _ = m.get_published_posts(page=1, per_page=9999)
    return jsonify({"posts": posts, "total": len(posts)})


@blog_bp.route("/blog/api/publish/<int:post_id>", methods=["POST"])
def api_publish_post(post_id):
    """（内部用）发布指定文章"""
    m.publish_post(post_id)
    return jsonify({"success": True})
