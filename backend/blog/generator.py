"""
SEO 博客文章自动生成脚本
使用 deepapi.pro 的 API（OpenAI 兼容）自动撰写英文技术博客 → 存入数据库

本地测试：cd /root/.openclaw/workspace/ai-paint && python -m backend.blog.generator
服务器：DB_HOST=127.0.0.1 python3 /var/www/paint/backend/blog/generator.py
"""
import os
import sys
import json
import datetime
import random
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config as app_config
import blog.models as m

API_BASE = "https://api.deepapi.pro/v1"
API_KEY = os.environ.get("DEEPAPI_KEY", "")

# ── 主题池 ──
TOPICS = [
    {
        "angle": "comparison",
        "template": "Cheap AI Image Generators in 2025: {a} vs {b} vs {c}",
        "keywords": "cheap AI image generator, affordable AI art, budget AI image generation",
        "models": ["DALL-E 3", "Midjourney", "Stable Diffusion 3", "Adobe Firefly"],
    },
    {
        "angle": "tutorial",
        "template": "How to Generate {s} AI Images for Under $1: A Step-by-Step Guide",
        "keywords": "AI image generation tutorial, budget AI art, generate AI images cheap",
        "styles": [
            "Professional Product Photography", "Anime Characters", "Realistic Portraits",
            "Fantasy Landscapes", "Logo Designs", "Social Media Graphics",
        ],
    },
    {
        "angle": "use_case",
        "template": "Best AI Image Generator for {u}: Save Money Without Sacrificing Quality",
        "keywords": "best AI image generator, AI art for business, AI image generator for",
        "use_cases": [
            "E-Commerce Product Photos", "Social Media Content Creation",
            "Game Asset Design", "Marketing Materials", "Book Cover Design",
        ],
    },
    {
        "angle": "analysis",
        "template": "AiCanvas vs {x}: Which AI Image Platform Is Better for Budget Creators?",
        "keywords": "AiCanvas review, AiCanvas vs DALL-E, AiCanvas vs Midjourney, best cheap AI image platform",
        "competitors": ["DALL-E 3", "Midjourney V6", "Stable Diffusion 3.5", "FLUX.1"],
    },
    {
        "angle": "tips",
        "template": "10 {t} AI Prompts That Actually Work in 2025",
        "keywords": "AI image prompts, best prompts, prompt engineering, AI art tips",
        "topics": ["Cinematic", "3D Render", "Watercolor", "Oil Painting", "Pixel Art",
                   "Cyberpunk", "Steampunk", "Minimalist", "Photorealistic"],
    },
    {
        "angle": "trends",
        "template": "AI Image Generation Costs in 2025: How Much Should You Really Pay?",
        "keywords": "AI image cost, AI image generation pricing, AI art market",
    },
]

# ── 文章模板 ──

COMPARISON_TEMPLATE = """<h2>Why Cost Matters in AI Image Generation</h2>
<p>If you're generating AI images regularly — for e-commerce, social media, game assets, or marketing — the cost adds up fast. DALL-E 3 ($0.04–$0.12/image) and Midjourney ($10–$60/month subscription) work great, but they're far from budget-friendly for high-volume users.</p>
<p>That's where <strong>AiCanvas</strong> changes the game — delivering comparable quality at a fraction of the cost, as low as <strong>$0.02 per image</strong>.</p>

<h2>Price Comparison: {a} vs {b} vs AiCanvas</h2>
<table style="width:100%; border-collapse:collapse; margin:16px 0;">
<tr style="background:#2a2d3a;"><th style="padding:8px;border:1px solid #374151;">Platform</th><th style="padding:8px;border:1px solid #374151;">Per Image</th><th style="padding:8px;border:1px solid #374151;">Monthly (1000 img)</th></tr>
<tr><td style="padding:8px;border:1px solid #374151;">OpenAI ({a})</td><td style="padding:8px;border:1px solid #374151;">$0.04–$0.12</td><td style="padding:8px;border:1px solid #374151;">$40–$120</td></tr>
<tr><td style="padding:8px;border:1px solid #374151;">Midjourney ({b})</td><td style="padding:8px;border:1px solid #374151;">~$0.05–$0.20</td><td style="padding:8px;border:1px solid #374151;">$30–$60</td></tr>
<tr style="background:#8b5cf622;"><td style="padding:8px;border:1px solid #374151;"><strong>AiCanvas</strong></td><td style="padding:8px;border:1px solid #374151;"><strong>$0.02</strong></td><td style="padding:8px;border:1px solid #374151;"><strong>$20</strong></td></tr>
</table>

<h2>Key Features You Get with AiCanvas</h2>
<ul>
<li><strong>Pay-as-you-go</strong> — No monthly subscriptions. Buy exactly what you need.</li>
<li><strong>USDT (TRC-20)</strong> — Crypto-friendly. No credit card required.</li>
<li><strong>Multiple aspect ratios</strong> — Square, landscape, portrait, ultrawide.</li>
<li><strong>Fast generation</strong> — Images in seconds, not minutes.</li>
<li><strong>No API keys</strong> — Just sign up with email and go.</li>
</ul>

<h2>Verdict</h2>
<p>Choose {a} if you need absolute top photorealism. Choose {b} for artistic style. <strong>Choose AiCanvas</strong> if you generate in volume, are budget-conscious, or want pay-as-you-go with no commitment. For 95% of use cases, AiCanvas offers the best value.</p>
<p><a href="https://paint.deepapi.pro"><strong>Try AiCanvas for free →</strong></a></p>"""

