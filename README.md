# LLM Prompt-Injection Evaluation Lab

![LLM Prompt-Injection Evaluation Lab workflow](assets/workflow.svg)

A reproducible offline evaluator for synthetic direct, retrieved-content and role-spoofing test cases.

**Fresh portfolio implementation • Python 3.10+ • Standard library only**

## Run

```bash
python3 --version
python3 evaluate.py --responses examples/toy-unsafe.json
python3 -m unittest discover -s tests -v
```

Compare fixtures:
```bash
python3 evaluate.py --responses examples/toy-filtered.json
```
Both response sets are synthetic and must never be reported as a live model benchmark.

## Implemented behavior

- Cases separate attack inputs, untrusted documents and benign utility checks.
- Scores recorded responses using explicit case-insensitive exact-marker criteria.
- Reports attack failures, missing coverage and benign utility separately.
- Toy response sets illustrate scorer behavior; no API key, network call or live model is required.

## Scope and limitations

The supplied responses are HAND-WRITTEN toy fixtures, not model outputs or measured defenses. No model is invoked. The marker is synthetic, not a real secret; output matching measures instruction redirection, not credential theft. No-marker observations do not establish resistance: paraphrases, encodings, tool actions and semantic violations can be missed. Missing cases are excluded from the rate and counted explicitly. Small tests do not establish a model ranking. Add real recorded outputs only with model/version, prompt, configuration and provenance.

## Validation

6 unit tests passed locally on Python 3.12.14. Synthetic CLI examples were executed and results are included under `examples/`. No customer data, historical lab results or production effectiveness is claimed. CI configuration is supplied; remote CI status must be checked after publishing.

## Files

- `evaluate.py` — implementation and CLI.
- `tests/test_main.py` — regression and boundary tests.
- `examples/` — synthetic inputs and generated output.
- `assets/workflow.svg` — project-specific animation with reduced-motion support.
- `.github/workflows/ci.yml` — pinned-action CI.

## Safe operation

Use inputs and hosts you own or are authorized to assess. Review reports before publication; real files, headers and logs can contain sensitive information. These tools do not establish that a system is secure or compromised.
