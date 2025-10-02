#!/usr/bin/env python3
"""
YAPS Content Generator - AI-powered content generator untuk maximize YAPS points
Bahasa Indonesia
"""

from flask import Flask, render_template, request, jsonify
import os
from openai import OpenAI
import requests
import re

app = Flask(__name__)

def fetch_kaito_projects():
    """Fetch top 20 projects dari Kaito Pre-TGE realtime"""
    try:
        response = requests.get("https://yaps.kaito.ai/pre-tge", timeout=10)
        if response.status_code != 200:
            return get_fallback_projects()
        
        html = response.text
        projects = []
        
        # Pattern untuk extract project names
        pattern = r'(MOMENTUM|LIMITLESS|POLYMARKET|SENTIENT|MONAD|OPENSEA|BASE|ALLORA|YIELDBASIS|CYSIC|BILLIONS|MET|WALLCHAIN|IRYS|RECALL|KITE|MASK|EVERLYN|DZ|TALUS|BERACHAIN|STORY)'
        matches = re.findall(pattern, html)
        
        # Deduplicate & get unique top 20
        seen = set()
        for match in matches:
            if match not in seen and len(projects) < 20:
                projects.append({
                    "name": match.title() if match != "MASK" else "MetaMask",
                    "mindshare": "High",
                    "category": get_category(match)
                })
                seen.add(match)
        
        return projects if projects else get_fallback_projects()
        
    except:
        return get_fallback_projects()

def get_fallback_projects():
    """Fallback jika fetch gagal"""
    return [
        {"name": "Limitless", "mindshare": "High", "category": "AI Tools"},
        {"name": "Polymarket", "mindshare": "Very High", "category": "Prediction Markets"},
        {"name": "Sentient", "mindshare": "High", "category": "AI Agents"},
        {"name": "Monad", "mindshare": "High", "category": "Layer 1"},
        {"name": "Base", "mindshare": "Very High", "category": "Layer 2"},
    ]

def get_category(project):
    """Get category untuk project"""
    categories = {
        "LIMITLESS": "AI Tools", "SENTIENT": "AI Agents", "POLYMARKET": "Prediction Markets",
        "MONAD": "Layer 1", "BASE": "Layer 2", "OPENSEA": "NFT Marketplace",
        "ALLORA": "AI Infrastructure", "YIELDBASIS": "DeFi", "CYSIC": "ZK Infra",
        "BILLIONS": "AI Agents", "MET": "Metaverse", "WALLCHAIN": "DeFi",
        "IRYS": "Data Storage", "RECALL": "AI Memory", "KITE": "DeFi",
        "MASK": "Wallet", "EVERLYN": "AI Agents", "DZ": "Gaming", "TALUS": "AI",
        "BERACHAIN": "Layer 1", "STORY": "IP Protocol", "MOMENTUM": "DeFi"
    }
    return categories.get(project, "DeFi")

