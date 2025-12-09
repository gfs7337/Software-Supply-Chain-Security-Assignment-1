import hashlib


def verify_inclusion(leaf_hash, index, root_hash, tree_size, hashes):
    computed_hash = leaf_hash
    for i, h in enumerate(hashes):
        if ((index >> i) & 1) == 0:
            computed_hash = hashlib.sha256(computed_hash + h).digest()
        else:
            computed_hash = hashlib.sha256(h + computed_hash).digest()
    if computed_hash != root_hash:
        raise ValueError("Merkle inclusion proof failed.")


def verify_consistency(old_root, new_root, hashes):
    computed = old_root
    for h in hashes:
        computed = hashlib.sha256(computed + h).digest()
    if computed != new_root:
        raise ValueError("Consistency proof failed.")
