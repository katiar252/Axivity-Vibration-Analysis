# Axivity Vibration Analysis

Analysis pipeline for processing whole-body vibration data collected from Axivity AX3 accelerometers, following the **ISO 2631-1** standard for evaluating human exposure to whole-body vibration.

This project was developed to assess vibration exposure and seat cushion performance in a heavy vehicle, using three synchronized sensors:

- **Floor** — mounted on the vehicle floor (input vibration)
- **Below Seat** — mounted on the rigid metal seat frame (below seat cushion)
- **Above Seat** — mounted on top of the seat cushion, where the operator sits (covered with seat pad to reduce vehicle operator discomfort)

## Pipeline 

1. Loads raw `.cwa` accelerometer files (Axivity AX3 format, data collected in g)
2. Aligns and resamples all three sensors to a common time base and sampling rate
3. Applies ISO 2631-1 frequency weighting filters (Wk for vertical/z-axis)
4. Trims out inactive/parked periods, keeping only active driving time
5. Calculates standard vibration exposure metrics: RMS, Crest Factor, Vibration Dose Value (VDV), and A(8) 8-hour equivalent exposure
6. Calculates the **SEAT value** (Seat Effective Amplitude Transmissibility) to quantify whether the seat cushion amplifies or attenuates vibration
7. Generates a weighted Power Spectral Density (PSD) plot comparing all three sensors from 0-30 Hz

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your data

Place your raw `.cwa` sensor files in a `data/` folder at the project root. 

Expected files (update filenames in `ingestion.py` to match your own):
```
data/
├── floor.cwa
├── above_seat.cwa
└── below_seat.cwa
```

### 3. Run the pipeline

First, convert raw `.cwa` files into aligned, cached `.pkl` files:
```bash
python ingestion.py
```

Then run the full analysis:
```bash
python main.py
```

## Configuration

Key analysis parameters are currently set as constants near the top of `main()` in `main.py`:

| Parameter | Default | Description |
|---|---|---|
| `crop_minutes` | 45 | Minutes trimmed from start/end to remove synchronization knocks |
| `threshold` | 0.075 m/s² | Vibration envelope threshold used to detect "active driving" vs. parked/idle |
| `fs` | 200 Hz | Target sampling rate after alignment |
| `k_factor` | 1.0 | ISO 2631-1 health weighting multiplier (vertical/seated) |

These may need adjustment for other setups.

## Output metrics explained

- **RMS** — root-mean-square of the frequency-weighted acceleration signal
- **Crest Factor** — peak-to-RMS ratio; flags whether exposure is dominated by shocks/transients vs. continuous vibration
- **VDV (Vibration Dose Value)** — a fourth-power-weighted dose metric, more sensitive to shocks than RMS alone
- **A(8)** — the 8-hour energy-equivalent daily vibration exposure, used to compare against ISO 2631-1 health guidance zones
- **SEAT (%)** — ratio of above-seat to below-seat RMS; SEAT > 100% means the seat cushion is amplifying vibration rather than reducing it

## Data availability

Raw sensor data is not included in this repository due to participant/study data restrictions. Data should be uploaded in raw .cwa format to the `data/` folder. 
