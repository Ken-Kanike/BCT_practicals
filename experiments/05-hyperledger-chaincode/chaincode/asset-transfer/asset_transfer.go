package main

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// SmartContract provides functions for managing an Asset on the ledger.
type SmartContract struct {
	contractapi.Contract
}

// Asset describes a basic asset with an ID, owner and value.
type Asset struct {
	ID     string `json:"id"`
	Owner  string `json:"owner"`
	Value  int    `json:"value"`
	Status string `json:"status"`
}

// CreateAsset stores a new asset in the world state.
func (s *SmartContract) CreateAsset(ctx contractapi.TransactionContextInterface, id string, owner string, value int) error {
	if strings.TrimSpace(id) == "" {
		return fmt.Errorf("asset id must not be empty")
	}
	if strings.TrimSpace(owner) == "" {
		return fmt.Errorf("asset owner must not be empty")
	}
	if value <= 0 {
		return fmt.Errorf("asset value must be greater than zero")
	}

	exists, err := s.AssetExists(ctx, id)
	if err != nil {
		return err
	}
	if exists {
		return fmt.Errorf("asset %s already exists", id)
	}

	asset := Asset{ID: id, Owner: owner, Value: value, Status: "ACTIVE"}
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	if err := ctx.GetStub().PutState(id, assetJSON); err != nil {
		return fmt.Errorf("failed to put asset %s: %w", id, err)
	}

	return ctx.GetStub().SetEvent("AssetCreated", assetJSON)
}

// ReadAsset returns the asset stored under the given ID.
func (s *SmartContract) ReadAsset(ctx contractapi.TransactionContextInterface, id string) (*Asset, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return nil, fmt.Errorf("failed to read asset %s: %w", id, err)
	}
	if assetJSON == nil {
		return nil, fmt.Errorf("asset %s does not exist", id)
	}

	var asset Asset
	if err := json.Unmarshal(assetJSON, &asset); err != nil {
		return nil, err
	}
	return &asset, nil
}

// TransferAsset changes the owner of an existing asset.
func (s *SmartContract) TransferAsset(ctx contractapi.TransactionContextInterface, id string, newOwner string) error {
	if strings.TrimSpace(newOwner) == "" {
		return fmt.Errorf("new owner must not be empty")
	}

	asset, err := s.ReadAsset(ctx, id)
	if err != nil {
		return err
	}
	if asset.Status != "ACTIVE" {
		return fmt.Errorf("asset %s is not active", id)
	}

	previousOwner := asset.Owner
	asset.Owner = newOwner
	assetJSON, err := json.Marshal(asset)
	if err != nil {
		return err
	}

	if err := ctx.GetStub().PutState(id, assetJSON); err != nil {
		return fmt.Errorf("failed to update asset %s: %w", id, err)
	}

	eventPayload, err := json.Marshal(map[string]string{
		"assetId":       id,
		"previousOwner": previousOwner,
		"newOwner":      newOwner,
	})
	if err != nil {
		return err
	}
	return ctx.GetStub().SetEvent("AssetTransferred", eventPayload)
}

// DeleteAsset removes an asset from the world state.
func (s *SmartContract) DeleteAsset(ctx contractapi.TransactionContextInterface, id string) error {
	exists, err := s.AssetExists(ctx, id)
	if err != nil {
		return err
	}
	if !exists {
		return fmt.Errorf("asset %s does not exist", id)
	}
	return ctx.GetStub().DelState(id)
}

// AssetExists reports whether an asset exists in the world state.
func (s *SmartContract) AssetExists(ctx contractapi.TransactionContextInterface, id string) (bool, error) {
	assetJSON, err := ctx.GetStub().GetState(id)
	if err != nil {
		return false, fmt.Errorf("failed to read asset %s: %w", id, err)
	}
	return assetJSON != nil, nil
}

// GetAllAssets returns every asset in the world state.
func (s *SmartContract) GetAllAssets(ctx contractapi.TransactionContextInterface) ([]*Asset, error) {
	iterator, err := ctx.GetStub().GetStateByRange("", "")
	if err != nil {
		return nil, err
	}
	defer iterator.Close()

	assets := make([]*Asset, 0)
	for iterator.HasNext() {
		response, err := iterator.Next()
		if err != nil {
			return nil, err
		}

		var asset Asset
		if err := json.Unmarshal(response.Value, &asset); err != nil {
			return nil, err
		}
		assets = append(assets, &asset)
	}
	return assets, nil
}

// InitLedger seeds the ledger with sample assets.
func (s *SmartContract) InitLedger(ctx contractapi.TransactionContextInterface) error {
	assets := []Asset{
		{ID: "asset1", Owner: "owner1", Value: 100, Status: "ACTIVE"},
		{ID: "asset2", Owner: "owner2", Value: 250, Status: "ACTIVE"},
		{ID: "asset3", Owner: "owner3", Value: 500, Status: "ACTIVE"},
	}

	for _, asset := range assets {
		assetJSON, err := json.Marshal(asset)
		if err != nil {
			return err
		}
		if err := ctx.GetStub().PutState(asset.ID, assetJSON); err != nil {
			return err
		}
	}
	return nil
}

func main() {
	chaincode, err := contractapi.NewChaincode(&SmartContract{})
	if err != nil {
		fmt.Printf("Error creating asset-transfer chaincode: %s", err.Error())
		return
	}

	if err := chaincode.Start(); err != nil {
		fmt.Printf("Error starting asset-transfer chaincode: %s", err.Error())
	}
}
