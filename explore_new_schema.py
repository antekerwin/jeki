#!/usr/bin/env python3
"""
Explore new YAPS schema to find scoring parameters
"""

import requests
import json
from datetime import datetime

GRAPHQL_URL = "https://base.easscan.org/graphql"
SCHEMA_UID = "0xcb66276cf243e78fad68dd5e633f7bb56814b49ac9a91256615340591577a0e8"

def query_graphql(query, variables=None):
    """Execute GraphQL query"""
    payload = {"query": query, "variables": variables or {}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    return response.json()

def explore_schema():
    """Get schema details and structure"""
    
    print(f"🔍 Exploring Schema: {SCHEMA_UID}")
    print("="*100)
    
    # Get schema details
    query = """
    query GetSchema($schemaId: String!) {
      schema(where: { id: $schemaId }) {
        id
        schema
        creator
        resolver
        revocable
        index
        txid
        time
      }
    }
    """
    
    result = query_graphql(query, {"schemaId": SCHEMA_UID})
    
    if 'data' in result and 'schema' in result['data']:
        schema = result['data']['schema']
        print("\n📋 SCHEMA DETAILS:")
        print(f"   Creator: {schema['creator']}")
        print(f"   Created: {datetime.fromtimestamp(schema['time'])}")
        print(f"   Index: {schema['index']}")
        print(f"   Revocable: {schema['revocable']}")
        print(f"\n   Schema Structure: {schema['schema']}")
        print("-"*100)

def get_attestations():
    """Get recent attestations from this schema"""
    
    print("\n📊 RECENT ATTESTATIONS:")
    print("-"*100)
    
    query = """
    query GetAttestations($schemaId: String!) {
      attestations(
        where: { schemaId: { equals: $schemaId } },
        take: 20,
        orderBy: [{ timeCreated: desc }]
      ) {
        id
        attester
        recipient
        data
        decodedDataJson
        timeCreated
        revoked
      }
    }
    """
    
    result = query_graphql(query, {"schemaId": SCHEMA_UID})
    
    if 'data' not in result or 'attestations' not in result['data']:
        print(f"❌ Error: {result}")
        return
    
    attestations = result['data']['attestations']
    print(f"✅ Found {len(attestations)} recent attestations\n")
    
    # Analyze first few attestations
    for i, att in enumerate(attestations[:5], 1):
        print(f"\n🔹 Attestation #{i}:")
        print(f"   ID: {att['id'][:20]}...")
        print(f"   Time: {datetime.fromtimestamp(att['timeCreated'])}")
        print(f"   Recipient: {att['recipient']}")
        
        if att['decodedDataJson']:
            try:
                decoded = json.loads(att['decodedDataJson'])
                print(f"   Fields:")
                
                for field in decoded:
                    name = field['name']
                    value = field['value']['value'] if 'value' in field['value'] else field['value']
                    field_type = field['type']
                    
                    # Format based on type
                    if isinstance(value, (int, float)) and 'point' in name.lower():
                        print(f"      • {name} ({field_type}): {int(value):,}")
                    else:
                        print(f"      • {name} ({field_type}): {value}")
                        
            except Exception as e:
                print(f"   ⚠️  Decode error: {e}")

def analyze_scoring_patterns():
    """Analyze all attestations to find scoring patterns"""
    
    print("\n\n🎯 SCORING PATTERN ANALYSIS:")
    print("="*100)
    
    query = """
    query GetAllAttestations($schemaId: String!) {
      attestations(
        where: { schemaId: { equals: $schemaId } },
        take: 500,
        orderBy: [{ timeCreated: desc }]
      ) {
        decodedDataJson
        timeCreated
      }
    }
    """
    
    result = query_graphql(query, {"schemaId": SCHEMA_UID})
    
    if 'data' not in result or 'attestations' not in result['data']:
        print(f"❌ Error: {result}")
        return
    
    attestations = result['data']['attestations']
    
    # Collect all field names and their ranges
    field_stats = {}
    
    for att in attestations:
        if not att['decodedDataJson']:
            continue
            
        try:
            decoded = json.loads(att['decodedDataJson'])
            
            for field in decoded:
                name = field['name']
                value = field['value']['value'] if 'value' in field['value'] else field['value']
                
                if name not in field_stats:
                    field_stats[name] = {
                        'type': field['type'],
                        'values': [],
                        'min': None,
                        'max': None,
                        'avg': None
                    }
                
                # Collect numeric values
                if isinstance(value, (int, float)):
                    field_stats[name]['values'].append(value)
                elif isinstance(value, str) and value.isdigit():
                    field_stats[name]['values'].append(int(value))
                    
        except Exception:
            continue
    
    # Calculate statistics
    print("\n📈 FIELD STATISTICS:\n")
    
    for field_name, stats in field_stats.items():
        if stats['values']:
            values = stats['values']
            stats['min'] = min(values)
            stats['max'] = max(values)
            stats['avg'] = sum(values) / len(values)
            
            print(f"🔸 {field_name} ({stats['type']}):")
            print(f"   Samples: {len(values)}")
            print(f"   Range: {int(stats['min']):,} - {int(stats['max']):,}")
            print(f"   Average: {int(stats['avg']):,}")
            
            # Show distribution for point fields
            if 'point' in field_name.lower() or 'score' in field_name.lower():
                print(f"   Distribution: {sorted(set(values))[:10]}")
            print()

if __name__ == "__main__":
    explore_schema()
    get_attestations()
    analyze_scoring_patterns()
    
    print("\n" + "="*100)
    print("✨ Schema Analysis Complete!")
