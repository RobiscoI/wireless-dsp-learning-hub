# Wireless DSP learning project instructions

- Two tracks, kept separate: `matlab/` (24-week MATLAB course) and `jetson/` (PC-Jetson Edge DSP). Run `jetson/` commands from inside `jetson/`; its relative paths (`labs/edge_dsp`, `build/`, `output/`) assume that folder.
- MATLAB lessons target R2025b. On older releases call `matlab/setup_path`, which adds stand-ins only for missing functions. The Notion workbook kit lives in the git-ignored `matlab/kit/`; never commit it or run outputs.
- Explain in Korean for a beginner. Connect purpose, assumptions, mathematics, code, execution and validation.
- Keep the personal Jetson Nano 2GB learning project separate from industrial DF and RF hardware projects.
- The baseline requires only PC/Linux Jetson over LAN and synthetic IQ. Do not assume extra RF boards.
- Document execution location, units, M-by-N layout, endian, complex sign, scaling, seed and tolerances.
- Preserve existing dist site, original attachments, session IDs and learner notes unless explicitly requested.
- Use complete source files with meaningful comments and exact commands; do not present pseudocode as runnable code.
- Nano uses the JetPack 4 family. Check installed versions before adding CUDA or Python dependencies.
- Validate numerical correctness and protocol failure cases before optimizing. Keep optional extensions distinct from implemented features.
- Never claim MATLAB, Jetson ARM64, GPU or RF validation without running that environment.
- Record source provenance and third-party licensing before importing external code.
- Keep build products, raw IQ, credentials and private learning notes out of commits.
- Use one focused change per commit. Review diffs and document test results and untested environments.
- GitHub source and Notion copies are not automatically synchronized. Update version links when publishing.
