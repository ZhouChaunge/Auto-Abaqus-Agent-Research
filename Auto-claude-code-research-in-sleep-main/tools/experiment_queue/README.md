# experiment-queue Tools

Scheduler and manifest builder for `/experiment-queue` skill.

## Files

- `build_manifest.py` — Expands grid spec (YAML/JSON) into explicit job manifest
- `queue_manager.py` — Scheduler that runs on the remote host; polls, launches, retries, cleans

## Install on Remote

The skill auto-installs these on the SSH host under `~/.aris_queue/`:

```bash
ssh <server> 'mkdir -p ~/.aris_queue'
scp queue_manager.py build_manifest.py <server>:~/.aris_queue/
```

## Example

### 1. Write grid spec (on local or remote)

`grid_spec.yaml`:
```yaml
project: dllm_distill
cwd: /home/rfyang/rfyang_code/dllm_experiments_torch
conda: dllm
gpus: [0, 1, 2, 3, 4, 5, 6, 7]
max_parallel: 8
oom_retry: {delay: 120, max_attempts: 3}

phases:
  - name: distill
    grid:
      N: [64, 128, 256]
      seed: [42, 200, 201]
      n_train_subset: [50000, 150000, 500000, 652000]
    template:
      id: "s${seed}_N${N}_n${n_train_subset}"
      cmd: >
        python run_pc_distill_exp.py --backbone softmax --lam 0.5
        --t_max_distill 0 --K 500 --L 96 --W 16 --n_steps 30000
        --batch_size 128 --lr 1e-4 --seed ${seed} --subset_seed 2024
        --n_hidden ${N} --n_train_subset ${n_train_subset}
      expected_output: "figures/pcdistill_sw_N${N}_*_seed${seed}.json"
```

### 2. Build manifest

```bash
python3 build_manifest.py --config grid_spec.yaml --output manifest.json
```

### 3. Launch scheduler

```bash
ssh <server> 'nohup python3 ~/.aris_queue/queue_manager.py \
    --manifest /tmp/manifest.json \
    --state /tmp/queue_state.json \
    --log-dir /home/rfyang/rfyang_code/dllm_experiments_torch \
    > /tmp/queue_mgr.log 2>&1 &'
```

### 4. Monitor

```bash
ssh <server> 'jq ".jobs | group_by(.status) | map({(.[0].status): length}) | add" /tmp/queue_state.json'
```

Returns:
```json
{"completed": 30, "running": 6, "pending": 0}
```

## State Machine

```
pending → running → completed
                  ↘ failed_oom → pending (after delay, up to max_attempts)
                               ↘ stuck (after max_attempts)
                  ↘ failed_other → stuck
```

## Dependencies

- Python 3.8+
- `nvidia-smi` on remote
- `screen` on remote
- Optional: `pyyaml` (only if using YAML grid specs)

## Invariants

- **No GPU overlap**: scheduler only assigns GPU with `memory.used < 500 MiB`
- **State is source of truth**: `queue_state.json` is written atomically every step
- **Idempotent**: safe to kill and restart the scheduler; picks up from state
- **Output-based completion**: completion is verified by `expected_output` existing, not just by screen/process exit

## Not Yet Supported

- Mid-run GPU reshuffling (if GPU becomes unavailable mid-job)
- Automatic GPU-per-job count (all jobs assumed single-GPU)
- Distributed multi-node queues
- Auto-sync results back to local
