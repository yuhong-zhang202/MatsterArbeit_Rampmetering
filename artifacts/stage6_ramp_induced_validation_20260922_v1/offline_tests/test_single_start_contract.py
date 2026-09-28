"""Pure in-memory reservation contract test; never starts a process."""
from dataclasses import dataclass

@dataclass
class Reservation:
    card_hash: str
    max_starts: int = 1
    retries: int = 0
    consumed: int = 0

    def reserve(self, presented_hash: str):
        if presented_hash != self.card_hash:
            raise ValueError("CARD_HASH_MISMATCH")
        if self.consumed >= self.max_starts:
            raise RuntimeError("START_QUOTA_CONSUMED")
        self.consumed += 1
        return "RESERVED_ONCE"

def main():
    r = Reservation("card-sha")
    assert r.reserve("card-sha") == "RESERVED_ONCE"
    try:
        r.reserve("card-sha")
    except RuntimeError as e:
        assert str(e) == "START_QUOTA_CONSUMED"
    else:
        raise AssertionError("duplicate reservation accepted")
    try:
        Reservation("card-sha").reserve("old-card-sha")
    except ValueError as e:
        assert str(e) == "CARD_HASH_MISMATCH"
    else:
        raise AssertionError("hash mismatch accepted")
    print({"status":"PASS", "simulator_process_started":False, "duplicate_blocked":True, "hash_mismatch_blocked":True})

if __name__ == "__main__":
    main()