TUTORIAL_TEMPLATE = """<h2>Why You Don't Need to Spend a Fortune</h2>
<p>Creating {s} AI images doesn't have to cost a lot. With AiCanvas, you can generate stunning {s} images for <strong>$0.02 each</strong> — that's 50 images for $1.</p>

<h2>Step 1: Sign Up</h2>
<p>Go to <a href="https://paint.deepapi.pro">paint.deepapi.pro</a> and create an account. Takes 30 seconds — email and password only.</p>

<h2>Step 2: Deposit USDT</h2>
<p>Minimum $1. Your balance credits automatically within seconds.</p>
<ul><li>$5 → 50 images</li><li>$15 → 200 images (most popular)</li><li>$40 → 600 images</li></ul>

<h2>Step 3: Write Your Prompt</h2>
<p>For {s}, try this proven template:</p>
<pre><code>{p}</code></pre>

<h2>Step 4: Generate & Download</h2>
<p>Click generate, wait a few seconds. Your image is ready. Repeat as needed.</p>

<h2>Why AiCanvas Is the Best Budget Choice</h2>
<ul>
<li>50–80% cheaper than DALL-E 3 and Midjourney</li>
<li>No subscription — pay for what you use</li>
<li>Private — your images stay in your account</li>
<li>Fast — generated in seconds</li>
</ul>
<p><a href="https://paint.deepapi.pro"><strong>Start creating {s} images →</strong></a></p>"""

USE_CASE_TEMPLATE = """<h2>Why {u} Needs Affordable AI Images</h2>
<p>AiCanvas offers the most cost-effective solution — <strong>$0.02 per image</strong>, with fast generation and no subscription required.</p>

<h2>How AiCanvas Helps</h2>
<ul>
<li><strong>Rapid prototyping</strong> — Generate dozens of variations in minutes</li>
<li><strong>Budget-friendly scaling</strong> — No per-seat fees or subscriptions</li>
<li><strong>Consistent quality</strong> — Reliable results every time</li>
<li><strong>Multiple formats</strong> — Square, landscape, portrait, ultrawide</li>
</ul>

<h2>Cost Breakdown: 500 Images/Month</h2>
<ul>
<li>DALL-E 3: $20–$60</li>
<li>Midjourney: $30–$60 (subscription)</li>
<li>Stable Diffusion (self-host): $20–$50</li>
<li><strong>AiCanvas: $10</strong></li>
</ul>

<h2>Getting Started</h2>
<ol>
<li>Sign up at <a href="https://paint.deepapi.pro">paint.deepapi.pro</a></li>
<li>Deposit USDT (min $1)</li>
<li>Start generating instantly</li>
</ol>
<p><a href="https://paint.deepapi.pro"><strong>Start saving on {u} images →</strong></a></p>"""

