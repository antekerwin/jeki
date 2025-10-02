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
        # Mostly narrative insights (80% narrative, 20% quick)
        templates = [
            # Narrative insight formats (GM dude style)
            f"GM dude ??\n\n{project} is once again the focus of conversation in crypto\n\nWith ${funding}m in funding, they are no longer just an experiment, but serious candidates in their category\n\nWhy is this interesting? ??\n\n• TVL hit ${tvl}M (+{growth}% MoM)\n• User base expanding: {users}K active users  \n• Strong fundamentals vs market sentiment gap\n\ndo you see {project} winning the next cycle?",
            f"GM anon ??\n\n{project} numbers are telling a story\n\nWith {growth}% growth and ${tvl}M TVL, they're moving fast\n\nWhy this matters ??\n\n• Growth rate: {growth}% (top tier in category)\n• Capital backing: ${funding}M from top VCs\n• User traction: {users}K active wallets\n\nThe data suggests accumulation phase. Are we early?",
            f"{project} update — numbers don't lie:\n\n• ${tvl}M TVL (+{growth}% growth)\n• {users}K users (fastest growing in category)\n• Backed by ${funding}M funding\n\nCompare this to competitors trading at 3-5x higher valuations.\n\nAre we early or am I missing something?",
            f"Quick {project} breakdown ??\n\nFundamentals are strong but market hasn't caught up yet\n\nWhat I'm seeing ??\n\n• ${tvl}M TVL with {growth}% organic growth\n• {users}K users onboarded (no token incentives yet)\n• ${funding}M raised from tier-1 backers\n\nRisk/reward looking asymmetric here. Thoughts?",
            f"GM fam ??\n\n{project} is quietly building while everyone's distracted\n\nThe numbers ??\n\n• {growth}% growth (30-day)\n• ${tvl}M TVL milestone hit  \n• {users}K active users and growing\n\nFundamentals > hype. Do you see the potential here?",
            # Quick data tweets (20% probability)
            f"Data menarik: {project} TVL ${tvl}M (+{growth}%), user growth {users}K. Dibanding kompetitor masih undervalued. Accumulation zone?"
        ]
    elif prompt_type == 'competitive':
        templates = [
            f"Hot take on {project} ??\n\nTech-wise: {growth}% faster than competitors\nEconomics: Lower fees, higher throughput  \nChallenge: Awareness & community size\n\nIn a market that values narratives over tech, can {project} bridge this gap?\n\nThoughts? ??",
            f"GM anon ??\n\n{project} vs the competition — let's break it down\n\nWhat they're winning at ??\n\n• Performance: {growth}% faster processing\n• Economics: ${tvl}M TVL with better unit economics\n• Execution: Shipped {users}% more features than roadmap\n\nWhat they're losing at:\n• Marketing & awareness\n• Community size\n\nCan fundamentals win over narratives? History says...",
            f"Comparing {project} to competitors ??\n\nThe good ??\n• {growth}% faster than market leader\n• ${tvl}M TVL (growing organically)\n• Lower fees + better UX\n\nThe challenge:\n• Awareness gap vs competitors\n• Smaller community (for now)\n\nBet on tech or bet on hype? What's your play?"
        ]
    elif prompt_type == 'thesis':
        templates = [
            f"Contrarian take on {project} ??\n\nMarket is sleeping on this one. While everyone chases hype, {project} quietly:\n\n• Shipped {growth}% more features than roadmap\n• TVL growing ${tvl}M organically (no incentives)  \n• Team execution: flawless\n\nRisk/reward here looks asymmetric. What am I missing?",
            f"GM dude ??\n\n{project} is at a turning point\n\nWhy I'm watching closely ??\n\n• Growth trajectory: {growth}% (sustainable pace)\n• TVL milestone: ${tvl}M (next target: 2x from here)\n• Catalysts lined up: mainnet launch + partnerships\n\nIf they execute, we're looking at 5-10x potential.\n\nBullish or cautious?",
            f"Bold prediction on {project} ??\n\nThey will be top 3 in their category within 6 months\n\nWhy? ??\n\n• Tech: {growth}% superior performance vs competitors\n• Team: Proven track record (previous exits)\n• Timing: Market conditions aligning perfectly\n• Execution: Ahead of roadmap consistently\n\nAm I too bullish or are we genuinely early?",
            f"{project} thesis thread ??\n\nThe setup here is interesting\n\nBullish signals ??\n• {growth}% growth maintained for 90 days\n• ${tvl}M TVL (organic, no mercenary capital)\n• ${funding}M backing from smart money\n• Builder community growing fast\n\nBearish risk: Market timing, competition\n\nNet: Risk/reward heavily skewed to upside. Thoughts?"
        ]
    else:  # custom - multiple narrative styles
        if custom_request:
            templates = [
                # Technical Narrator style
                f"what is {project} pitch to founders and builders?\n\n{growth}% performance improvement and sub-second finality combined with being EVM compatible.\n\nthis means that {project} currently can call themselves one of the fastest chains.\n\nKey benefits:\n• ${tvl}M TVL with organic growth\n• {users}K active users and growing\n• Accelerator program for builders from zero to one\n• Integration within the ecosystem\n\nanother key benefit is their community program focused on securing attention. if new launches leverage this well, they can bootstrap their own mindshare.",
                
                # Personal Reflection style
                f"After much reflection on {project}'s journey\n\nIt's been incredible watching the growth: {growth}% expansion, ${tvl}M TVL milestone, and {users}K users onboarded.\n\nThe space has evolved beautifully, yet chaotically. Seeing fundamentals like these makes me believe we're still early in this cycle.\n\nWhat's your take on {project}'s trajectory?",
                
                # Indonesian Wisdom style
                f"Baru-baru ini saya menyadari bahwa proyek-proyek seperti {project} yang survive bear market selalu menemukan momentum di bull run.\n\nMereka telah mencapai:\n• {growth}% pertumbuhan organik\n• ${tvl}M TVL tanpa incentive farming\n• {users}K pengguna aktif yang loyal\n\nBelajarlah dari ini.\n\nSaya percaya jika sebuah proyek bertahan cukup lama dengan fundamentals kuat, mereka akan menemukan sukses mereka sendiri.\n\nSetuju?",
                
                # Default custom request
                f"{project}: {custom_request}\n\nCurrent metrics: {growth}% growth, ${tvl}M TVL, {users}K users\n\nThoughts?",
                
                # Indonesian variant
                f"Re: {custom_request}\n\n{project} showing strong signals:\n• {growth}% up (30d)\n• {users}K active users\n• ${tvl}M TVL milestone\n\nBagaimana menurut kalian?"
            ]
        else:
            # More narrative-style default templates
            templates = [
                # Technical Narrator
                f"what is {project} bringing to the table?\n\n{growth}% improvement over competitors with sub-second finality.\n\nKey metrics:\n• ${tvl}M TVL (organic growth)\n• {users}K active users\n• Strong builder ecosystem\n\nthis is interesting because they're solving real problems while others focus on hype.",
                
                # Personal Reflection
                f"Watching {project} develop has been fascinating\n\nThe fundamentals keep improving:\n• {growth}% growth rate\n• ${tvl}M TVL\n• {users}K users onboarded\n\nMarket sentiment is still mixed, but I think we're early here. What's your take? ??",
                
                # Indonesian Wisdom
                f"Menarik melihat {project} bertahan dan berkembang\n\nMetrik mereka solid:\n• {growth}% pertumbuhan organik\n• ${tvl}M TVL tanpa hype\n• {users}K pengguna aktif\n\nProyek yang fokus pada fundamentals biasanya menang jangka panjang. Setuju?"
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
