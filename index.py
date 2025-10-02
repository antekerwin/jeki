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

        # ? FIX: Define user_prompt variable BEFORE using it
        if prompt_type == 'custom' and custom_request:
            user_prompt = f"Generate tweet about {project}: {custom_request}"
        else:
            prompt_styles = {
                'data-driven': f"Generate data-driven tweet about {project} dengan metrics konkret",
                'competitive': f"Generate competitive analysis tweet comparing {project} dengan kompetitor",
                'thesis': f"Generate bold thesis/prediction tweet about {project}"
            }
            user_prompt = prompt_styles.get(prompt_type, f"Generate insightful tweet about {project}")

        # Randomize style & temp
        styles = ['analytical', 'contrarian', 'bullish', 'data-focused']
        chosen_style = random.choice(styles)
        temp = round(random.uniform(0.7, 0.95), 2)

        # Free API - No key needed
        headers = {"Content-Type": "application/json"}
        payload = {
            "inputs": user_prompt,
            "parameters": {
                "max_new_tokens": 280,
                "temperature": temp,
                "return_full_text": False
            }
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct",
            headers=headers,
            json=payload,
            timeout=30
        )
        if response.status_code != 200:
            return jsonify({"error": f"API error"}), 500

        # Parse response properly
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            content = result[0].get('generated_text', 'Error generating content')
        else:
            content = "Error: Unexpected API response format"

        char_count = len(content)
        optimal_length = 150 <= char_count <= 280
        has_data = any(char.isdigit() for char in content)
        has_question = '?' in content
        quality = 7 + (1 if optimal_length else 0) + (1 if has_data else 0) + (1 if has_question else 0)

        scoring = {
            "crypto_relevance": quality,
            "engagement_potential": 9 if has_question else 7,
            "semantic_quality": 9 if (has_data and optimal_length) else 7,
            "total": quality + (9 if has_question else 7) + (9 if has_data else 7),
            "rating": f"????{'?' if quality >= 9 else ''} Quality: {quality}/10",
            "feedback": [
                f"?? {char_count} chars" + (" ?" if optimal_length else " ??"),
                f"?? Data: {'?' if has_data else '??'}",
                f"?? Engage: {'?' if has_question else '??'}",
                f"?? Est. YAPS: ~{int(quality*0.7*75)} pts",
                f"?? Style: {chosen_style}"
            ]
        }
        return jsonify({"success": True, "content": content, "scoring": scoring})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_content():
    try:
        data = request.json
        content = data.get('content', '').strip()

        if not content:
            return jsonify({"error": "Content required"}), 400

        char_count = len(content)
        optimal_length = 150 <= char_count <= 280
        min_length = char_count >= 50

        crypto_keywords = ['defi', 'layer', 'l2', 'ai', 'rwa', 'tvl', 'airdrop', 'protocol', 'chain', 'token', 'nft', 'dao', 'staking', 'yield', 'bridge', 'zk', 'rollup', 'evm', 'smart contract']
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
        has_cta = any(word in content_lower for word in ['what', 'how', 'why', 'thoughts', 'think', 'opinion'])

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

        return jsonify({
            "success": True,
            "analysis": {
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
                },
                "content_types": content_types if content_types else ["?? Standard tweet format"],
                "penalties": penalties if penalties else ["? No penalties detected"],
                "suggestions": suggestions if suggestions else ["? Content is well-optimized!"],
                "total_score": total_score,
                "estimated_yaps": estimated_yaps,
                "rating": rating
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)