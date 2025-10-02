#!/usr/bin/env python3
"""
Query YAPS schemas #525 and #546 from EAS GraphQL API
"""

import requests
import json

# Base network GraphQL endpoint
GRAPHQL_URL = "https://base.easscan.org/graphql"

def query_graphql(query, variables=None):
    """Execute GraphQL query"""
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(GRAPHQL_URL, json=payload, headers=headers)
    return response.json()

def find_schemas_by_range():
    """Find schemas by looking at all schemas and filtering by creation order"""
    query = """
    query GetAllSchemas {
      schemata(orderBy: [{ id: asc }], take: 1000) {
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
        print(f"Found {len(schemas)} schemas")
        
        # Look for schemas around position 525 and 546
        target_positions = [525, 546]
        for target in target_positions:
            if target < len(schemas):
                schema = schemas[target-1]  # Array is 0-indexed
                print(f"\n=== Schema #{target} ===")
                print(f"UID: {schema['id']}")
                print(f"Schema: {schema['schema']}")
                print(f"Creator: {schema['creator']}")
                print(f"Time: {schema['time']}")
                print(f"TxID: {schema['txid']}")
    else:
        print("Error querying schemas:", result)

def query_attestations_by_schema_uid(schema_uid):
    """Get attestations for a specific schema UID"""
    query = """
    query GetAttestationsBySchema($schemaId: String!) {
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
        print(f"\n=== Found {len(attestations)} attestations for schema {schema_uid} ===")
        
        for i, attestation in enumerate(attestations[:3]):  # Show first 3
            print(f"\nAttestation #{i+1}:")
            print(f"  ID: {attestation['id']}")
            print(f"  Attester: {attestation['attester']}")
            print(f"  Recipient: {attestation['recipient']}")
            print(f"  Time: {attestation['timeCreated']}")
            print(f"  Revoked: {attestation['revoked']}")
            
            if attestation['decodedDataJson']:
                try:
                    decoded = json.loads(attestation['decodedDataJson'])
                    print(f"  Decoded Data: {json.dumps(decoded, indent=4)}")
                except json.JSONDecodeError:
                    print(f"  Decoded Data: {attestation['decodedDataJson']}")
    else:
        print(f"Error querying attestations for {schema_uid}:", result)

def search_yaps_related():
    """Search for YAPS-related schemas by looking at schema descriptions"""
    query = """
    query SearchSchemas {
      schemata(take: 800) {
        id
        schema
        creator
        index
      }
    }
    """
    
    result = query_graphql(query)
    if 'data' in result and 'schemata' in result['data']:
        schemas = result['data']['schemata']
        
        # Look for potential YAPS schemas by checking schema content
        yaps_candidates = []
        for i, schema in enumerate(schemas):
            schema_text = schema['schema'].lower()
            # Look for score, yaps, lifetime, monthly keywords
            if any(keyword in schema_text for keyword in ['score', 'yaps', 'lifetime', 'monthly', 'point', 'rating']):
                yaps_candidates.append((i+1, schema))
                
        print(f"\n=== Found {len(yaps_candidates)} potential YAPS-related schemas ===")
        for pos, schema in yaps_candidates:
            print(f"\nSchema #{pos} (estimated)")
            print(f"  UID: {schema['id']}")  
            print(f"  Schema: {schema['schema']}")
            print(f"  Creator: {schema['creator']}")

if __name__ == "__main__":
    print("=== Querying YAPS Schemas from EAS GraphQL ===")
    print("Endpoint:", GRAPHQL_URL)
    
    # Try multiple approaches
    print("\n1. Searching for YAPS-related schemas by content...")
    search_yaps_related()
    
    print("\n2. Looking at schemas by position...")
    find_schemas_by_range()
    
    # Found YAPS schemas - let's query their attestations
    yaps_schema_uids = [
        "0x2d5c948c6fb42412de88dc8fba09abed76f948136f3628b55b8a9560f288e701",  # Schema #155
        "0x2df5d9cbf7ed0cdc7ce5daa6e7aba03aa4e7f538aa515e5c56de053887938ddf",  # Schema #156  
        "0x30c23ae07a72d6c4cafbe3c7a24f6b85427b9dacde030366376c8f87d794a802"   # Schema #169
    ]
    
    print("\n3. Querying YAPS attestations for algorithm analysis...")
    for uid in yaps_schema_uids:
        query_attestations_by_schema_uid(uid)