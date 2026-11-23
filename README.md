# Adaptive IoT — Energy-Aware Adaptive Sensor Network

An experimental IoT sensor-network framework that reduces communication overhead through adaptive transmission strategies while balancing measurement reconstruction accuracy and data freshness.

**Live Dashboard:**  
https://energy-aware-adaptive-iot-hiedp2lxuxam4tc4ttnwkh.streamlit.app/

**GitHub Repository:**  
https://github.com/Sravan05nani/Energy-Aware-Adaptive-IoT

## 1. Project Overview

Wireless sensor nodes often transmit measurements at fixed intervals, even when environmental conditions remain stable. This can create unnecessary communication overhead and increase energy consumption.

This project evaluates five transmission strategies using historical wireless sensor network measurements.

The five evaluated strategies are:

1. **Fixed:** Transmit at a fixed 60-second interval.
2. **Rate:** Adapt the transmission interval according to observed rates of change.
3. **Threshold:** Transmit when a sensor value changes beyond a calibrated threshold.
4. **Threshold-H120:** Threshold-triggered transmission with a 120-second maximum heartbeat interval.
5. **Threshold-H180:** Threshold-triggered transmission with a 180-second maximum heartbeat interval.

The main objective is to reduce unnecessary transmissions while maintaining acceptable reconstruction accuracy and data freshness.

The project currently uses offline simulation and historical dataset evaluation. It does not represent a live physical sensor deployment.

## 2. Dataset

The evaluation uses the Intel Berkeley Research Lab wireless sensor network dataset, collected from a physical deployment in 2004.

### Dataset Information

- **Source:** Intel Berkeley Research Lab sensor dataset
- **Original data file:** `data.txt.gz`
- **Selected sensor nodes:** 22, 31, 45, 47, 48
- **Selected common period:** 2004-02-28 01:06:46 to 2004-03-24 05:57:47
- **Selected records:** 272,278
- **Evaluation records:** 210,598
- **Eligible environmental observations:** 209,275

The dataset contains historical measurements of:

- Temperature
- Humidity
- Light
- Voltage

The dashboard uses these historical measurements for interactive playback. It must not be interpreted as real-time sensing.

### Data Preparation

The following preprocessing steps were performed:

- The selected five nodes were restricted to a common observation period.
- Raw data was retained separately from cleaned data.
- Provisional plausibility checks were applied to temperature, humidity, light and voltage.
- Invalid environmental observations were excluded from algorithm evaluation.
- Original records and validity flags were retained.
- A chronological calibration/evaluation split was used.

**Calibration period ended:** 2004-03-04 02:04:58.

The remaining observations were used for evaluation.

### Source Data Segmentation

A source-data gap greater than 300 seconds starts a new segment.

Each segment requires a fresh initial transmission. This prevents reconstructed values from being carried across long source-data outages.

The 300-second segmentation threshold is an operational analysis choice. It is not a claim about the original network's formal outage definition.

## 3. System Workflow

The system follows this general workflow:

1. Load historical sensor measurements.
2. Select the required sensor nodes.
3. Clean and validate the measurements.
4. Separate calibration and evaluation periods chronologically.
5. Calibrate transmission thresholds.
6. Apply the five transmission strategies.
7. Simulate transmission decisions.
8. Reconstruct sensor measurements from transmitted observations.
9. Calculate transmission reduction, reconstruction accuracy and freshness.
10. Estimate energy consumption using an illustrative energy model.
11. Display the experimental results through an interactive dashboard.

The dashboard supports historical data playback and visualization of the evaluated transmission strategies.

## 4. Experimental Results

All results below are from the Intel dataset evaluation period.

The transmission reduction denominator is 209,275 eligible environmental observations.

### 4.1 Transmission Comparison

| Algorithm | Transmissions | Transmission Reduction |
|---|---:|---:|
| Fixed | 89,935 | 57.03% |
| Rate | 75,807 | 63.78% |
| Threshold | 41,750 | 80.05% |
| Threshold-H120 | 70,016 | 66.54% |
| Threshold-H180 | 58,327 | 72.13% |

Transmission reduction is calculated relative to the eligible environmental observation count.

### 4.2 Reconstruction Accuracy

Reconstruction accuracy is evaluated using Mean Absolute Error (MAE).