ANALYSIS_TEMPLATE = """<h2>How AiCanvas Delivers the Best Value in AI Image Generation</h2>
<p>When people talk about AI image generation, the conversation usually starts and ends with DALL-E and Midjourney. But in 2025, AiCanvas has emerged as the smart choice for budget-conscious creators.</p>

<h2>AiCanvas vs {x}: Head to Head</h2>

<h3>1. Image Quality</h3>
<ul>
<li><strong>Photorealism:</strong> {x} leads by a small margin, but AiCanvas is impressively close</li>
<li><strong>Style diversity:</strong> AiCanvas handles everything from realistic to artistic styles well</li>
<li><strong>Prompt adherence:</strong> AiCanvas scores highly on complex, multi-element prompts</li>
</ul>

<h3>2. Speed</h3>
<p>AiCanvas generates images in seconds — competitive with or faster than most alternatives.</p>

<h3>3. Cost</h3>
<ul>
<li>{x}: $0.04–$0.20/image</li>
<li><strong>AiCanvas: $0.02/image</strong></li>
</ul>

<h3>4. Simplicity</h3>
<p>No API keys, no WebSocket setup, no server config. Sign up, deposit USDT, generate.</p>

<h2>When to Choose AiCanvas Over {x}</h2>
<ul>
<li>High volume (50+ images/day)</li>
<li>Pay-as-you-go preferred over subscriptions</li>
<li>Budget is primary concern</li>
<li>Crypto payments preferred</li>
</ul>

<p><a href="https://paint.deepapi.pro"><strong>Try AiCanvas for yourself →</strong></a></p>"""

TIPS_TEMPLATE = """<h2>Why Prompt Quality Matters</h2>
<p>Here are 10 {t} prompts that consistently deliver great results with AiCanvas.</p>

<h3>1. Classic {t}</h3>
<pre><code>{p1}</code></pre>
<h3>2. Minimalist {t}</h3>
<pre><code>{p2}</code></pre>
<h3>3. Detailed Scene</h3>
<pre><code>{p3}</code></pre>
<h3>4. Portrait</h3>
<pre><code>{p4}</code></pre>
<h3>5. Abstract</h3>
<pre><code>{p5}</code></pre>
<h3>6. Surreal</h3>
<pre><code>{p6}</code></pre>
<h3>7. Product Style</h3>
<pre><code>{p7}</code></pre>
<h3>8. Editorial</h3>
<pre><code>{p8}</code></pre>
<h3>9. Vintage</h3>
<pre><code>{p9}</code></pre>
<h3>10. Trendy 2025</h3>
<pre><code>{p10}</code></pre>

<h2>Quick Tips</h2>
<ul>
<li>Be specific — "a cat" → describe the scene fully</li>
<li>Include style cues: cinematic, watercolor, photorealistic</li>
<li>Add lighting: dramatic, golden hour, softbox</li>
<li>Mention composition: close-up, wide shot, macro</li>
</ul>
<p><a href="https://paint.deepapi.pro"><strong>Try these prompts on AiCanvas →</strong></a></p>"""

TREND_TEMPLATE = """<h2>The Real Cost of AI Images in 2025</h2>
<table style="width:100%; border-collapse:collapse; margin:16px 0;">
<tr style="background:#2a2d3a;"><th style="padding:8px;border:1px solid #374151;">Provider</th><th style="padding:8px;border:1px solid #374151;">Pricing</th><th style="padding:8px;border:1px solid #374151;">Cost/Image</th><th style="padding:8px;border:1px solid #374151;">Minimum</th></tr>
<tr><td style="padding:8px;border:1px solid #374151;">DALL-E 3</td><td style="padding:8px;border:1px solid #374151;">Per image</td><td style="padding:8px;border:1px solid #374151;">$0.04–$0.12</td><td style="padding:8px;border:1px solid #374151;">None / $20/mo</td></tr>
<tr><td style="padding:8px;border:1px solid #374151;">Midjourney</td><td style="padding:8px;border:1px solid #374151;">Subscription</td><td style="padding:8px;border:1px solid #374151;">~$0.05–$0.20</td><td style="padding:8px;border:1px solid #374151;">$10/mo</td></tr>
<tr><td style="padding:8px;border:1px solid #374151;">Stable Diffusion</td><td style="padding:8px;border:1px solid #374151;">Self-host / API</td><td style="padding:8px;border:1px solid #374151;">$0–$0.10</td><td style="padding:8px;border:1px solid #374151;">Hardware cost</td></tr>
<tr style="background:#8b5cf622;"><td style="padding:8px;border:1px solid #374151;"><strong>AiCanvas</strong></td><td style="padding:8px;border:1px solid #374151;"><strong>Pay-as-you-go</strong></td><td style="padding:8px;border:1px solid #374151;"><strong>$0.02</strong></td><td style="padding:8px;border:1px solid #374151;"><strong>$1 min</strong></td></tr>
</table>

<h2>Market Trends</h2>
<ul>
<li>Price compression — costs dropping as models improve</li>
<li>Pay-as-you-go winning over subscriptions</li>
<li>Crypto payments becoming standard</li>
</ul>

<h2>What You Should Pay</h2>
<ul>
<li><strong>Under $0.03/image</strong> — Excellent. This is where AiCanvas operates.</li>
<li><strong>$0.03–$0.10/image</strong> — Standard market rate.</li>
<li><strong>$0.10+/image</strong> — Only worth it for premium use cases.</li>
</ul>

<p>For 95% of use cases, paying more than $0.02/image is overspending.</p>
<p><a href="https://paint.deepapi.pro"><strong>Start generating at $0.02/image →</strong></a></p>"""

