#!/usr/bin/env python3
"""
Get YAPS attestations from specific schemas to analyze algorithm parameters
"""

import requests
import json

GRAPHQL_URL = "https://base.easscan.org/graphql"

def query_graphql(query, variables=None):
    """Execute GraphQL query"""
    payload = {"query": query, "variables": variables or {}}
    headers = {"Content-Type": "application/json"}
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    return response.json()

def analyze_yaps_attestations():
    """Get and analyze YAPS attestations from known schemas"""
    
    # YAPS schemas we discovered
    yaps_schemas = {
        "Schema #155": {
            "uid": "0x2d5c948c6fb42412de88dc8fba09abed76f948136f3628b55b8a9560f288e701",
            "fields": "uint64 twitterUserId, string twitterUsername, uint64 yapPoints, uint64 timestamp"
        },
        "Schema #156": {
            "uid": "0x2df5d9cbf7ed0cdc7ce5daa6e7aba03aa4e7f538aa515e5c56de053887938ddf", 
            "fields": "uint64 twitterUserId, string twitterUsername, uint64 yapPoints, uint64 timestamp"
        },
        "Schema #169": {
            "uid": "0x30c23ae07a72d6c4cafbe3c7a24f6b85427b9dacde030366376c8f87d794a802",
            "fields": "uint64 twitterUserId, uint64 yapScaledPoints, uint64 yap24HScaledPoints, uint64 timestamp"
        }
    }
    
    for schema_name, schema_info in yaps_schemas.items():
        print(f"\n{'='*60}")
        print(f"Analyzing {schema_name}")  
        print(f"UID: {schema_info['uid']}")
        print(f"Fields: {schema_info['fields']}")
        print(f"{'='*60}")
        
        # Query attestations for this schema
        query = """
        query GetYAPSAttestations($schemaId: String!) {
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
        
        variables = {"schemaId": schema_info["uid"]}
        result = query_graphql(query, variables)
        
        if 'data' in result and 'attestations' in result['data']:
            attestations = result['data']['attestations']
            print(f"Found {len(attestations)} attestations\n")
            
            if attestations:
                # Analyze first few attestations for parameters
                for i, att in enumerate(attestations[:5]):
                    print(f"--- Attestation {i+1} ---")
                    print(f"Time: {att['timeCreated']}")
                    print(f"Attester: {att['attester']}")
                    print(f"Recipient: {att['recipient']}")
                    
                    # Decode and analyze the data
                    if att['decodedDataJson']:
                        try:
                            decoded = json.loads(att['decodedDataJson'])
                            print("Decoded Parameters:")
                            
                            for field in decoded:
                                field_name = field['name']
                                field_value = field['value']['value'] if 'value' in field['value'] else field['value']
                                field_type = field['type']
                                print(f"  {field_name} ({field_type}): {field_value}")
                                
                                # Extract specific YAPS parameters
                                if 'yapPoints' in field_name or 'yapScaled' in field_name:
                                    print(f"    -> YAP SCORE FOUND: {field_value}")
                                elif 'twitter' in field_name.lower():
                                    print(f"    -> TWITTER ID: {field_value}")
                                    
                        except json.JSONDecodeError as e:
                            print(f"  Error decoding JSON: {e}")
                            print(f"  Raw decodedDataJson: {att['decodedDataJson']}")
                    
                    print()
                    
                # Extract patterns and parameters
                print("\n--- ALGORITHM PARAMETER ANALYSIS ---")
                
                if schema_name == "Schema #169" and attestations:
                    # This schema has scaled points and 24h points
                    print("🔍 Advanced scoring schema detected!")
                    print("Fields: yapScaledPoints + yap24HScaledPoints")
                    
                    try:
                        sample = json.loads(attestations[0]['decodedDataJson'])
                        yap_scaled = None
                        yap_24h = None
                        
                        for field in sample:
                            if 'yapScaledPoints' in field['name']:
                                yap_scaled = field['value']['value'] if 'value' in field['value'] else field['value']
                            elif 'yap24HScaledPoints' in field['name']:
                                yap_24h = field['value']['value'] if 'value' in field['value'] else field['value']
                        
                        if yap_scaled and yap_24h:
                            ratio = float(yap_scaled) / float(yap_24h) if float(yap_24h) > 0 else 0
                            print(f"Total Scaled: {yap_scaled}")
                            print(f"24H Scaled: {yap_24h}")
                            print(f"Ratio (Total/24H): {ratio:.2f}")
                            print(f"Possible multiplier detected: {ratio}")
                            
                    except Exception as e:
                        print(f"Analysis error: {e}")
                        
            else:
                print("No attestations found for this schema")
        else:
            print(f"Error querying attestations: {result}")

if __name__ == "__main__":
    print("🚀 YAPS Algorithm Parameter Analysis")
    print("Analyzing attestations from discovered YAPS schemas...\n")
    analyze_yaps_attestations()