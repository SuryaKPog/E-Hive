import pandas as pd
import matplotlib.pyplot as plt

# Load results
df = pd.read_csv("ev_count_sensitivity.csv")

# Plot
plt.figure(figsize=(7,5))
plt.plot(
    df["EV_Count"],
    df["Avg_Waiting_Time"],
    marker="o",
    linewidth=2
)

# Labels and title
plt.xlabel("Number of Electric Vehicles")
plt.ylabel("Average Waiting Time")
plt.title("Sensitivity Analysis: EV Count vs Average Waiting Time")

# Grid for readability
plt.grid(True)

# Save figure (IMPORTANT for paper)
plt.savefig("ev_count_sensitivity.png", dpi=300, bbox_inches="tight")

# Show plot
plt.show()
