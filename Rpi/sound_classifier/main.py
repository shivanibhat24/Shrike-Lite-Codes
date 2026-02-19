from machine import ADC, Pin
import utime
import math

# -------- CONFIG --------
MIC_PIN = 27        # CHANGE THIS
SAMPLE_SIZE = 128
DELAY_US = 1000     # ~1kHz sampling

# -------- ADC SETUP (WORKS FOR MOST BOARDS) --------
try:
    adc = ADC(Pin(MIC_PIN))   # ESP32 / generic
except:
    adc = ADC(MIC_PIN)        # Pico

# -------- SAFE ADC READ --------
def read_adc():
    try:
        return adc.read()        # ESP32
    except:
        return adc.read_u16()    # Pico

# -------- MODEL (Tiny Neural Network) --------
# Input: 4 features → Hidden: 6 → Output: 3 classes

W1 = [
    [0.15, -0.05, 0.04, 0.2],
    [-0.2, 0.3, 0.1, -0.1],
    [0.1, 0.2, -0.15, 0.25],
    [0.3, -0.2, 0.15, 0.1],
    [-0.1, 0.25, 0.3, -0.05],
    [0.2, 0.1, -0.2, 0.15]
]

B1 = [0.05, -0.1, 0.02, 0.05, -0.05, 0.1]

W2 = [
    [0.3, -0.2, 0.35, 0.1, -0.25, 0.2],   # CLAP
    [-0.1, 0.4, -0.2, 0.25, 0.2, -0.3],   # KNOCK
    [0.2, -0.1, 0.1, -0.15, 0.25, 0.3]    # NOISE
]

B2 = [0.1, -0.05, 0.05]

labels = ["CLAP", "KNOCK", "NOISE"]

# -------- ACTIVATION FUNCTIONS --------
def relu(x):
    return x if x > 0 else 0

def softmax(x):
    max_x = max(x)  # stability
    exps = [math.exp(i - max_x) for i in x]
    s = sum(exps)
    return [i / s for i in exps]

# -------- FEATURE EXTRACTION --------
def extract_features(samples):
    n = len(samples)

    # Mean
    mean = sum(samples) / n

    # Normalize signal (IMPORTANT)
    norm = [x - mean for x in samples]

    # Variance
    var = sum(x * x for x in norm) / n

    # RMS Energy
    rms = math.sqrt(var)

    # Zero Crossing Rate
    zcr = 0
    for i in range(1, n):
        if norm[i-1] * norm[i] < 0:
            zcr += 1
    zcr = zcr / n

    # Return normalized mean too (optional)
    return [mean, var, rms, zcr]

# -------- NN INFERENCE --------
def predict(features):
    # Hidden layer
    hidden = []
    for i in range(6):
        s = B1[i]
        for j in range(4):
            s += W1[i][j] * features[j]
        hidden.append(relu(s))

    # Output layer
    out = []
    for i in range(3):
        s = B2[i]
        for j in range(6):
            s += W2[i][j] * hidden[j]
        out.append(s)

    return softmax(out)

# -------- SAMPLE COLLECTION --------
def collect_samples():
    samples = []
    for _ in range(SAMPLE_SIZE):
        samples.append(read_adc())
        utime.sleep_us(DELAY_US)
    return samples

# -------- MAIN LOOP --------
print("TinyML Sound Classifier Started...")

while True:
    samples = collect_samples()

    features = extract_features(samples)

    probs = predict(features)

    idx = probs.index(max(probs))
    confidence = probs[idx]

    print("Prediction:", labels[idx], "Confidence:", round(confidence, 3))

    utime.sleep_ms(200)