The reconstructed measurements are compared with the original eligible observations.

| Algorithm | Temperature MAE | Humidity MAE | Light MAE |
|---|---:|---:|---:|
| Fixed | 0.01549 | 0.03724 | 3.26429 |
| Rate | 0.01460 | 0.03729 | 2.13223 |
| Threshold | 0.02441 | 0.05488 | 1.95698 |
| Threshold-H120 | 0.01180 | 0.03293 | 0.94211 |
| Threshold-H180 | 0.01424 | 0.03782 | 1.17040 |

Sensor units follow the original dataset.

Temperature and humidity errors are expressed in the dataset's recorded units. Light error is expressed in the dataset's light measurement units.

### 4.3 Data Freshness

Freshness age represents the elapsed time between an original observation and the most recent prior transmitted measurement for that node and segment.

| Algorithm | Mean Age (s) | 95th Percentile Age (s) | Maximum Age (s) |
|---|---:|---:|---:|
| Fixed | 21.95 | 59.12 | 60 |
| Rate | 31.97 | 86.97 | 90 |
| Threshold | 293.41 | 1111.78 | 6544.97 |
| Threshold-H120 | 42.52 | 114.97 | 120 |
| Threshold-H180 | 63.36 | 166.80 | 180 |

The heartbeat variants limit the maximum reconstruction freshness age within each source-data segment.

### 4.4 Illustrative Energy Model

The project estimates energy consumption using assumed energy costs.

The model uses the following parameters:

| Operation | Assumed Energy Cost |
|---|---:|
| Sensing | 0.5 mJ per eligible observation |
| Processing | 0.2 mJ per eligible observation |
| Transmission | 50 mJ per transmitted packet |

### Estimated Energy Comparison

| Algorithm | Estimated Total Energy (J) | Savings vs Fixed |
|---|---:|---:|
| Fixed | 4,643.242 | 0.00% |
| Rate | 3,936.842 | 15.21% |
| Threshold | 2,233.992 | 51.89% |
| Threshold-H120 | 3,647.292 | 21.45% |
| Threshold-H180 | 3,062.842 | 34.04% |

**Important:** These energy values are model-based estimates, not measured hardware energy consumption.

The current model does not include:

- Radio reception energy
- Idle listening energy
- Sleep-state energy
- Retransmissions
- Communication protocol overhead
- Device-specific power characteristics

The assumed battery capacity is not used to claim a measured or validated battery lifetime.

## 5. Current Design Choice

Threshold-H120 is the current preferred candidate for the evaluated dataset.

It achieved:

- 66.54% fewer transmissions relative to the eligible observation count.
- The lowest MAE among the five evaluated algorithms for temperature, humidity and light.
- A maximum reconstruction freshness age of approximately 120 seconds within each source-data segment.
- 21.45% lower estimated energy consumption than the fixed strategy under the stated illustrative model.

Threshold-only achieved the greatest transmission reduction and estimated energy savings, but its freshness performance was substantially worse.

Threshold-H180 offers another communication-efficient alternative with a longer maximum freshness age.

The preference for Threshold-H120 is based on the current dataset and experimental assumptions. It does not establish that H120 is universally optimal for all sensor networks.

## 6. Important Limitations

The following limitations must be considered when interpreting the results.

### 6.1 Historical Dataset

The measurements come from a physical wireless sensor network deployment conducted in 2004.

The dashboard performs historical playback, not real-time sensing.

### 6.2 Simulated Transmission Decisions

The original dataset does not provide the packet transmission logs required to validate the simulated transmission decisions against actual network transmissions.

Therefore, the transmission counts represent simulation results.

### 6.3 Estimated Energy Consumption

Energy consumption is calculated using explicitly stated assumptions.

No physical energy measurements were collected from ESP32 boards or the original sensor hardware.

### 6.4 No Event Ground Truth

The dataset does not provide reliable event labels.

This project does not claim validated event-detection accuracy.

### 6.5 Source Data Outages

Long gaps in the original dataset are handled through segmentation.

This prevents stale reconstructed values from being carried across long source-data outages.

### 6.6 Dataset-Specific Calibration

Transmission thresholds are calibrated on an earlier chronological period and evaluated on later observations.

