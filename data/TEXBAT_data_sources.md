# Data Sources — TEXBAT (Texas Spoofing Test Battery)

This file documents where the raw data used in `Network_PNT.ipynb` comes from, so
anyone cloning this repo can find, download, and cite it correctly. The dataset
itself is **not included in this repo** (see redistribution note below) — it must
be downloaded directly from the official source.

---

## 1. Dataset origin

- **Name:** TEXBAT — Texas Spoofing Test Battery
- **Produced by:** Radionavigation Laboratory (RNL), The University of Texas at Austin
  (Prof. Todd Humphreys' research group)
- **Official project page:** https://radionavlab.ae.utexas.edu/texbat/
- **Direct data download:** https://radionavlab.ae.utexas.edu/datastore/texbat/
- **Contact for download issues:** todd.humphreys@utexas.edu

---

## 2. Documentation / README-equivalent sources

| Document | Link |
|---|---|
| Original TEXBAT description paper (v1.0, covers ds1–ds6) — Humphreys, Bhatti, Shepard, Wesson, "The Texas Spoofing Test Battery: Toward a Standard for Evaluating GPS Signal Authentication Techniques," Proc. ION GNSS, Nashville, TN, 2012 | https://radionavlab.ae.utexas.edu/images/stories/files/papers/tbION_for_distribution.pdf |
| Official ds7 & ds8 scenario description (added Aug 2015) — "TEXBAT Data Sets 7 and 8," Todd Humphreys | https://rnl-data.ae.utexas.edu/datastore/texbat/texbat_ds7_and_ds8.pdf |
| Independent validation paper — Lemmenes, Corbell, Gunawardena, "Detailed Analysis of the TEXBAT Datasets Using a High Fidelity Software GPS Receiver," Proc. ION GNSS+, Portland, OR, 2016 | https://radionavlab.ae.utexas.edu/images/stories/files/papers/LemmenesGNSSpaper.pdf |
| MATLAB helper script to parse the raw `.bin` recordings (author: Logan Scott) | https://rnl-data.ae.utexas.edu/datastore/texbat/scott.m |

### 2.1 Processed observable files (the actual `navsol.mat` / `channel.mat` used in this notebook)

The raw TEXBAT `.bin` recordings were run through the UT GRID/pprx software
receiver, and the resulting per-scenario `navsol.mat` / `channel.mat` files
are hosted directly by RNL — this is the source this project's `.mat` files
came from:

| Resource | Link |
|---|---|
| Processed data index (folders for `cleanStatic`, `ds2`, `ds3`, `ds7`) | https://rnl-data.ae.utexas.edu/datastore/texbat/processed/ |
| README explaining the processed folder + pointing to the column-format docs | https://rnl-data.ae.utexas.edu/datastore/texbat/processed/readme.txt |

### 2.2 Official column-by-column format definitions

These are the authoritative definitions for every column in `navsol.mat` and
`channel.mat` — this is what confirmed the exact column order, count, and the
`NISratio` field missing from our copy of `navsol.mat`:

| File | Defines | Link |
|---|---|---|
| `navsoldef.txt` | All 13 columns of `navsol.mat` (position, velocity, clock error, fix flag, NISratio) | https://rnl-data.ae.utexas.edu/datastore/satNavCourse/logFileDocumentation/navsoldef.txt |
| `channeldef.txt` | All 14 columns of `channel.mat` (RRT/ORT timestamps, Doppler, carrier phase, pseudorange, C/N0, valid flag, error indicator bits, channel status, signal type, TXID) | https://rnl-data.ae.utexas.edu/datastore/satNavCourse/logFileDocumentation/channeldef.txt |
| `signaltype.h` | Encoding used by the `signal_type` column in `channel.mat` | https://rnl-data.ae.utexas.edu/datastore/satNavCourse/signaltype.h |
| Parent index of all GRID log-format docs (attitude, iono, IQ, sbrtk, scint, txinfo, etc.) | https://rnl-data.ae.utexas.edu/datastore/satNavCourse/logFileDocumentation/ |

---

## 3. Citation requirement (per TEXBAT usage terms)

Any publication or write-up based on this data must cite:

> T.E. Humphreys, J.A. Bhatti, D.P. Shepard, and K.D. Wesson, "The Texas Spoofing
> Test Battery: Toward a Standard for Evaluating GPS Signal Authentication
> Techniques," Proceedings of ION GNSS, Nashville, TN, 2012.

**License note:** Copyright (c) 2012–2025 The University of Texas. Free to use,
copy, and modify for research purposes — but users are asked **not to
redistribute the raw data**. This is why the `.mat`/`.bin` files themselves are
kept out of this repo; only this documentation and the processed/derived CSVs
built from them (if any) are checked in.

---

## 4. Scenarios actually used in this project

| Scenario | Raw files loaded | What it is | Role in `Network_PNT.ipynb` |
|---|---|---|---|
| `cleanStatic` | `navsol.mat`, `channel.mat` | Authentic-only recording, no spoofing, static receiver on the roof of the UT Austin Aerospace Engineering building | Normal-only baseline for training |
| `ds2` | `navsol-ds2.mat`, `channel-ds2.mat` | "Overpowered time-push" — simple, abrupt spoofing takeover | Training + labeled testing |
| `ds3` | `navsol-ds3.mat`, `channel-ds3.mat` | "Matched-power time-push" — slower, more gradual takeover | Training + labeled testing |
| `ds7` | `navsol-ds7.mat`, `channel-ds7.mat` | Power-matched **and** carrier-phase-aligned time-push, built on top of `cleanStatic`; added Aug 2015; the most sophisticated/stealthy of the three | Held-out generalization test only — **not used in training** |

**Important:** the official TEXBAT files are distributed as raw `.bin` RF
recordings. The `.mat` files used in this notebook (`navsol*.mat`,
`channel*.mat`) are the **receiver-processed observables** (position/velocity
solution and per-satellite channel measurements) produced by running those
`.bin` files through a GPS receiver/tracking chain — not the raw signal samples
themselves.

---

## 5. Column reference (per official `navsoldef.txt` / `channeldef.txt`)

**`navsol.mat` — 13 columns:**

| # | Column | Notes |
|---|---|---|
| 1 | `ort_week` | GPS week number |
| 2 | `ort_sec` | ORT whole seconds of week |
| 3 | `ort_frac_sec` | ORT fractional second |
| 4–6 | `x, y, z` | Receiver antenna position, ECEF frame, meters |
| 7 | `clock_error` (deltR) | Receiver clock error, in equivalent **meters** (TGT = ORT − deltR/c) |
| 8–10 | `x_vel, y_vel, z_vel` | Receiver antenna velocity, ECEF frame, m/s |
| 11 | `clock_error_rate` (deltRdot) | Receiver clock error rate, equivalent m/s |
| 12 | `fix_flag` | 0 = no fix, 1 = preliminary, 2 = standard, 3 = precise |
| 13 | `NISratio` | Normalized-innovation-squared ratio; should be ≈1 if the filter is well-tuned — **this column is missing from the `.mat` files used in this project** |

**`channel.mat` — 14 columns:**

| # | Column | Notes |
|---|---|---|
| 1–2 | `rrt_week, rrt_sec` | Raw Receiver Time — internal, never adjusted, strictly non-decreasing |
| 3–5 | `ort_week, ort_whole_sec, ort_frac_sec` | Offset Receiver Time — RRT + periodic correction toward true GPS time (this correction causes small jumps in `pseudorange`/`carrier_phase`; see §6) |
| 6 | `doppler_hz` | Apparent Doppler frequency, Hz — **positive = satellite approaching** |
| 7 | `carrier_phase` | Beat carrier phase, cycles — moves in the same direction as `pseudorange` |
| 8 | `pseudorange` | Meters |
| 9 | `cn0` | Carrier-to-noise ratio, dB-Hz |
| 10 | `valid_flag` | 1 = pseudorange/carrier phase measurements valid, 0 = not valid |
| 11 | `error_indicator` | **8-bit encoded field, not a single number.** Bit 0 = phase tracking anomaly, **bit 1 = spoofing detected**, bit 2 = possible half-cycle offset, bits 3–7 reserved. Must be decoded bitwise, e.g. `(error_indicator >> 1) & 1` for the spoofing bit specifically |
| 12 | `channel_status` | 0 NULL → 1 ALLOCATED → 2 ACQUIRED → 3 SYMBOL_LOCK → 4 FREQ_LOCK → 5 PHASE_LOCK → 6 DATA_LOCK |
| 13 | `signal_type` | Encoded byte `[g g g T T T T T]` (Group + GenericType) — see `signaltype.h` |
| 14 | `txid` | Transmitter (satellite) ID |

---

## 6. Notes for reproducing this repo

- The notebook expects the `.mat` files at a Google Drive path (`/content/drive/MyDrive/Network/...`).
  To reproduce: download the corresponding `.bin` files from the official
  download link above, process them into `navsol*.mat` / `channel*.mat`
  (or source them if already available in that processed form), and place
  them in the same directory structure.
- Ground-truth spoofing labels could **not** be reliably taken from the
  receiver's own `error_indicator` "spoofing detected" bit for `ds2`/`ds3`/`ds7`
  (it stayed at 0 throughout for all three). Attack onset times used for
  labeling in this project were derived manually per scenario — combining
  visual inspection, statistical onset detection, and cross-referencing against
  the official ds7/ds8 documentation PDF linked above.
- Per `channeldef.txt`: `error_indicator` is a bitfield, not a plain integer —
  extracting the spoofing label with `!= 0` instead of a bitwise mask on bit 1
  will conflate it with unrelated phase-tracking/half-cycle error states.
- Per `channeldef.txt`: periodic `tOffset` corrections to ORT introduce small
  artificial jumps in `pseudorange`/`carrier_phase` that are unrelated to
  spoofing — worth checking for before using either column in a rate-of-change
  feature.
- Rows with `valid_flag == 0` or `channel_status < 5` (not yet in full phase
  lock) reflect normal acquisition/tracking noise, not attack behavior, and
  should generally be filtered out before computing per-satellite baselines.
