#!/usr/bin/env python3
"""
DNSPerf (Cached values excluded)
---------------------------------------------------------------------------------------
DNSPerf is a simple Python script to benchmark the performance of various DNS resolvers.

Resolvers tested include:
  • Google (8.8.8.8, 8.8.4.4)
  • Cloudflare (1.1.1.1, 1.0.0.1)
  • Quad9 (9.9.9.9)
  • OpenDNS (208.67.222.222, 208.67.220.220)
  • Verisign (64.6.64.6, 64.6.65.6)

Tested domains include 31 popular sites like google.com, facebook.com, youtube.com, etc.
"""

import dns.resolver
import time
import statistics

# Define the resolvers (name: IP)
resolvers = {
    "Google 8.8.8.8": "8.8.8.8",
    "Google 8.8.4.4": "8.8.4.4",
    "Cloudflare 1.1.1.1": "1.1.1.1",
    "Cloudflare 1.0.0.1": "1.0.0.1",
    "Quad9 9.9.9.9": "9.9.9.9",
    "OpenDNS 208.67.222.222": "208.67.222.222",
    "OpenDNS 208.67.220.220": "208.67.220.220",
    "Verisign 64.6.64.6": "64.6.64.6",
    "Verisign 64.6.65.6": "64.6.65.6",
}

# List of domains to test (31 popular domains)
domains = [
    "google.com", "facebook.com", "youtube.com", "twitter.com", "amazon.com",
    "wikipedia.org", "reddit.com", "linkedin.com", "instagram.com", "apple.com",
    "microsoft.com", "netflix.com", "nytimes.com", "cnn.com", "bbc.com",
    "paypal.com", "espn.com", "stackoverflow.com", "github.com", "bitbucket.org",
    "tumblr.com", "dropbox.com", "bing.com", "wordpress.com", "blogspot.com",
    "quora.com", "ebay.com", "imdb.com", "pinterest.com", "whatsapp.com",
    "vimeo.com"
]

# Number of queries per domain/resolver combination
num_trials = 3

# Data structure to store results: { resolver: { domain: [times in ms] } }
results = {}

print("Starting DNS benchmarking...\n")
for resolver_name, resolver_ip in resolvers.items():
    results[resolver_name] = {}
    print(f"Testing resolver: {resolver_name} ({resolver_ip})")
    for domain in domains:
        results[resolver_name][domain] = []
        for trial in range(1, num_trials + 1):
            # Create a fresh resolver instance to avoid caching effects.
            r = dns.resolver.Resolver()
            r.nameservers = [resolver_ip]
            try:
                start = time.monotonic()
                # Query for A record (IPv4 address)
                r.resolve(domain, 'A')
                end = time.monotonic()
                elapsed = (end - start) * 1000.0  # Convert seconds to ms
                results[resolver_name][domain].append(elapsed)
                print(f"  {domain:20} trial {trial}: {elapsed:8.2f} ms")
            except Exception as e:
                # Record None for failed queries and log a warning.
                results[resolver_name][domain].append(None)
                print(f"  {domain:20} trial {trial}: ERROR ({e})")
    print("-" * 60)

# Print overall summary statistics per resolver, filtering out cached results (0 ms)
print("\nOverall DNS Resolution Performance (in ms, excluding cached 0 ms results):")
print("{:<30} {:>10} {:>10} {:>10} {:>10}".format("Resolver", "Avg", "Min", "Max", "StdDev"))
overall_stats = {}  # Store stats for final ranking
for resolver_name in resolvers.keys():
    all_times = []
    for domain in domains:
        for t in results[resolver_name][domain]:
            if t is not None and t > 0:  # Exclude cached responses (0 ms)
                all_times.append(t)
    if all_times:
        avg_time = statistics.mean(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        std_dev = statistics.stdev(all_times) if len(all_times) > 1 else 0.0
    else:
        avg_time = min_time = max_time = std_dev = float('nan')
    overall_stats[resolver_name] = {
        "avg": avg_time,
        "min": min_time,
        "max": max_time,
        "std": std_dev,
        "count": len(all_times)
    }
    print("{:<30} {:10.2f} {:10.2f} {:10.2f} {:10.2f}".format(
        resolver_name, avg_time, min_time, max_time, std_dev
    ))

# Detailed per-domain breakdown for each resolver (excluding cached 0 ms responses)
print("\nDetailed Domain Breakdown per Resolver (times in ms, excluding cached 0 ms results):")
for resolver_name in resolvers.keys():
    print(f"\nResolver: {resolver_name}")
    print("{:<20} {:>10} {:>10} {:>10} {:>10}".format("Domain", "Avg", "Min", "Max", "StdDev"))
    for domain in domains:
        times = [t for t in results[resolver_name][domain] if t is not None and t > 0]
        if times:
            avg = statistics.mean(times)
            min_val = min(times)
            max_val = max(times)
            std = statistics.stdev(times) if len(times) > 1 else 0.0
            print("{:<20} {:10.2f} {:10.2f} {:10.2f} {:10.2f}".format(domain, avg, min_val, max_val, std))
        else:
            print("{:<20} {:>10} {:>10} {:>10} {:>10}".format(domain, "N/A", "N/A", "N/A", "N/A"))

# Final Ranking Report: sort resolvers by average resolution time (lowest is best)
# If a resolver had zero valid queries, assign a high average for ranking.
ranking_stats = {}
for resolver_name, stats in overall_stats.items():
    if stats["count"] == 0 or stats["avg"] != stats["avg"]:  # Check for NaN
        ranking_stats[resolver_name] = float('inf')
    else:
        ranking_stats[resolver_name] = stats["avg"]

sorted_resolvers = sorted(ranking_stats.items(), key=lambda item: item[1])

print("\nFinal Ranking Report (excluding cached results):")
print("{:<5} {:<30} {:>10} {:>10} {:>10} {:>10}".format("Rank", "Resolver", "Avg", "Min", "Max", "StdDev"))
for rank, (resolver_name, avg) in enumerate(sorted_resolvers, start=1):
    stats = overall_stats[resolver_name]
    if stats["avg"] == float('inf'):
        avg_str = "N/A"
        min_str = "N/A"
        max_str = "N/A"
        std_str = "N/A"
    else:
        avg_str = f"{stats['avg']:.2f}"
        min_str = f"{stats['min']:.2f}"
        max_str = f"{stats['max']:.2f}"
        std_str = f"{stats['std']:.2f}"
    print("{:<5} {:<30} {:>10} {:>10} {:>10} {:>10}".format(rank, resolver_name, avg_str, min_str, max_str, std_str))

# Final calculation
if sorted_resolvers and sorted_resolvers[0][1] != float('inf'):
    best_resolver = sorted_resolvers[0][0]
    best_avg = overall_stats[best_resolver]["avg"]
    print(f"\nFinal Verdict: The fastest DNS resolver is '{best_resolver}' with an average resolution time of {best_avg:.2f} ms (cached values excluded).")
else:
    print("\nNo valid DNS resolution data was collected. Check your network or resolver configurations.")
