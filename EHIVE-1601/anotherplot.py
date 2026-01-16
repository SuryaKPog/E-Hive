import pandas as pd
import matplotlib.pyplot as plt

# Load results
df = pd.read_csv("ev_count_low_soc_sensitivity.csv")

# Convert to percentage
df["Low_SoC_Served_Rate"] *= 100

# Plot
plt.figure(figsize=(6,4))
plt.plot(
    df["EV_Count"],
    df["Low_SoC_Served_Rate"],
    marker="o",
    linewidth=2
)

plt.xlabel("Number of EVs")
plt.ylabel("Low-SoC EVs Served (%)")
plt.title("E-Hive Sensitivity to EV Population Size")
plt.grid(True)

# Save for paper
plt.tight_layout()
plt.savefig("ev_count_vs_low_soc_service.png", dpi=300)
plt.show()