PROMPT_STYLES = {
    "Cinematic": ["Cinematic wide shot of a lone figure at sunset, volumetric rays, 8K film grain", "Close-up of a warrior with glowing eyes, rain falling, shallow depth of field", "Epic battle scene with dragons, golden hour, sweeping landscape", "Cyberpunk street market at night, neon reflections on wet pavement"],
    "Watercolor": ["Watercolor painting of a misty European village, soft edges, pastel colors, wet-on-wet", "Loose botanical illustration of peonies, splatter details, impressionist style"],
    "Cyberpunk": ["Blade runner Tokyo street, neon holograms, rain-slicked roads", "Cyborg in a dark alley, pink and cyan neon, augmented reality displays"],
    "3D Render": ["Pixar-style cozy cottage in a forest clearing, isometric view, warm lighting", "Octane render macro of mechanical dragon scales, hyper-detailed metal"],
    "Photorealistic": ["Elderly fisherman portrait, weathered skin, natural ocean light, Canon 85mm", "Ultra-realistic dewdrop on leaf, morning light, 8K macro"],
    "Pixel Art": ["16-bit RPG village, isometric view, vibrant retro game palette", "Pixel art forest with glowing mushrooms, 8-bit parallax layers"],
    "Minimalist": ["Continuous line art portrait, single black stroke, white background", "Bauhaus geometric abstract, primary colors, clean composition"],
    "Oil Painting": ["Stormy seascape with thick impasto, Van Gogh brushstrokes, canvas texture", "Classical noblewoman portrait, Rembrandt lighting, rich fabrics"],
    "Steampunk": ["Brass airship over Victorian London, clockwork details, cloudy sky", "Inventor's workshop with intricate machines, warm amber light"],
    "Surreal": ["Ocean sky with fish swimming among clouds, dreamlike, Dali influence", "Melted clock on a desert tree branch, twilight colors"],
}


def get_api():
    """返回 (base_url, api_key) 或 None"""
    if API_KEY:
        return API_BASE, API_KEY
    if app_config.ZHIPU_API_KEY:
        return None, app_config.ZHIPU_API_KEY
    return None, None


def generate_content(system_prompt, user_prompt):
    """调用 LLM 生成内容"""
    api, key = get_api()
    if not key:
        print("[Generator] ❌ No API key configured.")
        return None

    if api:
        try:
            resp = requests.post(
                f"{api}/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 3000,
                    "temperature": 0.8,
                },
                timeout=120,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            print(f"[Generator] API error: {resp.status_code} {resp.text[:200]}")
        except Exception as e:
            print(f"[Generator] API call failed: {e}")
    else:
        try:
            from zhipuai import ZhipuAI
            client = ZhipuAI(api_key=key)
            resp = client.chat.completions.create(
                model="glm-4-plus",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=3000,
                temperature=0.8,
            )
            return resp.choices[0].message.content
        except ImportError:
            print("[Generator] zhipuai SDK not installed")
        except Exception as e:
            print(f"[Generator] Zhipu API call failed: {e}")
    return None