PROMPT_TEMPLATES = {
    "data_driven": {
        "name": "📊 Analisis Data & Metrik",
        "description": "Konten berdasarkan data funding, TVL, pertumbuhan user",
        "system": """Anda adalah crypto analyst yang ahli membuat konten Twitter data-driven untuk YAPS.

ATURAN YAPS:
- Crypto Relevance (30%): Data konkret, metrics, original insight
- Smart Followers Engagement (50%): Konten yang engage influencers
- Semantic Analysis (20%): LLM evaluate depth & originality

STRUKTUR:
1. Hook dengan data point terkuat
2. 2-3 metric spesifik dengan konteks
3. Analisis kenapa metrics ini penting
4. Thesis/prediction
5. Question untuk drive discussion

HINDARI:
- Keyword stuffing
- Lebih dari 2 tags
- Generic statements
- Copy-paste news

BAHASA: Indonesia (natural, tidak kaku)
LENGTH: 150-280 karakter optimal"""
    },
    
    "competitive": {
        "name": "🎯 Positioning & Kompetitor",
        "description": "Analisis competitive landscape dan unique differentiation",
        "system": """Anda adalah crypto strategist yang ahli analisis kompetitif untuk YAPS.

ATURAN YAPS:
- Crypto Relevance (30%): Market structure understanding
- Smart Followers Engagement (50%): Thought leadership
- Semantic Analysis (20%): Original positioning analysis

STRUKTUR:
1. Market context & kategori
2. Competitive map (2-3 competitors)
3. Unique differentiation project ini
4. Thesis siapa yang menang dan kenapa
5. Question untuk community perspective

HINDARI:
- Shilling tanpa objektif
- Excessive tags
- Surface-level comparison

BAHASA: Indonesia (professional tapi approachable)
LENGTH: 150-280 karakter optimal"""
    },
    
    "thesis": {
        "name": "💡 Forward-Looking Thesis",
        "description": "Prediksi trend, market impact, contrarian take",
        "system": """Anda adalah crypto thought leader yang ahli membuat thesis & prediction untuk YAPS.

ATURAN YAPS:
- Crypto Relevance (30%): Trend understanding
- Smart Followers Engagement (50%): Provocative but backed thesis
- Semantic Analysis (20%): Original thinking, contrarian OK

STRUKTUR:
1. Trend observation (apa yang shifting)
2. Positioning project dalam trend ini
3. Clear thesis/prediction (bold OK)
4. 2-3 supporting reasoning
5. Risk/consideration (show balanced thinking)
6. Question untuk invite debate

HINDARI:
- Opinion tanpa backing
- Emotional statements
- Hype without substance

BAHASA: Indonesia (confident, analytical)
LENGTH: 150-280 karakter optimal"""
    }
}

@app.route('/')
def index():
    projects = fetch_kaito_projects()
    return render_template('index.html', projects=projects, prompts=PROMPT_TEMPLATES)

