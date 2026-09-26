# aoray NG

> A real Xray-powered proxy client for legacy Android phones.

A size-obsessed fork of [v2rayNG](https://github.com/2dust/v2rayNG) (base 1.8.12, Xray engine 1.8.11) targeting legacy Android 4.4+ devices: single ABI, aggressively subset routing geodata, installable to SD card. No new features - one goal only: **the smallest possible APK that still runs the real engine**.

**License:** GPL-3.0 | **Min SDK:** 19 (Android 4.4) | **ABI:** `armeabi-v7a` only

---

## Why 9 MB is impossible

A pure-Java rewrite route for even smaller size was evaluated and abandoned - see `V2rayNG/BUILD-AORAY.md`.

The engine's `libgojni.so` alone is **27,169,852 bytes** unpacked (~9.88 MB compressed into the APK) - that is the Xray/Go core itself, not something you can trim away. Strategy: keep the real engine, cut or offload everything else.

## Build outputs

| Variant | APK size | Notes |
|---|---|---|
| Release | **16.4 MB** | Upstream build setup, no minification; predictable behavior. |

Baseline 19.9 MB -> 16.4 MB. See "SD card" below for on-device footprint.

## What was cut

| Item | How | Gain |
|---|---|---|
| Engine AAR: 4 ABIs -> `armeabi-v7a` only | Repacked as `engine-libv2ray-1.8.11-slim.aar` (repo root) | 45 MB -> 9.5 MB |
| `geoip.dat` 10.22->0.14 MB; `geosite.dat` 1.65->0.15 MB | `tools/shrink_geodata.py`: item-level protobuf subsetting, keeps only `cn` / `private` / `category-ads*` actually referenced by the built-in templates; non-protobuf tail kept verbatim | **-2.55 MB** |
| Languages: en / zh-rCN / zh-rTW only | `resConfigs` (also strips ar/fa/ru/vi translations bundled with AndroidX) | **-0.55 MB** |
| QR scanner (quickie + barcode native) | Removed; zxing core kept | -2.83 MB |
| `montserrat_thin.ttf` decorative font | Dropped together with its `fontFamily` references | -0.14 MB |
| Whole-app install to SD card | `android:installLocation="preferExternal"`; on 4.4 the APK and its unpacked native libs move into the `asec` container | internal-storage footprint can drop to **~2 MB** |
| ZIP alignment | `zipAlignEnabled true` (aids mmap, zero size cost) | - |

**Caveats**
- Geodata is subset: routing beyond the built-in templates (bypass-mainland / ad-blocking, etc.) **will not work with other geocodes**; import or download full `geoip.dat`/`geosite.dat` on the device if you need them.
- On some 4.4-era OEM ROMs the SD container is mounted `noexec` (installs fine, crashes the moment you hit connect) - move the app back to internal storage.

## Repository layout

```
aoray/
|-- V2rayNG/                      # Android project; builds directly in Android Studio or via Gradle
|   |-- BUILD-AORAY.md            # * Rationale, measurements & risk notes (read this first)
|   `-- app/
|       |-- libs/libv2ray.aar     # Slimmed engine (v7a-only ABI + subset geodata in its assets)
|       `-- src/main/...          # v2rayNG 1.8.12 sources + aoray changes
|-- engine-libv2ray-1.8.11-slim.aar  # Pristine copy of the slim engine AAR (9.5 MB)
|-- tools/shrink_geodata.py       # Geodata subsetting tool
`-- README.md / LICENSE           # GPL-3.0
```

## Key specs

| | |
|---|---|
| `applicationId` | `io.aoray.client` |
| `versionName` / `versionCode` | `1.0-aoray1` / `1` (ABI version-code mapping in `app/build.gradle`) |
| `minSdk` / `targetSdk` / `compileSdk` | 19 / 34 / 34 |
| AGP / Gradle / Kotlin | 7.4.2 / 7.5 (wrapper) / 1.8.0, requires **JDK 17** |
| ABI splits | `armeabi-v7a` only, `universalApk false` |
| Output name | `v2rayNG_1.0-aoray1_armeabi-v7a.apk` |

## Building

```bash
cd V2rayNG
./gradlew assembleRelease
# artifact: app/build/outputs/apk/release/v2rayNG_1.0-aoray1_armeabi-v7a.apk
```

**Signing**: the release config points to `V2rayNG/aoray.keystore` (alias `aoray`; password in `app/build.gradle`), which is **not in this repo** (gitignored). Either generate your own keystore or remove the release signing lines:

```bash
# Option A: make your own keystore
keytool -genkeypair -keystore V2rayNG/aoray.keystore -alias aoray \
        -keyalg RSA -keysize 2048 -validity 10000
# then update the passwords in app/build.gradle accordingly

# Option B: verify compilation first
./gradlew assembleDebug   # or point the release signingConfig at your own store
```

> The keystore password committed in `build.gradle` is a placeholder - **always ship under your own signature**. A different signature means users cannot install upgrades over an existing build.

### Regenerating subset geodata

```bash
python3 tools/shrink_geodata.py <dir-containing-geoip.dat-geosite.dat>
# point it at a folder with the full geoip.dat / geosite.dat; it rewrites them in place
```

Unpack the engine AAR (built from [AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite)), run the script over its `assets/*.dat`, repack.

## Credits

- Upstream client: [2dust/v2rayNG](https://github.com/2dust/v2rayNG) (GPL-3.0) - this repository is a modification of v2rayNG, distributed under the original GPL-3.0 license.
- Engine: [XTLS/Xray-core](https://github.com/XTLS/Xray-core) via [2dust/AndroidLibXrayLite](https://github.com/2dust/AndroidLibXrayLite). For building cores from source, see the [Go Mobile](https://github.com/golang/go/wiki/Mobile) guide.
- Full routing rules come from [Loyalsoldier/v2ray-rules-dat](https://github.com/Loyalsoldier/v2ray-rules-dat) (only relevant when importing/downloading full `dat` files on-device).

## Disclaimer

This project is for the study of proxy and DPI-evasion techniques only; comply with your local laws and regulations.
