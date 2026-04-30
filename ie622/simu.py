import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon, poisson
from math import factorial

# --- 1. Simulation Parameters ---
lam = 5.0      # Rate (lambda): Average number of events per unit time
T = 1000.0     # Total simulation time
dt = 1.0       # Fixed time interval for checking the Poisson property

# --- 2. Generate the Poisson Process ---
# Estimate number of events needed (with a safety buffer)
expected_events = int(lam * T * 1.2)

# Inter-arrival times are exponentially distributed: ~ Exp(lambda)
# Note: numpy's exponential takes 'scale' which is 1/lambda
inter_arrivals = np.random.exponential(scale=1.0/lam, size=expected_events)

# Arrival times are the cumulative sum of inter-arrival times
arrival_times = np.cumsum(inter_arrivals)

# Keep only the arrivals that happen before our max time T
arrival_times = arrival_times[arrival_times < T]
actual_events = len(arrival_times)

# --- 3. Visualization ---
fig, axs = plt.subplots(1, 3, figsize=(18, 5))

# Plot 1: The Counting Process N(t) (Zoomed in for visibility)
# We only plot the first 10 units of time so you can actually see the steps
zoom_T = 10.0
zoom_arrivals = arrival_times[arrival_times < zoom_T]
# Create step function data
y_vals = np.arange(1, len(zoom_arrivals) + 1)

axs[0].step(zoom_arrivals, y_vals, where='post', color='b', linewidth=2)
axs[0].plot(zoom_arrivals, y_vals, 'ro', alpha=0.5) # Mark the exact arrival points
axs[0].set_title(f'Counting Process N(t)\n(First {zoom_T} time units)')
axs[0].set_xlabel('Time (t)')
axs[0].set_ylabel('Number of Events N(t)')
axs[0].grid(True, alpha=0.3)

# Plot 2: Distribution of Inter-arrival Times
# Should match an Exponential Distribution PDF
count, bins, ignored = axs[1].hist(inter_arrivals[:actual_events], bins=50, density=True, 
                                   alpha=0.6, color='g', edgecolor='black')
# Theoretical Exponential PDF: f(x) = lambda * exp(-lambda * x)
x_exp = np.linspace(0, max(bins), 100)
y_exp = lam * np.exp(-lam * x_exp)
axs[1].plot(x_exp, y_exp, 'r-', linewidth=2, label='Theoretical Exp(λ)')
axs[1].set_title('Inter-arrival Times Distribution')
axs[1].set_xlabel('Time between events')
axs[1].set_ylabel('Density')
axs[1].legend()

# Plot 3: Number of events in fixed intervals dt
# Should match a Poisson Distribution PMF
# Create bins of size dt
time_bins = np.arange(0, T + dt, dt)
events_per_bin, _ = np.histogram(arrival_times, bins=time_bins)

# Count frequencies of 0 events, 1 event, 2 events, etc.
max_events = max(events_per_bin)
event_counts = np.bincount(events_per_bin)
x_poisson = np.arange(len(event_counts))
empirical_probs = event_counts / len(events_per_bin)

axs[2].bar(x_poisson, empirical_probs, alpha=0.6, color='orange', edgecolor='black', label='Simulated')

# Theoretical Poisson PMF: P(k) = ( (lambda*dt)^k * exp(-lambda*dt) ) / k!
mu = lam * dt
y_poisson = poisson.pmf(x_poisson, mu)
axs[2].plot(x_poisson, y_poisson, 'ro-', linewidth=2, label=f'Theoretical Poisson(λ*dt)')
axs[2].set_title(f'Events per fixed interval (Δt={dt})')
axs[2].set_xlabel('Number of events in interval')
axs[2].set_ylabel('Probability')
axs[2].legend()

plt.tight_layout()
plt.show()