import argparse
import base64
import json
import requests
import hashlib

from .merkle_proof import verify_inclusion, verify_consistency
from .util import extract_public_key, verify_artifact_signature

REKOR_API = "https://rekor.sigstore.dev"


def fetch_entry(identifier):
    if identifier.isdigit():
        url = f"{REKOR_API}/api/v1/log/entries?logIndex={identifier}"
    else:
        url = f"{REKOR_API}/api/v1/log/entries/{identifier}"
    response = requests.get(url)
    response.raise_for_status()
    return (
        list(response.json().values())[0] if identifier.isdigit() else response.json()
    )


def decode_body(entry):
    raw_body = base64.b64decode(entry["body"])
    body_json = json.loads(raw_body.decode("utf-8"))
    return body_json, raw_body


def extract_signature_and_cert(body_json):
    try:
        sig_b64 = body_json["spec"]["signature"]["content"]
        cert_b64 = body_json["spec"]["signature"]["publicKey"]["content"]
    except KeyError:
        sig_b64 = body_json["spec"]["data"]["signature"]["content"]
        cert_b64 = body_json["spec"]["data"]["signature"]["publicKey"]["content"]
    signature = base64.b64decode(sig_b64)
    cert = base64.b64decode(cert_b64)
    return signature, cert


def fetch_latest_checkpoint():
    url = f"{REKOR_API}/api/v1/log"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def fetch_consistency_proof(tree_id, tree_size):
    url = f"{REKOR_API}/api/v1/log/proof?treeID={tree_id}&treeSize={tree_size}"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def run_inclusion_verification(identifier, artifact_path):
    entry = fetch_entry(identifier)
    body_json, raw_body = decode_body(entry)

    signature, cert = extract_signature_and_cert(body_json)
    public_key = extract_public_key(cert)

    with open(artifact_path, "rb") as f:
        artifact_bytes = f.read()
    verify_artifact_signature(public_key, signature, artifact_bytes)
    print("Signature is valid.")

    proof = entry["verification"]["inclusionProof"]
    root_hash = bytes.fromhex(proof["rootHash"])
    hashes = [bytes.fromhex(h) for h in proof["hashes"]]
    index = entry["logIndex"]
    tree_size = proof["treeSize"]

    entry_hash = hashlib.sha256(raw_body).digest()
    leaf_hash = hashlib.sha256(b"\x00" + entry_hash).digest()

    verify_inclusion(leaf_hash, index, root_hash, tree_size, hashes)
    print("Offline root hash calculation for inclusion verified.")


def run_consistency_verification(tree_id, tree_size, root_hash_hex):
    old_root = bytes.fromhex(root_hash_hex)
    latest = fetch_latest_checkpoint()
    new_root = bytes.fromhex(latest["rootHash"])

    proof = fetch_consistency_proof(tree_id, tree_size)
    hashes = [bytes.fromhex(h) for h in proof["consistencyProof"]["hashes"]]

    verify_consistency(old_root, new_root, hashes)
    print("Consistency verification successful.")


def run_checkpoint_fetch():
    checkpoint = fetch_latest_checkpoint()

    if "inactiveShards" in checkpoint and checkpoint["inactiveShards"]:
        print("Inactive Shards:")
        for shard in checkpoint["inactiveShards"]:
            print(shard)  # Each shard is a signed checkpoint string
    else:
        print("Active Checkpoint:")
        print(
            json.dumps(
                {
                    "treeSize": checkpoint.get("treeSize"),
                    "rootHash": checkpoint.get("rootHash"),
                    "timestamp": checkpoint.get("signedTreeHead", {}).get("timestamp"),
                },
                indent=2,
            )
        )


def main():
    parser = argparse.ArgumentParser(description="Rekor log verifier")
    parser.add_argument("--inclusion", help="Log index or UUID for inclusion proof")
    parser.add_argument("--artifact", help="Path to artifact file")
    parser.add_argument(
        "--consistency",
        action="store_true",
        help="Run consistency verification",
    )
    parser.add_argument("--tree-id", help="Previous checkpoint tree ID")
    parser.add_argument("--tree-size", type=int, help="Previous checkpoint tree size")
    parser.add_argument("--root-hash", help="Previous checkpoint root hash (hex)")
    parser.add_argument(
        "-c",
        "--checkpoint",
        action="store_true",
        help="Fetch latest checkpoint",
    )
    args = parser.parse_args()

    if args.inclusion and args.artifact:
        run_inclusion_verification(args.inclusion, args.artifact)
    elif args.consistency:
        if not args.tree_id or not args.tree_size or not args.root_hash:
            print(
                "Error: --tree-id, --tree-size, and --root-hash are required for consistency check."
            )
        else:
            run_consistency_verification(args.tree_id, args.tree_size, args.root_hash)
    elif args.checkpoint:
        run_checkpoint_fetch()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
