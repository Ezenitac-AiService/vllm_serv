# CLI Contract: `make_seed_pack.sh`

```bash
./make_seed_pack.sh [OPTIONS]
```

### Options

| Flag | Description | Default |
|------|-------------|---------|
| `-o, --output PATH` | Specify output archive path | `dist/vllm_serv_seed.tar.gz` |
| `--zip` | Create `.zip` archive instead of `.tar.gz` | `false` |
| `--include-profiles` | Include `config/model_context_profiles.json` | `false` |
| `--build-legacy` | Precompile i7-930 wheel package | `true` |
| `--skip-legacy-build` | Skip i7-930 wheel precompilation | `false` |
| `-h, --help` | Display help message and exit | - |
