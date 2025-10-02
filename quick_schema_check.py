#!/usr/bin/env python3
import requests
import json

GRAPHQL_URL = "https://base.easscan.org/graphql"
SCHEMA_UID = "0xcb66276cf243e78fad68dd5e633f7bb56814b49ac9a91256615340591577a0e8"

query = """
query GetAttestations($schemaId: String!) {
  attestations(
    where: { schemaId: { equals: $schemaId } },
    take: 50,
    orderBy: [{ timeCreated: desc }]
  ) {
    decodedDataJson
    timeCreated
  }
}
"""

result = requests.post(GRAPHQL_URL, json={"query": query, "variables": {"schemaId": SCHEMA_UID}}).json()

if 'data' in result and 'attestations' in result['data']:
    attestations = result['data']['attestations']
    print(f"✅ Found {len(attestations)} attestations\n")
    
    points_data = []
    
    for att in attestations[:10]:
        if att['decodedDataJson']:
            try:
                decoded = json.loads(att['decodedDataJson'])
                data = {}
                for field in decoded:
                    name = field['name']
                    value = field['value']['value'] if 'value' in field['value'] else field['value']
                    data[name] = value
                
                points_data.append(data)
                print(f"🔸 {data.get('twitterUsername', 'Unknown')}")
                print(f"   Twitter ID: {data.get('twitterUserId', 'N/A')}")
                print(f"   YAP Points: {int(data.get('yapPoints', 0)):,}")
                print(f"   Timestamp: {data.get('timestamp', 'N/A')}\n")
            except:
                pass
    
    if points_data:
        all_points = [int(d.get('yapPoints', 0)) for d in points_data if d.get('yapPoints')]
        print(f"\n📊 STATISTICS:")
        print(f"   Min Points: {min(all_points):,}")
        print(f"   Max Points: {max(all_points):,}")
        print(f"   Avg Points: {int(sum(all_points)/len(all_points)):,}")
