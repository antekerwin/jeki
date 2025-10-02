#!/usr/bin/env python3
"""
Check YAPS score for specific Twitter user from on-chain attestations
"""

import requests
import json

GRAPHQL_URL = "https://base.easscan.org/graphql"
TWITTER_USER_ID = "1422186185196113922"

def query_graphql(query, variables=None):
    """Execute GraphQL query"""
    payload = {"query": query, "variables": variables or {}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    return response.json()

def check_yaps_score():
    """Check YAPS score for user"""
    
    print(f"🔍 Checking YAPS score for Twitter ID: {TWITTER_USER_ID}")
    print(f"Username: @dgkorojr (KoroJR)")
    print("="*80)
    
    # Schema UIDs we need to check
    schemas = {
        "Schema #517 (Scaled Points)": "0x30c23ae07a72d6c4cafbe3c7a24f6b85427b9dacde030366376c8f87d794a802",
        "Schema #546 (Monthly Points)": "0x69a0626ec645ae8c2429f9190782f396ce64e5ce0a82096d09891b9515e67fa7"
    }
    
    for schema_name, schema_uid in schemas.items():
        print(f"\n📊 {schema_name}")
        print("-"*80)
        
        # Query attestations for this schema
        query = """
        query GetUserAttestations($schemaId: String!) {
          attestations(
            where: { schemaId: { equals: $schemaId } },
            take: 1000,
            orderBy: [{ timeCreated: desc }]
          ) {
            id
            data
            decodedDataJson
            timeCreated
            revoked
          }
        }
        """
        
        variables = {"schemaId": schema_uid}
        result = query_graphql(query, variables)
        
        if 'data' not in result or 'attestations' not in result['data']:
            print(f"❌ Error querying: {result}")
            continue
        
        attestations = result['data']['attestations']
        
        # Find attestations for this Twitter user
        user_attestations = []
        
        for att in attestations:
            if not att['decodedDataJson']:
                continue
                
            try:
                decoded = json.loads(att['decodedDataJson'])
                
                # Check if this attestation is for our user
                for field in decoded:
                    if 'twitterUserId' in field['name']:
                        twitter_id = str(field['value']['value'] if 'value' in field['value'] else field['value'])
                        
                        if twitter_id == TWITTER_USER_ID:
                            user_attestations.append({
                                'decoded': decoded,
                                'timestamp': att['timeCreated'],
                                'revoked': att['revoked']
                            })
                            break
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not user_attestations:
            print(f"❌ No attestations found for this user in {schema_name}")
            continue
        
        print(f"✅ Found {len(user_attestations)} attestation(s)")
        
        # Display the most recent attestation
        latest = user_attestations[0]
        print(f"\n📅 Latest Attestation:")
        print(f"   Timestamp: {latest['timestamp']}")
        print(f"   Revoked: {latest['revoked']}")
        print(f"\n   Data:")
        
        for field in latest['decoded']:
            name = field['name']
            value = field['value']['value'] if 'value' in field['value'] else field['value']
            field_type = field['type']
            
            # Format display
            if 'Points' in name or 'points' in name:
                if str(value).isdigit():
                    print(f"   • {name}: {int(value):,}")
                else:
                    print(f"   • {name}: {value}")
            else:
                print(f"   • {name}: {value}")
    
    print("\n" + "="*80)
    print("✨ YAPS Score Check Complete!")

if __name__ == "__main__":
    check_yaps_score()
