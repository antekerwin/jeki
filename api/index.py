from flask import Flask, render_template, request, jsonify
import os
import requests
import re
import random

app = Flask(__name__)

def fetch_kaito_projects():
    try:
        response = requests.get("https://yaps.kaito.ai/pre-tge", timeout=10)
        if response.status_code != 200:
            return get_fallback_projects()
        html = response.text
        pattern = r'(MOMENTUM|LIMITLESS|POLYMARKET|SENTIENT|MONAD|OPENSEA|BASE|ALLORA|YIELDBASIS|CYSIC|BILLIONS|MET|WALLCHAIN|IRYS|RECALL|KITE|MASK|EVERLYN|DZ|TALUS|BERACHAIN|STORY)'
        matches = re.findall(pattern, html)
        seen = set()
        projects = []
        for match in matches:
            if match not in seen and len(projects) < 20:
                projects.append({"name": match.title() if match != "MASK" else "MetaMask", "mindshare": "High", "category": get_category(match)})
                seen.add(match)
        return projects if projects else get_fallback_projects()
    except:
        return get_fallback_projects()

def get_fallback_projects():
    return [
        {"name": "Limitless", "mindshare": "High", "category": "AI Tools"},
        {"name": "Polymarket", "mindshare": "Very High", "category": "Prediction Markets"},
        {"name": "Sentient", "mindshare": "High", "category": "AI Agents"},
    ]

def get_category(project):
    categories = {
        "LIMITLESS": "AI Tools", "SENTIENT": "AI Agents", "POLYMARKET": "Prediction Markets",
        "MONAD": "Layer 1", "BASE": "Layer 2", "OPENSEA": "NFT Marketplace",
    }
    return categories.get(project, "DeFi")

PROMPTS = {
    "data-driven": {"name": "?? Data & Metrics", "description": "Lead dengan data konkret"},
    "competitive": {"name": "?? Competitive Edge", "description": "Compare kompetitor"},
    "thesis": {"name": "?? Bold Prediction", "description": "Trend analysis"},
    "custom": {"name": "?? Custom Request", "description": "Request bebas"}
}