@app.route('/generate', methods=['POST'])
def generate_content():
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Invalid request'}), 400
        
        project_name = data.get('project')
        prompt_type = data.get('prompt_type')
        
        projects = fetch_kaito_projects()
        project = next((p for p in projects if p['name'] == project_name), None)
        if not project:
            return jsonify({'error': 'Project tidak ditemukan'}), 400
        
        if prompt_type not in PROMPT_TEMPLATES:
            return jsonify({'error': 'Prompt type tidak valid'}), 400
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return jsonify({
                'error': 'OpenAI API Key belum diset',
                'message': 'Silakan set OPENAI_API_KEY di Secrets'
            }), 400
        
        client = OpenAI(api_key=api_key)
        
        prompt_template = PROMPT_TEMPLATES[prompt_type]
        
        user_message = f"""Generate konten Twitter untuk project: {project_name}

Category: {project['category']}
Current Mindshare: {project['mindshare']}

Buat 1 tweet berkualitas tinggi yang:
1. Optimized untuk YAPS scoring (Crypto Relevance 30% + Smart Engagement 50% + Semantic 20%)
2. Include data/metrics spesifik (bisa estimated berdasarkan mindshare dan category)
3. Original analysis, bukan copy-paste
4. Natural bahasa Indonesia
5. Max 2 tags (atau tanpa tag lebih baik)
6. 150-280 karakter

Generate HANYA konten tweet-nya. Jangan include penjelasan atau metadata."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt_template['system']},
                {"role": "user", "content": user_message}
            ],
            temperature=0.8,
            max_tokens=500
        )
        
        generated_content = response.choices[0].message.content
        if generated_content:
            generated_content = generated_content.strip()
        else:
            generated_content = ""
        
        scoring = analyze_yaps_score(generated_content)
        
        return jsonify({
            'content': generated_content,
            'project': project,
            'prompt_type': prompt_type,
            'scoring': scoring
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_content():
    """Analyze user's content berdasarkan Kaito YAPS + Twitter Algorithm"""
    try:
        data = request.json
        content = data.get('content', '').strip()
        
        if not content:
            return jsonify({"error": "Content required"}), 400
        
        # === KAITO YAPS ANALYSIS ===
        char_count = len(content)
        optimal_length = 150 <= char_count <= 280
        min_length = char_count >= 50
        
        # Crypto keywords detection
        crypto_keywords = ['defi', 'layer', 'l2', 'ai', 'rwa', 'tvl', 'airdrop', 'protocol', 'chain', 'token', 'nft', 'dao', 'staking', 'yield', 'bridge', 'zk', 'rollup', 'evm', 'smart contract']
        content_lower = content.lower()
        keyword_count = sum(1 for kw in crypto_keywords if kw in content_lower)
        has_crypto_focus = keyword_count >= 1
        
        # Keyword stuffing detection
        keyword_stuffing = keyword_count > 5
        
        # Original insight
        generic_phrases = ['to the moon', 'lfg', 'gm', 'ser', 'ngmi', 'wagmi', 'bullish', 'bearish']
        generic_count = sum(1 for phrase in generic_phrases if phrase in content_lower)
        is_original = generic_count < 2
        
        # 1. CONTENT OPTIMIZATION (30%)
        content_opt_score = 0
        if min_length: content_opt_score += 2
        if optimal_length: content_opt_score += 3
        if has_crypto_focus: content_opt_score += 3
        if is_original: content_opt_score += 2
        content_opt_score = min(10, content_opt_score)
        
        # 2. ENGAGEMENT STRATEGY (50%)
        has_question = '?' in content
        has_data = any(char.isdigit() for char in content)
        has_cta = any(word in content_lower for word in ['what', 'how', 'why', 'thoughts', 'think', 'opinion', 'apa', 'bagaimana', 'mengapa', 'gimana'])
        
        engagement_score = 0
        if has_question: engagement_score += 4
        if has_data: engagement_score += 3
        if has_cta: engagement_score += 3
        engagement_score = min(10, engagement_score)
        
        # 3. CONTENT QUALITY (20%)
        has_metrics = bool(re.search(r'\d+[%$MBK]|\$\d+|\d+x', content))
        has_analysis = len(content.split()) > 15
        no_spam_pattern = not bool(re.search(r'(.)\1{3,}', content))
        
        quality_score = 0
        if has_metrics: quality_score += 4
        if has_analysis: quality_score += 3
        if no_spam_pattern: quality_score += 3
        quality_score = min(10, quality_score)
        
        # === TWITTER ALGORITHM ANALYSIS ===
        # Based on Twitter's engagement weights
        twitter_score = 0
        twitter_factors = []
        
        # Reply potential (75x weight in Twitter algo)
        if has_question:
            twitter_score += 35
            twitter_factors.append("✅ Question drives replies (75x Twitter weight)")
        
        # Conversation starter (27-30x weight)
        if has_cta or '?' in content:
            twitter_score += 25
            twitter_factors.append("✅ Conversation starter (30x weight)")
        
        # Rich content (higher engagement)
        if has_data or has_metrics:
            twitter_score += 15
            twitter_factors.append("✅ Data-rich content (better retention)")
        
        # Optimal length for engagement
        if 50 <= char_count <= 280:
            twitter_score += 15
            twitter_factors.append("✅ Optimal length (not cut off)")
        else:
            twitter_factors.append("⚠️ Length not optimal for feed")
        
        # Recency/velocity potential (first 30 mins critical)
        if not any(spam in content_lower for spam in ['follow', 'rt', 'like if']):
            twitter_score += 10
            twitter_factors.append("✅ No engagement farming (avoid penalty)")
        else:
            twitter_score -= 20
            twitter_factors.append("❌ Engagement farming detected (-74x penalty risk)")
        
        # Twitter penalties check
        twitter_penalties = []
        if keyword_stuffing:
            twitter_score -= 15
            twitter_penalties.append("⚠️ Keyword stuffing may trigger spam filter")
        
        if content_lower.count('http') > 1:
            twitter_score -= 10
            twitter_penalties.append("⚠️ Multiple links reduce reach by ~30%")
        
        if '@' in content and content.count('@') > 3:
            twitter_score -= 10
            twitter_penalties.append("⚠️ Too many mentions may reduce distribution")
        
        twitter_score = max(0, min(100, twitter_score))
        
        # === HIGH-SCORING CONTENT TYPES ===
        content_types = []
        if 'tvl' in content_lower or 'revenue' in content_lower:
            content_types.append("📊 Protocol analysis")
        if has_metrics and ('vs' in content_lower or 'compare' in content_lower):
            content_types.append("⚖️ Comparison analysis")
        if 'airdrop' in content_lower and 'risk' in content_lower:
            content_types.append("💰 Airdrop strategy")
        if re.search(r'thread|1/', content_lower):
            content_types.append("🧵 Thread format")
        
        # === KAITO PENALTIES ===
        kaito_penalties = []
        if keyword_stuffing:
            kaito_penalties.append("⚠️ Keyword stuffing detected")
        if 'kaito' in content_lower and '@' in content:
            kaito_penalties.append("⚠️ Avoid tagging Kaito")
        if generic_count >= 3:
            kaito_penalties.append("⚠️ Too many generic phrases")
        if char_count < 50:
            kaito_penalties.append("⚠️ Too short (min 50 chars)")
        if not has_crypto_focus:
            kaito_penalties.append("⚠️ No crypto-specific topic")
        
        # === OPTIMIZATION SUGGESTIONS ===
        suggestions = []
        if not has_question:
            suggestions.append("💡 Add question untuk drive discussion (75x Twitter boost)")
        if not has_data:
            suggestions.append("💡 Include metrics/data untuk credibility")
        if char_count < 150:
            suggestions.append("💡 Expand to 150-280 chars (optimal range)")
        if not content_types:
            suggestions.append("💡 Try protocol deep-dive atau comparison format")
        if not is_original:
            suggestions.append("💡 Add personal analysis/unique insight")
        if not has_cta:
            suggestions.append("💡 Add call-to-action untuk conversation")
        
        # === WEIGHTED SCORES ===
        kaito_total = (content_opt_score * 0.3) + (engagement_score * 0.5) + (quality_score * 0.2)
        kaito_total = round(kaito_total, 1)
        
        # Estimated YAPS Points
        estimated_yaps = int(kaito_total * 0.7 * 75)
        
        # Ratings
        if kaito_total >= 9:
            kaito_rating = "⭐⭐⭐⭐⭐ Excellent - High YAPS potential!"
        elif kaito_total >= 7:
            kaito_rating = "⭐⭐⭐⭐ Good - Solid content"
        elif kaito_total >= 5:
            kaito_rating = "⭐⭐⭐ Fair - Needs improvement"
        else:
            kaito_rating = "⭐⭐ Poor - Optimize further"
        
        if twitter_score >= 80:
            twitter_rating = "🚀 Viral Potential - High engagement expected"
        elif twitter_score >= 60:
            twitter_rating = "📈 Good Reach - Above average distribution"
        elif twitter_score >= 40:
            twitter_rating = "📊 Moderate Reach - Standard distribution"
        else:
            twitter_rating = "📉 Low Reach - Needs optimization"
        
        return jsonify({
            "success": True,
            "analysis": {
                "kaito_yaps": {
                    "total_score": kaito_total,
                    "rating": kaito_rating,
                    "estimated_yaps": estimated_yaps,
                    "breakdown": {
                        "content_optimization": {
                            "score": content_opt_score,
                            "weight": "30%",
                            "details": {
                                "length": f"{char_count} chars" + (" ✅ optimal" if optimal_length else " ⚠️ adjust to 150-280"),
                                "crypto_focus": "✅ Yes" if has_crypto_focus else "❌ No crypto topic",
                                "originality": "✅ Original" if is_original else "⚠️ Too generic",
                                "keywords": f"{keyword_count} keywords" + (" ✅" if 1 <= keyword_count <= 3 else " ⚠️")
                            }
                        },
                        "engagement_strategy": {
                            "score": engagement_score,
                            "weight": "50%",
                            "details": {
                                "question": "✅ Yes" if has_question else "❌ No",
                                "data_driven": "✅ Yes" if has_data else "❌ No data/metrics",
                                "cta": "✅ Yes" if has_cta else "❌ No call-to-action"
                            }
                        },
                        "content_quality": {
                            "score": quality_score,
                            "weight": "20%",
                            "details": {
                                "metrics": "✅ Includes metrics" if has_metrics else "❌ No specific metrics",
                                "depth": "✅ Detailed analysis" if has_analysis else "⚠️ Surface-level",
                                "spam_check": "✅ Clean" if no_spam_pattern else "⚠️ Spam pattern"
                            }
                        }
                    },
                    "penalties": kaito_penalties if kaito_penalties else ["✅ No penalties detected"]
                },
                "twitter_algorithm": {
                    "score": twitter_score,
                    "rating": twitter_rating,
                    "engagement_factors": twitter_factors if twitter_factors else ["ℹ️ Basic content"],
                    "penalties": twitter_penalties if twitter_penalties else ["✅ No Twitter penalties"],
                    "algorithm_notes": [
                        "📊 Reply weight: 75x (most powerful)",
                        "🔄 Retweet weight: 10x",
                        "❤️ Like weight: 1x",
                        "⏰ First 30 mins critical for velocity",
                        "🚫 Avoid: keyword stuffing, external links, engagement farming"
                    ]
                },
                "content_types": content_types if content_types else ["ℹ️ Standard tweet format"],
                "suggestions": suggestions if suggestions else ["✅ Content is well-optimized!"]
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def analyze_yaps_score(content):
    """Simple scoring analysis untuk generate endpoint"""
    score = {
        'crypto_relevance': 0,
        'engagement_potential': 0,
        'semantic_quality': 0,
        'total': 0,
        'feedback': []
    }
    
    if len(content) >= 50:
        score['crypto_relevance'] += 3
        score['feedback'].append('✅ Length optimal (50+ chars)')
    
    crypto_keywords = ['DeFi', 'L2', 'TVL', 'funding', 'protocol', 'AI', 'crypto', 'blockchain']
    if any(kw.lower() in content.lower() for kw in crypto_keywords):
        score['crypto_relevance'] += 4
        score['feedback'].append('✅ Crypto-relevant topics')
    
    if any(char.isdigit() for char in content):
        score['crypto_relevance'] += 3
        score['feedback'].append('✅ Contains data/metrics')
    else:
        score['feedback'].append('⚠️ Tidak ada data numerik')
    
    tags_count = content.count('@')
    if tags_count <= 2:
        score['engagement_potential'] += 5
        score['feedback'].append(f'✅ Tags optimal ({tags_count} tags)')
    else:
        score['engagement_potential'] += 2
        score['feedback'].append(f'⚠️ Terlalu banyak tags ({tags_count})')
    
    if '?' in content:
        score['engagement_potential'] += 3
        score['feedback'].append('✅ Ada question untuk engagement')
    
    if len(content) <= 280:
        score['engagement_potential'] += 2
        score['feedback'].append('✅ Twitter-friendly length')
    
    if any(word in content.lower() for word in ['kenapa', 'bagaimana', 'mengapa', 'analisis', 'thesis']):
        score['semantic_quality'] += 3
        score['feedback'].append('✅ Analytical tone')
    
    if not any(spam in content.lower() for spam in ['gm', 'gn', 'lfg', 'wagmi']):
        score['semantic_quality'] += 4
        score['feedback'].append('✅ Tidak ada spam phrases')
    
    if len(content.split()) > 15:
        score['semantic_quality'] += 3
        score['feedback'].append('✅ Depth content (15+ words)')
    
    score['total'] = score['crypto_relevance'] + score['engagement_potential'] + score['semantic_quality']
    
    if score['total'] >= 18:
        score['rating'] = 'EXCELLENT (High YAPS potential)'
    elif score['total'] >= 14:
        score['rating'] = 'GOOD (Medium-High YAPS)'
    elif score['total'] >= 10:
        score['rating'] = 'FAIR (Medium YAPS)'
    else:
        score['rating'] = 'NEEDS IMPROVEMENT'
    
    return score

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
