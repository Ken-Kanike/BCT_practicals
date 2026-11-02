#!/usr/bin/env bash
set -eo pipefail

NET="${FABRIC_SAMPLES:-$HOME/fabric-samples}/test-network"
CHANNEL="mychannel"
CC="asset-transfer"
ORDERER="localhost:7050"
PEER1="localhost:7051"
PEER2="localhost:9051"

cd "$NET"
export PATH="${PWD}/../bin:${PATH}"
export FABRIC_CFG_PATH="${PWD}/../config"
# shellcheck disable=SC1091
source scripts/envVar.sh
setGlobals 1

invoke() {
  peer chaincode invoke \
    -o "$ORDERER" --ordererTLSHostnameOverride orderer.example.com \
    --tls --cafile "$ORDERER_CA" \
    -C "$CHANNEL" -n "$CC" \
    --peerAddresses "$PEER1" --tlsRootCertFiles "$PEER0_ORG1_CA" \
    --peerAddresses "$PEER2" --tlsRootCertFiles "$PEER0_ORG2_CA" \
    "$@" --waitForEvent
}

query() {
  peer chaincode query -C "$CHANNEL" -n "$CC" "$@"
}

echo "=== COMMITTED CHAINCODE DEFINITION ==="
peer lifecycle chaincode querycommitted --channelID "$CHANNEL" --name "$CC"

echo
echo "=== INIT LEDGER (asset1, asset2, asset3) ==="
invoke -c '{"function":"InitLedger","Args":[]}'

echo
echo "=== GET ALL ASSETS ==="
query -c '{"function":"GetAllAssets","Args":[]}'

echo
echo "=== CREATE ASSET asset4 (owner4, value 400) ==="
invoke -c '{"function":"CreateAsset","Args":["asset4","owner4","400"]}'

echo
echo "=== READ ASSET asset4 ==="
query -c '{"function":"ReadAsset","Args":["asset4"]}'

echo
echo "=== TRANSFER ASSET asset4 -> owner5 ==="
invoke -c '{"function":"TransferAsset","Args":["asset4","owner5"]}'

echo
echo "=== READ ASSET asset4 AFTER TRANSFER ==="
query -c '{"function":"ReadAsset","Args":["asset4"]}'

echo
echo "=== ASSET EXISTS asset4 ==="
query -c '{"function":"AssetExists","Args":["asset4"]}'

echo
echo "=== DELETE ASSET asset4 ==="
invoke -c '{"function":"DeleteAsset","Args":["asset4"]}'

echo
echo "=== ASSET EXISTS asset4 AFTER DELETE ==="
query -c '{"function":"AssetExists","Args":["asset4"]}'

echo
echo "=== READ DELETED ASSET (expected error) ==="
if query -c '{"function":"ReadAsset","Args":["asset4"]}'; then
  echo "ERROR: deleted asset was still readable"
  exit 1
else
  echo "ReadAsset rejected the deleted asset as expected."
fi

echo
echo "=== FINAL LEDGER STATE ==="
query -c '{"function":"GetAllAssets","Args":[]}'
