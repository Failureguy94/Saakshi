"""Unit tests for append-only custody chain, anchors, and tamper detection."""

import copy

import pytest

from app.modules.custody.anchor.fabric import FabricAnchor
from app.modules.custody.anchor.local_ledger import LocalLedgerAnchor
from app.modules.custody.chain import (
    GENESIS_PREVIOUS_HASH,
    CustodyLog,
    verify_chain,
)


def test_custody_genesis_and_chaining() -> None:
    log = CustodyLog()
    assert len(log.records) == 0

    r0 = log.append(
        actor="OFFICER-42",
        action="ACQUISITION",
        evidence_id="EVID-001",
        evidence_hash="aa" * 32,
        details={"intake": "SATA direct"},
    )
    assert r0.index == 0
    assert r0.previous_hash == GENESIS_PREVIOUS_HASH
    assert len(r0.entry_hash) == 64

    r1 = log.append(
        actor="WORKER-CARVER",
        action="ANNEXB_CARVE",
        evidence_id="EVID-001",
        evidence_hash="bb" * 32,
        details={"nal_count": 420},
    )
    assert r1.index == 1
    assert r1.previous_hash == r0.entry_hash

    is_valid, err = log.verify()
    assert is_valid is True
    assert err is None


def test_custody_tamper_detection() -> None:
    log = CustodyLog()
    log.append(actor="OFFICER-1", action="ACQUIRE", evidence_id="E1", evidence_hash="11" * 32)
    log.append(actor="OFFICER-1", action="PARSE", evidence_id="E1", evidence_hash="22" * 32)
    log.append(actor="OFFICER-2", action="EXPORT", evidence_id="E1", evidence_hash="33" * 32)

    # 1. Mutate record payload
    tampered_records = copy.deepcopy(log.records)
    tampered_records[1].actor = "MALICIOUS_ACTOR"

    valid, err = verify_chain(tampered_records)
    assert valid is False
    assert "Tampering detected at block 1" in str(err)

    # 2. Mutate previous_hash link
    tampered_records2 = copy.deepcopy(log.records)
    tampered_records2[2].previous_hash = "00" * 32

    valid2, err2 = verify_chain(tampered_records2)
    assert valid2 is False
    assert "Broken hash link at block 2" in str(err2)


def test_local_ledger_anchor() -> None:
    anchor = LocalLedgerAnchor()
    root = "fe" * 32
    receipt = anchor.anchor(root, {"case_number": "FIR-001"})

    assert len(receipt) == 64
    assert anchor.verify_anchor(receipt, root) is True
    assert anchor.verify_anchor(receipt, "00" * 32) is False
    assert anchor.verify_anchor("nonexistent_id", root) is False


def test_fabric_anchor_stub_raises() -> None:
    anchor = FabricAnchor()
    with pytest.raises(NotImplementedError) as exc_info:
        anchor.anchor("ab" * 32)
    assert "planned: Hyperledger Fabric" in str(exc_info.value)
