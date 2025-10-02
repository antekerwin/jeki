#!/usr/bin/env python3
"""
Find YAPS advanced schemas (517-520) with yap24HScaledPoints and yapScaledPoints
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

def find_schemas_by_position():
    """Find schemas 517-520 by querying all schemas and finding by position"""
    query = """
    query GetSchemas {
      schemata(orderBy: [{ id: asc }], take: 600) {
        id
        schema
        creator
        txid
        time
        index
      }
    }
    """
    
    result = query_graphql(query)
    if 'data' in result and 'schemata' in result['data']:
        schemas = result['data']['schemata']
        print(f"Found {len(schemas)} total schemas")
        
        # Check schemas 517-520
        target_positions = [517, 518, 519, 520]
        found_schemas = {}
        
        for target in target_positions:
            if target <= len(schemas):
                schema = schemas[target-1]  # Array is 0-indexed
                found_schemas[target] = schema
                
                print(f"\n{'='*60}")
                print(f"SCHEMA #{target}")
                print(f"{'='*60}")
                print(f"UID: {schema['id']}")
                print(f"Schema: {schema['schema']}")
                print(f"Creator: {schema['creator']}")
                print(f"Time: {schema['time']}")
                print(f"TxID: {schema['txid']}")
                
                # Check if it contains YAPS-related fields
                schema_lower = schema['schema'].lower()
                if any(keyword in schema_lower for keyword in ['yap', 'scaled', '24h']):
                    print("🎯 POTENTIAL YAPS SCHEMA DETECTED!")
                    
                    if 'yap24hscaled' in schema_lower:
                        print("✅ Contains yap24HScaledPoints")
                    if 'yapscaled' in schema_lower:
                        print("✅ Contains yapScaledPoints")
        
        return found_schemas
    else:
        print(f"Error querying schemas: {result}")
        return {}

def analyze_advanced_yaps_schema(schema_uid, schema_structure):
    """Analyze attestations from advanced YAPS schema"""
    print(f"\n🔍 ANALYZING ATTESTATIONS FROM {schema_uid}")
    print(f"Schema structure: {schema_structure}")
    
    query = """
    query GetAttestations($schemaId: String!) {
      attestations(
        where: { schemaId: { equals: $schemaId } },
        take: 10,
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
    
    variables = {"schemaId": schema_uid}
    result = query_graphql(query, variables)
    
    if 'data' in result and 'attestations' in result['data']:
        attestations = result['data']['attestations']
        print(f"Found {len(attestations)} attestations")
        
        if attestations:
            print("\n📊 SAMPLE ATTESTATIONS FOR ALGORITHM ANALYSIS:")
            
            for i, att in enumerate(attestations[:3]):
                print(f"\n--- Attestation {i+1} ---")
                print(f"Time: {att['timeCreated']}")
                print(f"Attester: {att['attester']}")
                
                if att['decodedDataJson']:
                    try:
                        decoded = json.loads(att['decodedDataJson'])
                        
                        yap_scaled = None
                        yap_24h = None
                        twitter_id = None
                        
                        print("Decoded fields:")
                        for field in decoded:
                            name = field['name']
                            value = field['value']['value'] if 'value' in field['value'] else field['value']
                            field_type = field['type']
                            
                            print(f"  {name} ({field_type}): {value}")
                            
                            # Extract key values for analysis
                            if 'yapScaledPoints' in name and 'yap24H' not in name:
                                yap_scaled = int(value) if str(value).isdigit() else value
                            elif 'yap24HScaledPoints' in name:
                                yap_24h = int(value) if str(value).isdigit() else value
                            elif 'twitterUserId' in name:
                                twitter_id = value
                        
                        # Calculate ratios and patterns
                        if yap_scaled and yap_24h and isinstance(yap_scaled, int) and isinstance(yap_24h, int):
                            if yap_24h > 0:
                                ratio = yap_scaled / yap_24h
                                print(f"\n🧮 ALGORITHM ANALYSIS:")
                                print(f"  Total Scaled Points: {yap_scaled:,}")
                                print(f"  24H Scaled Points: {yap_24h:,}")
                                print(f"  Ratio (Total/24H): {ratio:.2f}")
                                
                                # Detect potential multipliers
                                if ratio > 100:
                                    estimated_days = ratio / 24 if ratio > 24 else ratio
                                    print(f"  Estimated active days: {estimated_days:.1f}")
                                
                                # Look for scaling patterns
                                print(f"  Potential scaling factor detected")
                        
                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
        else:
            print("No attestations found")
    else:
        print(f"Error querying attestations: {result}")

if __name__ == "__main__":
    print("🚀 SEARCHING FOR ADVANCED YAPS SCHEMAS (517-520)")
    print("Looking for yap24HScaledPoints and yapScaledPoints...")
    
    schemas = find_schemas_by_position()
    
    # Analyze any YAPS schemas found
    for pos, schema in schemas.items():
        schema_lower = schema['schema'].lower()
        if any(keyword in schema_lower for keyword in ['yap', 'scaled']):
            print(f"\n🎯 Found YAPS schema at position {pos}!")
            analyze_advanced_yaps_schema(schema['id'], schema['schema'])