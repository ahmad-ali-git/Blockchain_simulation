class LPCDefense:
    def __init__(self, max_consecutive=6):
        self.max_consecutive = max_consecutive
        self.is_enabled = False
        self.rejected_blocks_count = 0
        self.event_log = []

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False

    def check_consecutive_blocks(self, chain, miner_id):
        if len(chain) == 0:
            return 0
        count = 0
        for block in reversed(chain):
            if block.miner_id == miner_id:
                count += 1
            else:
                break
        return count

    def should_reject_block(self, chain, miner_id):
        if not self.is_enabled:
            return False

        consecutive = self.check_consecutive_blocks(chain, miner_id)
        if consecutive >= self.max_consecutive - 1:
            self.rejected_blocks_count += 1
            self.event_log.append(
                f"REJECTED: Block by {miner_id} (would be {consecutive + 1} consecutive)"
            )
            return True
        return False