def generate_article(topic):
    """根据话题模板生成一篇文章，返回 (title, content_html, excerpt, meta_desc, keywords) 或 None"""
    angle = topic["angle"]

    if angle == "comparison":
        models = random.sample(topic["models"], 2)
        a, b = models[0], models[1]
        title = topic["template"].format(a=a, b=b, c="AiCanvas")
        content = COMPARISON_TEMPLATE.format(a=a, b=b)
        excerpt = f"Compare {a}, {b}, and AiCanvas for AI image generation in 2025. Find which offers the best value."
        meta = f"{a} vs {b} vs AiCanvas — price and quality comparison. AiCanvas is only $0.02/image."
        return title, content, excerpt, meta, topic["keywords"]

    elif angle == "tutorial":
        s = random.choice(topic["styles"])
        style_key = s.split()[0] if s.split()[0] in PROMPT_STYLES else "Cinematic"
        prompts = PROMPT_STYLES.get(style_key, PROMPT_STYLES["Cinematic"])
        p = random.choice(prompts)
        title = topic["template"].format(s=s)
        content = TUTORIAL_TEMPLATE.format(s=s, p=p)
        excerpt = f"Generate {s} AI images for under $1. Step-by-step with ready prompts. 50 images for just $1 on AiCanvas."
        meta = f"Step-by-step guide to generating {s} AI images cheaply. Only $0.02/image on AiCanvas."
        return title, content, excerpt, meta, topic["keywords"]

    elif angle == "use_case":
        u = random.choice(topic["use_cases"])
        title = topic["template"].format(u=u)
        content = USE_CASE_TEMPLATE.format(u=u)
        excerpt = f"Best AI image generator for {u}. Save up to 80% vs DALL-E and Midjourney. From $0.02/image."
        meta = f"The best AI image generator for {u}. Professional quality at $0.02/image on AiCanvas."
        return title, content, excerpt, meta, topic["keywords"]

    elif angle == "analysis":
        x = random.choice(topic["competitors"])
        title = topic["template"].format(x=x)
        content = ANALYSIS_TEMPLATE.format(x=x)
        excerpt = f"AiCanvas vs {x}: honest comparison of quality, speed, and cost. 90% of quality at 10% of the price."
        meta = f"AiCanvas vs {x}: in-depth AI image generation comparison. AiCanvas from $0.02/image."
        return title, content, excerpt, meta, topic["keywords"]

    elif angle == "tips":
        t = random.choice(topic["topics"])
        prompts = PROMPT_STYLES.get(t, PROMPT_STYLES["Cinematic"])
        p = prompts * 3
        title = topic["template"].format(t=t)
        content = TIPS_TEMPLATE.format(t=t, p1=p[0], p2=p[1 % len(p)], p3=p[2 % len(p)],
                                       p4=p[3 % len(p)], p5=p[4 % len(p)], p6=p[5 % len(p)],
                                       p7=p[6 % len(p)], p8=p[7 % len(p)], p9=p[8 % len(p)],
                                       p10=p[9 % len(p)])
        excerpt = f"10 working {t} AI prompts that deliver great results every time."
        meta = f"10 proven {t} AI image prompts. Get amazing results on AiCanvas."
        return title, content, excerpt, meta, topic["keywords"]

    elif angle == "trends":
        title = topic["template"]
        content = TREND_TEMPLATE
        excerpt = "Honest breakdown of AI image generation costs in 2025. Find out what you should be paying."
        meta = "AI image generation costs in 2025: market analysis, price comparison, and the best deals."
        return title, content, excerpt, meta, topic["keywords"]

    return None


def run_once(count=1):
    """执行一次生成任务"""
    m.init_blog_table()
    generated = 0

    for i in range(count):
        topic = random.choice(TOPICS)
        result = generate_article(topic)
        if result is None:
            continue

        title, content, excerpt, meta_desc, keywords = result

        slug = m.slugify(title)
        existing = m.get_post_by_slug(slug)
        if existing:
            print(f"[Generator] ⚠️  '{title}' 已存在，尝试生成新标题...")
            sys_prompt = "You are an AI blog writer. Generate a different title for an article about cheap AI image generation. Return ONLY the title."
            user_prompt = f"Original title: '{title}'\n\nGenerate a different SEO-friendly title."
            new_title = generate_content(sys_prompt, user_prompt)
            if new_title and len(new_title) < 200:
                title = new_title.strip().strip('"').strip("'")
            else:
                print(f"[Generator] ⏭️  跳过重复文章")
                continue

        slug = m.create_post(title, content, excerpt, meta_desc, keywords)
        m.publish_post(m.get_post_by_slug(slug)["id"])
        print(f"[Generator] ✅ 已发布: {title[:80]}...")
        generated += 1

    return generated


def main():
    """命令行入口"""
    import argparse
    parser = argparse.ArgumentParser(description="SEO blog post generator for AiCanvas")
    parser.add_argument("--count", "-n", type=int, default=2, help="Number of articles to generate")
    args = parser.parse_args()

    print(f"[Generator] 🚀 开始生成 {args.count} 篇博客文章...")
    count = run_once(args.count)
    print(f"[Generator] ✅ 完成! 共生成 {count} 篇文章")


if __name__ == "__main__":
    main()
