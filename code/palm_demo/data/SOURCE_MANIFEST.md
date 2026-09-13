# Source Data Manifest

This records what arrived in the workspace. It does **not** grant a licence or authorise distribution, model training, publication, or biometric collection.

| Local archive | SHA-256 | Observed content | Intended local use | Permission status |
| --- | --- | --- | --- | --- |
| `../../data/PalmBigDataBase.zip` | `8BDCBC155F43EFB4F6E7D4BEE66C1794A181E222BEE54A956BAFAE1445552829` | `PalmBigDataBase/P_F_<identity>_<sample>.bmp`; 7,754 archive entries | Fast-CC offline development/repeatability check | **[GAP]** Get the original dataset URL/agreement and intended-use confirmation from the provider. |
| `../../data/CASIA-Multi-Spectral-PalmprintV1.rar` | `80CD65007AB84E600D5022B21F20C62489A8BA56BC8F98FC7EE3636668722838` | 7,200 apparent multispectral palm images; six spectrum labels in filenames | Later, permissioned offline cross-spectral baseline only | **[GAP]** Standard RGB Pi frames are not this sensor condition. Confirm CASIA terms before use. |
| `../../data/palmprint-device-intro.zip` | `C54A33BD5C6F7A2E0104867BD46FA50E0BA862FB40ADD8D305D830386457A8B4` | Manual, images and demonstration videos; no runtime code/model detected | Reference-only | **[GAP]** Identify the vendor and reuse terms before showing/reusing media. |

## Derived development subset

`data/processed/palmbigdata-dev/` is created only by `tools/prepare_palmbigdata.py --confirm-authorized-dataset`. The current local manifest hash is `E00306E9FF8AB8DFE7EF8AB908CE94A6131F8CE0FEB59D73C5B52EB11096D759`; it contains 20 identities x 10 images and is intentionally ignored by Git. It is a developer smoke-test subset, not a test set and not a distributable dataset.

The archive and derived images stay local. Do not add them to Git, slides, a public repository, or a demo release without confirmed terms.
