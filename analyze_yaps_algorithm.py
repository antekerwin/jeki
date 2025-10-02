#!/usr/bin/env python3
"""
Analyze YAPS algorithm from Schema #517 attestations
"""

import requests
import json
import statistics

GRAPHQL_URL = "https://base.easscan.org/graphql"

def query_graphql(query, variables=None):
    """Execute GraphQL query"""
    payload = {"query": query, "variables": variables or {}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    return response.json()

def analyze_yaps_attestations():
    """Analyze YAPS attestations to reverse engineer algorithm"""
    
    schema_uid = "0x30c23ae07a72d6c4cafbe3c7a24f6b85427b9dacde030366376c8f87d794a802"
    
    print("🎯 ANALYZING YAPS ALGORITHM FROM SCHEMA #517")
    print("Schema structure: uint64 twitterUserId, uint64 yapScaledPoints, uint64 yap24HScaledPoints, uint64 timestamp")
    print("="*80)
    
    # Query more attestations for better analysis
    query = """
    query GetYAPSAttestations($schemaId: String!) {
      attestations(
        where: { schemaId: { equals: $schemaId } },
        take: 50,
        orderBy: [{ timeCreated: desc }]
      ) {
        id
        attester
        data
        decodedDataJson
        timeCreated
      }
    }
    """
    
    variables = {"schemaId": schema_uid}
    result = query_graphql(query, variables)
    
    if 'data' not in result or 'attestations' not in result['data']:
        print(f"Error querying attestations: {result}")
        return
    
    attestations = result['data']['attestations']
    print(f"📊 Analyzing {len(attestations)} attestations...\n")
    
    # Parse attestation data
    parsed_data = []
    
    for att in attestations[:20]:  # Analyze first 20 for detailed view
        if att['decodedDataJson']:
            try:
                decoded = json.loads(att['decodedDataJson'])
                
                data_point = {
                    'timestamp': att['timeCreated'],
                    'twitter_id': None,
                    'yap_scaled': None,
                    'yap_24h': None
                }
                
                for field in decoded:
                    name = field['name']
                    value = field['value']['value'] if 'value' in field['value'] else field['value']
                    
                    if 'twitterUserId' in name:
                        data_point['twitter_id'] = str(value)
                    elif 'yapScaledPoints' in name and '24H' not in name:
                        data_point['yap_scaled'] = int(value) if str(value).isdigit() else 0
                    elif 'yap24HScaledPoints' in name:
                        data_point['yap_24h'] = int(value) if str(value).isdigit() else 0
                
                if data_point['yap_scaled'] is not None and data_point['yap_24h'] is not None:
                    parsed_data.append(data_point)
                    
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                continue
    
    if not parsed_data:
        print("❌ No valid data found for analysis")
        return
    
    print(f"✅ Successfully parsed {len(parsed_data)} data points\n")
    
    # Display sample data
    print("📋 SAMPLE ATTESTATION DATA:")
    print("-" * 80)
    for i, data in enumerate(parsed_data[:10]):
        ratio = data['yap_scaled'] / data['yap_24h'] if data['yap_24h'] > 0 else 0
        print(f"{i+1:2d}. Twitter ID: {data['twitter_id'][:12]}...")
        print(f"    Total Scaled:  {data['yap_scaled']:>12,}")
        print(f"    24H Scaled:    {data['yap_24h']:>12,}")
        print(f"    Ratio:         {ratio:>12.2f}")
        print()
    
    # Statistical analysis
    print("\n🔍 ALGORITHM PATTERN ANALYSIS:")
    print("=" * 80)
    
    total_scaled_points = [d['yap_scaled'] for d in parsed_data if d['yap_scaled'] > 0]
    yap_24h_points = [d['yap_24h'] for d in parsed_data if d['yap_24h'] > 0]
    ratios = [d['yap_scaled'] / d['yap_24h'] for d in parsed_data if d['yap_24h'] > 0]
    
    if total_scaled_points:
        print(f"📈 TOTAL SCALED POINTS ANALYSIS:")
        print(f"   Range: {min(total_scaled_points):,} to {max(total_scaled_points):,}")
        print(f"   Average: {statistics.mean(total_scaled_points):,.0f}")
        print(f"   Median: {statistics.median(total_scaled_points):,.0f}")
        
    if yap_24h_points:
        print(f"\n⏰ 24H SCALED POINTS ANALYSIS:")
        print(f"   Range: {min(yap_24h_points):,} to {max(yap_24h_points):,}")
        print(f"   Average: {statistics.mean(yap_24h_points):,.0f}")
        print(f"   Median: {statistics.median(yap_24h_points):,.0f}")
    
    if ratios:
        print(f"\n🧮 RATIO ANALYSIS (Total/24H):")
        print(f"   Range: {min(ratios):.1f} to {max(ratios):.1f}")
        print(f"   Average: {statistics.mean(ratios):.2f}")
        print(f"   Median: {statistics.median(ratios):.2f}")
        
        # Look for patterns
        common_ratios = []
        for ratio in ratios:
            rounded = round(ratio, 1)
            if rounded not in [r[0] for r in common_ratios]:
                common_ratios.append((rounded, 1))
            else:
                for i, (r, count) in enumerate(common_ratios):
                    if r == rounded:
                        common_ratios[i] = (r, count + 1)
                        break
        
        common_ratios.sort(key=lambda x: x[1], reverse=True)
        print(f"   Most common ratios: {common_ratios[:5]}")
    
    # Detect algorithm patterns
    print(f"\n🎯 ALGORITHM INSIGHTS:")
    print("=" * 80)
    
    # Pattern 1: Time-based accumulation
    if ratios and statistics.mean(ratios) > 7:
        avg_ratio = statistics.mean(ratios)
        estimated_days = avg_ratio / 24 if avg_ratio > 24 else avg_ratio
        print(f"📅 Time Pattern Detected:")
        print(f"   Average ratio suggests {estimated_days:.1f} days of accumulation")
        print(f"   Indicates rolling/cumulative scoring system")
    
    # Pattern 2: Scaling factors
    if total_scaled_points and yap_24h_points:
        # Look for common scaling factors
        scaling_factors = []
        for data in parsed_data:
            if data['yap_24h'] > 0 and data['yap_scaled'] > 0:
                # Check if there's a consistent multiplier
                factor = data['yap_scaled'] / data['yap_24h']
                scaling_factors.append(factor)
        
        if scaling_factors:
            # Find most common scaling range
            factor_ranges = {}
            for factor in scaling_factors:
                range_key = int(factor / 10) * 10  # Group by tens
                factor_ranges[range_key] = factor_ranges.get(range_key, 0) + 1
            
            most_common_range = max(factor_ranges.items(), key=lambda x: x[1])
            print(f"📊 Scaling Factor Pattern:")
            print(f"   Most common range: {most_common_range[0]}-{most_common_range[0]+10}")
            print(f"   Occurrence: {most_common_range[1]}/{len(scaling_factors)} samples")
    
    # Pattern 3: Point distribution
    if total_scaled_points:
        # Check for tier-based distribution
        sorted_points = sorted(total_scaled_points)
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        
        print(f"\n📊 POINT DISTRIBUTION (Possible Tiers):")
        for p in percentiles:
            idx = int((p / 100) * len(sorted_points))
            if idx < len(sorted_points):
                print(f"   {p:2d}th percentile: {sorted_points[idx]:>12,}")
    
    print(f"\n🔬 REVERSE ENGINEERED ALGORITHM HYPOTHESIS:")
    print("=" * 80)
    print("Based on the data patterns observed:")
    print("1. yapScaledPoints = Cumulative lifetime points with scaling")
    print("2. yap24HScaledPoints = Recent 24-hour activity with scaling")
    print("3. Scaling factor appears to be applied consistently") 
    print("4. Time-based accumulation suggests rolling window calculations")
    print("5. Point ranges suggest tier-based multiplier system")

if __name__ == "__main__":
    analyze_yaps_attestations()