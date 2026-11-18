**1. Hugging Face Authentication**

```text
Warning: You are sending unauthenticated requests to the HF Hub.
Please set a HF_TOKEN to enable higher rate limits and faster downloads.
```

Kokoro obtains its model and voice files from the Hugging Face Hub. When `HF_TOKEN` is absent, Hugging Face treats the request as anonymous.

What that means:

- Public Kokoro files can still be downloaded.
- Anonymous requests have lower rate limits.
- Initial downloads may be slower or temporarily throttled.
- A first run can fail if the anonymous limit is reached or the network is interrupted.
- Once downloaded, model files are normally cached locally, so later runs generally do not download everything again.

The cache is typically under:

```text
C:\Users\ricky\.cache\huggingface\hub
```

For the current test, no action is required. If automation frequently downloads models, use a read-only Hugging Face access token through an environment variable:

```powershell
$env:HF_TOKEN = 'your-read-only-token'
```

Do not place the token in source files, documentation, or Git. The better production behavior is to download/cache the model once under the scheduled account before enabling Task Scheduler.

---

**2. PyTorch/Kokoro Warnings**

These warnings originate inside Kokoro’s model dependencies, not from your chapter text or Drive queue.

### LSTM dropout

```text
dropout option adds dropout after all but last recurrent layer...
num_layers=1
```

PyTorch’s recurrent layers apply dropout between stacked layers. Kokoro initializes an LSTM with:

- `dropout=0.2`
- `num_layers=1`

Because there is only one recurrent layer, there is no intermediate layer where that dropout can be applied. PyTorch warns that the configured dropout is effectively unused.

Practical effect:

- It does not stop synthesis.
- It does not indicate damaged audio.
- It primarily concerns model training rather than normal inference.
- Fixing it would require an upstream Kokoro/model change, not a change to your chapter pipeline.

### `weight_norm` deprecation

```text
torch.nn.utils.weight_norm is deprecated
```

Kokoro or one of its model libraries calls an older PyTorch weight-normalization API. PyTorch still supports it, but recommends a newer API.

Practical effect:

- The old API still works in the installed PyTorch version.
- It does not affect the current narration result.
- A future PyTorch release might eventually remove it.
- The correct long-term fix is an updated Kokoro dependency, not locally rewriting installed package code.

### `torch.jit.script` deprecation

```text
torch.jit.script is deprecated
```

Kokoro uses PyTorch’s older TorchScript compilation mechanism. PyTorch now prefers `torch.compile` or `torch.export`.

Practical effect:

- TorchScript still works today.
- The warning does not mean synthesis failed.
- Future Kokoro/PyTorch compatibility may require updated packages.
- Avoid upgrading PyTorch independently without testing Kokoro; the pinned working environment is currently safer.

These warnings should be recorded as dependency-maintenance items, but they are not reasons to reject the generated audio.

---

**3. Python 3.10 Support Warning**

```text
You are using a non-supported Python version (3.10.11).
Google will not post any further updates to google.api_core supporting
this Python version.
```

This comes from Google’s Python client libraries. It does not mean Python 3.10 or the installed Drive client has stopped working.

It means:

- Your currently installed Google libraries still run.
- Future `google-api-core` releases may no longer support Python 3.10.
- New bug fixes and security updates might require Python 3.11 or newer.
- A later dependency upgrade may fail to install under Python 3.10.

This should be addressed before calling the scheduler production-ready, but it does not block the current test.

Use Python 3.11 for the replacement environment because it is supported by both the Google libraries and Kokoro 0.9.4. A virtual environment cannot be upgraded in place; create a new one and validate it separately:

```powershell
py -3.11 -m venv .venv311

.\.venv311\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv311\Scripts\python.exe -m pip install -r .\requirements-kokoro.txt
.\.venv311\Scripts\python.exe -m pip install -r .\requirements-drive.txt

.\.venv311\Scripts\python.exe -m unittest discover `
  -s tests `
  -p "test_*.py" `
  -v
```

Do not remove the working `.venv` until the new environment passes narration, Drive, render, and test-suite checks.

---

**4. Orphaned Workspaces**

```text
orphaned workspace retained for review: work\manual-acceptance
orphaned workspace retained for review:
work\16I1fIFasAJf6IQm21ZAxaxJHm_9E8JJ4-00b3a6c5987e
```

The queue uses both:

- Local directories under `work\`.
- Job records in `work\tts_gen.db`.

At startup, it compares existing workspace directories against snapshot paths recorded in the database. A directory without a matching recorded snapshot is considered orphaned. This check is in <ref_snippet file="C:\Users\ricky\Tools\TTS_gen\run_drive_queue.py" lines="81-90" />.

The worker deliberately preserves it instead of deleting it because it might contain:

- A partially downloaded Drive snapshot.
- Rendered narration or video worth reusing.
- Diagnostic files from a failed job.
- A manually prepared acceptance-test workspace.
- Evidence needed to understand a crash.

Your two messages likely have different causes:

- `work\manual-acceptance` is a manually created test workspace and is not expected to have a Drive database record.
- The long ID/hash directory likely came from the earlier Drive job that failed before snapshot registration completed because no recognized chapter file was found.

An orphan:

- Is not automatically uploaded.
- Is not automatically selected as a new Drive job.
- Does not by itself fail the queue.
- Continues producing the warning until archived, registered, or removed.
- Should not be modified or removed while the queue is running.

After the current run finishes, inspect the directories:

```powershell
Get-ChildItem .\work -Directory

Get-ChildItem `
  .\work\16I1fIFasAJf6IQm21ZAxaxJHm_9E8JJ4-00b3a6c5987e `
  -Recurse
```

If the hashed workspace only contains files from the rejected missing-chapter attempt, it can eventually be archived or removed. Review it first—the preservation behavior exists specifically to prevent automatic data loss.