Performance may differ under other environmental conditions, sensor configurations and deployment scenarios.

### 6.7 Physical Hardware Validation

The current implementation focuses on software simulation and historical data evaluation.

Physical ESP32 deployment and hardware-level energy measurement are considered future extensions.

## 7. Repository Structure

The project repository is organized as follows:

```text
Energy-Aware-Adaptive-IoT/
│
├── README.md
├── requirements.txt
├── algorithm_configuration.json
├── experiment_summary.json
│
├── notebooks/
│   └── energy_aware_simulation.ipynb
│
├── datasets/
│   ├── ground_truth.csv
│   └── sensor_measurements.csv
│
├── dashboard/
│   └── app.py
│
├── dashboard_data/
│   └── Prepared dashboard datasets
│
├── src/
│   └── dashboard_engine.py
│
└── results/
    ├── configuration/
    └── csv/
```

The repository contains the source code, notebook, prepared datasets, lightweight experiment results, configuration files and documentation required for the current implementation.

Some large intermediate datasets and bulky reconstruction exports are excluded from the GitHub repository.

## 8. Running the Experiments

The experiment notebook is designed primarily for Google Colab.

### Steps

1. Open `notebooks/energy_aware_simulation.ipynb` in Google Colab.
2. Download the Intel Berkeley sensor dataset from its official source.
3. Follow the notebook cells to prepare the dataset.
4. Calibrate the transmission algorithms.
5. Run the simulations.
6. Generate the evaluation tables.
7. Review the assumptions and limitations before interpreting the energy results.

Maintain the chronological separation between calibration and evaluation periods.

**Note:** The experiment notebook is a development notebook containing historical experiments and intermediate cells. It should not be assumed to execute cleanly from the first cell without the required dataset preparation and runtime setup.

Python 3 and the packages listed in `requirements.txt` are required.

## 9. Running the Dashboard Locally

The interactive dashboard can be executed locally from the repository root.

### Step 1: Clone the repository

```bash
git clone https://github.com/Sravan05nani/Energy-Aware-Adaptive-IoT.git
```

### Step 2: Enter the project directory

```bash
cd Energy-Aware-Adaptive-IoT
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard uses the prepared files in `dashboard_data/`, which are included in the repository.

## 10. Public Dashboard

The interactive dashboard is deployed using Streamlit Community Cloud.

**Access the dashboard:**

https://energy-aware-adaptive-iot-hiedp2lxuxam4tc4ttnwkh.streamlit.app/

Users can open the dashboard through a web browser without installing Python or running the project locally.

The dashboard provides an interactive interface for exploring historical sensor measurements and comparing the evaluated transmission strategies.

The dashboard is a historical data visualization and simulation interface, not a live IoT monitoring system.

## 11. Roadmap

- [x] Acquire and inspect the Intel Berkeley sensor dataset.
- [x] Select five sensor nodes and prepare a common evaluation period.
- [x] Implement fixed, rate-based and threshold-based transmission strategies.
- [x] Add heartbeat variants with 120-second and 180-second limits.
- [x] Implement source-outage-aware segmentation and reconstruction.
- [x] Evaluate transmission reduction.
- [x] Evaluate reconstruction accuracy.
- [x] Evaluate data freshness.
- [x] Implement an assumption-based energy comparison.
- [x] Build an interactive monitoring dashboard.
- [x] Integrate historical dataset playback controls.
- [x] Validate dashboard operation locally in Google Colab.
- [x] Publish the project repository on GitHub.
- [x] Deploy the interactive dashboard using Streamlit Community Cloud.

## 12. Project Status

The adaptive transmission simulation, offline evaluation and interactive historical playback dashboard have been implemented.

The project has been evaluated using historical Intel Berkeley Research Lab wireless sensor network measurements.

The interactive dashboard has been tested locally in Google Colab and publicly deployed using Streamlit Community Cloud.

The source code and supporting project files are available in the GitHub repository.

Physical ESP32 validation and hardware-level energy measurements are considered possible future extensions.

---

**Project:** Adaptive IoT — Energy-Aware Adaptive Sensor Network

**Implementation:** Offline Simulation and Historical Dataset Evaluation

**Dashboard:** Streamlit Community Cloud

**Repository:** GitHub