@app.route('/')
def home():
    projects = fetch_kaito_projects()
    return render_template('index.html', projects=projects, prompts=PROMPTS)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        project = data.get('project')
        prompt_type = data.get('prompt_type')
        custom_request = data.get('custom_request', '')
        
        # Template-based generation (no API needed)
        content = generate_template_content(project, prompt_type, custom_request)
        
        # Get full Kaito analysis for generated content
        analysis = analyze_content_full(content)
        
        return jsonify({
            "success": True, 
            "content": content, 
            "analysis": analysis
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def analyze_content_full(content):
    """Shared function for full Kaito + Twitter algorithm analysis"""
    char_count = len(content)
    optimal_length = 150 <= char_count <= 280
    min_length = char_count >= 50
    
    crypto_keywords = ['defi', 'layer', 'l2', 'ai', 'rwa', 'tvl', 'airdrop', 'protocol', 'chain', 'token', 'nft', 'dao', 'staking', 'yield', 'bridge', 'zk', 'rollup', 'evm', 'smart contract', 'agi', 'funding', 'liquidity']
    content_lower = content.lower()
    keyword_count = sum(1 for kw in crypto_keywords if kw in content_lower)
    has_crypto_focus = keyword_count >= 1
    
    keyword_stuffing = keyword_count > 5
    
    generic_phrases = ['to the moon', 'lfg', 'gm', 'ser', 'ngmi', 'wagmi', 'bullish', 'bearish']
    generic_count = sum(1 for phrase in generic_phrases if phrase in content_lower)
    is_original = generic_count < 2
    
    content_opt_score = 0
    if min_length: content_opt_score += 2
    if optimal_length: content_opt_score += 3
    if has_crypto_focus: content_opt_score += 3
    if is_original: content_opt_score += 2
    content_opt_score = min(10, content_opt_score)
    
    has_question = '?' in content
    has_data = any(char.isdigit() for char in content)
    has_cta = any(word in content_lower for word in ['what', 'how', 'why', 'thoughts', 'think', 'opinion', 'see', 'do you'])
    
    engagement_score = 0
    if has_question: engagement_score += 4
    if has_data: engagement_score += 3
    if has_cta: engagement_score += 3
    engagement_score = min(10, engagement_score)
    
    has_metrics = bool(re.search(r'\d+[%$MBK]|\$\d+|\d+x', content))
    has_analysis = len(content.split()) > 15
    no_spam_pattern = not bool(re.search(r'(.)\1{3,}', content))
    
    quality_score = 0
    if has_metrics: quality_score += 4
    if has_analysis: quality_score += 3
    if no_spam_pattern: quality_score += 3
    quality_score = min(10, quality_score)
    
    content_types = []
    if 'tvl' in content_lower or 'revenue' in content_lower: content_types.append("Protocol analysis ?")
    if has_metrics and ('vs' in content_lower or 'compare' in content_lower): content_types.append("Comparison ?")
    if 'airdrop' in content_lower and 'risk' in content_lower: content_types.append("Airdrop strategy ?")
    if re.search(r'thread|1/', content_lower): content_types.append("Thread format ?")
    if '•' in content or '??' in content: content_types.append("Narrative format ?")
    
    penalties = []
    if keyword_stuffing: penalties.append("?? Keyword stuffing detected")
    if 'kaito' in content_lower and '@' in content: penalties.append("?? Avoid tagging Kaito")
    if generic_count >= 3: penalties.append("?? Too many generic phrases")
    if char_count < 50: penalties.append("?? Too short (min 50 chars)")
    if not has_crypto_focus: penalties.append("?? No crypto-specific topic")
    
    suggestions = []
    if not has_question: suggestions.append("?? Add question untuk drive discussion")
    if not has_data: suggestions.append("?? Include metrics/data untuk credibility")
    if char_count < 150: suggestions.append("?? Expand to 150-280 chars (optimal)")
    if not content_types: suggestions.append("?? Try protocol deep-dive atau comparison format")
    if not is_original: suggestions.append("?? Add personal analysis/unique insight")
    
    total_score = (content_opt_score * 0.3) + (engagement_score * 0.5) + (quality_score * 0.2)
    total_score = round(total_score, 1)
    
    estimated_yaps = int(total_score * 0.7 * 75)
    
    if total_score >= 9:
        rating = "????? Excellent - High YAPS potential!"
    elif total_score >= 7:
        rating = "???? Good - Solid content"
    elif total_score >= 5:
        rating = "??? Fair - Needs improvement"
    else:
        rating = "?? Poor - Optimize further"
    
    # Twitter Algorithm scoring
    twitter_score = 0
    engagement_factors = []
    twitter_penalties = []
    
    if has_question:
        twitter_score += 35
        engagement_factors.append("? Has question (+35 pts, drives Reply 75x)")
    if has_cta:
        twitter_score += 25
        engagement_factors.append("?? Call-to-action (+25 pts)")
    if has_data:
        twitter_score += 15
        engagement_factors.append("?? Data/metrics (+15 pts)")
    if optimal_length:
        twitter_score += 15
        engagement_factors.append("?? Optimal length 150-280 chars (+15 pts)")
    if no_spam_pattern:
        twitter_score += 10
        engagement_factors.append("?? No spam patterns (+10 pts)")
    
    spam_keywords = ['follow me', 'rt this', 'like if']
    if any(spam in content_lower for spam in spam_keywords):
        twitter_score -= 20
        twitter_penalties.append("?? Engagement farming detected (-20 pts)")
    if keyword_stuffing:
        twitter_score -= 15
        twitter_penalties.append("?? Keyword stuffing (-15 pts)")
    
    twitter_score = max(0, min(100, twitter_score))
    
    if twitter_score >= 80:
        twitter_rating = "?? Potensi Viral - Engagement sangat tinggi"
    elif twitter_score >= 60:
        twitter_rating = "?? Jangkauan Bagus - Above average"
    elif twitter_score >= 40:
        twitter_rating = "?? Jangkauan Sedang - Standard"
    else:
        twitter_rating = "?? Jangkauan Rendah - Perlu optimasi"
    
    return {
        "kaito_yaps": {
            "total_score": total_score,
            "rating": rating,
            "estimated_yaps": estimated_yaps,
            "breakdown": {
                "content_optimization": {
                    "score": content_opt_score,
                    "weight": "30%",
                    "details": {
                        "length": f"{char_count} chars" + (" ? optimal" if optimal_length else " ?? adjust to 150-280"),
                        "crypto_focus": "? Yes" if has_crypto_focus else "? No crypto topic",
                        "originality": "? Original" if is_original else "?? Too generic",
                        "keywords": f"{keyword_count} keywords" + (" ?" if 1 <= keyword_count <= 3 else " ??")
                    }
                },
                "engagement_strategy": {
                    "score": engagement_score,
                    "weight": "50%",
                    "details": {
                        "question": "? Yes" if has_question else "? No",
                        "data_driven": "? Yes" if has_data else "? No data/metrics",
                        "cta": "? Yes" if has_cta else "? No call-to-action"
                    }
                },
                "content_quality": {
                    "score": quality_score,
                    "weight": "20%",
                    "details": {
                        "metrics": "? Includes metrics" if has_metrics else "? No specific metrics",
                        "depth": "? Detailed analysis" if has_analysis else "?? Surface-level",
                        "spam_check": "? Clean" if no_spam_pattern else "?? Spam pattern detected"
                    }
                }
            },
            "penalties": penalties if penalties else ["? No penalties detected"]
        },
        "twitter_algorithm": {
            "score": twitter_score,
            "rating": twitter_rating,
            "engagement_factors": engagement_factors if engagement_factors else ["?? Standard engagement"],
            "penalties": twitter_penalties if twitter_penalties else [],
            "algorithm_notes": [
                "?? Reply (75x) > Conversation (30x) > Retweet (10x) > Like (1x)",
                "? 30 menit pertama paling penting untuk velocity",
                "? Question = boost Reply = 75x engagement weight"
            ]
        },
        "content_types": content_types if content_types else ["?? Standard tweet format"],
        "suggestions": suggestions if suggestions else ["? Content is well-optimized!"]
    }

def generate_template_content(project, prompt_type, custom_request):
    """Generate content using templates - no API needed"""
    
    # Random metrics for variety
    growth = random.randint(150, 500)
    tvl = random.randint(10, 500)
    users = random.randint(50, 300)
    funding = random.randint(20, 150)
    
    if prompt_type == 'data-driven':
        # Mix of quick tweets and narrative insights
        templates = [
            # Quick data tweets
            f"{project} menunjukkan pertumbuhan {growth}% dalam 30 hari terakhir dengan TVL mencapai ${tvl}M. Active users naik {users}K. Fundamental kuat atau hype sementara?",
            f"Data menarik: {project} TVL ${tvl}M (+{growth}%), user growth {users}K. Dibanding kompetitor masih undervalued. Accumulation zone?",
            # Narrative insight format
            f"GM anon ??\n\n{project} is once again the focus of conversation in crypto\n\nWith ${funding}m in funding and {growth}% growth, they're no longer just an experiment\n\nWhy is this interesting? ??\n\n• TVL hit ${tvl}M (+{growth}% MoM)\n• User base expanding: {users}K active users\n• Strong fundamentals vs market sentiment gap\n\ndo you see this winning the next cycle?",
            f"{project} update — numbers don't lie:\n\n• ${tvl}M TVL (+{growth}% growth)\n• {users}K users (fastest growing in category)\n• Backed by ${funding}M funding\n\nCompare this to competitors trading at 3-5x higher valuations.\n\nAre we early or am I missing something?"
        ]
    elif prompt_type == 'competitive':
        templates = [
            f"Comparing {project} vs kompetitor: lebih cepat ({growth} TPS), fee lebih rendah, tapi awareness masih kurang. Marketing push bisa game changer?",
            f"Hot take on {project}:\n\nTech-wise: {growth}% faster than competitors\nEconomics: Lower fees, higher throughput\nChallenge: Awareness & community size\n\nIn a market that values narratives over tech, can {project} bridge this gap?\n\nThoughts? ??",
            f"{project} has a superior tech stack ({growth}% improvement on key metrics) but lags in ecosystem mindshare.\n\nHistory shows: best tech doesn't always win.\n\nWhat matters more — technical excellence or community momentum?",
        ]
    elif prompt_type == 'thesis':
        templates = [
            f"Bold prediction: {project} akan jadi top 3 di kategorinya dalam 6 bulan. Alasan: tech superior ({growth}% faster), team proven, timing perfect. Setuju?",
            f"Contrarian take on {project} ??\n\nMarket is sleeping on this one. While everyone chases hype, {project} quietly:\n\n• Shipped {growth}% more features than roadmap\n• TVL growing ${tvl}M organically (no incentives)\n• Team execution: flawless\n\nRisk/reward here looks asymmetric. What am I missing?",
            f"{project} is at a turning point.\n\nIf they maintain {growth}% growth rate and TVL breaks ${tvl}M, we're looking at potential 5-10x from here.\n\nKey catalysts: mainnet launch, partnerships, token mechanics.\n\nBullish or cautious? ??"
        ]
    else:  # custom
        if custom_request:
            templates = [
                f"{project}: {custom_request}\n\nCurrent metrics: {growth}% growth, ${tvl}M TVL, {users}K users\n\nThoughts?",
                f"Re: {custom_request}\n\n{project} showing strong signals:\n• {growth}% up (30d)\n• {users}K active users\n• ${tvl}M TVL milestone\n\nBagaimana menurut kalian?"
            ]
        else:
            templates = [
                f"{project} update: {growth}% growth, ecosystem expanding with {users}K active users. Bullish or cautious?",
                f"Watching {project} closely\n\nMetrics look solid:\n• {growth}% growth rate\n• ${tvl}M TVL\n• {users}K users onboarded\n\nBut market sentiment still mixed. What's your take? ??"
            ]
    
    return random.choice(templates)

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.json
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Content required"}), 400
        
        analysis = analyze_content_full(content)
        return jsonify({"success": True, "analysis": analysis})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
