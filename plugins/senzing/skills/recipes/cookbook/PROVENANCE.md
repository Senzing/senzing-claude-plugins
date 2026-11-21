# Cookbook provenance

Vendored verbatim from [`senzing/recipes`](https://github.com/senzing/recipes) — **do not hand-edit**.
Re-vendor with `scripts/vendor-cookbook.sh [ref]`; `mcp-version-sync.yml` runs it on
every version bump, so each published plugin version carries the cookbook as it stood
when that version was cut.

- Upstream commit: `bedaa7905b22914e642ec2ce4b1ccc93fe864940`
- Vendored at: 2026-11-20T23:36:31Z
- Files: 9 · bytes: 81939
- Upstream license: Apache-2.0 (`LICENSE`, included)

Ingredients, images and repo furniture are excluded on purpose: the directory accepts only
Markdown/text/JSON/YAML/images from a non-Verified org, and the skill never renders an image.

Ingredient data is stored with a `.txt` suffix on its real name (`crm.csv` ->
`crm.csv.txt`), and a file over 256 KB is split on line boundaries into
`<name>.partNN.txt`. The directory accepts Markdown, text, JSON, YAML and images and
must be able to read each file in full; the data is plain UTF-8 text either way, so this
keeps it inspectable rather than hiding it. The skill restores the documented filenames
when it copies them into the workspace.

| sha256 | file |
| --- | --- |
| `be67d4c32fcfd8afe819e555c809a192d1f0b61a0c3dfa23e3f71e46dfa8b745` | `cookbook.md` |
| `a42402debe35cff97880e1bcac1e8bb68fa17c4d7741cb9ca6d465ac48ce2ae8` | `getting-started.md` |
| `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | `LICENSE` |
| `68264207e20a98e4c08488c0fdc7620d6ef8f5ad59a73409932851e8cd4a79be` | `mcp-setup-troubleshooting.md` |
| `9d9c2f1577c438761eff449e6708b6af5d97f8a80b5b491e532a8223956a0f71` | `recipes/clair-data-ingestion-starter.md` |
| `7ae7c357bbd625ce138ce087e888faca335d2caf293c067e06ff35ee8d8d4c87` | `recipes/customer-360-crm-online.md` |
| `afe9237b4949234bbebe0ec20beb42b25039f6470eb4b861453be4469350a7c7` | `recipes/customer-360-stewardship.md` |
| `3febaaa52de16f99885f3cd1ccd5a9a2b61fd9b8871d892d89d4f86e599f43e5` | `recipes/nigel-healthcare-aws-entity-browser.md` |
| `63dfb5b3f359f45c355d16974f181914eefcec7139c893e8ca6d749fd9152fb7` | `recipes/patient-fraud-uk.md` |
